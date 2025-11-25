"""キーワードフィルタと日付フィルタを扱うモジュール。"""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterable

from .parser import LogEntry


def keyword_match(entry: LogEntry, keyword: str, *, case_sensitive: bool = False) -> bool:
    """部分一致によるキーワードフィルタを評価する。

    デフォルトは大文字小文字を区別しない。CLI の仕様に合わせ、1 キーワードのみを扱う。
    """

    haystack = entry.raw
    needle = keyword
    if not case_sensitive:
        haystack = haystack.lower()
        needle = keyword.lower()
    return needle in haystack


def date_in_range(
    entry: LogEntry, date_from: dt.date | None, date_to: dt.date | None
) -> bool:
    """日付範囲フィルタを評価する。

    - date_from/date_to が両方 None の場合は True（フィルタなし）。
    - 行頭に日付が無い場合、日付フィルタを要求されたときは False を返す。
    """

    if date_from is None and date_to is None:
        return True

    if entry.date is None:
        # 仕様: 日付フィルタ指定時、日付を持たない行は結果に含めない。
        return False

    if date_from is not None and entry.date < date_from:
        return False
    if date_to is not None and entry.date > date_to:
        return False
    return True


def filter_entries(
    entries: Iterable[LogEntry],
    *,
    keyword: str | None,
    date_from: dt.date | None,
    date_to: dt.date | None,
    case_sensitive: bool = False,
) -> list[LogEntry]:
    """キーワードと日付の AND 条件でログをフィルタするヘルパー。"""

    filtered: list[LogEntry] = []
    for entry in entries:
        if keyword is not None and not keyword_match(entry, keyword, case_sensitive=case_sensitive):
            continue
        if not date_in_range(entry, date_from=date_from, date_to=date_to):
            continue
        filtered.append(entry)
    return filtered
