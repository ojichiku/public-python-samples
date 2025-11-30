"""filters モジュールの挙動を検証する pytest テスト。

想定インターフェイス:
- filters.keyword_match(entry: LogEntry, keyword: str, *, case_sensitive: bool = False) -> bool
- filters.date_in_range(entry: LogEntry, date_from: datetime.date | None, date_to: datetime.date | None) -> bool
- filters.filter_entries(entries: Iterable[LogEntry], *, keyword: str | None, date_from: datetime.date | None, date_to: datetime.date | None, case_sensitive: bool = False) -> list[LogEntry]
"""

from __future__ import annotations

import datetime as dt

from logfilter_cli import filters, parser


def test_keyword_filter_partial_match_default_case_insensitive():
    entries = [
        parser.parse_line("2025-11-01 INFO Service started"),
        parser.parse_line("2025-11-01 ERROR Failed to connect"),
        parser.parse_line("NoDateLine simple message"),
    ]

    matched = [e for e in entries if filters.keyword_match(e, "error")]

    assert len(matched) == 1
    assert "ERROR" in matched[0].raw


def test_keyword_filter_respects_case_sensitive_flag():
    entries = [
        parser.parse_line("2025-11-01 ERROR Failed to connect"),
    ]

    insensitive = [e for e in entries if filters.keyword_match(e, "error")]
    sensitive = [
        e for e in entries if filters.keyword_match(e, "error", case_sensitive=True)
    ]

    assert len(insensitive) == 1
    assert len(sensitive) == 0


def test_date_filter_is_inclusive_and_skips_missing_dates():
    entries = [
        parser.parse_line("2025-11-01 INFO Service started"),
        parser.parse_line("2025-11-02 ERROR Failed to connect"),
        parser.parse_line("2025-11-03 INFO Recovered"),
        parser.parse_line("NoDateLine This line does not start with a date"),
    ]

    in_range = [
        e
        for e in entries
        if filters.date_in_range(
            e, date_from=dt.date(2025, 11, 1), date_to=dt.date(2025, 11, 2)
        )
    ]

    assert {e.raw for e in in_range} == {
        "2025-11-01 INFO Service started",
        "2025-11-02 ERROR Failed to connect",
    }


def test_filter_entries_combines_keyword_and_date_filters():
    entries = [
        parser.parse_line("2025-11-01 INFO boot complete"),
        parser.parse_line("2025-11-02 ERROR database down"),
        parser.parse_line("2025-11-03 ERROR late error"),
        parser.parse_line("NoDateLine ERROR without date"),
    ]

    filtered = filters.filter_entries(
        entries,
        keyword="error",
        date_from=dt.date(2025, 11, 1),
        date_to=dt.date(2025, 11, 2),
    )

    assert len(filtered) == 1
    assert filtered[0].raw == "2025-11-02 ERROR database down"
