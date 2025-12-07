from __future__ import annotations

from pathlib import Path

import pytest

import python_common_sample.io_utils as io_utils


def test_write_and_read_text(tmp_path: Path) -> None:
    """テキストの上書き・追記が期待通り動作するか。"""

    path = tmp_path / "hello.txt"
    io_utils.write_text(path, "hello")
    assert io_utils.read_text(str(path)) == "hello"

    io_utils.append_text(path, " world")
    assert io_utils.read_text(path) == "hello world"


def test_read_and_write_lines(tmp_path: Path) -> None:
    """行単位の読み書きと keep_newline の挙動を確認する。"""

    path = tmp_path / "lines.txt"
    io_utils.write_lines(path, ["a", "b"])
    assert io_utils.read_lines(path) == ["a", "b"]
    assert io_utils.read_lines(path, keep_newline=True) == ["a\n", "b\n"]

    io_utils.append_lines(path, ["c"])
    assert io_utils.read_lines(path) == ["a", "b", "c"]


def test_write_lines_respects_custom_newline(tmp_path: Path) -> None:
    """write_lines の newline 指定が反映されるか。"""

    path = tmp_path / "custom.txt"
    io_utils.write_lines(path, ["1", "2"], newline="\r\n")
    with path.open("r", encoding="utf-8", newline="") as fh:
        assert fh.read() == "1\r\n2\r\n"


def test_csv_write_and_read(tmp_path: Path) -> None:
    """CSV の上書き読み書きで dict が維持されるか。"""

    path = tmp_path / "data.csv"
    rows = [
        {"name": "alice", "score": "10"},
        {"name": "bob", "score": "20"},
    ]
    io_utils.write_csv_dict(path, rows, fieldnames=["name", "score"])
    loaded = io_utils.read_csv_dict(path)
    assert loaded == rows


def test_csv_append_adds_rows_and_creates_header_when_missing(tmp_path: Path) -> None:
    """ヘッダが無い場合は作成し、既存ファイルには追記のみ行うか。"""

    path = tmp_path / "log.csv"
    first = [{"name": "carol", "score": "30"}]
    second = [{"name": "dave", "score": "40"}]

    io_utils.append_csv_dict(path, first, fieldnames=["name", "score"])
    io_utils.append_csv_dict(path, second, fieldnames=["name", "score"])

    loaded = io_utils.read_csv_dict(path)
    assert loaded == first + second


def test_write_text_raises_when_parent_missing(tmp_path: Path) -> None:
    """親ディレクトリが無い場合に FileNotFoundError が送出されるか。"""

    path = tmp_path / "missing" / "file.txt"
    with pytest.raises(FileNotFoundError):
        io_utils.write_text(path, "data")
