import pytest

from beginner_budget_cli import build_report, calculate_budget, parse_amounts


def test_parse_amounts_returns_integer_list():
    assert parse_amounts("1200, 850,3000") == [1200, 850, 3000]


def test_parse_amounts_rejects_empty_input():
    with pytest.raises(ValueError, match="at least one"):
        parse_amounts("   ")


def test_parse_amounts_rejects_negative_value():
    with pytest.raises(ValueError, match="0 or greater"):
        parse_amounts("100,-50")


def test_calculate_budget_builds_expected_values():
    summary = calculate_budget(30000, [1200, 850, 3000])

    assert summary.count == 3
    assert summary.total_spent == 5050
    assert summary.remaining == 24950
    assert summary.status == "Comfortable"


def test_build_report_formats_output():
    summary = calculate_budget(10000, [2500, 3000, 1500])

    report = build_report(summary)

    assert "Budget Report" in report
    assert "Total spent: 7000 yen" in report
    assert "Status: Watch spending" in report
