from __future__ import annotations

import sys
from pathlib import Path

import pytest

# src を import パスに追加
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from csvfilter_cli import filters


def test_contains_condition_matches() -> None:
    cond = filters.ContainsCondition("abc")
    assert cond.matches("xyzabc123")
    assert not cond.matches("XYZ")


def test_regex_condition_matches() -> None:
    cond = filters.RegexCondition(filters.re.compile(r"^foo"))
    assert cond.matches("foobar")
    assert not cond.matches("barfoo")


def test_build_condition_invalid_operator() -> None:
    with pytest.raises(ValueError):
        filters.build_condition("unknown", "x")


def test_build_condition_invalid_regex_error_message() -> None:
    with pytest.raises(ValueError) as excinfo:
        filters.build_condition("regex", "(")
    assert "正規表現が不正" in str(excinfo.value)
