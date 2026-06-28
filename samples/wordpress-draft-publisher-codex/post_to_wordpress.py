"""Markdown記事をWordPressへ下書き投稿または更新するツールです。"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import markdown
import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
POSTS_ENDPOINT = "posts"
CATEGORIES_ENDPOINT = "categories"
TAGS_ENDPOINT = "tags"


class WordPressDraftPublisherError(Exception):
    """WordPress下書き投稿ツール用の例外です。"""


@dataclass(frozen=True)
class WordPressConfig:
    """WordPress接続情報です。"""

    url: str
    user: str
    app_password: str


@dataclass(frozen=True)
class Article:
    """Markdownから読み取った投稿情報です。"""

    title: str
    slug: str
    category: str
    tags: list[str]
    body: str


def load_config() -> WordPressConfig:
    """`.env` からWordPress接続情報を読み込みます。"""
    env_path = BASE_DIR / ".env"

    if not env_path.exists():
        raise WordPressDraftPublisherError(
            ".env が見つかりません。.env.example をコピーして設定してください。"
        )

    load_dotenv(env_path)

    missing = [
        name
        for name in ("WP_SITE_URL", "WP_USERNAME", "WP_APP_PASSWORD")
        if not os.getenv(name)
    ]

    if missing:
        joined = ", ".join(missing)
        raise WordPressDraftPublisherError(
            f"WordPress接続情報が不足しています: {joined}"
        )

    return WordPressConfig(
        url=os.environ["WP_SITE_URL"].rstrip("/"),
        user=os.environ["WP_USERNAME"],
        app_password=os.environ["WP_APP_PASSWORD"],
    )


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析します。"""
    parser = argparse.ArgumentParser(
        description="Markdown記事をWordPressへ下書き投稿または更新します。"
    )
    parser.add_argument(
        "draft_dir",
        nargs="?",
        default="draft",
        help="投稿対象のMarkdownファイルが入ったフォルダです。省略時は draft です。",
    )
    return parser.parse_args()


def resolve_target_dir(draft_dir: str) -> Path:
    """投稿対象フォルダを解決します。"""
    path = Path(draft_dir)

    if not path.is_absolute():
        path = BASE_DIR / path

    if not path.exists():
        raise WordPressDraftPublisherError(f"対象フォルダが存在しません: {path}")

    if not path.is_dir():
        raise WordPressDraftPublisherError(f"対象パスがフォルダではありません: {path}")

    return path


def find_markdown_files(target_dir: Path) -> list[Path]:
    """対象フォルダ直下のMarkdownファイルを取得します。"""
    markdown_files = sorted(target_dir.glob("*.md"))

    if not markdown_files:
        raise WordPressDraftPublisherError(
            f"Markdownファイルが見つかりません: {target_dir}"
        )

    return markdown_files


def get_section(text: str, start_marker: str, end_marker: str | None = None) -> str:
    """Markdown本文から指定した見出し範囲を取り出します。"""
    start_index = text.find(start_marker)

    if start_index == -1:
        return ""

    start_index += len(start_marker)

    if end_marker is None:
        return text[start_index:].strip()

    end_index = text.find(end_marker, start_index)

    if end_index == -1:
        return text[start_index:].strip()

    return text[start_index:end_index].strip()


def parse_article(file_path: Path) -> Article:
    """Markdownファイルから投稿情報を読み取ります。"""
    text = file_path.read_text(encoding="utf-8")
    title = get_section(text, "## 1. タイトル", "## 2. スラッグ")
    slug = get_section(text, "## 2. スラッグ", "## 3. カテゴリ")
    category = get_section(text, "## 3. カテゴリ", "## 4. タグ")
    tags_text = get_section(text, "## 4. タグ", "## 5. 本文")
    body = get_section(text, "## 5. 本文")

    missing = [
        label
        for label, value in (
            ("タイトル", title),
            ("スラッグ", slug),
            ("カテゴリ", category),
            ("タグ", tags_text),
            ("本文", body),
        )
        if not value
    ]

    if missing:
        joined = "、".join(missing)
        raise WordPressDraftPublisherError(
            f"Markdownから必要な投稿情報を取得できません: {joined}"
        )

    tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

    if not tags:
        raise WordPressDraftPublisherError("タグを取得できません。")

    return Article(title=title, slug=slug, category=category, tags=tags, body=body)


