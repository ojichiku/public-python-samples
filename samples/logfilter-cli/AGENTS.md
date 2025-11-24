# AGENTS.md
# Project Specification for logfilter-cli

このファイルは、logfilter-cli プロジェクトに取り組むエージェント（Codex）への
仕様書・コンテキスト・行動指針です。

エージェントは、この AGENTS.md を読み、PLANS.md を作成し、
計画に沿ってコード・テスト・ドキュメントを生成します。

---

## 1. プロジェクト概要（Overview）

- **プロジェクト名**: logfilter-cli  
- **所在パス**: `public-python-samples/samples/logfilter-cli`

### 1-1. 目的（Purpose）

テキスト形式のログファイルから、  
**キーワードの部分一致**および**日付範囲**に基づいて行をフィルタリングする  
シンプルな Python 製 CLI ツールを開発する。

このツールは、ブログ記事の題材・サンプルコードとしても利用する。

### 1-2. 成果物（Deliverables）

- Python 3.13 で動作する CLI ツール
- `uv` を用いた環境構築（pyproject.toml）
- `pytest` によるユニットテスト一式（dev 依存）
- 実用的な README（使い方・設計概要）
- 将来的に Nuitka でビルド可能な構成（余計な依存を持たない）

---

## 2. 要件（Requirements）

### 2-1. 対象と前提

- 対象は **ログファイルのみ**
- CSV 対応は今回のスコープに含めない（Future Work）
- ログは **テキストファイルで、行ごとに 1 レコード**
- ログのフォーマットは **スペース区切り**を前提とする

例：

```text
2025-11-01 12:30:10 INFO User logged in
2025-11-02 08:15:00 ERROR Failed to connect to database
NoDateLine This line does not start with a date
```

### 2-2. 日付フィルタ仕様（Date Filter）

* **行の先頭が `YYYY-MM-DD` 形式の場合のみ** 日付フィルタ対象とする

  * 例: `2025-11-01 12:30:10 INFO ...`
* `--date-from` および `--date-to` を指定した場合：

  * 上記形式の日付を持つ行のみを比較対象とする
  * 日付がパースできない行は「日付フィルタの対象外」とし、
    デフォルトでは **フィルタ結果に含めない** 方針とする
* `--date-from` のみ指定、`--date-to` のみ指定のケースもサポートする

### 2-3. キーワードフィルタ仕様（Keyword Filter）

* `--contains` オプションでキーワードを 1 つ指定する
* **部分一致**で行をフィルタする（大文字小文字の扱いはエージェントが合理的に決めてよいが、README に明記すること）
* 複数キーワード対応はスコープ外（将来の拡張）

### 2-4. CLI 仕様（Command Line Interface）

想定コマンド例：

```bash
logfilter-cli log.txt --contains ERROR

logfilter-cli log.txt \
  --contains ERROR \
  --date-from 2025-11-01 \
  --date-to 2025-11-03 \
  --output filtered.log
```

* 必須引数:

  * 入力ログファイルパス（例: `log.txt`）
* 主なオプション:

  * `--contains TEXT` : 部分一致キーワード
  * `--date-from YYYY-MM-DD` : 開始日（この日付以降を含む）
  * `--date-to YYYY-MM-DD` : 終了日（この日付以前を含む）
  * `--output PATH` : 出力ファイルパス（省略時は標準出力）

---

## 3. 技術要件（Technical Requirements）

* **Python バージョン**: 3.13
* **パッケージ管理**: `uv` を使用

  * 本番依存（runtime dependencies）は最小限にする
  * `pytest` は **dev-dependencies** として追加し、本番ビルド環境には含めない
* **ビルド**: Nuitka での実行ファイル作成を想定

  * 余計なパッケージを含めない構成にすること
* **テスト**: `pytest` によるユニットテスト
* **CLI 実装**: `argparse` を基本とする（他を使う場合は README に明記）
* 対応 OS: Windows / macOS / Linux を想定（特別な OS 依存コードは避ける）

---

## 4. ディレクトリ構成（Directory Structure）

本プロジェクトは `public-python-samples` リポジトリ内の 1 サンプルとして配置される。

