"""パス操作ユーティリティを提供するモジュール。"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

__all__ = [
    "add_suffix_before_extension",
    "change_extension",
    "create_temp_file",
    "exists",
    "get_app_dir",
    "get_cwd",
    "get_temp_dir",
    "get_user_home_dir",
    "is_dir",
    "is_file",
    "list_dirs",
    "list_files",
    "resolve_path",
    "safe_filename",
    "temporary_directory",
    "to_path",
]


def to_path(path: str | Path) -> Path:
    """引数を Path に変換する。

    Args:
        path: 文字列または Path オブジェクト。

    Returns:
        Path オブジェクト。
    """

    return path if isinstance(path, Path) else Path(path)


def resolve_path(path: str | Path) -> Path:
    """Path に変換し、絶対パスに解決する。

    Args:
        path: 文字列または Path。

    Returns:
        絶対パスに解決した Path。
    """

    return to_path(path).expanduser().resolve()


def get_cwd() -> Path:
    """現在の作業ディレクトリを返す。

    Returns:
        カレントディレクトリの Path。
    """

    return Path.cwd()


def get_app_dir() -> Path:
    """アプリケーションの起点ディレクトリを取得する。

    Returns:
        EXE/スクリプト/ライブラリ状況に応じた起点ディレクトリの Path。
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    main_module = sys.modules.get("__main__")
    main_file = getattr(main_module, "__file__", None)
    if main_file:
        return Path(main_file).resolve().parent

    return Path(__file__).resolve().parent


def get_user_home_dir() -> Path:
    """現在ユーザーのホームディレクトリを返す。

    Returns:
        Path.home() の結果。
    """

    return Path.home()


def get_temp_dir(subdir: str | None = None) -> Path:
    """OS の一時ディレクトリ、または指定サブディレクトリを返す。

    Args:
        subdir: サブディレクトリ名。指定時は作成して返す。

    Returns:
        一時ディレクトリまたはその配下の Path。
    """

    base = Path(tempfile.gettempdir())
    if subdir is None:
        return base
    target = base / safe_filename(subdir)
    target.mkdir(parents=True, exist_ok=True)
    return target


def create_temp_file(
    prefix: str = "tmp",
    suffix: str = "",
    dir: str | Path | None = None,
    delete: bool = False,
) -> Path:
    """一時ファイルを作成し、その Path を返す。

    Args:
        prefix: ファイル名の接頭辞。
        suffix: ファイル名の接尾辞。
        dir: 生成先ディレクトリ。None は OS 既定。
        delete: True の場合は即座に削除する。

    Returns:
        生成されたファイルの Path。
    """

    directory = to_path(dir) if dir is not None else None
    fd, raw_path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=directory)
    os.close(fd)
    temp_path = Path(raw_path)
    if delete:
        temp_path.unlink(missing_ok=True)
    return temp_path


@contextmanager
def temporary_directory(prefix: str = "tmp") -> Iterator[Path]:
    """with ブロック終了時に削除される一時ディレクトリを提供する。

    Args:
        prefix: 作成する一時ディレクトリ名の接頭辞。

    Yields:
        作成された一時ディレクトリ Path。
    """

    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def exists(path: str | Path) -> bool:
    """パスが存在するかどうかを返す。

    Args:
        path: 確認したいパス。

    Returns:
        存在する場合 True。
    """

    return to_path(path).exists()


def is_file(path: str | Path) -> bool:
    """通常ファイルであるかどうかを返す。

    Args:
        path: 目標パス。

    Returns:
        ファイルなら True。
    """

    return to_path(path).is_file()


def is_dir(path: str | Path) -> bool:
    """ディレクトリであるかどうかを返す。

    Args:
        path: 目標パス。

    Returns:
        ディレクトリなら True。
    """

    return to_path(path).is_dir()


def list_files(
    dir_path: str | Path, pattern: str = "*", recursive: bool = False
) -> list[Path]:
    """指定ディレクトリ配下のファイル一覧を返す。

    Args:
        dir_path: 走査対象ディレクトリ。
        pattern: glob パターン。
        recursive: True の場合は再帰的に検索。

    Returns:
        条件に一致するファイル Path のリスト。
    """

    base = to_path(dir_path)
    if recursive:
        return sorted(path for path in base.rglob(pattern) if path.is_file())
    return sorted(path for path in base.glob(pattern) if path.is_file())


def list_dirs(dir_path: str | Path, recursive: bool = False) -> list[Path]:
    """指定ディレクトリ配下のサブディレクトリ一覧を返す。

    Args:
        dir_path: 走査対象ディレクトリ。
        recursive: True の場合、再帰的に列挙。

    Returns:
        サブディレクトリ Path のリスト。
    """

    base = to_path(dir_path)
    if recursive:
        return sorted(path for path in base.rglob("*") if path.is_dir())
    return sorted(path for path in base.iterdir() if path.is_dir())


def safe_filename(name: str, max_length: int = 255) -> str:
    """禁止文字を除去して安全なファイル名に変換する。

    Args:
        name: 元のファイル名。
        max_length: 最大長。超える場合は切り詰め。

    Returns:
        安全なファイル名文字列。
    """

    forbidden = '<>:"/\\|?*\x00'
    safe = "".join(ch for ch in name if ch not in forbidden)
    safe = safe.strip()
    if not safe:
        safe = "untitled"
    if len(safe) > max_length:
        safe = safe[:max_length]
    return safe


def add_suffix_before_extension(path: str | Path, suffix: str) -> Path:
    """拡張子直前に suffix を付与した Path を返す。

    Args:
        path: 変更対象のファイルパス。
        suffix: 付与したいサフィックス文字列。

    Returns:
        サフィックスを挿入した Path。
    """

    target = to_path(path)
    if not suffix:
        return target
    if target.suffix:
        new_name = f"{target.stem}{suffix}{target.suffix}"
    else:
        new_name = f"{target.name}{suffix}"
    return target.with_name(new_name)


def change_extension(path: str | Path, new_ext: str) -> Path:
    """ファイル拡張子を new_ext に変更した Path を返す。

    Args:
        path: 変更対象のファイルパス。
        new_ext: 新しい拡張子（`.log` / `log` など）。

    Returns:
        拡張子を置き換えた Path。
    """

    target = to_path(path)
    if new_ext in {"", "."}:
        suffix = ""
    else:
        suffix = new_ext if new_ext.startswith(".") else f".{new_ext}"
    return target.with_suffix(suffix)
