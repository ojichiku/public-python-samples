# Codexへの依頼文

Pythonで、Markdown記事をWordPressへ下書き投稿するツールを作成してください。

今回は、細かい実装方法を指定しすぎず、要件をもとにCodexに設計と実装を任せます。

まず、以下の2つのファイルを作成してください。

* AGENTS.md
* PLANS.md

そのうえで、PLANS.mdの内容に沿ってツールを実装してください。

## ツールの目的

Markdownで書いた記事を読み込み、WordPress REST APIを使ってWordPressへ下書き投稿するツールを作成します。

このツールは、最小限の投稿ツールです。

複雑な管理画面や、本格的なWordPressプラグインを作るものではありません。

## 作成するフォルダ

第4回の記事で `samples/wordpress-post-tool` は使用済みのため、今回は別フォルダで作成してください。

例：

```text
samples/wordpress-draft-publisher-codex/
```

このフォルダ配下に、必要なファイルを作成してください。

## 作成してほしいファイル

最低限、以下のファイルを作成してください。

```text
samples/wordpress-draft-publisher-codex/
  AGENTS.md
  PLANS.md
  post_to_wordpress.py
  requirements.txt
  README.md
  draft/
  done/
```

## ツールの要件

ツールでは、以下を実現してください。

* `.env` からWordPress接続情報を読み込む
* 指定フォルダ内のMarkdownファイルを読み込む
* Markdownファイルから投稿情報を取得する
* Markdown本文をWordPress投稿用に変換する
* WordPress REST APIを使って下書き投稿する
* スラッグが既に登録済みの場合は、新規投稿ではなく既存記事を更新する
* 投稿または更新が成功したMarkdownファイルは `done` フォルダへ移動する
* 処理に失敗したMarkdownファイルは移動しない

## コマンドライン引数

投稿対象のMarkdownファイルが入ったフォルダを、コマンドライン引数で指定できるようにしてください。

例：

```bash
python post_to_wordpress.py draft
```

引数が指定されない場合は、デフォルトで `draft` フォルダを対象にしてください。

## 投稿後のファイル移動

投稿または更新が成功したMarkdownファイルは、終了フォルダへ移動してください。

終了フォルダは `done` とします。

例：

```text
draft/
done/
```

`done` フォルダが存在しない場合は、自動作成してください。

同名ファイルが `done` フォルダに存在する場合は、上書きして移動してください。

## .env の仕様

`.env` には、以下の情報を設定する想定です。

```env
WP_SITE_URL=https://example.com
WP_USERNAME=your_username
WP_APP_PASSWORD=your_application_password
```

`.env` や認証情報はGitHubに公開しない前提にしてください。

必要であれば、`.env.example` を作成しても構いません。

## Markdownファイルの仕様

Markdownファイルは、以下の形式を想定します。

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

## 見出しのテスト

本文では、通常のMarkdown書式を使えるようにしてください。

* 箇条書き
* 太字
* コードブロック
* 表
```

取得する投稿情報は以下です。

* タイトル
* スラッグ
* カテゴリ
* タグ
* 本文

本文部分は、Markdownの書式指定が使えるようにしてください。

## カテゴリ・タグ

カテゴリ名、タグ名からWordPress上のIDを取得してください。

存在しないカテゴリ・タグは自動作成してください。

カテゴリやタグの名前を間違えると、新しいカテゴリ・タグが作成されるため、READMEにも注意書きを入れてください。

## 投稿・更新の仕様

投稿ステータスは必ず `draft` にしてください。

いきなり公開する `publish` は使わないでください。

スラッグで既存記事を検索し、同じスラッグの記事がある場合は更新してください。

* 同じスラッグの記事がない場合：新規下書き投稿
* 同じスラッグの記事がある場合：既存記事を更新

## エラー処理

最低限、以下の場合は分かりやすいメッセージを表示してください。

* `.env` が存在しない
* WordPress接続情報が不足している
* 対象フォルダが存在しない
* Markdownファイルが存在しない
* Markdownから必要な投稿情報を取得できない
* スラッグが取得できない
* WordPress APIでエラーが返った
* 投稿後のファイル移動に失敗した

エラーが発生したMarkdownファイルは、`done` フォルダへ移動しないでください。

## AGENTS.mdに書いてほしい内容

AGENTS.mdには、このツールをCodexが修正・拡張するときのルールを書いてください。

最低限、以下を含めてください。

* このツールの目的
* 最小限の投稿ツールであること
* 読みやすさを優先すること
* `.env` や認証情報をGitHubに公開しないこと
* 投稿は必ず下書きにすること
* 既存記事はスラッグで検索して更新すること
* 投稿成功後にMarkdownファイルを `done` に移動すること
* エラー時はファイルを移動しないこと

## PLANS.mdに書いてほしい内容

PLANS.mdには、実装計画を書いてください。

細かい関数名までは指定しなくてよいです。

ただし、以下の流れが分かるようにしてください。

1. `.env` を読み込む
2. 投稿対象フォルダを決める
3. Markdownファイルを読み込む
4. Markdownから投稿情報を取得する
5. 本文MarkdownをWordPress投稿用に変換する
6. WordPress REST APIでカテゴリ・タグを取得または作成する
7. スラッグで既存記事を検索する
8. 新規投稿または更新を行う
9. 成功したMarkdownファイルを `done` に移動する
10. READMEに使い方を書く

## READMEに書いてほしい内容

READMEには、以下を含めてください。

* ツールの概要
* 必要な準備
* `.env` の設定例
* Markdownファイルの書き方
* 実行方法
* 投稿後に `done` フォルダへ移動されること
* スラッグが既に存在する場合は更新されること
* カテゴリ・タグ名の入力ミスに注意すること
* `.env` をGitHubに公開しないこと

## 最終的にやってほしいこと

まず `AGENTS.md` と `PLANS.md` を作成してください。

その後、PLANS.mdに沿ってPythonツールを実装してください。

実装後、READMEに使い方をまとめてください。
