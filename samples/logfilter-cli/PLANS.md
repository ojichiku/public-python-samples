# PLANS.md
# Execution Plan for logfilter-cli

このファイルは、AGENTS.md に基づいてエージェントが行う作業計画をまとめる。
エージェントは、この計画に沿ってコード生成・テスト作成・ドキュメント作成を行う。

---

## 1. 全体方針（Overall Strategy）

- AGENTS.md の仕様内容に従い、最小構成の logfilter-cli を構築する。
- 作業は「構造の作成 → 実装 → テスト → README」を順に行う。
- 各ファイルは src/logfilter_cli/ 配下に配置し、pytest 用に tests/ を作成する。
- docstring とコメントを適切に記述し、理解しやすいコードにする。

---

## 2. 実装タスク一覧（Implementation Tasks）

### 2-1. ディレクトリと初期ファイルの準備
- `src/logfilter_cli/` ディレクトリを作成する。
- 次のファイルを生成:
  - `__init__.py`
  - `cli.py`
  - `parser.py`
  - `filters.py`

- `tests/` ディレクトリを作成し、以下を生成:
  - `test_parser.py`
  - `test_filters.py`

---

## 3. モジュール別の実装計画（Module-Level Plan）

### 3-1. parser.py
- 行テキストを受け取り、構造化データに変換する関数を作成。
- 先頭の `YYYY-MM-DD` を検出するロジックを実装。
- 日付パース用の関数を実装（datetime.date を返す）。
- 日付が無い行の扱いを仕様に従って整理。
- docstring を記述。

### 3-2. filters.py
- 部分一致キーワードフィルタの関数を作成。
- 日付範囲フィルタ（from/to）の関数を実装。
- 複合フィルタ（キーワード AND 日付）のヘルパー関数を作成。
- docstring を記述。

### 3-3. cli.py
- argparse を用いて CLI の引数を定義。
- 引数バリデーション（存在チェック、日付形式チェックなど）。
- parser / filters を呼び出してフィルタ処理を実行する関数を定義。
- 標準出力またはファイルへの書き込みを実装。
- 実行例のロジックが明確になるようコメントを書く。

---

## 4. テスト計画（Test Plan）

### 4-1. test_parser.py
- 正しい日付行 → 日付パース成功
- 不正な形式 → パース不可で None など適切な扱い
- 行の分解（スペース区切り）が正しく動く

### 4-2. test_filters.py
- キーワード部分一致の基本動作テスト
- 大文字小文字の扱いが仕様どおりになるか確認
- 日付範囲フィルタの境界チェック
- 2つのフィルタを組み合わせた場合の動作確認

---

## 5. README 生成計画（README Plan）

README には以下を含める：

- プロジェクト概要
- 対応ログ形式（スペース区切り／先頭日付の説明）
- Python 3.13 / uv のセットアップ方法
- 基本的な使い方
- オプション一覧
- 実行例
- テストの実行方法（uv run pytest）
- Nuitka ビルドの簡易手順
- ディレクトリ構成

---

## 6. 仕上げ（Finalization）

- 全ファイルに docstring を付与する。
- 必要なコメントを記入し、可読性を高める。
- 余計な依存を追加しないこと（Nuitka を念頭に置く）。
- PLANS.md が完了したら、コード生成フェーズへ進む。

---

# End of PLANS.md
