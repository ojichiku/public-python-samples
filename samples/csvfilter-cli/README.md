# csvfilter-cli

CSV を行単位でストリーム処理し、指定した条件に一致する行だけを出力するシンプルな CLI です。入力は UTF-8 のみ、標準入力は非対応です。

## 必要要件
- Python 3.13 以上

## 実行方法
- `samples/csvfilter-cli/` に移動してから実行してください。
- インストール不要で動かす場合（推奨）:
  - Linux/macOS: `PYTHONPATH=src python -m csvfilter_cli --help`
  - Windows PowerShell: `$env:PYTHONPATH=\"src\"; python -m csvfilter_cli --help`
- 任意で `python -m pip install -e .` してから `python -m csvfilter_cli ...` と実行しても動きます（開発インストールが必要なときだけ）。

## 使い方
- 基本: `python -m csvfilter_cli --input data.csv --and name:contains:Alice --and status:regex:^active$`
- 出力先指定: `python -m csvfilter_cli --input data.csv --output filtered.csv --and city:contains:Tokyo`
- ヘッダーなし（1 始まり列番号）: `python -m csvfilter_cli --input data.csv --no-header --and 2:contains:Alice`
- 区切り変更（TSVなど）: `python -m csvfilter_cli --input data.tsv --delimiter "\t" --and 1:regex:^[0-9]+$`
- 詳細ログ: `python -m csvfilter_cli --input data.csv --and name:contains:Bob -v`

### オプション
- `--input PATH` (必須): 入力 CSV ファイルパス。標準入力は非対応。
- `--output PATH`: 出力先ファイル。未指定なら標準出力。指定時は上書き。
- `--delimiter`: 区切り文字（デフォルト`,`）。
- `--quotechar`: クオート文字（デフォルト`"`）。
- `--no-header`: 先頭行をヘッダーとみなさずデータとして扱う。
- `--and col:op:val`: AND 条件を複数指定可。ヘッダーありならカラム名、`--no-header` 時は 1 始まり列番号。
- `-v / --verbose`: 処理件数・マッチ件数・スキップ件数を stderr に表示。

### 演算子
- `contains`: 部分一致（指定文字列を含む）。
- `regex`: Python `re` による正規表現マッチ（フラグなし）。コンパイルエラー時は終了コード 1。

### 挙動・エラー
- 複数条件は AND のみ。
- ヘッダーありで存在しないカラムを指定した場合は終了コード 1。
- ヘッダーなし時は 1 始まりの列番号で指定。行が短く指定列が無い場合はスキップ。
- 条件に合致する行が 0 件でも終了コード 0。ただし stderr に "0 rows matched" を出力。
- `-v` 指定時は stderr に `processed=..., matched=..., skipped=...` を出力。

## テスト
- `cd samples/csvfilter-cli`
- `PYTHONPATH=src python -m pytest -q` で全テストを実行（uv を使う場合は `uv run` を先頭に付けても可）。

## ディレクトリ構成
```
samples/csvfilter-cli/
├── AGENTS.md              # 仕様詳細
├── PLANS.md               # 実行手順メモ
├── README.md              # このドキュメント
├── pyproject.toml
├── src/
│   └── csvfilter_cli/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py         # CLI 引数処理と実行フロー
│       ├── filters.py     # contains / regex 条件
│       └── io.py          # CSV の読み書きと適用
└── tests/
    ├── test_cli.py
    ├── test_filters.py
    └── test_io.py
```

## ファイル構成（主な役割）
- `src/csvfilter_cli/cli.py` : CLI 引数パースと実行フロー。
- `src/csvfilter_cli/filters.py` : contains / regex 条件の実装。
- `src/csvfilter_cli/io.py` : CSV の読み書きとフィルター適用。
- `src/csvfilter_cli/__main__.py` : `python -m csvfilter_cli` のエントリポイント。
- `tests/` : pytest テスト一式。