```text
public-python-samples/
  samples/
    logfilter-cli/
      AGENTS.md        # 本ファイル（仕様書）
      PLANS.md         # エージェントが作成・更新する計画ファイル
      pyproject.toml   # uv 用設定（Python 3.13 / dev-deps に pytest）
      src/
        logfilter_cli/
          __init__.py
          cli.py        # CLI エントリーポイント
          parser.py     # ログ行のパース・日付抽出
          filters.py    # キーワードフィルタ・日付フィルタ
      tests/
        test_parser.py
        test_filters.py
```

---

## 5. 実装方針（Implementation Notes）

### 5-1. モジュールの役割

* `src/logfilter_cli/cli.py`

  * `argparse` による CLI 定義
  * 引数のバリデーション
  * `parser` / `filters` を呼び出して処理を実行
  * ファイル入出力（読み込み・書き込み）

* `src/logfilter_cli/parser.py`

  * 各ログ行を表現するための型（例: `NamedTuple` や `dataclass`）を定義してもよい
  * 行から日付文字列の抽出
  * 日付のパース（`datetime.date`）
  * 1 行単位の情報を分解して返す純粋関数を中心に設計する

* `src/logfilter_cli/filters.py`

  * キーワードフィルタ関数
  * 日付フィルタ関数
  * フィルタ条件の組み合わせ（AND 条件）を提供するヘルパ関数

### 5-2. テスト方針

* `tests/test_parser.py`

  * 正しい形式の日付行から `YYYY-MM-DD` を抽出・パースできる
  * 日付がない行／形式が異なる行を適切に扱う
* `tests/test_filters.py`

  * 部分一致フィルタが期待どおりに動作する
  * 日付範囲フィルタが境界値（ちょうど from/to の日付）を含むかどうかを正しく処理する
  * キーワードと日付フィルタの組み合わせ動作を確認する

---

## 6. README に含めるべき内容（For README Generation）

エージェントは README を生成する際、最低限以下の内容を含めること：

1. プロジェクト概要
2. 対応しているログ形式（スペース区切り / 先頭日付フォーマットの説明）
3. 必要環境

   * Python 3.13
   * uv のインストール方法（簡潔に）
4. インストール手順

   * `uv sync`（開発）
   * `uv sync --no-dev`（本番ビルド用）
5. 基本的な使い方

   * シンプルなフィルタ例
   * 日付フィルタを含む例
6. オプション一覧
7. テストの実行方法

   * `uv run pytest`
8. Nuitka でビルドする際の簡単な例（必要に応じて）
9. ディレクトリ構成の説明
10. ライセンス（例: MIT License）

---

## 7. エージェントへの行動指針（Agent Behavior Instructions）

* **AGENTS.md を最優先で参照すること。**
* まず PLANS.md を生成・更新し、作業手順を明示してからコードを作成すること。
* 曖昧な点があっても、この仕様内で合理的なデフォルトを選択し、コード内コメントや README で説明を付けること。
* ユーザーに追加の質問は行わず、この AGENTS.md の内容に基づいて完結させること。
* コードはテストしやすいよう、関数に分割して「純粋な処理」と「IO処理」を分けること。
* 創作で仕様を勝手に拡張しないこと（CSV対応などは Future Expansion に留める）。
* 実行ファイルビルドを考慮し、依存関係は最小限に保つこと。
* すべての関数・クラスには **docstring（Google Style または Sphinx Style）** を必ず日本語で書くこと。
* コードの意図や重要な処理には **適切なコメント** を日本語で記述し、後から読んだときに理解しやすいようにすること。
* コメントは「何をしたか」ではなく **“なぜそうするのか”** を中心に書くこと（コードで明らかなことはコメントしない）。
* 複雑な処理や枝分かれ部分はコメントで明確に説明すること。 
---

## 8. 今後の拡張候補（Future Expansion）

このプロジェクトは今後、以下のような拡張を行う可能性がある：

* CSV 対応
* 複数キーワードによるフィルタ（AND/OR 条件）
* 正規表現検索
* ログレベル（INFO/ERROR など）によるフィルタ
* JSON ログフォーマットへの対応
* 複数ファイル入力・マージ処理

これらは現時点のスコープには含めない。

---

# End of AGENTS.md