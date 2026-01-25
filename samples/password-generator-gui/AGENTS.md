# AGENTS.md — Password Generator GUI (PySide6)

## ゴール（最重要）
- **PySide6 を使ったパスワード生成GUIツール**を作成する。
- **パスワード生成ロジックは既存CLI実装を必ず流用**する（挙動を勝手に変えない）。
  - 参照元（コピー元）：`samples/password-generator-cli/password_gen.py`
  - URL: https://github.com/ojichiku/public-python-samples/blob/main/samples/password-generator-cli/password_gen.py

## 重要方針
- UIは **Qt Designer の `.ui`（XML）** を使う（Pythonで手書きUIしない）。
- UIは `.ui` を **実行時に読み込む方式（QUiLoader）** を採用する。
- ロジック（生成処理）とGUI（画面・イベント）を分離する。
- テストは **pytest必須**（少なくともロジック層はテストする）。
- 追加機能は「仕様に書いた範囲のみ」。勝手な拡張は禁止。

---

## 想定環境
- Windows 11
- Python 3.13
- 依存：PySide6 / pytest（＋必要なら ruff, mypy は任意）
- 乱数は `random` ではなく **`secrets`** を使用（CLI実装に合わせる）

---

## プロジェクト構成（必須）
`password-generator-gui` という新しいサンプルとして追加する想定。

```

samples/password-generator-gui/
pyproject.toml
README.md
resources/
ui/
main_window.ui
src/
password_gui/
**init**.py
**main**.py
main_window.py
generator.py
tests/
test_generator.py

```

---

## UI仕様（main_window.ui）
### 1) UIファイル
- 置き場所：`src/resources/ui/main_window.ui`
- Qt Designerで作成し、XMLとしてコミットする。

### 2) objectName（固定・必須）
Qt Designer上で、以下の **objectName を必ず設定**する（Python側はこれ前提で findChild する）：

- `spinLength`（QSpinBox）… パスワード長
- `spinCount`（QSpinBox）… 生成数
- `chkDigits`（QCheckBox）… 数字
- `chkLower`（QCheckBox）… 小文字
- `chkUpper`（QCheckBox）… 大文字
- `chkSymbols`（QCheckBox）… 記号
- `chkExcludeAmbiguous`（QCheckBox）… 紛らわしい文字除外（任意だがUIに入れる）
- `btnGenerate`（QPushButton）… 生成
- `btnClear`（QPushButton）… クリア
- `btnCopySelected`（QPushButton）… 選択行をコピー
- `btnCopyAll`（QPushButton）… 全てコピー
- `txtResult`（QPlainTextEdit 推奨）… 結果表示（readOnly）

### 3) 初期値（推奨）
- `spinLength`: 20（min 4 / max 128）
- `spinCount`: 3（min 1 / max 50）
- `chkDigits/chkLower/chkUpper/chkSymbols`: すべてON
- `chkExcludeAmbiguous`: OFF

---

## 実装仕様（Python）

### A. ロジック層：`src/password_gui/generator.py`（必須）
- ここに **CLIのパスワード生成実装を移植**する。
- 既存CLI（password_gen.py）から、生成に必要な関数/定数/文字セット定義をコピーし、
  GUIから呼べる形に最小限ラップする。
- **アルゴリズムや文字セットの意味を勝手に変更しない**（「改善」はしない）。

#### 提供する公開関数（必須）
```python
def generate_passwords(
    length: int,
    kinds: list[str],
    count: int,
    exclude_ambiguous: bool = False,
) -> list[str]:
    """
    kinds は 'digits', 'lower', 'upper', 'symbols' のみを受け付ける。
    CLI実装（password_gen.py）と同等の生成結果になること。
    不正な入力は ValueError。
    """
```

#### バリデーション（必須）

* `kinds` が空 → ValueError
* 候補文字が空 → ValueError
* length/count が不正 → ValueError（UIでも制限するが、関数でも防御）

