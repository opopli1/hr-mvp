"""Utilities to work with the employee roster CSV file.

This module intentionally keeps the logic straightforward so that a
non-developer can follow how data is loaded and analysed.  The
:class:`EmployeeRoster` class is the main entry point that provides handy
helpers for listing staff, computing summaries and spotting upcoming
probation deadlines.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence


def _parse_date(value: str) -> Optional[date]:
    value = value.strip()
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_int(value: str) -> Optional[int]:
    value = value.strip()
    if not value:
        return None
    return int(value)


def _format_months(months: Optional[int]) -> str:
    if months is None:
        return "-"
    years, remaining_months = divmod(months, 12)
    if years and remaining_months:
        return f"{years}년 {remaining_months}개월"
    if years:
        return f"{years}년"
    return f"{remaining_months}개월"


@dataclass
class EmployeeRecord:
    """Represents a single row from the roster CSV file."""

    employee_id: str
    payroll_id: str
    name: str
    gender: str
    birthdate: Optional[date]
    age_group: str
    team: str
    part: str
    title: str
    start_date: Optional[date]
    probation_end: Optional[date]
    resignation_date: Optional[date]
    tenure_text: str
    prior_experience_text: str
    total_experience_text: str
    contract_type: str
    phone: str
    email: str
    work_location: str
    job_type: str
    employment_status: str
    employment_status_detail: str
    prior_experience_months: Optional[int]
    current_experience_months: Optional[int]
    total_experience_months: Optional[int]

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "EmployeeRecord":
        return cls(
            employee_id=row["employee_id"].strip(),
            payroll_id=row["payroll_id"].strip(),
            name=row["name"].strip(),
            gender=row["gender"].strip(),
            birthdate=_parse_date(row["birthdate"]),
            age_group=row["age_group"].strip(),
            team=row["team"].strip(),
            part=row["part"].strip(),
            title=row["title"].strip(),
            start_date=_parse_date(row["start_date"]),
            probation_end=_parse_date(row["probation_end"]),
            resignation_date=_parse_date(row["resignation_date"]),
            tenure_text=row["tenure_text"].strip(),
            prior_experience_text=row["prior_experience_text"].strip(),
            total_experience_text=row["total_experience_text"].strip(),
            contract_type=row["contract_type"].strip(),
            phone=row["phone"].strip(),
            email=row["email"].strip(),
            work_location=row["work_location"].strip(),
            job_type=row["job_type"].strip(),
            employment_status=row["employment_status"].strip(),
            employment_status_detail=row["employment_status_detail"].strip(),
            prior_experience_months=_parse_int(row["prior_experience_months"]),
            current_experience_months=_parse_int(row["current_experience_months"]),
            total_experience_months=_parse_int(row["total_experience_months"]),
        )

    @property
    def is_active(self) -> bool:
        if self.resignation_date is not None:
            return False
        return "재직" in self.employment_status

    @property
    def tenure_months(self) -> Optional[int]:
        return self.current_experience_months

    def tenure_display(self) -> str:
        if self.tenure_months is not None:
            return _format_months(self.tenure_months)
        return self.tenure_text or "-"

    def total_experience_display(self) -> str:
        if self.total_experience_months is not None:
            return _format_months(self.total_experience_months)
        return self.total_experience_text or "-"

    def matches(self, keyword: str) -> bool:
        keyword_lower = keyword.lower()
        return (
            keyword_lower in self.name.lower()
            or keyword_lower in self.team.lower()
            or keyword_lower in self.part.lower()
            or keyword_lower in self.title.lower()
        )

    def probation_days_remaining(self, reference_date: Optional[date] = None) -> Optional[int]:
        if self.probation_end is None:
            return None
        reference_date = reference_date or date.today()
        delta = self.probation_end - reference_date
        return delta.days


class EmployeeRoster:
    """Collection of :class:`EmployeeRecord` objects with helper methods."""

    def __init__(self, employees: Sequence[EmployeeRecord]):
        self._employees: List[EmployeeRecord] = list(employees)

    def __iter__(self) -> Iterable[EmployeeRecord]:
        return iter(self._employees)

    def __len__(self) -> int:
        return len(self._employees)

    @property
    def employees(self) -> Sequence[EmployeeRecord]:
        return tuple(self._employees)

    @classmethod
    def from_csv(cls, path: Path) -> "EmployeeRoster":
        with path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            employees = [EmployeeRecord.from_row(row) for row in reader]
        return cls(employees)

    def active(self) -> List[EmployeeRecord]:
        return [employee for employee in self._employees if employee.is_active]

    def summary_by_team(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for employee in self.active():
            key = employee.team or "(미지정)"
            counts[key] = counts.get(key, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: item[0]))

    def summary_by_status(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for employee in self._employees:
            key = employee.employment_status or "(미지정)"
            counts[key] = counts.get(key, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: item[0]))

    def average_tenure_months(self, active_only: bool = True) -> Optional[float]:
        population = self.active() if active_only else list(self._employees)
        tenures = [emp.tenure_months for emp in population if emp.tenure_months is not None]
        if not tenures:
            return None
        return sum(tenures) / len(tenures)

    def search(self, keyword: str) -> List[EmployeeRecord]:
        keyword = keyword.strip()
        if not keyword:
            return []
        return [employee for employee in self._employees if employee.matches(keyword)]

    def upcoming_probation_end(
        self, within_days: int = 30, reference_date: Optional[date] = None
    ) -> List[EmployeeRecord]:
        reference_date = reference_date or date.today()
        window_end = reference_date + timedelta(days=within_days)
        results: List[EmployeeRecord] = []
        for employee in self.active():
            if employee.probation_end is None:
                continue
            if reference_date <= employee.probation_end <= window_end:
                results.append(employee)
        results.sort(key=lambda emp: emp.probation_end or date.max)
        return results

    def to_table(self, employees: Sequence[EmployeeRecord]) -> str:
        headers = ["사번", "이름", "팀", "직책", "고용형태", "근속기간", "총경력"]
        rows = []
        for employee in employees:
            rows.append(
                [
                    employee.employee_id,
                    employee.name,
                    employee.team or "-",
                    employee.title or "-",
                    employee.contract_type or "-",
                    employee.tenure_display(),
                    employee.total_experience_display(),
                ]
            )

        col_widths = [len(header) for header in headers]
        for row in rows:
            for idx, cell in enumerate(row):
                col_widths[idx] = max(col_widths[idx], len(str(cell)))

        def format_row(row_values: Sequence[str]) -> str:
            return " | ".join(
                str(value).ljust(col_widths[idx]) for idx, value in enumerate(row_values)
            )

        lines = [format_row(headers), "-+-".join("-" * width for width in col_widths)]
        lines.extend(format_row(row) for row in rows)
        return "\n".join(lines)


def load_default_roster() -> EmployeeRoster:
    """Load the roster.csv file bundled with the project."""

    default_path = Path(__file__).resolve().parent.parent / "data" / "roster.csv"
    return EmployeeRoster.from_csv(default_path)
