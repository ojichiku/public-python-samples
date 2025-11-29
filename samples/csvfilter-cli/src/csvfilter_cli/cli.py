from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from .filters import build_condition
from .io import CsvFilterError, FilterBinding, filter_csv


@dataclass(frozen=True)
class Args:
    input: Path
    output: Path | None
    delimiter: str
    quotechar: str
    no_header: bool
    filters: list[str]
    verbose: bool


def parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="指定条件に一致するCSV行のみを出力します。")
    parser.add_argument("--input", required=True, help="入力CSVファイルのパス")
    parser.add_argument("--output", help="出力先ファイルのパス（未指定時は標準出力）")
    parser.add_argument(
        "--delimiter",
        default=",",
        help="区切り文字（デフォルト: ,）",
    )
    parser.add_argument(
        "--quotechar",
        default='"',
        help='クオート文字（デフォルト: "）',
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="先頭行をヘッダーとみなさずデータとして扱う",
    )
    parser.add_argument(
        "--and",
        dest="filters",
        action="append",
        default=[],
        help="AND条件を指定（形式: col:op:val）。複数指定可。",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="処理件数などを stderr に出力",
    )

    ns = parser.parse_args(argv)
    return Args(
        input=Path(ns.input),
        output=Path(ns.output) if ns.output else None,
        delimiter=ns.delimiter,
        quotechar=ns.quotechar,
        no_header=ns.no_header,
        filters=ns.filters,
        verbose=ns.verbose,
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        bindings = [_parse_filter(f, args.no_header) for f in args.filters]
    except ValueError as exc:
        _error(str(exc))
        return 1

    if not bindings:
        _error("フィルターを1件以上指定してください (--and col:op:val)")
        return 1

    try:
        stats = filter_csv(
            input_path=args.input,
            output_path=args.output,
            filters=bindings,
            delimiter=args.delimiter,
            quotechar=args.quotechar,
            no_header=args.no_header,
        )
    except CsvFilterError as exc:
        _error(str(exc))
        return 1

    if stats.matched == 0:
        _error("0 rows matched")

    if args.verbose:
        _error(f"processed={stats.processed}, matched={stats.matched}, skipped={stats.skipped}")

    return 0


def _parse_filter(text: str, no_header: bool) -> FilterBinding:
    parts = text.split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"フィルター指定が不正です: {text}")

    col, op, val = parts
    if not col:
        raise ValueError(f"カラム指定が空です: {text}")

    if no_header:
        try:
            col_index = int(col)
        except ValueError as exc:
            raise ValueError("ヘッダーなしの場合、列番号は整数で指定してください") from exc
        if col_index < 1:
            raise ValueError("列番号は1以上で指定してください")
        column_key: str | int = col_index - 1  # 内部では0始まり
    else:
        column_key = col

    condition = build_condition(op, val)
    return FilterBinding(column=column_key, condition=condition)


def _error(message: str) -> None:
    print(message, file=sys.stderr)
