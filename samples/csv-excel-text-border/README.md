# csv-excel-text-border

CSV ファイルを Excel ファイルに変換するシンプルなコマンドラインツールです。

CSV の値を変えずに、Excel で確認しやすい形式へ変換します。先頭の 0、日付のように見える値、数値のように見える値も、文字列としてそのまま出力します。

## できること

- CSV ファイルを `.xlsx` ファイルに変換
- すべての値を文字列として Excel に出力
- 先頭の 0 を保持
- 日付や数値のように見える値の自動変換を防止
- 出力範囲全体に罫線を設定
- ヘッダー行を太字に設定
- 内容に合わせて列幅を自動調整

## 必要環境

- Python 3.13 以上
- [uv](https://docs.astral.sh/uv/) または pip が利用可能であること

## インストール方法

### uv を使う場合

```bash
cd samples/csv-excel-text-border
uv sync
```

### pip を使う場合

```bash
cd samples/csv-excel-text-border
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Windows の PowerShell で仮想環境を有効化する場合は、次のコマンドを使います。

```powershell
.\.venv\Scripts\Activate.ps1
```

## 実行方法

```bash
python csv_to_excel.py sample.csv
```

`sample.csv` を指定した場合、同じフォルダに `sample.xlsx` が作成されます。

uv を使う場合:

```bash
uv run python csv_to_excel.py sample.csv
```

出力例:

```text
Excelファイルを作成しました: sample.xlsx
```

## サンプル CSV での実行例

```bash
cd samples/csv-excel-text-border
uv run python csv_to_excel.py sample.csv
```

作成されるファイル:

```text
sample.xlsx
```

## 出力される Excel ファイルについて

- CSV の 1 行目は Excel の 1 行目に出力されます。
- CSV の 2 行目以降は Excel の 2 行目以降に出力されます。
- すべてのセルは文字列として出力されます。
- ヘッダー行は太字になります。
- データが入っている範囲には罫線が引かれます。
- 列幅は内容を確認しやすい幅に調整されます。

## 注意事項

- 入力ファイルは `.csv` 拡張子のファイルを指定してください。
- 出力先に同名の `.xlsx` ファイルがある場合は上書きされます。
- CSV の読み込みは UTF-8 または UTF-8 BOM 付きのファイルを想定しています。
- Excel 側でセルを編集すると、入力内容によっては Excel の自動変換が働く場合があります。

## ファイル構成

```text
samples/csv-excel-text-border/
  AGENTS.md          # このサンプルで守るルール
  PLANS.md           # 実装計画
  README.md          # 本ドキュメント
  csv_to_excel.py    # CSV から Excel へ変換するスクリプト
  pyproject.toml     # uv 用の実行環境定義
  requirements.txt   # pip 用の依存関係
  sample.csv         # 動作確認用のサンプル CSV
  docs/
    requirements.md  # ChatGPT に作ってもらった依頼内容
```
