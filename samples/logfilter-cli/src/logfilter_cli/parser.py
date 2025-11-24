"""ログ行のパースと日付抽出を扱うモジュール。

主な機能:
- `parse_line` で 1 行をパースし、日付やトークンを保持した `LogEntry` を返す。
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import re
from typing import Iterable

DATE_PREFIX_PATTERN = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})")


@dataclasses.dataclass(frozen=True)
class LogEntry:
    """ログ 1 行分の構造化データ。

    Attributes:
        date: 行頭に YYYY-MM-DD があればその日付。形式不正または欠如の場合は None。
        tokens: スペース区切りで分割したトークン一覧。
        raw: 元の行テキスト。
    """

    date: dt.date | None
    tokens: list[str]
    raw: str


def _parse_date(token: str) -> dt.date | None:
    """YYYY-MM-DD 形式の文字列を日付に変換する。

    不正な値は None を返す。日付フィルタは行頭限定のため、単一トークンのみ扱う。
    """

    try:
        return dt.date.fromisoformat(token)
    except ValueError:
        return None


def parse_line(line: str) -> LogEntry:
    """1 行のログ文字列をパースし、日付とトークンを返す。

    行頭が YYYY-MM-DD で始まる場合のみ日付フィルタ対象とし、形式不正なら None を設定する。
    """

    tokens = line.strip("\\n").split()

    date: dt.date | None = None
    if tokens:
        # 行頭が日付形式かだけ確認し、以降の時刻やメッセージはフィルタ対象外。
        if DATE_PREFIX_PATTERN.match(tokens[0]):
            date = _parse_date(tokens[0])

    return LogEntry(date=date, tokens=tokens, raw=line)
