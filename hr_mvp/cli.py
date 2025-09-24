"""Command line helper around :mod:`hr_mvp.roster`.

Usage examples::

    # 전체 요약 정보 출력
    python -m hr_mvp.cli summary

    # 특정 팀 이름으로 검색
    python -m hr_mvp.cli search --keyword GURM

    # 60일 이내에 시용(수습) 종료 예정자 확인
    python -m hr_mvp.cli probation --within 60
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Optional, Sequence

from .roster import EmployeeRecord, EmployeeRoster, load_default_roster


def _load_roster(path: Optional[Path]) -> EmployeeRoster:
    if path is None:
        return load_default_roster()
    return EmployeeRoster.from_csv(path)


def _describe_months(months: Optional[float]) -> str:
    if months is None:
        return "-"
    rounded = round(months)
    years = int(rounded // 12)
    remaining_months = int(rounded % 12)
    parts = []
    if years:
        parts.append(f"{years}년")
    if remaining_months:
        parts.append(f"{remaining_months}개월")
    if not parts:
        parts.append("0개월")
    if rounded != months:
        parts.append(f"(약 {months:.1f}개월)")
    return " ".join(parts)


def cmd_summary(roster: EmployeeRoster) -> None:
    active_count = len(roster.active())
    total_count = len(roster)
    avg_tenure = roster.average_tenure_months()

    print("================")
    print("인사 현황 요약")
    print("================")
    print(f"전체 인원: {total_count}명")
    print(f"재직 인원: {active_count}명")
    print(f"평균 근속기간(재직자): {_describe_months(avg_tenure)}")
    print()

    print("[팀별 재직 인원]")
    for team, count in roster.summary_by_team().items():
        print(f"- {team}: {count}명")
    print()

    print("[재직구분별 인원]")
    for status, count in roster.summary_by_status().items():
        print(f"- {status}: {count}명")


def cmd_list(roster: EmployeeRoster, active_only: bool = False) -> None:
    employees = roster.active() if active_only else list(roster)
    if not employees:
        print("표시할 인원이 없습니다.")
        return
    print(roster.to_table(employees))


def cmd_search(roster: EmployeeRoster, keyword: str) -> None:
    results = roster.search(keyword)
    if not results:
        print(f"'{keyword}'에 해당하는 인원을 찾을 수 없습니다.")
        return
    print(f"총 {len(results)}명 발견")
    print(roster.to_table(results))


def cmd_probation(roster: EmployeeRoster, within_days: int, reference_date: Optional[date]) -> None:
    results = roster.upcoming_probation_end(within_days=within_days, reference_date=reference_date)
    if not results:
        print("해당 기간 내 시용 종료 예정자가 없습니다.")
        return
    print("시용 종료 예정자 목록")
    print("--------------------")
    for employee in results:
        remaining = employee.probation_days_remaining(reference_date)
        end_date = employee.probation_end.strftime("%Y-%m-%d") if employee.probation_end else "-"
        print(f"{employee.name} ({employee.team}) - 종료일: {end_date} / D-{remaining}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="인사 명부 분석 도구")
    parser.add_argument(
        "--path",
        type=Path,
        help="다른 CSV 파일을 사용하고 싶으면 경로를 지정하세요.",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("summary", help="요약 통계 확인")

    list_parser = subparsers.add_parser("list", help="직원 목록 출력")
    list_parser.add_argument(
        "--active-only",
        action="store_true",
        help="재직 중인 인원만 보여줍니다.",
    )

    search_parser = subparsers.add_parser("search", help="이름/팀/직책 검색")
    search_parser.add_argument("--keyword", required=True, help="검색어(부분 일치)")

    probation_parser = subparsers.add_parser("probation", help="시용 종료 예정자 확인")
    probation_parser.add_argument(
        "--within",
        type=int,
        default=30,
        help="며칠 이내 종료 예정자를 볼지 지정합니다 (기본 30일).",
    )
    probation_parser.add_argument(
        "--reference-date",
        type=lambda value: date.fromisoformat(value),
        help="기준일(YYYY-MM-DD). 지정하지 않으면 오늘 날짜.",
    )

    return parser


def run_interactive_menu(roster: EmployeeRoster) -> None:
    """간단한 텍스트 메뉴를 통해 주요 기능을 실행한다."""

    def _pause() -> None:
        input("\n계속하려면 Enter 키를 누르세요...")

    while True:
        print("==========================")
        print("인사 명부 도우미 (MVP)")
        print("==========================")
        print("1. 전체 요약 보기")
        print("2. 전체 직원 목록 보기")
        print("3. 재직자만 목록 보기")
        print("4. 이름/팀/직책 검색")
        print("5. 시용 종료 예정자 확인")
        print("Q. 종료")

        choice = input("원하는 번호를 입력하세요: ").strip().lower()
        print()

        if choice in {"q", "quit", "exit"}:
            print("프로그램을 종료합니다.")
            return
        if choice == "1":
            cmd_summary(roster)
            _pause()
        elif choice == "2":
            cmd_list(roster, active_only=False)
            _pause()
        elif choice == "3":
            cmd_list(roster, active_only=True)
            _pause()
        elif choice == "4":
            keyword = input("검색어를 입력하세요: ").strip()
            if not keyword:
                print("검색어를 입력하지 않았습니다.")
            else:
                print()
                cmd_search(roster, keyword)
            _pause()
        elif choice == "5":
            within_raw = input("며칠 이내 종료 예정자를 볼까요? (기본 30): ").strip()
            if within_raw:
                try:
                    within_days = int(within_raw)
                except ValueError:
                    print("숫자로 입력해주세요.")
                    _pause()
                    continue
            else:
                within_days = 30
            reference_raw = input("기준일이 있다면 YYYY-MM-DD 형식으로 입력하세요 (엔터시 오늘 기준): ").strip()
            reference_date = None
            if reference_raw:
                try:
                    reference_date = date.fromisoformat(reference_raw)
                except ValueError:
                    print("날짜 형식이 올바르지 않습니다.")
                    _pause()
                    continue
            print()
            cmd_probation(roster, within_days=within_days, reference_date=reference_date)
            _pause()
        else:
            print("지원하지 않는 선택입니다. 다시 입력해주세요.")
            _pause()
        print()


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    roster = _load_roster(args.path)

    if args.command is None:
        run_interactive_menu(roster)
        return

    if args.command == "summary":
        cmd_summary(roster)
    elif args.command == "list":
        cmd_list(roster, active_only=args.active_only)
    elif args.command == "search":
        cmd_search(roster, args.keyword)
    elif args.command == "probation":
        cmd_probation(roster, args.within, args.reference_date)
    else:
        parser.error("알 수 없는 명령입니다.")


if __name__ == "__main__":
    main()
