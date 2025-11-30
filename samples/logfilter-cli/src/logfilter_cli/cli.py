"""logfilter-cli の CLI エントリーポイントを定義するモジュール。"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import sys

from . import filters, parser


def _parse_date(value: str) -> dt.date:
    """YYYY-MM-DD 形式の文字列を日付に変換する。

    Argparse から利用されるため、形式不正時は ArgumentTypeError を送出する。
    """

    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:  # 形式不正を明示する
        raise argparse.ArgumentTypeError(f"無効な日付形式です: {value}") from exc


def build_parser() -> argparse.ArgumentParser:
    """CLI 用の ArgumentParser を生成する。"""

    ap = argparse.ArgumentParser(
        prog="logfilter-cli",
        description="ログファイルをキーワードと日付範囲でフィルタします。",
    )
    ap.add_argument("input", type=Path, help="入力ログファイルのパス")
    ap.add_argument(
        "--contains",
        dest="keyword",
        help="部分一致で探すキーワード（大文字小文字は無視）",
    )
    ap.add_argument(
        "--date-from", type=_parse_date, help="YYYY-MM-DD 形式の開始日（含む）"
    )
    ap.add_argument(
        "--date-to", type=_parse_date, help="YYYY-MM-DD 形式の終了日（含む）"
    )
    ap.add_argument(
        "--output",
        type=Path,
        help="出力先ファイルパス（指定しない場合は標準出力へ出力）",
    )
    ap.add_argument(
        "--case-sensitive",
        action="store_true",
        help="キーワード検索で大文字小文字を区別する",
    )
    return ap


def _load_entries(path: Path):
    """ファイルを読み込み、LogEntry のリストを返す。

    単純な一括読み込み。ログは通常テキスト量が小さい想定のためメモリ優先。
    """

    with path.open("r", encoding="utf-8") as f:
        return [parser.parse_line(line) for line in f]


def _write_output(entries, output: Path | None):
    """フィルタ結果を出力する。"""

    lines = [
        entry.raw if entry.raw.endswith("\n") else f"{entry.raw}\n" for entry in entries
    ]
    if output is None:
        sys.stdout.writelines(lines)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as f:
            f.writelines(lines)


def main(argv: list[str] | None = None) -> int:
    """エントリーポイント。引数を解釈してフィルタ処理を実行する。"""

    ap = build_parser()
    args = ap.parse_args(argv)

    if not args.input.exists():
        ap.error(f"入力ファイルが見つかりません: {args.input}")

    entries = _load_entries(args.input)
    filtered = filters.filter_entries(
        entries,
        keyword=args.keyword,
        date_from=args.date_from,
        date_to=args.date_to,
        case_sensitive=bool(args.case_sensitive),
    )
    _write_output(filtered, args.output)
    return 0


if __name__ == "__main__":  # 実行可能モジュールとしても動作
    raise SystemExit(main())