def markdown_to_html(markdown_text: str) -> str:
    """Markdown断片をHTMLへ変換します。"""
    return markdown.markdown(
        markdown_text,
        extensions=["extra", "fenced_code", "sane_lists", "tables"],
    ).strip()


def wrap_block(block_name: str, inner_html: str, attrs: str = "") -> str:
    """HTMLをGutenbergブロックコメントで囲みます。"""
    attrs_text = f" {attrs}" if attrs else ""
    return (
        f"<!-- wp:{block_name}{attrs_text} -->\n"
        f"{inner_html}\n"
        f"<!-- /wp:{block_name} -->"
    )


def is_heading(line: str) -> bool:
    """本文内で対応するMarkdown見出しか判定します。"""
    return bool(re.match(r"^#{2,6}\s+.+", line))


def is_horizontal_rule(line: str) -> bool:
    """Markdownの水平線か判定します。"""
    return bool(re.match(r"^\s{0,3}(-{3,}|\*{3,}|_{3,})\s*$", line))


def is_list_start(line: str) -> bool:
    """箇条書きまたは番号付きリストの開始行か判定します。"""
    return bool(re.match(r"^\s*([-*+]\s+|\d+\.\s+)", line))


def is_table_start(lines: list[str], index: int) -> bool:
    """Markdownテーブルの開始位置か判定します。"""
    if index + 1 >= len(lines):
        return False

    header = lines[index]
    separator = lines[index + 1]

    return "|" in header and bool(
        re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", separator)
    )


def convert_code_block(lines: list[str], start_index: int) -> tuple[str, int]:
    """フェンス付きコードブロックをGutenbergコードブロックへ変換します。"""
    code_lines: list[str] = []
    index = start_index + 1

    while index < len(lines):
        if lines[index].startswith("```"):
            escaped_code = html.escape("\n".join(code_lines))
            block_html = (
                '<pre class="wp-block-code"><code>' f"{escaped_code}" "</code></pre>"
            )
            return wrap_block("code", block_html), index + 1

        code_lines.append(lines[index])
        index += 1

    raise WordPressDraftPublisherError("コードブロックの終了 ``` が見つかりません。")


def convert_heading(line: str) -> str:
    """Markdown見出しをGutenberg見出しブロックへ変換します。"""
    match = re.match(r"^(#{2,6})\s+(.+)", line)

    if not match:
        raise WordPressDraftPublisherError(f"見出しを変換できません: {line}")

    level = len(match.group(1))
    heading_html = markdown_to_html(line)
    attrs = "" if level == 2 else f'{{"level":{level}}}'
    return wrap_block("heading", heading_html, attrs)


def convert_quote_block(lines: list[str], start_index: int) -> tuple[str, int]:
    """引用ブロックをGutenberg引用ブロックへ変換します。"""
    quote_lines: list[str] = []
    index = start_index

    while index < len(lines) and lines[index].lstrip().startswith(">"):
        quote_lines.append(re.sub(r"^\s*>\s?", "", lines[index]))
        index += 1

    quote_html = markdown_to_html("\n".join(quote_lines))
    block_html = f'<blockquote class="wp-block-quote">{quote_html}</blockquote>'
    return wrap_block("quote", block_html), index


