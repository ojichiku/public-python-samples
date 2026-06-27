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

## Markdown投稿の確認

このサンプルでは、WordPressへ送信した本文がMarkdown形式のまま扱えるかを確認します。

### 確認したいポイント

- `##`の見出しが記事内で表示されること
- `###`の小見出しが記事内で表示されること
- 箇条書きが崩れずに表示されること
- テーブルが読みやすく表示されること
- コードブロックがそのまま表示されること

### 投稿前に準備するもの

1. WordPressのURL
2. WordPressのユーザー名
3. WordPressのアプリケーションパスワード
4. 投稿したいMarkdownファイル

## テーブルの表示確認

| 項目 | 内容 | 備考 |
| --- | --- | --- |
| タイトル | Markdown投稿テスト | `## 1. タイトル`から読み込みます |
| スラッグ | chatgpt-wordpress-post-test | `## 2. スラッグ`から読み込みます |
| カテゴリ | Python | 存在しない場合は作成します |
| タグ | ChatGPT, WordPress, Python | カンマ区切りで複数指定します |

## コードブロックの表示確認

PythonでMarkdownファイルを読み込む処理の例です。

```python
from pathlib import Path


text = Path("sample_post.md").read_text(encoding="utf-8")
print(text[:100])
```

コマンド例もコードブロックとして記載できます。

```bash
uv run python post_to_wordpress.py
```

## まとめ

この本文には、見出し、箇条書き、番号付きリスト、テーブル、コードブロックが含まれています。
WordPressへ下書き投稿したあと、編集画面で表示を確認してください。
