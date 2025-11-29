# logfilter-cli

キーワードの部分一致と日付範囲でログをフィルタするシンプルな Python CLI ツールです。スペース区切りで、行頭に `YYYY-MM-DD` が付くテキストログを対象とします。

## 対応ログ形式
- 1 行 1 レコードのテキストログを想定
- 行頭が `YYYY-MM-DD` なら日付フィルタ対象（それ以外の行は日付フィルタ指定時に除外）
- スペース区切りでレベルやメッセージが続く形式

例:
```
2025-11-01 12:30:10 INFO User logged in
2025-11-02 08:15:00 ERROR Failed to connect to database
NoDateLine This line does not start with a date
```

## 必要環境
- Python 3.13
- [uv](https://docs.astral.sh/uv/) が利用可能であること

## セットアップ
開発環境（dev 依存含む）:
```
uv sync
```

本番ビルド用（dev 依存除外）:
```
uv sync --no-dev
```

## 使い方
セットアップ方法に応じて 2 通りの呼び出し方を用意しています。

### 方法A: モジュールとして直接実行（最小構成）
```
cd samples/logfilter-cli
PYTHONPATH=src uv run python -m logfilter_cli.cli log.txt --contains ERROR
```

### 方法B: スクリプトとして実行（編集インストール済み）
```
cd samples/logfilter-cli
uv pip install -e .
uv run logfilter-cli log.txt --contains ERROR
```

日付フィルタを含む例（どちらの方法でも引数は同じ）:
```
uv run -m logfilter_cli.cli log.txt \
  --contains ERROR \
  --date-from 2025-11-01 \
  --date-to 2025-11-03 \
  --output filtered.log
```

### 主なオプション
- `--contains TEXT` : 部分一致キーワード（デフォルトで大文字小文字を無視）
- `--date-from YYYY-MM-DD` : 開始日（この日付以降を含む）
- `--date-to YYYY-MM-DD` : 終了日（この日付以前を含む）
- `--output PATH` : 出力先ファイル（省略時は標準出力）
- `--case-sensitive` : キーワード検索で大文字小文字を区別する

## テスト
```
uv run pytest
```

## Nuitka でのビルド例（簡易）
依存を本番用に揃えた上で実行してください（例: `uv sync --no-dev` 済み想定）。
```
uv run python -m nuitka --onefile src/logfilter_cli/cli.py
```

## ディレクトリ構成
```
samples/logfilter-cli/
  AGENTS.md          # 仕様と行動指針
  PLANS.md           # 実装計画
  README.md          # 本ドキュメント
  src/logfilter_cli/
    __init__.py
    cli.py           # CLI エントリーポイント
    parser.py        # 行のパースと日付抽出
    filters.py       # キーワード＆日付フィルタ
  tests/
    test_parser.py
    test_filters.py
    test_cli.py
```

## ライセンス
MIT License
