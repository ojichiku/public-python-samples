from __future__ import annotations

from pathlib import Path

import python_common_sample.codes as codes_module

# API インポート。内部キャッシュ書き換えのためモジュール自体も参照。
from python_common_sample import get_codes, get_value, reload_codes
from python_common_sample.codes import CodeItem, FileCodeSource


def setup_module(_) -> None:
    """各テスト開始前に既定の CSV でキャッシュを初期化する。"""

    reload_codes()


def teardown_module(_) -> None:
    """テスト後にデフォルトソースへ戻し、副作用を残さない。"""

    codes_module._source = FileCodeSource()
    reload_codes()


def test_get_codes_returns_enabled_items_sorted() -> None:
    """有効コードのみ sort_order 順で取得できるか。"""

    gender_codes = get_codes("GENDER")
    assert [item.code for item in gender_codes] == ["1", "2"]


def test_get_codes_can_include_disabled_items() -> None:
    """only_enabled=False で無効コードが含まれるか。"""

    gender_codes = get_codes("GENDER", only_enabled=False)
    assert [item.code for item in gender_codes] == ["1", "2", "9"]


def test_get_value_returns_matching_value() -> None:
    """存在するコードから value が取得できるか。"""

    assert get_value("STATUS", "1") == "有効"


def test_get_value_returns_default_when_missing() -> None:
    """存在しないコードで default 指定の有無を確認。"""

    assert get_value("STATUS", "999", default="unknown") == "unknown"
    assert get_value("STATUS", "999") is None


def test_reload_codes_reflects_updates(tmp_path: Path) -> None:
    """CSV を書き換えた後 reload_codes で反映されるか。"""

    csv_path = tmp_path / "codes.csv"
    csv_path.write_text(
        "code_group,code,value,sort_order,enabled,extra\n" "PREF,01,北海道,1,true,\n",
        encoding="utf-8",
    )
    codes_module._source = FileCodeSource(csv_path)
    reload_codes()
    assert get_value("PREF", "01") == "北海道"

    csv_path.write_text(
        "code_group,code,value,sort_order,enabled,extra\n" "PREF,01,道北,1,true,\n",
        encoding="utf-8",
    )
    reload_codes()
    assert get_value("PREF", "01") == "道北"


def test_cache_prevents_duplicate_reads() -> None:
    """キャッシュ使用でソース読み込みが 1 度だけか確認。"""

    class DummySource:
        def __init__(self) -> None:
            self.calls = 0

        def load_all(self) -> list[CodeItem]:
            self.calls += 1
            return [
                CodeItem(code_group="TMP", code="1", value="A", sort_order=1),
            ]

    dummy = DummySource()
    codes_module._source = dummy
    reload_codes()
    assert dummy.calls == 1

    get_codes("TMP")
    get_value("TMP", "1")
    assert dummy.calls == 1
