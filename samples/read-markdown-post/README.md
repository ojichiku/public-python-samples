# read-markdown-post

Markdown 形式の記事ファイルから、タイトル、スラッグ、本文を読み取る最小サンプルです。

`sample_article.md` の見出しを区切りとして、`read_markdown.py` が投稿用の情報を取り出して表示します。

## 必要環境

- Python 3.13 以上
- [uv](https://docs.astral.sh/uv/) または pip が利用可能であること

## セットアップ

### uv を使う場合

```bash
cd samples/read-markdown-post
uv sync
```

### pip を使う場合

```bash
cd samples/read-markdown-post
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows の PowerShell で仮想環境を有効化する場合は、次のコマンドを使います。

```powershell
.\.venv\Scripts\Activate.ps1
```

このサンプルは標準ライブラリだけで動くため、追加の Python パッケージはありません。

## 使い方

uv を使う場合:

```bash
uv run python read_markdown.py
```

pip を使う場合:

```bash
python read_markdown.py
```

出力例:

```text
title:
ChatGPTで作った記事をWordPressへ投稿するテスト

slug:
chatgpt-wordpress-post-test

body:
これはWordPress投稿ツールのテスト用Markdownです。
Pythonでこのファイルを読み込み、タイトル、スラッグ、本文を取り出します。

### 見出しの例

本文には見出しや文章が入ります。
まずは、Markdownの中身をそのまま本文として扱います。
```

## ファイル構成

```text
samples/read-markdown-post/
  README.md          # 本ドキュメント
  pyproject.toml     # uv 用の実行環境定義
  read_markdown.py   # Markdown 読み取りスクリプト
  sample_article.md  # 読み取り対象のサンプル記事
```

## ライセンス

MIT License
