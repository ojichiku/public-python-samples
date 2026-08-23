"""補助金公募一覧のHTML解析テスト。"""

import pytest

from subsidy_scraper import (
    HtmlStructureError,
    SubsidyRecord,
    TargetYearNotFoundError,
    format_published_date,
    parse_subsidies,
    split_name_and_period,
)

BASE_URL = "https://www.chusho.meti.go.jp/koukai/hojyokin/kobo.html"


def test_parse_subsidies_extracts_only_2026_records() -> None:
    html = """
    <h2>2027年度</h2>
    <dl class="p-top__news__list">
      <dt>2027年1月1日</dt>
      <dd><a href="future.html">対象外【申請受付期間：1/1～1/2】</a></dd>
    </dl>
    <h2> 2026年度 </h2>
    <dl class="p-top__news__list">
      <dt>2026年8月20日</dt>
      <dd><a href="/detail/first.html">
        第一補助金を 公開しました
        【申請受付期間：9/29～10/29】
      </a></dd>
      <dt>2026年7月8日</dt>
      <dd><a href="detail/second.html">
        第二補助金【申請受付：7月上旬～7月下旬予定】
      </a></dd>
      <dt>2026年6月5日</dt>
      <dd><a href="https://example.com/third.html">
        第三補助金【公募期間： 随時受付中 】
      </a></dd>
      <dt>2026年4月1日</dt>
      <dd><a href="detail/no-period.html">期間表記のない補助金</a></dd>
      <dt>2026年8月20日</dt>
      <dd><a href="/detail/first.html">
        第一補助金を 公開しました【申請受付期間：別の期間】
      </a></dd>
    </dl>
    <h2>2025年度</h2>
    <dl class="p-top__news__list">
      <dt>2025年12月1日</dt>
      <dd><a href="old.html">対象外【公募期間：12/1～12/2】</a></dd>
    </dl>
    """

    records = parse_subsidies(html, BASE_URL)

    assert records == [
        SubsidyRecord(
            published_date="2026/08/20",
            subsidy_name="第一補助金を 公開しました",
            application_period="9/29～10/29",
            detail_url="https://www.chusho.meti.go.jp/detail/first.html",
        ),
        SubsidyRecord(
            published_date="2026/07/08",
            subsidy_name="第二補助金",
            application_period="7月上旬～7月下旬予定",
            detail_url=(
                "https://www.chusho.meti.go.jp/koukai/hojyokin/detail/second.html"
            ),
        ),
        SubsidyRecord(
            published_date="2026/06/05",
            subsidy_name="第三補助金",
            application_period="随時受付中",
            detail_url="https://example.com/third.html",
        ),
        SubsidyRecord(
            published_date="2026/04/01",
            subsidy_name="期間表記のない補助金",
            application_period="",
            detail_url=(
                "https://www.chusho.meti.go.jp/koukai/hojyokin/detail/no-period.html"
            ),
        ),
    ]


def test_parse_subsidies_returns_empty_list_for_empty_year_list() -> None:
    html = """
    <h2>2026年度</h2>
    <dl class="p-top__news__list"></dl>
    <h2>2025年度</h2>
    """

    assert parse_subsidies(html) == []


def test_parse_subsidies_rejects_missing_target_year() -> None:
    with pytest.raises(TargetYearNotFoundError, match="2026年度"):
        parse_subsidies("<h2>2025年度</h2>")


def test_parse_subsidies_stops_at_next_year_heading() -> None:
    html = """
    <h2>2026年度</h2>
    <p>一覧がありません。</p>
    <h2>2025年度</h2>
    <dl class="p-top__news__list"></dl>
    """

    with pytest.raises(HtmlStructureError, match="公募一覧がありません"):
        parse_subsidies(html)


def test_parse_subsidies_rejects_missing_list_at_end_of_document() -> None:
    html = """
    <h2>2026年度</h2>
    <p>一覧がありません。</p>
    """

    with pytest.raises(HtmlStructureError, match="公募一覧がありません"):
        parse_subsidies(html)


def test_parse_subsidies_rejects_odd_definition_entries() -> None:
    html = """
    <h2>2026年度</h2>
    <dl class="p-top__news__list"><dt>2026年1月1日</dt></dl>
    """

    with pytest.raises(HtmlStructureError, match="組が一致しません"):
        parse_subsidies(html)


def test_parse_subsidies_rejects_reversed_definition_entries() -> None:
    html = """
    <h2>2026年度</h2>
    <dl class="p-top__news__list">
      <dd><a href="detail.html">補助金</a></dd>
      <dt>2026年1月1日</dt>
    </dl>
    """

    with pytest.raises(HtmlStructureError, match="並びが想定と異なります"):
        parse_subsidies(html)


def test_parse_subsidies_rejects_missing_detail_link() -> None:
    html = """
    <h2>2026年度</h2>
    <dl class="p-top__news__list">
      <dt>2026年1月1日</dt>
      <dd>リンクのない補助金</dd>
    </dl>
    """

    with pytest.raises(HtmlStructureError, match="詳細リンクがありません"):
        parse_subsidies(html)


def test_format_published_date_rejects_unexpected_format() -> None:
    with pytest.raises(HtmlStructureError, match="形式を解析できません"):
        format_published_date("2026/08/20")


def test_format_published_date_rejects_invalid_date() -> None:
    with pytest.raises(HtmlStructureError, match="正しい日付ではありません"):
        format_published_date("2026年2月30日")


def test_split_name_and_period_removes_period_from_middle() -> None:
    name, period = split_name_and_period("補助金【申請受付期間：4/1～4/30】 のお知らせ")

    assert name == "補助金 のお知らせ"
    assert period == "4/1～4/30"
