from datetime import date
from pathlib import Path

from hr_mvp.roster import EmployeeRoster, load_default_roster


def test_load_default_roster(tmp_path):
    roster = load_default_roster()
    assert len(roster) == 6
    assert roster.employees[0].name == "이종윤"


def test_summary_by_team():
    roster = load_default_roster()
    summary = roster.summary_by_team()
    assert summary["GURM"] == 2
    assert summary["임원"] == 1


def test_search_by_name():
    roster = load_default_roster()
    results = roster.search("이호")
    assert len(results) == 1
    assert results[0].team == "GURM"


def test_probation_window():
    roster = load_default_roster()
    reference = date(2016, 8, 1)
    results = roster.upcoming_probation_end(within_days=120, reference_date=reference)
    assert {employee.name for employee in results} == {"이다영"}
