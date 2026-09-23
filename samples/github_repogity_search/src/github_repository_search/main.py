"""検索欄を操作してGitHubの上位10件をCSVへ保存する。"""

import csv
from pathlib import Path
import random
import re
import sys
import time
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page, sync_playwright

SEARCH_URL = "https://github.com/search?type=repositories"
OUTPUT_PATH = Path("github_repository_search.csv")
HEADERS = ["リポジトリ名", "説明", "リポジトリURL", "使用言語", "Star数"]
TIMEOUT_MS = 30_000
LIMIT = 10
OPERATION_DELAY_MIN = 1.0
OPERATION_DELAY_MAX = 3.0

# 2026-09-23の実画面で確認。生成されたCSSクラスのハッシュには依存しない。
RESULT_CARD = '[data-testid="results-list"] > div'
DESCRIPTION = '[class*="Content-module__Content__"] .search-match'
EMPTY_MESSAGE = "Your search did not match any repositories"


class SearchError(Exception):
    """利用者へ日本語で表示するエラー。"""


def pause_between_operations() -> None:
    """画面操作を確認しやすいよう、操作間にランダムな間隔を入れる。"""
    seconds = random.uniform(OPERATION_DELAY_MIN, OPERATION_DELAY_MAX)
    print(f"次の操作まで {seconds:.1f} 秒待機します。", flush=True)
    time.sleep(seconds)


def optional_text(locator: Locator) -> str:
    """検索結果に存在しない任意項目は空文字にする。"""
    return locator.first.inner_text().strip() if locator.count() else ""


def read_repository(card: Locator) -> dict[str, str]:
    link = card.locator(".search-title a")
    if link.count() != 1:
        raise SearchError("リポジトリ名を取得できません。GitHubの画面構造が変わった可能性があります。")
    name = link.inner_text().strip()
    href = link.get_attribute("href") or ""
    if not name or not re.fullmatch(r"/[^/\s]+/[^/\s?#]+", href):
        raise SearchError("検索結果のリポジトリ名またはURLを確認できません。")

    stars_link = card.locator('a[href$="/stargazers"]')
    stars = optional_text(stars_link)
    if stars_link.count():
        label = stars_link.first.get_attribute("aria-label") or ""
        match = re.fullmatch(r"([\d,]+) stars?", label)
        if match:
            stars = match[1].replace(",", "")
    return dict(zip(HEADERS, [
        name,
        optional_text(card.locator(DESCRIPTION)),
        "https://github.com" + href,
        optional_text(card.locator('[aria-label$=" language"]')),
        stars,
    ], strict=True))


def collect_results(page: Page) -> list[dict[str, str]]:
    """結果カードか明示的な0件表示まで待ち、表示順に取得する。"""
    cards = page.locator(RESULT_CARD)
    empty = page.get_by_text(EMPTY_MESSAGE, exact=True)
    try:
        cards.first.or_(empty).first.wait_for(state="visible")
    except PlaywrightError as exc:
        raise SearchError(
            "検索結果を取得できません。通信状態、GitHubのアクセス制限、"
            "ログイン要求、画面構造の変更を確認してください。"
        ) from exc
    if empty.is_visible():
        pause_between_operations()
        return []
    pause_between_operations()
    return [read_repository(cards.nth(i)) for i in range(min(cards.count(), LIMIT))]


def search_repositories(page: Page, keyword: str) -> list[dict[str, str]]:
    try:
        # 検索語はURLへ付けず、GitHubの入力欄を操作する。
        response = page.goto(SEARCH_URL, wait_until="domcontentloaded")
    except PlaywrightError as exc:
        raise SearchError("GitHubにアクセスできません。ネットワークやプロキシ設定を確認してください。") from exc
    if response is not None and response.status >= 400:
        raise SearchError(f"GitHubへのアクセスに失敗しました（HTTP {response.status}）。時間を置いて確認してください。")

    try:
        search_input = page.get_by_role("textbox", name="Search GitHub", exact=True)
        search_input.wait_for(state="visible")
        pause_between_operations()
        search_input.fill(keyword)
    except PlaywrightError as exc:
        raise SearchError("検索入力欄が見つからないか入力できません。GitHubの画面変更やアクセス制限を確認してください。") from exc
    try:
        pause_between_operations()
        search_input.press("Enter")
        # URLは移動先の確認だけに使用する。検索種別と検索語を検証する。
        page.wait_for_url(
            lambda url: (
                urlsplit(url).path == "/search"
                and parse_qs(urlsplit(url).query).get("q") == [keyword]
                and parse_qs(urlsplit(url).query).get("type") == ["repositories"]
            ),
            wait_until="domcontentloaded",
        )
    except PlaywrightError as exc:
        raise SearchError("検索の実行を確認できません。通信状態やGitHubの画面を確認してください。") from exc
    return collect_results(page)


def save_csv(rows: list[dict[str, str]], path: Path) -> None:
    try:
        # Excelで日本語を開けるようBOM付きUTF-8で保存する。
        with path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        raise SearchError(
            f"CSVを保存できません: {path.resolve()}。Excelで開いていないか、"
            "保存先の権限や空き容量を確認してください。"
        ) from exc


def run(keyword: str, output_path: Path = OUTPUT_PATH) -> int:
    with sync_playwright() as playwright:
        try:
            # chromiumは操作エンジン名。実際に起動するのはPC内のEdge。
            browser = playwright.chromium.launch(channel="msedge", headless=False)
        except PlaywrightError as exc:
            raise SearchError(
                "Microsoft Edgeを起動できません。Edgeがインストール済みか、"
                "組織のポリシーで起動が制限されていないか確認してください。"
            ) from exc
        try:
            print("Microsoft Edgeを起動しました。")
            page = browser.new_page(locale="en-US")
            page.set_default_timeout(TIMEOUT_MS)
            print(f"GitHubで「{keyword}」を検索します。")
            rows = search_repositories(page, keyword)
            save_csv(rows, output_path)
            if not rows:
                print("検索結果は0件でした。ヘッダーのみのCSVを保存します。")
            print(f"{len(rows)}件取得しました。")
            print(f"{output_path.resolve()} に保存しました。")
            pause_between_operations()
            return len(rows)
        finally:
            # 取得・保存に失敗した場合も、このプログラムのEdgeを終了する。
            browser.close()


def main() -> int:
    try:
        keyword = input("検索キーワードを入力してください: ").strip()
        if not keyword:
            print("検索キーワードが空です。文字を入力して再実行してください。", file=sys.stderr)
            return 1
        run(keyword)
        return 0
    except (EOFError, KeyboardInterrupt):
        print("\n入力または処理を中止しました。", file=sys.stderr)
        return 130
    except SearchError as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1
    except PlaywrightError:
        print("エラー: ブラウザ操作に失敗しました。Edgeの終了や通信状態を確認してください。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
