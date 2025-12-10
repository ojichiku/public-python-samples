from __future__ import annotations

import re
import time
from datetime import date, datetime

import pytest

import python_common_sample.datetime as dt_utils


def test_now_str_returns_default_format() -> None:
    """now_str が既定フォーマットの文字列を返すか。"""

    value = dt_utils.now_str()
    datetime.strptime(value, dt_utils.DISPLAY_DATETIME_FORMAT)


def test_now_str_accepts_custom_format() -> None:
    """now_str にフォーマットを指定できるか。"""

    fmt = "%Y%m%d"
    value = dt_utils.now_str(fmt)
    datetime.strptime(value, fmt)


def test_today_str_returns_date_string() -> None:
    """today_str が日付フォーマットの文字列を返すか。"""

    value = dt_utils.today_str()
    datetime.strptime(value, dt_utils.DISPLAY_DATE_FORMAT)


def test_now_for_filename_matches_pattern() -> None:
    """now_for_filename がファイル名向け書式を返すか。"""

    value = dt_utils.now_for_filename()
    assert re.fullmatch(r"\d{8}_\d{6}", value)


def test_parse_datetime_and_date() -> None:
    """parse_datetime / parse_date が正しく変換するか。"""

    dt_value = "2025/12/08 22:30:01"
    parsed_dt = dt_utils.parse_datetime(dt_value)
    assert parsed_dt == datetime(2025, 12, 8, 22, 30, 1)

    date_value = "2025-12-08"
    parsed_date = dt_utils.parse_date(date_value)
    assert parsed_date == date(2025, 12, 8)


def test_parse_datetime_invalid_raises() -> None:
    """不正な文字列を parse_datetime/parse_date に渡すと ValueError になるか。"""

    with pytest.raises(ValueError):
        dt_utils.parse_datetime("invalid")
    with pytest.raises(ValueError):
        dt_utils.parse_date("invalid")


def test_timer_measures_elapsed_time() -> None:
    """Timer が経過秒数を計測できるか。"""

    with dt_utils.Timer() as timer:
        time.sleep(0.01)
    assert timer.elapsed is not None
    assert timer.elapsed >= 0.0
