from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from .filters import Condition


@dataclass(frozen=True)
class FilterBinding:
    column: str | int  # ヘッダーあり: カラム名, ヘッダーなし: 0 始まりの列インデックス
    condition: Condition


@dataclass
class FilterStats:
    processed: int = 0
    matched: int = 0
    skipped: int = 0


class CsvFilterError(Exception):
    """フィルター処理に関する例外"""


def filter_csv(
    *,
    input_path: Path,
    output_path: Path | None,
    filters: list[FilterBinding],
    delimiter: str,
    quotechar: str,
    no_header: bool,
) -> FilterStats:
    stats = FilterStats()

    infile = _open_input(input_path)
    outfile, should_close_output = _open_output(output_path)

    try:
        if no_header:
            _filter_no_header(infile, outfile, filters, delimiter, quotechar, stats)
        else:
            _filter_with_header(infile, outfile, filters, delimiter, quotechar, stats)
    finally:
        infile.close()
        if should_close_output:
            outfile.close()

    return stats


def _open_input(path: Path) -> TextIO:
    try:
        return path.open("r", encoding="utf-8", newline="")
    except FileNotFoundError as exc:
        raise CsvFilterError(f"入力ファイルが見つかりません: {path}") from exc
    except OSError as exc:
        raise CsvFilterError(f"入力ファイルを開けません: {path} ({exc})") from exc


def _open_output(path: Path | None) -> tuple[TextIO, bool]:
    if path is None:
        return sys.stdout, False
    try:
        return path.open("w", encoding="utf-8", newline=""), True
    except OSError as exc:
        raise CsvFilterError(f"出力ファイルを書き込めません: {path} ({exc})") from exc


def _filter_no_header(
    infile: TextIO,
    outfile: TextIO,
    filters: list[FilterBinding],
    delimiter: str,
    quotechar: str,
    stats: FilterStats,
) -> None:
    reader = csv.reader(infile, delimiter=delimiter, quotechar=quotechar)
    writer = csv.writer(
        outfile, delimiter=delimiter, quotechar=quotechar, lineterminator="\n"
    )

    for row in reader:
        stats.processed += 1
        match, skipped = _row_matches_no_header(row, filters)
        if skipped:
            stats.skipped += 1
            continue

        if match:
            writer.writerow(row)
            stats.matched += 1
        else:
            pass


def _row_matches_no_header(
    row: list[str], filters: list[FilterBinding]
) -> tuple[bool, bool]:
    """戻り値: (マッチしたか, カラム不足でスキップすべきか)"""
    for binding in filters:
        if not isinstance(binding.column, int):
            raise CsvFilterError("ヘッダーなしの場合、列番号で指定してください")

        if binding.column >= len(row):
            # 指定列が存在しない行はスキップ
            return False, True

        value = row[binding.column]
        if not binding.condition.matches(value):
            return False, False
    return True, False


def _filter_with_header(
    infile: TextIO,
    outfile: TextIO,
    filters: list[FilterBinding],
    delimiter: str,
    quotechar: str,
    stats: FilterStats,
) -> None:
    reader = csv.DictReader(infile, delimiter=delimiter, quotechar=quotechar)
    if reader.fieldnames is None:
        raise CsvFilterError(
            "ヘッダー行が存在しません。`--no-header` を指定してください。"
        )

    _ensure_columns_exist(reader.fieldnames, filters)

    writer = csv.DictWriter(
        outfile,
        fieldnames=reader.fieldnames,
        delimiter=delimiter,
        quotechar=quotechar,
        lineterminator="\n",
    )
    writer.writeheader()

    for row in reader:
        stats.processed += 1
        try:
            if _row_matches_with_header(row, filters):
                writer.writerow(row)
                stats.matched += 1
            # スキップは _row_matches_with_header 内で判断
        except CsvFilterError:
            stats.skipped += 1


def _ensure_columns_exist(fieldnames: list[str], filters: list[FilterBinding]) -> None:
    missing = {
        f.column
        for f in filters
        if isinstance(f.column, str) and f.column not in fieldnames
    }
    if missing:
        names = ", ".join(sorted(missing))
        raise CsvFilterError(f"カラムが存在しません: {names}")


def _row_matches_with_header(row: dict[str, str], filters: list[FilterBinding]) -> bool:
    for binding in filters:
        if isinstance(binding.column, int):
            raise CsvFilterError(
                "ヘッダーありの場合、列番号ではなくカラム名で指定してください"
            )

        value = row.get(binding.column)
        if value is None:
            # カラム不足行はスキップ
            raise CsvFilterError("カラム数が不足している行をスキップしました")

        if not binding.condition.matches(value):
            return False
    return True
