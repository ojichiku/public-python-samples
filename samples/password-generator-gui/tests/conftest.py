"""pytest のテスト設定。

このサンプルはインストールせずに `src/` 直下のパッケージを直接 import するため、
テスト実行時に `sys.path` を調整する。
"""

from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    """テスト開始前に import パスをセットアップする。

    Args:
        None
    """
    src_dir = Path(__file__).resolve().parents[1] / "src"
    sys.path.insert(0, str(src_dir))
