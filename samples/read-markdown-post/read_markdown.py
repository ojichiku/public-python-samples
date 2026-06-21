from pathlib import Path


TITLE_HEADING = "## 1. タイトル"
SLUG_HEADING = "## 2. スラッグ"
CATEGORY_HEADING = "## 3. カテゴリ"
BODY_HEADING = "## 5. 本文"


def get_section(text: str, start_heading: str, end_heading: str | None = None) -> str:
    if start_heading not in text:
        raise ValueError(f"{start_heading}が見つかりません。")

    start_index = text.index(start_heading) + len(start_heading)

    if end_heading is None:
        section_text = text[start_index:]
    else:
        if end_heading not in text:
            raise ValueError(f"{end_heading}が見つかりません。")

        end_index = text.index(end_heading)
        section_text = text[start_index:end_index]

    return section_text.strip()


def read_markdown(file_path: str) -> dict[str, str]:
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")

    title = get_section(text, TITLE_HEADING, SLUG_HEADING)
    slug = get_section(text, SLUG_HEADING, CATEGORY_HEADING)
    body = get_section(text, BODY_HEADING)

    return {
        "title": title,
        "slug": slug,
        "body": body,
    }


def main() -> None:
    article = read_markdown("sample_article.md")

    print("title:")
    print(article["title"])
    print()
    print("slug:")
    print(article["slug"])
    print()
    print("body:")
    print(article["body"])


if __name__ == "__main__":
    main()
