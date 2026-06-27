"""Markdownファイルを読み込み、WordPressへ下書き投稿するサンプルです。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


POSTS_ENDPOINT = "posts"
CATEGORIES_ENDPOINT = "categories"
TAGS_ENDPOINT = "tags"


class WordPressPostToolError(Exception):
    """WordPress投稿ツール用の例外です。"""


def get_required_env(name: str) -> str:
    """必須の環境変数を取得します。

    Args:
        name: 取得する環境変数名。

    Returns:
        環境変数の値。WP_URLの場合は末尾のスラッシュを取り除いた値。

    Raises:
        WordPressPostToolError: 指定した環境変数が未設定の場合。
    """
    value = os.getenv(name)

    if not value:
        raise WordPressPostToolError(
            f"{name} が設定されていません。.envを確認してください。"
        )

    return value.rstrip("/") if name == "WP_URL" else value


def get_section(text: str, start_marker: str, end_marker: str | None = None) -> str:
    """Markdown本文から指定した見出し範囲のテキストを取り出します。

    Args:
        text: Markdownファイル全体の文字列。
        start_marker: 抽出開始位置になる見出し文字列。
        end_marker: 抽出終了位置になる見出し文字列。Noneの場合は末尾まで抽出します。

    Returns:
        見出し間の文字列。開始見出しが見つからない場合は空文字列。
    """
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


def read_markdown_file(file_path: str | Path) -> dict[str, str]:
    """投稿用Markdownファイルを読み込み、投稿データの辞書に変換します。

    Args:
        file_path: 読み込むMarkdownファイルのパス。

    Returns:
        title、slug、category、tags、bodyを持つ投稿データ。

    Raises:
        WordPressPostToolError: 必須項目が不足している場合。
    """
    text = Path(file_path).read_text(encoding="utf-8")

    article = {
        "title": get_section(text, "## 1. タイトル", "## 2. スラッグ"),
        "slug": get_section(text, "## 2. スラッグ", "## 3. カテゴリ"),
        "category": get_section(text, "## 3. カテゴリ", "## 4. タグ"),
        "tags": get_section(text, "## 4. タグ", "## 5. 本文"),
        "body": get_section(text, "## 5. 本文"),
    }

    validate_article(article)
    return article


def validate_article(article: dict[str, str]) -> None:
    """投稿データに必須項目がそろっているか確認します。

    Args:
        article: Markdownから読み取った投稿データ。

    Raises:
        WordPressPostToolError: タイトル、スラッグ、カテゴリ、タグ、本文のいずれかが空の場合。
    """
    required_fields = {
        "title": "タイトル",
        "slug": "スラッグ",
        "category": "カテゴリ",
        "tags": "タグ",
        "body": "本文",
    }

    missing_fields = [
        label for key, label in required_fields.items() if not article.get(key)
    ]

    if missing_fields:
        joined = "、".join(missing_fields)
        raise WordPressPostToolError(
            f"Markdownファイルの項目が不足しています: {joined}"
        )


def request_wordpress(
    method: str,
    wp_url: str,
    wp_user: str,
    wp_app_password: str,
    endpoint: str,
    **kwargs: Any,
) -> requests.Response:
    """WordPress REST APIへHTTPリクエストを送信します。

    Args:
        method: HTTPメソッド。GETやPOSTなどを指定します。
        wp_url: WordPressサイトのURL。
        wp_user: WordPressのユーザー名。
        wp_app_password: WordPressのアプリケーションパスワード。
        endpoint: WordPress REST APIのエンドポイント名。
        **kwargs: requests.requestへ渡す追加オプション。

    Returns:
        WordPress REST APIから返されたレスポンス。
    """
    url = f"{wp_url}/wp-json/wp/v2/{endpoint}"

    response = requests.request(
        method,
        url,
        auth=(wp_user, wp_app_password),
        timeout=20,
        **kwargs,
    )

    return response


def find_term_id(
    wp_url: str,
    wp_user: str,
    wp_app_password: str,
    endpoint: str,
    name: str,
) -> int | None:
    """カテゴリまたはタグを名前で検索し、見つかったIDを返します。

    Args:
        wp_url: WordPressサイトのURL。
        wp_user: WordPressのユーザー名。
        wp_app_password: WordPressのアプリケーションパスワード。
        endpoint: 検索対象のエンドポイント名。categoriesまたはtagsを指定します。
        name: 検索するカテゴリ名またはタグ名。

    Returns:
        一致するカテゴリまたはタグのID。見つからない場合はNone。

    Raises:
        WordPressPostToolError: 検索リクエストに失敗した場合。
    """
    response = request_wordpress(
        "GET",
        wp_url,
        wp_user,
        wp_app_password,
        endpoint,
        params={"search": name},
    )

    if response.status_code != 200:
        raise WordPressPostToolError(
            f"{name} の検索に失敗しました。\n"
            f"status_code: {response.status_code}\n"
            f"response: {response.text}"
        )

    terms = response.json()

    for term in terms:
        if term.get("name") == name:
            return int(term["id"])

    return None


def create_term(
    wp_url: str,
    wp_user: str,
    wp_app_password: str,
    endpoint: str,
    name: str,
) -> int:
    """カテゴリまたはタグを新規作成し、作成されたIDを返します。

    Args:
        wp_url: WordPressサイトのURL。
        wp_user: WordPressのユーザー名。
        wp_app_password: WordPressのアプリケーションパスワード。
        endpoint: 作成対象のエンドポイント名。categoriesまたはtagsを指定します。
        name: 作成するカテゴリ名またはタグ名。

    Returns:
        作成されたカテゴリまたはタグのID。

    Raises:
        WordPressPostToolError: 作成リクエストに失敗した場合。
    """
    response = request_wordpress(
        "POST",
        wp_url,
        wp_user,
        wp_app_password,
        endpoint,
        json={"name": name},
    )

    if response.status_code not in (200, 201):
        raise WordPressPostToolError(
            f"{name} の作成に失敗しました。\n"
            f"status_code: {response.status_code}\n"
            f"response: {response.text}"
        )

    return int(response.json()["id"])


def get_or_create_term_id(
    wp_url: str,
    wp_user: str,
    wp_app_password: str,
    endpoint: str,
    name: str,
) -> int:
    """カテゴリまたはタグを取得し、存在しない場合は作成してIDを返します。

    Args:
        wp_url: WordPressサイトのURL。
        wp_user: WordPressのユーザー名。
        wp_app_password: WordPressのアプリケーションパスワード。
        endpoint: 対象のエンドポイント名。categoriesまたはtagsを指定します。
        name: 取得または作成するカテゴリ名またはタグ名。

    Returns:
        取得または作成したカテゴリまたはタグのID。
    """
    term_id = find_term_id(wp_url, wp_user, wp_app_password, endpoint, name)

    if term_id is not None:
        return term_id

    return create_term(wp_url, wp_user, wp_app_password, endpoint, name)


def get_tag_ids(
    wp_url: str,
    wp_user: str,
    wp_app_password: str,
    tags_text: str,
) -> list[int]:
    """カンマ区切りのタグ文字列をWordPressのタグID一覧に変換します。

    Args:
        wp_url: WordPressサイトのURL。
        wp_user: WordPressのユーザー名。
        wp_app_password: WordPressのアプリケーションパスワード。
        tags_text: カンマ区切りのタグ名。

    Returns:
        タグIDのリスト。
    """
    tag_names = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

    return [
        get_or_create_term_id(wp_url, wp_user, wp_app_password, TAGS_ENDPOINT, tag_name)
        for tag_name in tag_names
    ]


def post_to_wordpress(
    wp_url: str,
    wp_user: str,
    wp_app_password: str,
    article: dict[str, str],
) -> dict[str, Any]:
    """投稿データをWordPressへ下書きとして投稿します。

    Args:
        wp_url: WordPressサイトのURL。
        wp_user: WordPressのユーザー名。
        wp_app_password: WordPressのアプリケーションパスワード。
        article: title、slug、category、tags、bodyを持つ投稿データ。

    Returns:
        WordPress REST APIから返された投稿情報。

    Raises:
        WordPressPostToolError: 投稿リクエストに失敗した場合。
    """
    category_id = get_or_create_term_id(
        wp_url,
        wp_user,
        wp_app_password,
        CATEGORIES_ENDPOINT,
        article["category"],
    )

    tag_ids = get_tag_ids(wp_url, wp_user, wp_app_password, article["tags"])

    post_data = {
        "title": article["title"],
        "content": article["body"],
        "status": "draft",
        "slug": article["slug"],
        "categories": [category_id],
        "tags": tag_ids,
    }

    response = request_wordpress(
        "POST",
        wp_url,
        wp_user,
        wp_app_password,
        POSTS_ENDPOINT,
        json=post_data,
    )

    if response.status_code not in (200, 201):
        raise WordPressPostToolError(
            "投稿に失敗しました。\n"
            f"status_code: {response.status_code}\n"
            f"response: {response.text}"
        )

    return response.json()


def main() -> None:
    """環境変数とMarkdownファイルを読み込み、WordPressへ下書き投稿します。"""
    load_dotenv()

    wp_url = get_required_env("WP_URL")
    wp_user = get_required_env("WP_USER")
    wp_app_password = get_required_env("WP_APP_PASSWORD")

    article = read_markdown_file("sample_post.md")
    result = post_to_wordpress(wp_url, wp_user, wp_app_password, article)

    post_id = result["id"]
    status = result["status"]
    edit_url = f"{wp_url}/wp-admin/post.php?post={post_id}&action=edit"

    print("WordPressへ下書き投稿しました")
    print(f"投稿ID: {post_id}")
    print(f"ステータス: {status}")
    print(f"編集URL: {edit_url}")


if __name__ == "__main__":
    try:
        main()
    except WordPressPostToolError as error:
        print("エラーが発生しました")
        print(error)
