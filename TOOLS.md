# TOOLS

ブログ掲載用に、本リポジトリのパスワード生成ツールをまとめています。

## 1. パスワード生成CLIツール

- 対象ディレクトリ: `samples/password-generator-cli`
- 形式: コマンドラインツール（`argparse`）
- 概要:
  - 文字数・生成数・文字種を指定して、条件に合ったパスワードを生成します。
  - Pythonスクリプトとして実行でき、PyInstaller/Nuitkaで実行ファイル化する想定のサンプルです。

### 主な機能

- 文字種の選択（数字/小文字/大文字/記号）
- パスワード長の指定
- 生成件数の指定
- 記号セットのカスタマイズ（`--symbols`）
- 選択した文字種を各1文字以上含む生成ロジック

### 利用イメージ

```bash
python samples/password-generator-cli/password_gen.py -l 20 -k digits lower upper symbols -n 3
```

---

## 2. パスワード生成GUIツール

- 対象ディレクトリ: `samples/password-generator-gui`
- 形式: デスクトップGUI（PySide6 + Qt Designer）
- 概要:
  - CLI版の生成ロジックをベースに、画面操作でパスワードを生成できるツールです。
  - 設定保存やコピー操作など、日常利用を意識したUI機能を備えています。

### 主な機能

- 文字数・生成数・文字種（数字/小文字/大文字/記号）の指定
- 紛らわしい文字（`0 O 1 I l`）の除外
- 使用記号セットの入力・既定値への復帰
- 生成結果の「選択コピー」「全件コピー」
- `QSettings` による前回設定の保存・復元

### 起動イメージ

```bash
cd samples/password-generator-gui
uv run python -m password_gui
```

---

## 関連README

- CLI: `samples/password-generator-cli/README.md`
- GUI: `samples/password-generator-gui/README.md`
