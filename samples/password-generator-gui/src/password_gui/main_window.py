"""メインウィンドウ（GUI層）。

Qt Designer で作成した `.ui` を実行時に読み込み、objectName を前提にウィジェット参照を取得して
イベントを接続する。生成ロジックは `password_gui.generator` に委譲し、GUI から分離する。
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import TypeVar

from PySide6.QtCore import QSettings
from PySide6.QtGui import QGuiApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QCheckBox,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSpinBox,
    QWidget,
)

from password_gui.generator import DEFAULT_SYMBOLS, generate_passwords

_TWidget = TypeVar("_TWidget", bound=QWidget)


def resource_path(relative_path: str) -> Path:
    """リソースファイルのパスを返す。

    Nuitka / PyInstaller 等で EXE 化された場合でも `.ui` をファイルシステムから読み込めるようにする。

    Args:
        relative_path: プロジェクトルートからの相対パス（例: "src/resources/ui/main_window.ui"）。

    Returns:
        実ファイルのパス。
    """

    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2] / relative_path


class MainWindow(QMainWindow):
    """パスワード生成ツールのメインウィンドウ。"""

    def __init__(self) -> None:
        """ウィンドウを初期化する。

        - `.ui` を読み込んで `QMainWindow` を構築
        - objectName で各ウィジェット参照を取得
        - 設定（QSettings）を復元し、イベントを接続
        """
        super().__init__()
        self._settings = QSettings("public-python-samples", "password-generator-gui")

        loaded = self._load_ui()
        self._apply_loaded_main_window(loaded)

        self.spinLength = self._find(QSpinBox, "spinLength")
        self.spinCount = self._find(QSpinBox, "spinCount")
        self.chkDigits = self._find(QCheckBox, "chkDigits")
        self.chkLower = self._find(QCheckBox, "chkLower")
        self.chkUpper = self._find(QCheckBox, "chkUpper")
        self.chkSymbols = self._find(QCheckBox, "chkSymbols")
        self.chkExcludeAmbiguous = self._find(QCheckBox, "chkExcludeAmbiguous")
        self.txtSymbols = self._find(QLineEdit, "txtSymbols")
        self.btnResetSymbols = self._find(QPushButton, "btnResetSymbols")
        self.btnGenerate = self._find(QPushButton, "btnGenerate")
        self.btnClear = self._find(QPushButton, "btnClear")
        self.btnCopySelected = self._find(QPushButton, "btnCopySelected")
        self.btnCopyAll = self._find(QPushButton, "btnCopyAll")
        self.txtResult = self._find(QPlainTextEdit, "txtResult")

        self._restore_settings()
        self._connect_signals()

    def _load_ui(self) -> QMainWindow:
        """Qt Designer の `.ui` を読み込んで `QMainWindow` を返す。

        Returns:
            読み込んだ `QMainWindow` インスタンス。

        Raises:
            FileNotFoundError: `.ui` が見つからない場合。
            RuntimeError: UI のロードに失敗した場合。
            TypeError: ルートが `QMainWindow` ではない場合。
        """
        ui_path = resource_path("src/resources/ui/main_window.ui")
        if not ui_path.exists():
            raise FileNotFoundError(f".ui が見つかりません: {ui_path}")

        loader = QUiLoader()
        widget = loader.load(str(ui_path), None)
        if widget is None:
            raise RuntimeError("UI の読み込みに失敗しました")
        if not isinstance(widget, QMainWindow):
            raise TypeError("main_window.ui のルートは QMainWindow を想定しています")
        return widget

    def _apply_loaded_main_window(self, loaded: QMainWindow) -> None:
        """読み込んだ `QMainWindow` の内容を現在のインスタンスへ反映する。

        QUiLoader が返す `QMainWindow` をそのまま使うのではなく、`centralWidget` 等を取り出して
        この `MainWindow` に移し替える。

        Args:
            loaded: `.ui` からロードした `QMainWindow`。

        Raises:
            RuntimeError: `centralWidget` が存在しない場合。
        """
        self.setWindowTitle(loaded.windowTitle())

        if loaded.menuBar() is not None:
            self.setMenuBar(loaded.menuBar())
        if loaded.statusBar() is not None:
            self.setStatusBar(loaded.statusBar())

        central = loaded.centralWidget()
        if central is None:
            raise RuntimeError("UI に centralWidget がありません")
        self.setCentralWidget(central)

    def _find(self, widget_type: type[_TWidget], object_name: str) -> _TWidget:
        """objectName を使って子ウィジェットを取得する。

        Args:
            widget_type: 取得したいウィジェット型。
            object_name: Qt Designer 上の objectName。

        Returns:
            取得したウィジェット。

        Raises:
            RuntimeError: 対象ウィジェットが見つからない場合。
        """
        widget = self.findChild(widget_type, object_name)
        if widget is None:
            raise RuntimeError(f"UI からウィジェットが取得できません: {object_name}")
        return widget

    def _connect_signals(self) -> None:
        """ボタンのクリックイベントを接続する。"""
        self.btnGenerate.clicked.connect(self.on_generate_clicked)
        self.btnClear.clicked.connect(self.on_clear_clicked)
        self.btnCopySelected.clicked.connect(self.on_copy_selected_clicked)
        self.btnCopyAll.clicked.connect(self.on_copy_all_clicked)
        self.btnResetSymbols.clicked.connect(self.on_reset_symbols_clicked)
        self.chkSymbols.toggled.connect(self._update_symbols_enabled)
        self._update_symbols_enabled(self.chkSymbols.isChecked())

    def _restore_settings(self) -> None:
        """前回終了時の設定を復元する（任意機能）。"""
        length = self._settings.value("length")
        count = self._settings.value("count")
        if isinstance(length, int):
            self.spinLength.setValue(length)
        if isinstance(count, int):
            self.spinCount.setValue(count)

        for key, checkbox in [
            ("digits", self.chkDigits),
            ("lower", self.chkLower),
            ("upper", self.chkUpper),
            ("symbols", self.chkSymbols),
            ("exclude_ambiguous", self.chkExcludeAmbiguous),
        ]:
            value = self._settings.value(f"chk/{key}")
            if isinstance(value, bool):
                checkbox.setChecked(value)

        symbols_text = self._settings.value("symbols")
        if isinstance(symbols_text, str) and symbols_text != "":
            self.txtSymbols.setText(symbols_text)
        else:
            self.txtSymbols.setText(DEFAULT_SYMBOLS)

    def _save_settings(self) -> None:
        """現在の設定を保存する（任意機能）。"""
        self._settings.setValue("length", self.spinLength.value())
        self._settings.setValue("count", self.spinCount.value())
        symbols_text = self.txtSymbols.text()
        self._settings.setValue(
            "symbols", symbols_text if symbols_text != "" else DEFAULT_SYMBOLS
        )
        self._settings.setValue("chk/digits", self.chkDigits.isChecked())
        self._settings.setValue("chk/lower", self.chkLower.isChecked())
        self._settings.setValue("chk/upper", self.chkUpper.isChecked())
        self._settings.setValue("chk/symbols", self.chkSymbols.isChecked())
        self._settings.setValue(
            "chk/exclude_ambiguous", self.chkExcludeAmbiguous.isChecked()
        )

    def closeEvent(self, event) -> None:  # noqa: N802
        """ウィンドウ終了時に設定を保存する。

        Args:
            event: Qt の close イベント。
        """
        self._save_settings()
        super().closeEvent(event)

    def on_generate_clicked(self) -> None:
        """「生成」ボタン押下時の処理を行う。"""
        kinds: list[str] = []
        if self.chkDigits.isChecked():
            kinds.append("digits")
        if self.chkLower.isChecked():
            kinds.append("lower")
        if self.chkUpper.isChecked():
            kinds.append("upper")
        if self.chkSymbols.isChecked():
            kinds.append("symbols")

        length = self.spinLength.value()
        count = self.spinCount.value()
        exclude_ambiguous = self.chkExcludeAmbiguous.isChecked()
        symbols = self.txtSymbols.text()

        try:
            passwords = generate_passwords(
                length=length,
                kinds=kinds,
                count=count,
                exclude_ambiguous=exclude_ambiguous,
                symbols=symbols,
            )
        except ValueError as e:
            QMessageBox.warning(self, "エラー", str(e))
            if self.statusBar() is not None:
                self.statusBar().showMessage(str(e), 5000)
            return

        self.txtResult.setPlainText("\n".join(passwords))
        if self.statusBar() is not None:
            self.statusBar().showMessage(f"{len(passwords)} 件生成しました", 3000)

    def on_clear_clicked(self) -> None:
        """「クリア」ボタン押下時の処理を行う。"""
        self.txtResult.clear()
        if self.statusBar() is not None:
            self.statusBar().showMessage("クリアしました", 2000)

    def _copy_to_clipboard(self, text: str) -> None:
        """指定テキストをクリップボードへコピーする。

        Args:
            text: コピーする文字列。
        """
        QGuiApplication.clipboard().setText(text)
        if self.statusBar() is not None:
            self.statusBar().showMessage("クリップボードにコピーしました", 2000)

    def on_copy_selected_clicked(self) -> None:
        """「選択行をコピー」ボタン押下時の処理を行う。"""
        selected = self.txtResult.textCursor().selectedText()
        selected = selected.replace("\u2029", "\n").strip()
        if not selected:
            QMessageBox.information(self, "情報", "選択行がありません")
            return
        self._copy_to_clipboard(selected)

    def on_copy_all_clicked(self) -> None:
        """「全てコピー」ボタン押下時の処理を行う。"""
        text = self.txtResult.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "情報", "結果が空です")
            return
        self._copy_to_clipboard(text)

    def _update_symbols_enabled(self, enabled: bool) -> None:
        """記号入力欄の有効/無効を切り替える。

        Args:
            enabled: True の場合に入力可能とする。
        """
        self.txtSymbols.setEnabled(enabled)
        self.btnResetSymbols.setEnabled(enabled)

    def on_reset_symbols_clicked(self) -> None:
        """記号セットを既定値へ戻す。"""
        self.txtSymbols.setText(DEFAULT_SYMBOLS)
        if self.statusBar() is not None:
            self.statusBar().showMessage("記号セットを既定値に戻しました", 2000)
