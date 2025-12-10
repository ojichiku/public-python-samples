"""ファイル入出力をまとめたユーティリティ。"""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

__all__ = [
    "append_csv_dict",
    "append_lines",
    "append_text",
    "read_csv_dict",
    "read_lines",
    "read_text",
    "write_csv_dict",
    "write_lines",
    "write_text",
]


def read_text(path: str | Path, encoding: str = "utf-8") -> str:
    """指定パスのテキストファイルを読み込む。

    Args:
        path: 読み込むファイルパス。
        encoding: 使用する文字コード。

    Returns:
        読み込んだテキスト。
    """

    return Path(path).read_text(encoding=encoding)


def write_text(path: str | Path, text: str, encoding: str = "utf-8") -> None:
    """テキストファイルを上書き保存する。

    Args:
        path: 書き込み先のファイルパス。
        text: 保存する文字列。
        encoding: 使用する文字コード。
    """

    Path(path).write_text(text, encoding=encoding)


def append_text(path: str | Path, text: str, encoding: str = "utf-8") -> None:
    """テキストファイルへ追記する。

    Args:
        path: 追記対象のファイルパス。
        text: 末尾に追加する文字列。
        encoding: 使用する文字コード。
    """

    with Path(path).open("a", encoding=encoding) as fh:
        fh.write(text)


def read_lines(
    path: str | Path, encoding: str = "utf-8", keep_newline: bool = False
) -> list[str]:
    """テキストファイルを行単位で読み込む。

    Args:
        path: 読み込むファイルパス。
        encoding: 使用する文字コード。
        keep_newline: True の場合は行末の改行を維持する。

    Returns:
        読み込んだ各行のリスト。
    """

    with Path(path).open("r", encoding=encoding) as fh:
        if keep_newline:
            return fh.readlines()
        return fh.read().splitlines()


def write_lines(
    path: str | Path,
    lines: Iterable[str],
    encoding: str = "utf-8",
    newline: str = "\n",
) -> None:
    """行リストをテキストファイルとして保存する。

    Args:
        path: 書き込み先のファイルパス。
        lines: 出力する行イテラブル。
        encoding: 使用する文字コード。
        newline: 行末に付与する改行文字列（None で付与しない）。
    """

    with Path(path).open("w", encoding=encoding, newline="") as fh:
        for line in lines:
            fh.write(line)
            if newline is not None:
                fh.write(newline)


def append_lines(
    path: str | Path,
    lines: Iterable[str],
    encoding: str = "utf-8",
    newline: str = "\n",
) -> None:
    """行リストをテキストファイルへ追記する。

    Args:
        path: 追記対象のファイルパス。
        lines: 追記する行イテラブル。
        encoding: 使用する文字コード。
        newline: 行末に付与する改行文字列（None で付与しない）。
    """

    with Path(path).open("a", encoding=encoding, newline="") as fh:
        for line in lines:
            fh.write(line)
            if newline is not None:
                fh.write(newline)


def read_csv_dict(
    path: str | Path,
    encoding: str = "utf-8",
    dialect: str = "excel",
) -> list[dict[str, str]]:
    """CSV を dict のリストとして読み込む。

    Args:
        path: 読み込み対象の CSV ファイル。
        encoding: 使用する文字コード。
        dialect: csv モジュールのダイアレクト名。

    Returns:
        行ごとの dict リスト。
    """

    with Path(path).open("r", encoding=encoding, newline="") as fh:
        reader = csv.DictReader(fh, dialect=dialect)
        return [dict(row) for row in reader]


def write_csv_dict(
    path: str | Path,
    rows: list[dict[str, str]],
    fieldnames: list[str],
    encoding: str = "utf-8",
    dialect: str = "excel",
    newline: str = "",
) -> None:
    """dict のリストを CSV として保存する。

    Args:
        path: 書き込み先の CSV ファイル。
        rows: 出力するデータ行。
        fieldnames: 列名の順序リスト。
        encoding: 使用する文字コード。
        dialect: csv モジュールのダイアレクト名。
        newline: ファイル書き込み時の newline パラメータ。
    """

    with Path(path).open("w", encoding=encoding, newline=newline) as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, dialect=dialect)
        writer.writeheader()
        writer.writerows(rows)


def append_csv_dict(
    path: str | Path,
    rows: list[dict[str, str]],
    fieldnames: list[str],
    encoding: str = "utf-8",
    dialect: str = "excel",
    newline: str = "",
) -> None:
    """dict のリストを CSV の末尾に追記する。

    Args:
        path: 追記対象の CSV ファイル。
        rows: 追記するデータ行。
        fieldnames: CSV の列名順序。
        encoding: 使用する文字コード。
        dialect: csv モジュールのダイアレクト名。
        newline: ファイル書き込み時の newline パラメータ。
    """

    csv_path = Path(path)
    file_exists = csv_path.exists()
    mode = "a" if file_exists else "w"

    with csv_path.open(mode, encoding=encoding, newline=newline) as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, dialect=dialect)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)
