"""Tests for the shared logging configuration.

This suite ensures the default config/logging.ini file matches the
spec defined in specs/logging.md.
"""

from __future__ import annotations

import configparser
import logging
import logging.config
import re
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "logging.ini"


def load_logging_config() -> configparser.ConfigParser:
    """INI を読み込んで ConfigParser として返す。"""
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(CONFIG_PATH, encoding="utf-8")
    return parser


def configure_logging_with_temp_file(tmp_path: Path) -> Path:
    """logging.ini を一時ファイルに複製し、ログファイル出力先だけ差し替える。"""
    parser = load_logging_config()
    log_file = tmp_path / "logs" / "app.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    parser.set("handler_fileHandler", "args", f"({repr(str(log_file))}, 'a')")

    temp_config = tmp_path / "logging.ini"
    with temp_config.open("w", encoding="utf-8") as config_file:
        parser.write(config_file)

    logging.shutdown()
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    logging.config.fileConfig(temp_config, disable_existing_loggers=False)
    return log_file


def test_logging_config_file_exists():
    """config/logging.ini が存在することを確認する。"""
    # 単純に設定ファイルの有無を保証し、他テストの前提を担保
    assert CONFIG_PATH.exists(), "config/logging.ini must exist per spec"


def test_logging_config_writes_expected_console_and_file_output(tmp_path, capsys):
    """logging.ini を実際に読み込み、stdout とファイルへ仕様どおり出力されるか確認する。"""
    # コンソールとファイルの双方でフォーマットとログレベルが仕様通りかを網羅的に検証
    log_file = configure_logging_with_temp_file(tmp_path)
    info_message = "Runtime logging validation"

    # 既定レベルは INFO のため、DEBUG は無視される想定。
    logger = logging.getLogger()
    logger.debug("hidden debug log")
    logger.info(info_message)

    logging.shutdown()
    stdout_capture = capsys.readouterr().out
    stdout_lines = [line for line in stdout_capture.splitlines() if line.strip()]
    assert stdout_lines, "console handler should emit a line"
    console_line = stdout_lines[-1]

    expected_pattern = re.compile(
        rf"\d{{4}}/\d{{2}}/\d{{2}} \d{{2}}:\d{{2}}:\d{{2}}\.\d{{3}} \[INFO\] {re.escape(info_message)}"
    )
    assert expected_pattern.fullmatch(
        console_line
    ), "console log must follow the default formatter"

    # ファイル出力も INFO のみ記録される想定。
    assert log_file.exists(), "file handler must create logs/app.log"
    file_lines = [
        line
        for line in log_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(file_lines) == 1, "file handler should only record the INFO message"
    assert expected_pattern.fullmatch(
        file_lines[0]
    ), "file log must match the default formatter output"
