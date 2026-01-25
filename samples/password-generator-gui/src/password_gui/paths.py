from __future__ import annotations

from dataclasses import dataclass
import logging
import logging.config
from pathlib import Path
import sys


@dataclass(frozen=True)
class AppPaths:
    """アプリケーションのディレクトリ構成パス。"""

    app_dir: Path
    log_dir: Path


def _resolve_app_dir() -> Path:
    """アプリケーションの基準ディレクトリを解決する。"""
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        if exe_dir.name == "app":
            return exe_dir.parent
        return exe_dir
    return Path(__file__).resolve().parents[2]


def _resolve_logging_config_path() -> Path:
    """logging.ini の配置先を解決する。"""
    return Path(__file__).resolve().parent / "logging.ini"


def get_app_paths() -> AppPaths:
    """既定のアプリケーションパスを構築する。"""
    app_dir = _resolve_app_dir()
    return AppPaths(
        app_dir=app_dir,
        log_dir=app_dir / "log",
    )


def ensure_runtime_dirs(paths: AppPaths | None = None) -> AppPaths:
    """実行時ディレクトリの存在と書き込み可否を確認する。"""
    if paths is None:
        paths = get_app_paths()

    paths.log_dir.mkdir(parents=True, exist_ok=True)
    test_file = paths.log_dir / ".write_test"
    test_file.write_text("ok", encoding="utf-8")
    test_file.unlink(missing_ok=True)
    return paths


def init_logging(paths: AppPaths | None = None) -> AppPaths:
    """logging.ini を読み込んでロギングを初期化する。"""
    if logging.getLogger().handlers:
        return paths or get_app_paths()

    if paths is None:
        paths = get_app_paths()

    ensure_runtime_dirs(paths)
    config_path = _resolve_logging_config_path()
    log_file = str(paths.log_dir / "app.log").replace("\\", "/")
    logging.config.fileConfig(
        config_path,
        defaults={"log_file": log_file},
        disable_existing_loggers=False,
    )
    return paths


def get_resource_bases() -> list[Path]:
    """リソース探索の基準ディレクトリを返す。"""
    bases: list[Path] = []
    if hasattr(sys, "_MEIPASS"):
        bases.append(Path(sys._MEIPASS))  # type: ignore[attr-defined]

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        bases.append(exe_dir)
        bases.append(exe_dir / "src")
        app_dir = _resolve_app_dir()
        if app_dir not in bases:
            bases.append(app_dir)
    else:
        bases.append(_resolve_app_dir())

    return bases
