"""`python -m password_gui` で GUI を起動するエントリポイント。"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from password_gui.main_window import MainWindow


def main() -> int:
    """GUI アプリケーションを起動する。

    Returns:
        終了コード（0=正常）。
    """
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
