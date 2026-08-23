"""補助金公募一覧の取得、解析、CSV保存テスト。"""

import csv
import io
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from subsidy_scraper import (
    HTTP_TIMEOUT_SECONDS,
    HTTP_WAIT_SECONDS,
    USER_AGENT,
    CsvSaveError,
    HtmlStructureError,
    NoSubsidiesError,
    SubsidyRecord,
    TargetYearNotFoundError,
    WebFetchError,
    fetch_html,
    format_published_date,
    parse_subsidies,
    save_subsidies_csv,
    split_name_and_period,
)

BASE_URL = "https://www.chusho.meti.go.jp/koukai/hojyokin/kobo.html"


def test_fetch_html_waits_before_one_request_with_fixed_conditions() -> None:
    events: list[str] = []
    response = Mock(spec=requests.Response)
    response.text = "<html>取得結果</html>"

    def fake_sleep(seconds: float) -> None:
        assert seconds == HTTP_WAIT_SECONDS
        events.append("sleep")

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
    ) -> requests.Response:
        assert url == BASE_URL
        assert headers == {"User-Agent": USER_AGENT}
        assert timeout == HTTP_TIMEOUT_SECONDS
        events.append("get")
        return response

    html = fetch_html(BASE_URL, sleep=fake_sleep, get=fake_get)

    assert html == "<html>取得結果</html>"
    assert events == ["sleep", "get"]
    response.raise_for_status.assert_called_once_with()


@pytest.mark.parametrize(
    "error",
    [
        requests.HTTPError("403 Client Error"),
        requests.HTTPError("429 Client Error"),
        requests.HTTPError("500 Server Error"),
        requests.Timeout("30秒でタイムアウト"),
        requests.ConnectionError("DNSまたは接続エラー"),
    ],
    ids=["403", "429", "500", "timeout", "connection"],
)
def test_fetch_html_converts_request_errors(error: requests.RequestException) -> None:
    events: list[str] = []

    def fake_sleep(seconds: float) -> None:
        events.append(f"sleep:{seconds}")

    def failing_get(*args: object, **kwargs: object) -> requests.Response:
        events.append("get")
        raise error

    with pytest.raises(WebFetchError, match="Webページを取得できませんでした"):
        fetch_html(sleep=fake_sleep, get=failing_get)

    assert events == [f"sleep:{HTTP_WAIT_SECONDS}", "get"]


def test_fetch_html_converts_raise_for_status_error() -> None:
    response = Mock(spec=requests.Response)
    response.raise_for_status.side_effect = requests.HTTPError("503 Server Error")

    with pytest.raises(WebFetchError, match="503 Server Error"):
        fetch_html(sleep=lambda _: None, get=lambda *args, **kwargs: response)


def test_save_subsidies_csv_writes_bom_header_and_records(tmp_path: Path) -> None:
    output_path = tmp_path / "result.csv"
    records = [
        SubsidyRecord(
            published_date="2026/08/20",
            subsidy_name="第一補助金, 特別枠",
            application_period="9/29～10/29",
            detail_url="https://example.com/first.html",
        ),
        SubsidyRecord(
            published_date="2026/07/08",
            subsidy_name="第二補助金",
            application_period="",
            detail_url="https://example.com/second.html",
        ),
    ]

    saved_path = save_subsidies_csv(records, output_path)

    content = output_path.read_bytes()
    assert saved_path == output_path
    assert content.startswith(b"\xef\xbb\xbf")
    assert list(csv.reader(io.StringIO(content.decode("utf-8-sig")))) == [
        ["公開日", "補助金名", "申請受付期間", "詳細URL"],
        [
            "2026/08/20",
            "第一補助金, 特別枠",
            "9/29～10/29",
            "https://example.com/first.html",
        ],
        ["2026/07/08", "第二補助金", "", "https://example.com/second.html"],
    ]


def test_save_subsidies_csv_rejects_empty_records_without_file(tmp_path: Path) -> None:
    output_path = tmp_path / "result.csv"

    with pytest.raises(NoSubsidiesError, match="公募情報を取得できませんでした"):
        save_subsidies_csv([], output_path)

    assert not output_path.exists()


def test_save_subsidies_csv_converts_direct_write_error(tmp_path: Path) -> None:
    output_path = tmp_path / "missing" / "result.csv"
    record = SubsidyRecord("2026/08/20", "補助金", "随時", "https://example.com")

    with pytest.raises(CsvSaveError, match="CSVを保存できませんでした"):
        save_subsidies_csv([record], output_path)

    assert not output_path.exists()


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
