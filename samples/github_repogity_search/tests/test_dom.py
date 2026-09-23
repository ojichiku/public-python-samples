"""--run-edgeで実Edgeを使う。外部通信なしのDOM回帰テスト。"""

import pytest

from github_repository_search.main import EMPTY_MESSAGE, HEADERS, SearchError, collect_results

pytestmark = pytest.mark.edge


def card(index=0, details=True):
    # 実画面で確認したDOMの必要部分のみを再現する。
    extra = '''<div class="Content-module__Content__test"><span class="search-match">日本語の説明</span></div>
        <span aria-label="Python language">Python</span>
        <a href="/owner/repo/stargazers" aria-label="15015 stars">15k</a>''' if details else ""
    return f'<div><h3 class="search-title"><a href="/owner/repo{index}">owner/repo{index}</a></h3>{extra}</div>'


def test_fields_and_exact_stars(edge_page):
    edge_page.set_content(f'<div data-testid="results-list">{card()}</div>')
    assert list(collect_results(edge_page)[0].values()) == [
        "owner/repo0", "日本語の説明", "https://github.com/owner/repo0", "Python", "15015",
    ]


def test_limit_order_and_missing_fields(edge_page):
    edge_page.set_content('<div data-testid="results-list">' + ''.join(card(i, False) for i in range(12)) + '</div>')
    rows = collect_results(edge_page)
    assert len(rows) == 10
    assert rows[-1][HEADERS[0]] == "owner/repo9"
    assert [rows[0][HEADERS[i]] for i in (1, 3, 4)] == ["", "", ""]


def test_explicit_empty(edge_page):
    edge_page.set_content(f'<p>{EMPTY_MESSAGE}</p>')
    assert collect_results(edge_page) == []


def test_unknown_page_is_not_empty_result(edge_page):
    edge_page.set_content('<h1>Access restricted</h1>')
    with pytest.raises(SearchError, match="検索結果を取得できません"):
        collect_results(edge_page)


def test_broken_card_is_error(edge_page):
    edge_page.set_content('<div data-testid="results-list"><div>Unknown card</div></div>')
    with pytest.raises(SearchError, match="リポジトリ名を取得できません"):
        collect_results(edge_page)
