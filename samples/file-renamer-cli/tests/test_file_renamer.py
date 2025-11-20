"""file_renamerモジュールのユニットテスト。"""

from __future__ import annotations

from pathlib import Path

import pytest

from file_renamer import rename_files, replace_in_filenames


def _make_files(base_dir: Path, names: list[str]) -> None:
    """テスト用の空ファイルをまとめて作成する。"""
    for name in names:
        (base_dir / name).write_text("data", encoding="utf-8")


def test_rename_files_generates_sequential_names(tmp_path: Path) -> None:
    """rename_filesが連番でリネームし、結果を返すことを確認する。"""
    original = ["b.txt", "a.md", "c.txt"]
    _make_files(tmp_path, original)

    changes = rename_files(tmp_path, prefix="blog_", digits=3)

    assert changes == [
        ("a.md", "blog_001.md"),
        ("b.txt", "blog_002.txt"),
        ("c.txt", "blog_003.txt"),
    ]
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "blog_001.md",
        "blog_002.txt",
        "blog_003.txt",
    ]


def test_rename_files_expands_digit_width(tmp_path: Path) -> None:
    """digitsより多いファイルがある場合に桁数が自動拡張されることを確認する。"""
    original = [f"file{i}.txt" for i in range(1, 11)]
    _make_files(tmp_path, original)

    changes = rename_files(tmp_path, prefix="series_", digits=1)

    new_names = {new for _, new in changes}
    assert "series_01.txt" in new_names
    assert "series_09.txt" in new_names
    # 10番目は2桁のまま末尾に配置される
    assert "series_10.txt" in new_names


def test_replace_in_filenames_updates_matching_files(tmp_path: Path) -> None:
    """replace_in_filenamesで部分文字列の置換が行われることを確認する。"""
    original = ["draft_01.txt", "draft_02.txt", "final_03.txt"]
    _make_files(tmp_path, original)

    changes = replace_in_filenames(tmp_path, find_text="draft_", replace_text="final_")

    assert sorted(changes) == [
        ("draft_01.txt", "final_01.txt"),
        ("draft_02.txt", "final_02.txt"),
    ]
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "final_01.txt",
        "final_02.txt",
        "final_03.txt",
    ]


def test_replace_in_filenames_raises_for_empty_find(tmp_path: Path) -> None:
    """find_textが空のときにValueErrorが送出されることを確認する。"""
    _make_files(tmp_path, ["sample.txt"])

    with pytest.raises(ValueError):
        replace_in_filenames(tmp_path, find_text="", replace_text="x")


def test_rename_files_rejects_invalid_digits(tmp_path: Path) -> None:
    """digitsが0以下の場合にValueErrorとなることを確認する。"""
    _make_files(tmp_path, ["sample.txt"])

    with pytest.raises(ValueError):
        rename_files(tmp_path, prefix="p_", digits=0)
