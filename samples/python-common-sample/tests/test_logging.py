"""Tests for the shared logging configuration.

This suite ensures the default config/logging.yaml file matches the
spec defined in specs/logging.md.
"""

from __future__ import annotations

from pathlib import Path

import yaml


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "logging.yaml"


def load_logging_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


def test_logging_config_file_exists():
    assert CONFIG_PATH.exists(), "config/logging.yaml must exist per spec"


def test_logging_config_matches_spec_defaults():
    config = load_logging_config()

    assert config["level"] == "INFO"
    assert config["stdout"] == {"enabled": True}

    expected_file_section = {
        "enabled": True,
        "path": "logs/app.log",
        "rotation": None,
        "max_files": 5,
    }
    assert config["file"] == expected_file_section

    assert config["format"] == "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s"
    assert config["date_format"] == "%Y/%m/%d %H:%M:%S"
