import pytest
import importlib
from playwright.sync_api import sync_playwright


@pytest.fixture(autouse=True)
def skip_operation_delays(monkeypatch):
    # 画面表示の待機は実行し、操作を見せるための待機だけ省く。
    app = importlib.import_module("github_repository_search.main")
    monkeypatch.setattr(app.time, "sleep", lambda seconds: None)


def pytest_addoption(parser):
    parser.addoption("--run-edge", action="store_true", help="インストール済みEdgeでDOMテストも実行")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-edge"):
        for item in items:
            if "edge" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="--run-edgeで有効化"))


@pytest.fixture(scope="session")
def edge_browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=False)
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture
def edge_page(edge_browser):
    page = edge_browser.new_page()
    page.set_default_timeout(1000)
    try:
        yield page
    finally:
        page.close()