def convert_list_block(lines: list[str], start_index: int) -> tuple[str, int]:
    """リストブロックをGutenbergリストブロックへ変換します。"""
    list_lines: list[str] = []
    index = start_index

    while index < len(lines):
        line = lines[index]

        if not line.strip():
            break

        if (
            is_heading(line)
            or line.startswith("```")
            or line.lstrip().startswith(">")
            or is_horizontal_rule(line)
            or is_table_start(lines, index)
        ) and not line.startswith((" ", "\t")):
            break

        list_lines.append(line)
        index += 1

    list_html = markdown_to_html("\n".join(list_lines))
    return wrap_block("list", list_html), index


def convert_table_block(lines: list[str], start_index: int) -> tuple[str, int]:
    """MarkdownテーブルをGutenbergテーブルブロックへ変換します。"""
    table_lines: list[str] = []
    index = start_index

    while index < len(lines) and lines[index].strip() and "|" in lines[index]:
        table_lines.append(lines[index])
        index += 1

    table_html = markdown_to_html("\n".join(table_lines))
    block_html = f'<figure class="wp-block-table">{table_html}</figure>'
    return wrap_block("table", block_html), index


def convert_paragraph_block(lines: list[str], start_index: int) -> tuple[str, int]:
    """通常段落をGutenberg段落ブロックへ変換します。"""
    paragraph_lines: list[str] = []
    index = start_index

    while index < len(lines):
        line = lines[index]

        if not line.strip():
            break

        if (
            is_heading(line)
            or line.startswith("```")
            or line.lstrip().startswith(">")
            or is_horizontal_rule(line)
            or is_list_start(line)
            or is_table_start(lines, index)
        ):
            break

        paragraph_lines.append(line)
        index += 1

    paragraph_html = markdown_to_html("\n".join(paragraph_lines))
    return wrap_block("paragraph", paragraph_html), index


def convert_markdown_to_wordpress_blocks(markdown_text: str) -> str:
    """本文MarkdownをWordPressブロックエディター向けHTMLへ変換します。"""
    lines = markdown_text.splitlines()
    blocks: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]

        if not line.strip():
            index += 1
            continue

        if line.startswith("```"):
            block, index = convert_code_block(lines, index)
        elif is_heading(line):
            block = convert_heading(line)
            index += 1
        elif line.lstrip().startswith(">"):
            block, index = convert_quote_block(lines, index)
        elif is_horizontal_rule(line):
            block = '<!-- wp:separator -->\n<hr class="wp-block-separator has-alpha-channel-opacity"/>\n<!-- /wp:separator -->'
            index += 1
        elif is_table_start(lines, index):
            block, index = convert_table_block(lines, index)
        elif is_list_start(line):
            block, index = convert_list_block(lines, index)
        else:
            block, index = convert_paragraph_block(lines, index)

        blocks.append(block)

    return "\n\n".join(blocks)


def request_wordpress(
    method: str,
    config: WordPressConfig,
    endpoint: str,
    **kwargs: Any,
) -> requests.Response:
    """WordPress REST APIへリクエストを送信します。"""
    url = f"{config.url}/wp-json/wp/v2/{endpoint}"

    try:
        response = requests.request(
            method,
            url,
            auth=(config.user, config.app_password),
            timeout=20,
            **kwargs,
        )
    except requests.RequestException as error:
        raise WordPressDraftPublisherError(
            f"WordPress APIへの接続に失敗しました: {error}"
        ) from error

    return response


def raise_for_api_error(response: requests.Response, action: str) -> None:
    """WordPress APIのエラーレスポンスを例外に変換します。"""
    if 200 <= response.status_code < 300:
        return

    raise WordPressDraftPublisherError(
        f"{action}に失敗しました。\n"
        f"status_code: {response.status_code}\n"
        f"response: {response.text}"
    )


def find_term_id(config: WordPressConfig, endpoint: str, name: str) -> int | None:
    """カテゴリまたはタグを名前で検索し、完全一致するIDを返します。"""
    response = request_wordpress("GET", config, endpoint, params={"search": name})
    raise_for_api_error(response, f"{name} の検索")

    for term in response.json():
        if term.get("name") == name:
            return int(term["id"])

    return None


