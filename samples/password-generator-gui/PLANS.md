# PLANS.md — Password Generator GUI (PySide6)

## 目的
- AGENTS.md に定義された仕様に従い、
  **PySide6 + Qt Designer (.ui) + Nuitka対応**の
  パスワード生成GUIツールを確実に完成させる。

- 実装途中で迷った場合は、
  **「CLI実装と同等か」「EXE化で壊れないか」**を最優先判断基準とする。

---

## 全体方針
- 作業は **UI → ロジック → 接続 → テスト → ビルド確認** の順で進める
- 各ステップで「ここまでOKなら次へ進む」というチェックポイントを設ける
- UIとロジックを混ぜない（generator.py は GUI 非依存）

---

## STEP 0：事前準備（スキャフォールド）

### 作業内容
- `samples/password-generator-gui/` ディレクトリ作成
- `src/password_gui/` パッケージ作成
- `resources/ui/` ディレクトリ作成
- `pyproject.toml` に PySide6 / pytest を追加
- 空の README.md を作成

### 完了条件
- `python -m password_gui` を実行したときに
  「モジュールが見つからない」以外のエラーが出る状態になっている

---

## STEP 1：UI作成（Qt Designer）

### 作業内容
- Qt Designer で `main_window.ui` を作成
- レイアウトはシンプルでよい（見た目より構造優先）
- **AGENTS.mdで指定された objectName をすべて設定**

### チェックポイント
- 以下の objectName が `.ui` 内に存在する：
  - spinLength / spinCount
  - chkDigits / chkLower / chkUpper / chkSymbols
  - chkExcludeAmbiguous
  - btnGenerate / btnClear / btnCopySelected / btnCopyAll
  - txtResult
- `main_window.ui` が XML として `resources/ui/` に保存されている

---

## STEP 2：ロジック層実装（generator.py）

### 作業内容
- CLI版 `password_gen.py` を読み込み、生成ロジックを移植
- GUI用にラップした `generate_passwords()` を実装
- **挙動はCLIと同等。勝手な仕様変更は禁止**

### チェックポイント
- `generate_passwords()` が以下を満たす：
  - 正常系で `list[str]` を返す
  - 異常系で `ValueError` を送出する
  - `secrets` を使用している
- GUIに関する import が一切ない

---

## STEP 3：ロジック単体テスト（pytest）

### 作業内容
- `tests/test_generator.py` を作成
- ロジックのみをテストする（GUIはテストしない）

### 必須テスト観点
- kinds が空 → ValueError
- length / count の境界値
- exclude_ambiguous ON/OFF の挙動
- 出力文字列の長さ・文字種制約

### 完了条件
- `pytest` がすべて成功する
- テスト失敗時に原因が即分かる内容になっている

---

## STEP 4：GUI層実装（main_window.py）

### 作業内容
- QUiLoader で `main_window.ui` を読み込む
- resource_path() を使って `.ui` のパスを解決
- objectName 前提でウィジェット取得
- 各ボタンのイベントを実装

### チェックポイント
- GUI起動時に例外が出ない
- 以下の操作がすべて動作する：
  - パスワード生成
  - クリア
  - 選択コピー
  - 全コピー
- generator.py の例外が GUI で適切にハンドリングされている

---

## STEP 5：エントリポイント確認（__main__.py）

### 作業内容
- `python -m password_gui` で GUI が起動するようにする
- QApplication は 1 回のみ生成

### 完了条件
- コマンド1発で GUI が立ち上がる
- コンソールに不要なログが出ない

---

## STEP 6：Nuitkaビルド確認

### 作業内容
- AGENTS.md に記載された Nuitka コマンドで EXE を作成
- EXE を別フォルダへコピーして起動テスト

### チェックポイント
- `.ui not found` エラーが出ない
- Qt plugin error が出ない
- GUI操作がすべて通常実行時と同じ

---

## STEP 7：README 仕上げ

### 作業内容
- 以下を README.md に記載：
  - ツール概要
  - 起動方法（python / EXE）
  - UI操作説明
  - 参照元CLIリンク
  - Nuitkaビルド方法

### 完了条件
- READMEを見れば第三者が実行・ビルドできる

---

## 最終完了条件（Done）
- CLI実装と同等のパスワードが生成される
- GUI操作が直感的で破綻しない
- pytest が通る
- NuitkaでEXE化しても壊れない
- AGENTS.md / PLANS.md に書いた内容から逸脱していない

---

## 判断に迷ったら
- それは **CLIと同じか？**
- それは **EXE化で壊れないか？**
- それは **今やる必要があるか？**

→ 1つでも NO なら、やらない。
