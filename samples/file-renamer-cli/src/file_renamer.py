"""ファイル名の一括リネームと置換を行うCLIツール。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Sequence


def rename_files(directory: Path, prefix: str, digits: int) -> list[tuple[str, str]]:
    """プレフィックスと連番を用いてディレクトリ内のファイル名を変更する。"""
    # 入力値の妥当性を先にチェックし、日本語メッセージでエラーを返す
    if digits <= 0:
        raise ValueError("digitsは1以上の整数にしてください。")
    if not prefix:
        raise ValueError("prefixが指定されていません。")
    _ensure_directory(directory)

    files = sorted(path for path in directory.iterdir() if path.is_file())
    width = max(digits, len(str(len(files)))) if files else digits
    results: list[tuple[str, str]] = []

    # ファイルを決まった順番で処理し、重複がないかを都度確認する
    for index, file_path in enumerate(files, start=1):
        new_name = f"{prefix}{str(index).zfill(width)}{file_path.suffix}"
        new_path = directory / new_name
        if new_path.exists() and new_path != file_path:
            raise FileExistsError(f"{new_name} が既に存在します。")
        if new_path != file_path:
            file_path.rename(new_path)
        results.append((file_path.name, new_path.name))
    return results


def replace_in_filenames(
    directory: Path, find_text: str, replace_text: str
) -> list[tuple[str, str]]:
    """ファイル名中の文字列を検索・置換する。"""
    if not find_text:
        raise ValueError("findに空文字は指定できません。")
    _ensure_directory(directory)

    files = sorted(path for path in directory.iterdir() if path.is_file())
    results: list[tuple[str, str]] = []

    # 置換対象が含まれるファイルだけ処理して無駄なI/Oを避ける
    for file_path in files:
        if find_text not in file_path.name:
            continue
        new_name = file_path.name.replace(find_text, replace_text)
        new_path = directory / new_name
        if new_path.exists() and new_path != file_path:
            raise FileExistsError(f"{new_name} が既に存在します。")
        if new_path != file_path:
            file_path.rename(new_path)
        results.append((file_path.name, new_path.name))
    return results


def _ensure_directory(directory: Path) -> None:
    """ディレクトリの存在と種別を検証する内部ユーティリティ。"""
    # 存在し、かつディレクトリであることを保証する
    if not directory.exists():
        raise FileNotFoundError(f"ディレクトリが見つかりません: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"ディレクトリではありません: {directory}")


def _build_parser() -> argparse.ArgumentParser:
    """argparseのパーサー構築をまとめて記述する。"""
    parser = argparse.ArgumentParser(
        prog="file_renamer", description="ファイル名の一括変更ツール"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    rename_parser = subparsers.add_parser("rename", help="連番でリネームする")
    rename_parser.add_argument(
        "--dir", required=True, type=Path, help="対象ディレクトリ"
    )
    rename_parser.add_argument(
        "--prefix", required=True, help="新しいファイル名のプレフィックス"
    )
    rename_parser.add_argument(
        "--digits", type=int, default=3, help="連番の桁数 (デフォルト: 3)"
    )
    rename_parser.set_defaults(handler=_handle_rename)

    replace_parser = subparsers.add_parser("replace", help="ファイル名の一部を置換する")
    replace_parser.add_argument(
        "--dir", required=True, type=Path, help="対象ディレクトリ"
    )
    replace_parser.add_argument("--find", required=True, help="検索する文字列")
    replace_parser.add_argument("--replace", required=True, help="置換後の文字列")
    replace_parser.set_defaults(handler=_handle_replace)

    return parser


def _handle_rename(args: argparse.Namespace) -> Iterable[tuple[str, str]]:
    """renameサブコマンド実行時のハンドラー。"""
    directory = args.dir.expanduser()
    return rename_files(directory, args.prefix, args.digits)


def _handle_replace(args: argparse.Namespace) -> Iterable[tuple[str, str]]:
    """replaceサブコマンド実行時のハンドラー。"""
    directory = args.dir.expanduser()
    return replace_in_filenames(directory, args.find, args.replace)


def main(argv: Sequence[str] | None = None) -> int:
    """CLIエントリーポイント。"""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        changes = args.handler(args)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    # 実際に行ったリネーム結果を表示する
    for before, after in changes:
        print(f"{before} -> {after}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
