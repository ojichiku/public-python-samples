"""補助金公募一覧のHTML解析処理。"""

import re
from dataclasses import dataclass
from datetime import date
from typing import cast
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

TARGET_YEAR = 2026
TARGET_YEAR_LABEL = f"{TARGET_YEAR}年度"
TARGET_URL = "https://www.chusho.meti.go.jp/koukai/hojyokin/kobo.html"

_HEADING_NAMES = ("h1", "h2", "h3", "h4", "h5", "h6")
_YEAR_HEADING_PATTERN = re.compile(r"\d{4}年度")
_PUBLISHED_DATE_PATTERN = re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
_APPLICATION_PERIOD_PATTERN = re.compile(
    r"【\s*(?:申請受付期間|申請受付|公募期間)\s*：\s*(.*?)\s*】"
)


class HtmlStructureError(ValueError):
    """HTMLが想定した公募一覧の構造ではない場合のエラー。"""


class TargetYearNotFoundError(HtmlStructureError):
    """対象年度の見出しが見つからない場合のエラー。"""


@dataclass(frozen=True, slots=True)
class SubsidyRecord:
    """CSVへ出力する1件分の補助金公募情報。"""

    published_date: str
    subsidy_name: str
    application_period: str
    detail_url: str


def normalize_text(value: str) -> str:
    """前後の空白を除き、改行と連続空白を1個の空白へまとめる。"""

    return " ".join(value.split())


def format_published_date(value: str) -> str:
    """和文の公開日をゼロ埋めした ``YYYY/MM/DD`` 形式へ変換する。

    Args:
        value: Webページから取得した公開日の文字列。

    Returns:
        ``YYYY/MM/DD`` 形式の公開日。

    Raises:
        HtmlStructureError: 形式が異なるか、実在しない日付の場合。
    """

    normalized = normalize_text(value)
    match = _PUBLISHED_DATE_PATTERN.fullmatch(normalized)
    if match is None:
        raise HtmlStructureError(f"公開日の形式を解析できません: {normalized}")

    year, month, day = (int(part) for part in match.groups())
    try:
        published_date = date(year, month, day)
    except ValueError as exc:
        raise HtmlStructureError(
            f"公開日が正しい日付ではありません: {normalized}"
        ) from exc

    return published_date.strftime("%Y/%m/%d")


def split_name_and_period(value: str) -> tuple[str, str]:
    """公募情報の本文から補助金名と申請受付期間を分離する。

    Args:
        value: リンク内に掲載されている本文。

    Returns:
        補助金名と申請受付期間の組。期間がなければ空文字を返す。
    """

    normalized = normalize_text(value)
    match = _APPLICATION_PERIOD_PATTERN.search(normalized)
    if match is None:
        return normalized, ""

    subsidy_name = normalize_text(
        f"{normalized[: match.start()]} {normalized[match.end() :]}"
    )
    application_period = normalize_text(match.group(1))
    return subsidy_name, application_period


def parse_subsidies(
    html: str,
    base_url: str = TARGET_URL,
) -> list[SubsidyRecord]:
    """一覧HTMLから2026年度の補助金公募情報を抽出する。

    Args:
        html: 対象ページのHTML。
        base_url: 相対リンクを解決する基準URL。

    Returns:
        掲載順を維持し、重複を除いた公募情報。

    Raises:
        TargetYearNotFoundError: 2026年度の見出しがない場合。
        HtmlStructureError: 対象範囲のHTML構造を解析できない場合。
    """

    soup = BeautifulSoup(html, "html.parser")
    year_list = _find_target_year_list(soup)
    entries = year_list.find_all(["dt", "dd"], recursive=False)

    if len(entries) % 2 != 0:
        raise HtmlStructureError("公開日と公募情報の組が一致しません。")

    records: list[SubsidyRecord] = []
    seen: set[tuple[str, str, str]] = set()

    for published_date_tag, detail_tag in zip(entries[::2], entries[1::2], strict=True):
        record = _parse_record(published_date_tag, detail_tag, base_url)
        duplicate_key = (
            record.published_date,
            record.subsidy_name,
            record.detail_url,
        )
        if duplicate_key in seen:
            continue
        seen.add(duplicate_key)
        records.append(record)

    return records


def _find_target_year_list(soup: BeautifulSoup) -> Tag:
    """対象年度見出しから次年度見出しまでにある一覧を返す。"""

    target_heading = next(
        (
            heading
            for heading in soup.find_all(_HEADING_NAMES)
            if normalize_text(heading.get_text(" ", strip=True)) == TARGET_YEAR_LABEL
        ),
        None,
    )
    if target_heading is None:
        raise TargetYearNotFoundError(f"{TARGET_YEAR_LABEL}の見出しがありません。")

    for sibling in target_heading.next_siblings:
        if not isinstance(sibling, Tag):
            continue

        sibling_text = normalize_text(sibling.get_text(" ", strip=True))
        if sibling.name in _HEADING_NAMES and _YEAR_HEADING_PATTERN.fullmatch(
            sibling_text
        ):
            break

        classes = sibling.get("class", ())
        if sibling.name == "dl" and "p-top__news__list" in classes:
            return sibling

    raise HtmlStructureError(f"{TARGET_YEAR_LABEL}の公募一覧がありません。")


def _parse_record(
    published_date_tag: Tag,
    detail_tag: Tag,
    base_url: str,
) -> SubsidyRecord:
    """対応する ``dt`` と ``dd`` から1件の公募情報を作る。"""

    if published_date_tag.name != "dt" or detail_tag.name != "dd":
        raise HtmlStructureError("公開日と公募情報の並びが想定と異なります。")

    link = detail_tag.find("a", href=True)
    if not isinstance(link, Tag):
        raise HtmlStructureError("公募情報の詳細リンクがありません。")

    # BeautifulSoupではhrefは文字列として解析され、href=Trueで存在も確認済みです。
    href = cast(str, link["href"])

    published_date = format_published_date(published_date_tag.get_text(" ", strip=True))
    subsidy_name, application_period = split_name_and_period(
        link.get_text(" ", strip=True)
    )

    return SubsidyRecord(
        published_date=published_date,
        subsidy_name=subsidy_name,
        application_period=application_period,
        detail_url=urljoin(base_url, href),
    )
