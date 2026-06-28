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

これは、`wordpress-draft-publisher-codex` の動作確認用Markdownです。
WordPress REST APIを使って、この記事を下書きとして投稿または更新します。

## 見出しレベル2の確認

本文内の `##` は、WordPressの見出しレベル2として扱う想定です。
投稿タイトルは上部の「タイトル」欄から取得するため、本文内では `#` 見出しを使わない想定にしています。

### 見出しレベル3の確認

`###` は見出しレベル3として変換します。

#### 見出しレベル4の確認

`####` も本文内の小見出しとして変換対象です。

## 基本的なMarkdown記法

段落内では、**太字**、`インラインコード`、[リンク](https://example.com) を使います。

- 箇条書きの1つ目
- 箇条書きの2つ目
- 箇条書きの3つ目

1. 番号付きリストの1つ目
2. 番号付きリストの2つ目
3. 番号付きリストの3つ目

## コードブロックの確認

Pythonコードの表示確認です。

```python
from pathlib import Path


markdown_text = Path("docs/sample_post.md").read_text(encoding="utf-8")
print(markdown_text.splitlines()[0])
```

コマンド例の表示確認です。

```bash
uv run python post_to_wordpress.py draft
```

## 引用の確認

> これは引用ブロックの確認です。
> 複数行の引用も同じ引用ブロックとして扱う想定です。

## 水平線の確認

下に水平線を入れています。

---

水平線のあとに続く通常の段落です。

## 表の確認

| 項目 | 内容 | 備考 |
| --- | --- | --- |
| 投稿ステータス | draft | 公開せず下書きにします |
| スラッグ | wordpress-draft-publisher-codex-test | 既存記事があれば更新します |
| 移動先 | done | 成功したMarkdownだけ移動します |

## まとめ

このサンプルでは、見出し、段落、リスト、コードブロック、引用、水平線、表の変換を確認できます。
投稿後はWordPressの編集画面で、各ブロックが意図どおり表示されているか確認してください。
