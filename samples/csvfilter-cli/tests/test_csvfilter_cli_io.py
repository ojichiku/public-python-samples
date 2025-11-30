from __future__ import annotations

from pathlib import Path

import pytest


from csvfilter_cli.filters import build_condition
from csvfilter_cli.io import CsvFilterError, FilterBinding, filter_csv


def test_filter_csv_with_header(tmp_path: Path) -> None:
    src = tmp_path / "input.csv"
    src.write_text("name,status\nAlice,active\nBob,inactive\n", encoding="utf-8")
    dst = tmp_path / "out.csv"

    stats = filter_csv(
        input_path=src,
        output_path=dst,
        filters=[
            FilterBinding(
                column="status", condition=build_condition("regex", "^active$")
            )
        ],
        delimiter=",",
        quotechar='"',
        no_header=False,
    )

    assert stats.processed == 2
    assert stats.matched == 1
    assert stats.skipped == 0
    assert dst.read_text(encoding="utf-8") == "name,status\nAlice,active\n"


def test_filter_csv_no_header_skips_short_rows(tmp_path: Path) -> None:
    src = tmp_path / "input.csv"
    src.write_text("a,b\nc\nb,b\n", encoding="utf-8")
    dst = tmp_path / "out.csv"

    stats = filter_csv(
        input_path=src,
        output_path=dst,
        filters=[
            FilterBinding(column=1, condition=build_condition("contains", "b"))
        ],  # 0 始まりの列インデックス
        delimiter=",",
        quotechar='"',
        no_header=True,
    )

    assert stats.processed == 3
    assert stats.matched == 2
    assert stats.skipped == 1  # 2列目がない行
    assert dst.read_text(encoding="utf-8") == "a,b\nb,b\n"


def test_filter_csv_missing_header_column_raises(tmp_path: Path) -> None:
    src = tmp_path / "input.csv"
    src.write_text("name\nAlice\n", encoding="utf-8")
    dst = tmp_path / "out.csv"

    with pytest.raises(CsvFilterError):
        filter_csv(
            input_path=src,
            output_path=dst,
            filters=[
                FilterBinding(
                    column="city", condition=build_condition("contains", "Tokyo")
                )
            ],
            delimiter=",",
            quotechar='"',
            no_header=False,
        )
