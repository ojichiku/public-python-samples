"""parser モジュールの挙動を検証する pytest テスト。

想定インターフェイス:
- parser.parse_line(line: str) -> LogEntry
  - LogEntry は少なくとも以下の属性を持つ:
    - date: datetime.date | None（先頭が YYYY-MM-DD 形式ならパース結果、それ以外は None）
    - tokens: list[str]（スペース区切りで分割したトークン）
    - raw: str（元の行テキスト）
"""

from __future__ import annotations

import datetime as dt

from logfilter_cli import parser


def test_parse_line_with_valid_date():
    line = "2025-11-01 12:30:10 INFO User logged in"

    entry = parser.parse_line(line)

    assert entry.date == dt.date(2025, 11, 1)
    assert entry.tokens[0] == "2025-11-01"
    assert entry.tokens[2] == "INFO"
    assert entry.raw == line


def test_parse_line_without_date_prefix():
    line = "NoDateLine This line does not start with a date"

    entry = parser.parse_line(line)

    assert entry.date is None
    assert entry.tokens[0] == "NoDateLine"
    assert entry.raw == line


def test_parse_line_with_malformed_date():
    line = "2025-99-99 invalid date here"

    entry = parser.parse_line(line)

    assert entry.date is None
    # 日付が不正でもトークン化は行う前提
    assert entry.tokens[0] == "2025-99-99"
    assert entry.raw == line
