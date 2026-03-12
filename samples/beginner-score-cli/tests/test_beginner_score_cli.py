import pytest

from beginner_score_cli import build_report, calculate_summary, parse_scores


def test_parse_scores_returns_integer_list():
    assert parse_scores("80, 75,92") == [80, 75, 92]


def test_parse_scores_rejects_empty_input():
    with pytest.raises(ValueError, match="1つ以上"):
        parse_scores("   ")


def test_parse_scores_rejects_out_of_range_value():
    with pytest.raises(ValueError, match="0から100"):
        parse_scores("50,120")


def test_calculate_summary_builds_expected_values():
    summary = calculate_summary([80, 75, 92])

    assert summary.count == 3
    assert summary.average == pytest.approx(82.3333, rel=1e-4)
    assert summary.highest == 92
    assert summary.lowest == 75
    assert summary.grade == "B"


def test_build_report_formats_output():
    summary = calculate_summary([90, 88, 94])

    report = build_report("Aki", summary)

    assert "Akiさんの結果" in report
    assert "平均点: 90.7" in report
    assert "評価: S" in report