#### exclude_ambiguous（要件）

* ON の場合、候補文字から紛らわしい文字を除外する。
* 除外対象は **固定**にする（例：`0 O 1 I l`）。ただし CLI 側に定義があるならそれに合わせる。
* excludeのせいで候補が空になる場合は ValueError。

---

### B. GUI層：`src/password_gui/main_window.py`（必須）

* QMainWindowベースで、`.ui` を QUiLoader で読み込む。
* objectName を使ってウィジェット参照を取得し、イベント接続する。

#### UIロード（必須）

* `.ui` のパスは `src/resources/ui/main_window.ui`
* 実行時カレントに依存しないように、`Path(__file__)` 基準で解決する。

#### ボタン動作（必須）

* 生成（btnGenerate）

  * UI値取得→バリデーション→ `generator.generate_passwords` 呼び出し
  * 結果は `txtResult` に 1行1パスワードで表示
  * エラーは `QMessageBox.warning` + 可能ならステータス表示
* クリア（btnClear）

  * txtResult を空にする
* 選択行をコピー（btnCopySelected）

  * 選択テキストをクリップボードへ
  * 選択なしなら `QMessageBox.information`
* 全てコピー（btnCopyAll）

  * txtResult 全文をクリップボードへ
  * 空なら `QMessageBox.information`

#### 追加（任意だが推奨）

* `QSettings` で最終設定を保存/復元（長さ・生成数・チェック状態）

---

### C. エントリポイント：`src/password_gui/__main__.py`（必須）

* `python -m password_gui` で起動できること。
* `QApplication` を作成して MainWindow を表示。

---

## テスト（必須）

* `tests/test_generator.py` を作成し、ロジック層をテストする。
* 少なくとも以下をカバー：

  * kinds空で ValueError
  * length/count の境界（最小/最大、異常値）
  * exclude_ambiguous ON で候補が空になるケース
  * 同じ入力で「要件どおりの形式（長さ・文字種制約）」になっていること
* 乱数の完全一致までは求めないが、**出力仕様（長さ、文字集合に含まれる）**は必ず検証する。

---

## README（必須）

* 起動方法（uv / python）
* UI操作方法（チェック項目の意味、コピー方法）
* 参照元CLIの説明（リンク）

---

## 完了条件（Acceptance Criteria）

* `python -m password_gui` でGUIが起動する
* `.ui` は XML として `src/resources/ui/main_window.ui` に存在する
* 指定の objectName が設定されている
* 生成・クリア・コピー（選択/全体）が動作する
* 生成ロジックは CLI の `password_gen.py` を流用し、勝手な仕様変更がない
* `pytest` が通る

---

## 作業手順（推奨）

1. フォルダ/pyproject 作成（最小構成）
2. Qt Designerで `main_window.ui` 作成（objectName 固定）
3. `generator.py` を CLI から移植してテスト作成
4. `main_window.py` で `.ui` 読み込み＋イベント接続
5. README 作成、最終確認（pytest / 起動確認）

---

## 配布・ビルド仕様（Nuitka対応・必須）

### ゴール
- PySide6 GUIツールを **Nuitkaで単一実行ファイル（EXE）としてビルド**できること。
- EXE実行時でも **.ui（XML）が正しく読み込まれる**こと。

---

## Nuitkaビルド前提ルール（最重要）

### 1. リソース（.ui）の扱い
- `src/resources/ui/main_window.ui` は **外部ファイルとして同梱**する。
- Pythonコードでは **ファイルシステムから読み込む設計**にする（pkgutil等は使わない）。

#### UIファイルパス解決ルール（必須）
- 通常実行時と EXE 実行時の両方で動くよう、以下の方針を採用する：

```python
from pathlib import Path
import sys

def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        # Nuitka / PyInstaller 等で EXE 化された場合
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parents[2] / relative_path
