from __future__ import annotations

import sys
from pathlib import Path

import pytest

# src を import パスに追加
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from csvfilter_cli import cli


def run_cli(args: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, str, str]:
    code = cli.main(args)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_contains_filters_rows(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("name,status\nAlice,active\nBob,inactive\n", encoding="utf-8")

    code, out, err = run_cli(
        ["--input", str(csv_path), "--and", "name:contains:Ali"],
        capsys,
    )

    assert code == 0
    assert out == "name,status\nAlice,active\n"
    assert err == ""  # マッチありなのでメッセージなし


def test_regex_filters_rows(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("name,status\nAlice,active\nBob,inactive\n", encoding="utf-8")

    code, out, _ = run_cli(
        ["--input", str(csv_path), "--and", "status:regex:^active$"],
        capsys,
    )

    assert code == 0
    assert out == "name,status\nAlice,active\n"


def test_and_conditions_apply_all(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text(
        "name,status,city\nAlice,active,Tokyo\nAlice,inactive,Osaka\nBob,active,Tokyo\n",
        encoding="utf-8",
    )

    code, out, _ = run_cli(
        [
            "--input",
            str(csv_path),
            "--and",
            "name:contains:Alice",
            "--and",
            "status:regex:^active$",
        ],
        capsys,
    )

    assert code == 0
    assert out == "name,status,city\nAlice,active,Tokyo\n"


def test_no_header_uses_one_based_indices_and_skips_short_rows(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("a,b\nc\nb,b\n", encoding="utf-8")

    code, out, err = run_cli(
        ["--input", str(csv_path), "--no-header", "--and", "2:contains:b", "-v"],
        capsys,
    )

    assert code == 0
    assert out == "a,b\nb,b\n"
    assert "skipped=1" in err  # 2列目がない行が1件スキップされる


def test_custom_delimiter_and_quote(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv_path = tmp_path / "input.tsv"
    csv_path.write_text("name\tstatus\n\"A\"\t\"ok\"\n\"B\"\t\"ng\"\n", encoding="utf-8")

    code, out, _ = run_cli(
        [
            "--input",
            str(csv_path),
            "--delimiter",
            "\t",
            "--quotechar",
            '"',
            "--and",
            "status:contains:ok",
        ],
        capsys,
    )

    assert code == 0
    assert out == "name\tstatus\nA\tok\n"


def test_invalid_operator_returns_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("name\nAlice\n", encoding="utf-8")

    code, _, err = run_cli(
        ["--input", str(csv_path), "--and", "name:eq:Alice"],
        capsys,
    )

    assert code == 1
    assert "無効な演算子" in err


def test_missing_column_with_header_returns_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("name\nAlice\n", encoding="utf-8")

    code, _, err = run_cli(
        ["--input", str(csv_path), "--and", "city:contains:Tokyo"],
        capsys,
    )

    assert code == 1
    assert "カラムが存在しません" in err


def test_bad_regex_returns_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("name\nAlice\n", encoding="utf-8")

    code, _, err = run_cli(
        ["--input", str(csv_path), "--and", "name:regex:("],
        capsys,
    )

    assert code == 1
    assert "正規表現が不正" in err


def test_zero_match_outputs_message(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("name\nAlice\n", encoding="utf-8")

    code, out, err = run_cli(
        ["--input", str(csv_path), "--and", "name:contains:Bob"],
        capsys,
    )

    assert code == 0
    assert out == "name\n"
    assert "0 rows matched" in err
