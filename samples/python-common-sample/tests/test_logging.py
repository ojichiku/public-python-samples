"""Tests for the shared logging configuration.

This suite ensures the default config/logging.ini file matches the
spec defined in specs/logging.md.
"""

from __future__ import annotations

import configparser
from pathlib import Path


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "logging.ini"


def load_logging_config() -> configparser.ConfigParser:
    """INI を読み込んで ConfigParser として返す。"""
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(CONFIG_PATH, encoding="utf-8")
    return parser


def test_logging_config_file_exists():
    """config/logging.ini が存在することを確認する。"""
    assert CONFIG_PATH.exists(), "config/logging.ini must exist per spec"


def test_logging_config_matches_spec_defaults():
    """specs/logging.md に記載されたデフォルト値を検証する。"""
    config = load_logging_config()

    assert config.get("loggers", "keys") == "root"
    assert config.get("handlers", "keys") == "consoleHandler,fileHandler"
    assert config.get("formatters", "keys") == "defaultFormatter"

    assert config.get("logger_root", "level") == "INFO"
    assert config.get("logger_root", "handlers") == "consoleHandler,fileHandler"

    assert config.get("handler_consoleHandler", "class") == "StreamHandler"
    assert config.get("handler_consoleHandler", "formatter") == "defaultFormatter"
    assert config.get("handler_consoleHandler", "args") == "(sys.stdout,)"

    assert config.get("handler_fileHandler", "class") == "FileHandler"
    assert config.get("handler_fileHandler", "formatter") == "defaultFormatter"
    assert config.get("handler_fileHandler", "args") == "('logs/app.log', 'a')"

    assert (
        config.get("formatter_defaultFormatter", "format")
        == "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s"
    )
    assert config.get("formatter_defaultFormatter", "datefmt") == "%Y/%m/%d %H:%M:%S"
