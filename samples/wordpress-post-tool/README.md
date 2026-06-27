# WordPress Markdown Post Tool

Markdownファイルから投稿情報を読み込み、WordPressへ下書き投稿するPythonツールです。

第4回記事用の最小版コードです。

## できること

- Markdownファイルを読み込む
- タイトル、スラッグ、カテゴリ、タグ、本文を取得する
- Markdown本文を標準Gutenbergブロック形式に変換する
- カテゴリ名をWordPress側のIDに変換する
- タグ名をWordPress側のIDに変換する
- 存在しないカテゴリ、タグを作成する
- WordPressへ下書き投稿する
- 投稿ID、ステータス、編集URLを表示する

## ディレクトリ構成

```text
wordpress-post-tool/
├─ .env.example
├─ sample_post.md
├─ post_to_wordpress.py
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

## 事前準備

Python 3.13以上を使用します。

### uv を使う場合

このサンプルのディレクトリへ移動して、依存ライブラリをインストールします。

```bash
cd samples/wordpress-post-tool
uv sync
```

### pip を使う場合

`uv`を使わない場合は、仮想環境を作成してから`requirements.txt`をインストールします。

LinuxまたはmacOSの場合:

```bash
cd samples/wordpress-post-tool
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

WindowsのPowerShellの場合:

```powershell
cd samples/wordpress-post-tool
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`.env.example`をコピーして、`.env`を作成します。

LinuxまたはmacOSの場合:

```bash
cp .env.example .env
```

WindowsのPowerShellまたはコマンドプロンプトの場合:

```bat
copy .env.example .env
```

`.env`にWordPressの接続情報を書きます。

```env
WP_SITE_URL=https://example.com
WP_USERNAME=your_username
WP_APP_PASSWORD=your_application_password
```

`.env`には本物の接続情報を書くため、GitHubには公開しないでください。

## Markdownファイルの形式

`sample_post.md`は、次の形式で書きます。

```markdown
# 投稿情報

## 1. タイトル

ChatGPTで作った記事をWordPressへ投稿するテスト

## 2. スラッグ

chatgpt-wordpress-post-test

## 3. カテゴリ

Python

## 4. タグ

ChatGPT,WordPress,Python

## 5. 本文

これはWordPress投稿ツールのテスト用Markdownです。
Pythonでこのファイルを読み込み、WordPressへ下書き投稿します。
```

`##`、`###`、箇条書き、テーブル、コードブロックなどのMarkdown本文は、Python側で標準Gutenbergブロック形式へ変換してからWordPressへ送信します。
WordPress側にMarkdown変換プラグインを入れる必要はありません。

## 実行方法

uvを使う場合:

```bash
uv run python post_to_wordpress.py
```

pipを使う場合:

LinuxまたはmacOSの場合:

```bash
python post_to_wordpress.py
```

WindowsのPowerShellの場合:

```powershell
python post_to_wordpress.py
```

成功すると、次のように表示されます。

```text
WordPressへ下書き投稿しました
投稿ID: 123
ステータス: draft
編集URL: https://example.com/wp-admin/post.php?post=123&action=edit
```

## エラー確認

エラーが出た場合は、表示された`status_code`と`response`を確認します。

認証エラー、URL間違い、送信データの問題を切り分ける手がかりになります。
