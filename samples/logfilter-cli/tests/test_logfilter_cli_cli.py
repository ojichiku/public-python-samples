"""cli モジュールの統合テスト。

想定インターフェイス:
- cli.main(argv: list[str] | None) -> int
  - 引数をパースし、フィルタ結果を標準出力またはファイルに書き出す。
"""

from __future__ import annotations

from pathlib import Path

import pytest

from logfilter_cli import cli

DATA_DIR = Path(__file__).with_name("data")
SAMPLE_LOG = DATA_DIR / "sample.log"


def test_cli_filters_keyword_to_stdout(tmp_path, capsys):
    input_path = tmp_path / "input.log"
    input_path.write_text(
        "\n".join(
            [
                "2025-11-01 INFO boot complete",
                "2025-11-02 ERROR database down",
                "NoDateLine INFO without date",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = cli.main([str(input_path), "--contains", "ERROR"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "2025-11-02 ERROR database down\n"
    assert captured.err == ""


def test_cli_writes_to_output_file_with_date_range(tmp_path):
    input_path = tmp_path / "input.log"
    output_path = tmp_path / "out.log"
    input_path.write_text(
        "\n".join(
            [
                "2025-11-01 INFO boot complete",
                "2025-11-02 ERROR database down",
                "2025-11-03 ERROR late error",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = cli.main(
        [
            str(input_path),
            "--contains",
            "error",
            "--date-from",
            "2025-11-02",
            "--date-to",
            "2025-11-02",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "2025-11-02 ERROR database down\n"


def test_cli_errors_on_missing_input_file(tmp_path):
    missing_path = tmp_path / "missing.log"

    with pytest.raises(SystemExit):
        cli.main([str(missing_path), "--contains", "ERROR"])


def test_cli_filters_prepared_sample_data(capsys):
    assert SAMPLE_LOG.exists()

    exit_code = cli.main(
        [
            str(SAMPLE_LOG),
            "--contains",
            "error",
            "--date-from",
            "2025-01-03",
            "--date-to",
            "2025-01-12",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert captured.out == (
        "2025-01-03 ERROR payment queue stalled\n"
        "2025-01-05 ERROR cache miss storm\n"
        "2025-01-09 ERROR release rollback triggered\n"
        "2025-01-12 error fraud detection alert\n"
    )
