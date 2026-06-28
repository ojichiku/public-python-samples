# WordPress Draft Publisher Codex

Markdownファイルから投稿情報を読み込み、WordPress REST APIで下書き投稿または既存記事を更新するPythonツールです。

最小限の投稿ツールとして、ローカルのMarkdown記事をWordPressの下書きに送信します。管理画面やWordPressプラグインを作るものではありません。

## できること

- `.env` からWordPress接続情報を読み込む
- 指定フォルダ内のMarkdownファイルを読み込む
- タイトル、スラッグ、カテゴリ、タグ、本文を取得する
- Markdown本文をGutenbergブロックコメント付きHTMLへ変換する
- カテゴリ名とタグ名をWordPress側のIDに変換する
- 存在しないカテゴリ、タグを作成する
- 同じスラッグの記事がなければ新規下書き投稿する
- 同じスラッグの記事があれば既存記事を更新する
- 成功したMarkdownファイルを `done` フォルダへ移動する

## ディレクトリ構成

```text
wordpress-draft-publisher-codex/
├─ .env.example
├─ AGENTS.md
├─ PLANS.md
├─ README.md
├─ post_to_wordpress.py
├─ pyproject.toml
├─ requirements.txt
├─ uv.lock
├─ docs/
│  ├─ requirements.md
│  └─ sample_post.md
├─ draft/
│  └─ .gitkeep
└─ done/
   └─ .gitkeep
```

`draft/` と `done/` は実行時に使うフォルダです。`.gitkeep` 以外のファイルはGit管理対象外にしています。

## 事前準備

Python 3.13以上を使用します。

### uvを使う場合

このサンプルのディレクトリへ移動して、依存ライブラリをインストールします。

```bash
cd samples/wordpress-draft-publisher-codex
uv sync
```

### pipを使う場合

`uv`を使わない場合は、仮想環境を作成してから`requirements.txt`をインストールします。

LinuxまたはmacOSの場合:

```bash
cd samples/wordpress-draft-publisher-codex
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

WindowsのPowerShellの場合:

```powershell
cd samples/wordpress-draft-publisher-codex
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## .envの設定

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

## Markdownファイルの書き方

Markdownファイルは次の形式で書きます。

````markdown
# 投稿情報

## 1. タイトル

WordPress下書き投稿ツールの動作確認

## 2. スラッグ

wordpress-draft-publisher-codex-test

## 3. カテゴリ

Python

## 4. タグ

Python,WordPress,Codex

## 5. 本文

これは本文です。

## 見出しレベル2

本文ではMarkdown記法を使えます。

```python
print("hello")
```
````

取得する投稿情報は、タイトル、スラッグ、カテゴリ、タグ、本文です。

本文では、見出し、段落、リスト、コードブロック、引用、水平線、表などを使えます。本文内の見出しは `##` から `######` を想定しています。

サンプルファイルは `docs/sample_post.md` にあります。投稿テストに使う場合は、`draft/` フォルダへコピーします。

LinuxまたはmacOSの場合:

```bash
cp docs/sample_post.md draft/sample_post.md
```

WindowsのPowerShellまたはコマンドプロンプトの場合:

```bat
copy docs\sample_post.md draft\sample_post.md
```

## 実行方法

引数を指定しない場合は、`draft` フォルダ内のMarkdownファイルを処理します。

uvを使う場合:

```bash
uv run python post_to_wordpress.py
```

pipを使う場合:

```bash
python post_to_wordpress.py
```

投稿対象フォルダを指定することもできます。

```bash
uv run python post_to_wordpress.py draft
```

`draft` フォルダ直下に複数のMarkdownファイルがある場合は、すべて処理します。処理順はファイル名順です。

サブフォルダ内のMarkdownファイルは処理対象外です。

成功すると、投稿ID、ステータス、編集URL、移動先が表示されます。

```text
WordPressへの投稿に成功しました
投稿ID: 123
ステータス: draft
編集URL: https://example.com/wp-admin/post.php?post=123&action=edit
移動先: /path/to/wordpress-draft-publisher-codex/done/sample_post.md
```

## 投稿後のファイル移動

投稿または更新に成功したMarkdownファイルは、`done` フォルダへ移動します。

`done` フォルダに同名ファイルがある場合は上書きします。

エラーが発生したMarkdownファイルは、`done` フォルダへ移動しません。

複数ファイルを処理している場合、1つのファイルでエラーが発生しても、残りのファイルの処理は続行します。

## スラッグが既に存在する場合

このツールは、投稿前にWordPress REST APIで同じスラッグの記事を検索します。

- 同じスラッグの記事がない場合は、新規下書き投稿します。
- 同じスラッグの記事がある場合は、既存記事を更新します。

投稿ステータスは常に `draft` です。いきなり公開する `publish` は使いません。

## カテゴリとタグの注意

カテゴリ名とタグ名からWordPress上のIDを取得します。

存在しないカテゴリやタグは自動作成します。カテゴリ名やタグ名を入力ミスすると、新しいカテゴリやタグが作成されるため注意してください。

## エラー確認

エラーが出た場合は、表示されたメッセージを確認します。

WordPress APIでエラーが返った場合は、`status_code` と `response` を表示します。認証エラー、URL間違い、送信データの問題を切り分ける手がかりになります。