def create_term(config: WordPressConfig, endpoint: str, name: str) -> int:
    """カテゴリまたはタグを作成してIDを返します。"""
    response = request_wordpress("POST", config, endpoint, json={"name": name})
    raise_for_api_error(response, f"{name} の作成")

    return int(response.json()["id"])


def get_or_create_term_id(config: WordPressConfig, endpoint: str, name: str) -> int:
    """カテゴリまたはタグを取得し、存在しない場合は作成します。"""
    term_id = find_term_id(config, endpoint, name)

    if term_id is not None:
        return term_id

    return create_term(config, endpoint, name)


def find_existing_post_id(config: WordPressConfig, slug: str) -> int | None:
    """スラッグで下書きを含む既存投稿を検索します。"""
    response = request_wordpress(
        "GET",
        config,
        POSTS_ENDPOINT,
        params={"slug": slug, "status": "any"},
    )
    raise_for_api_error(response, f"スラッグ {slug} の投稿検索")

    for post in response.json():
        if post.get("slug") == slug:
            return int(post["id"])

    return None


def save_post(config: WordPressConfig, article: Article) -> dict[str, Any]:
    """記事をWordPressへ新規下書き投稿または更新します。"""
    category_id = get_or_create_term_id(
        config,
        CATEGORIES_ENDPOINT,
        article.category,
    )
    tag_ids = [
        get_or_create_term_id(config, TAGS_ENDPOINT, tag_name)
        for tag_name in article.tags
    ]
    content = convert_markdown_to_wordpress_blocks(article.body)

    post_data = {
        "title": article.title,
        "slug": article.slug,
        "status": "draft",
        "content": content,
        "categories": [category_id],
        "tags": tag_ids,
    }

    existing_post_id = find_existing_post_id(config, article.slug)

    if existing_post_id is None:
        response = request_wordpress("POST", config, POSTS_ENDPOINT, json=post_data)
        action = "投稿"
    else:
        endpoint = f"{POSTS_ENDPOINT}/{existing_post_id}"
        response = request_wordpress("POST", config, endpoint, json=post_data)
        action = "更新"

    raise_for_api_error(response, action)
    result = response.json()
    result["_action"] = action
    return result


def move_to_done(source_path: Path) -> Path:
    """成功したMarkdownファイルをdoneフォルダへ移動します。"""
    done_dir = BASE_DIR / "done"

    try:
        done_dir.mkdir(exist_ok=True)
        destination = done_dir / source_path.name
        if destination.exists():
            destination.unlink()
        shutil.move(str(source_path), destination)
    except OSError as error:
        raise WordPressDraftPublisherError(
            f"投稿後のファイル移動に失敗しました: {source_path} -> {done_dir}"
        ) from error

    return destination


def process_file(config: WordPressConfig, file_path: Path) -> None:
    """Markdownファイル1件を処理します。"""
    print(f"処理開始: {file_path.name}")

    article = parse_article(file_path)
    result = save_post(config, article)
    moved_path = move_to_done(file_path)

    post_id = result.get("id")
    status = result.get("status")
    action = result.get("_action", "投稿")
    edit_url = f"{config.url}/wp-admin/post.php?post={post_id}&action=edit"

    print(f"WordPressへの{action}に成功しました")
    print(f"投稿ID: {post_id}")
    print(f"ステータス: {status}")
    print(f"編集URL: {edit_url}")
    print(f"移動先: {moved_path}")


def main() -> int:
    """コマンドラインから実行するメイン処理です。"""
    args = parse_args()

    try:
        config = load_config()
        target_dir = resolve_target_dir(args.draft_dir)
        markdown_files = find_markdown_files(target_dir)
    except WordPressDraftPublisherError as error:
        print(f"エラー: {error}")
        return 1

    has_error = False

    for file_path in markdown_files:
        try:
            process_file(config, file_path)
        except WordPressDraftPublisherError as error:
            has_error = True
            print(f"エラー: {file_path.name}")
            print(error)

    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
