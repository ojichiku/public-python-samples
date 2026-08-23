# 中小企業庁 補助金公募情報CSV取得ツール

中小企業庁の「補助金公募情報」ページから2026年度の情報を取得し、CSVファイルへ保存するPythonツールです。

## 対象URL

https://www.chusho.meti.go.jp/koukai/hojyokin/kobo.html

## プロジェクトの準備

Python 3.14とuvを用意します。

リポジトリをまだ取得していない場合は、次のコマンドで取得し、このツールのディレクトリへ移動します。

```bash
git clone https://github.com/ojichiku/public-python-samples.git
cd public-python-samples/samples/subsidy_scraper
```

すでにリポジトリを取得済みの場合は、`samples/subsidy_scraper` ディレクトリへ移動してください。

依存パッケージと開発用パッケージをインストールします。

```bash
uv sync
```

## ディレクトリ構成

```text
subsidy_scraper/
├── main.py                         # CLIのエントリーポイント
├── pyproject.toml                  # Python、依存関係、テスト設定
├── requirements.txt               # 実行時依存パッケージ一覧
├── uv.lock                         # 依存バージョンのロックファイル
├── README.md                       # 利用方法
├── src/
│   └── subsidy_scraper/
│       ├── __init__.py
│       └── app.py                  # Web取得、HTML解析、CSV保存
└── tests/
    └── test_app.py                 # 自動テスト
```

## 実行方法

```bash
uv run python main.py
```

## 出力CSV

コマンドを実行したディレクトリに、UTF-8 BOM付きの `subsidy_kobo.csv` を保存します。既存の同名ファイルがある場合は上書きします。

## テストとコードチェック

自動テストを実行します。カバレッジ設定も `pyproject.toml` から適用されます。

```bash
uv run pytest
```

静的チェックとフォーマット確認を実行します。

```bash
uv run ruff check .
uv run ruff format --check .
```

## 利用上の注意

- Webアクセスの直前に3秒待機します。
- 対象サイトの仕様変更により、情報を取得できなくなる可能性があります。
- 対象サイトの利用規約を確認した上で利用してください。
