"""日時処理をまとめたユーティリティモジュール。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date as _date
from datetime import datetime
from time import perf_counter
from types import TracebackType

__all__ = [
    "DISPLAY_DATETIME_FORMAT",
    "DISPLAY_DATE_FORMAT",
    "FILENAME_DATETIME_FORMAT",
    "Timer",
    "now_for_filename",
    "now_str",
    "parse_date",
    "parse_datetime",
    "today_str",
]

DISPLAY_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"
DISPLAY_DATE_FORMAT = "%Y-%m-%d"
FILENAME_DATETIME_FORMAT = "%Y%m%d_%H%M%S"


def now_str(fmt: str | None = None) -> str:
    """現在のローカル日時を文字列にして返す。

    Args:
        fmt: 使用するフォーマット。None の場合は DISPLAY_DATETIME_FORMAT。

    Returns:
        指定フォーマットで表した日時文字列。
    """

    format_str = fmt or DISPLAY_DATETIME_FORMAT
    return datetime.now().strftime(format_str)


def today_str(fmt: str | None = None) -> str:
    """本日の日付を文字列で返す。

    Args:
        fmt: 使用するフォーマット。None の場合は DISPLAY_DATE_FORMAT。

    Returns:
        指定フォーマットで表した日付文字列。
    """

    format_str = fmt or DISPLAY_DATE_FORMAT
    return _date.today().strftime(format_str)


def now_for_filename() -> str:
    """ファイル名に利用しやすい現在日時文字列を返す。

    Returns:
        `YYYYMMDD_HHMMSS` 形式の文字列。
    """

    return datetime.now().strftime(FILENAME_DATETIME_FORMAT)


def parse_datetime(value: str, fmt: str | None = None) -> datetime:
    """日時文字列を datetime オブジェクトに変換する。

    Args:
        value: 変換対象の文字列。
        fmt: 使用するフォーマット。None の場合は DISPLAY_DATETIME_FORMAT。

    Returns:
        解析した datetime。

    Raises:
        ValueError: 文字列がフォーマットに一致しない場合。
    """

    format_str = fmt or DISPLAY_DATETIME_FORMAT
    return datetime.strptime(value, format_str)


def parse_date(value: str, fmt: str | None = None) -> _date:
    """日付文字列を date オブジェクトに変換する。

    Args:
        value: 変換対象の文字列。
        fmt: 使用するフォーマット。None の場合は DISPLAY_DATE_FORMAT。

    Returns:
        解析した date。

    Raises:
        ValueError: 文字列がフォーマットに一致しない場合。
    """

    format_str = fmt or DISPLAY_DATE_FORMAT
    return datetime.strptime(value, format_str).date()


@dataclass
class Timer:
    """処理時間を計測するためのコンテキストマネージャ。"""

    start: float | None = None
    end: float | None = None
    elapsed: float | None = None

    def __enter__(self) -> "Timer":
        """計測を開始する。

        Returns:
            自身のインスタンス。
        """

        self.start = perf_counter()
        self.end = None
        self.elapsed = None
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        """計測を終了し、経過秒数を記録する。

        Args:
            exc_type: 例外の型。
            exc: 例外インスタンス。
            tb: トレースバック。

        Returns:
            False を返し、例外をそのまま伝播させる。
        """

        self.end = perf_counter()
        if self.start is None:
            self.elapsed = 0.0
        else:
            self.elapsed = self.end - self.start
        return False
