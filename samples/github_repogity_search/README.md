# GitHubリポジトリ検索

Python 3.14とPlaywrightの同期APIで、Windowsにインストール済みのMicrosoft Edgeを操作する学習用サンプルです。

GitHubの検索欄へ文字を入力し、リポジトリ検索の上位10件をCSVに保存します。GitHub APIやrequestsは使用しません。

## 動作環境

- Windows、インストール済みMicrosoft Edge
- Python 3.14、uv、GitHubへアクセスできるネットワーク

## セットアップと実行

このディレクトリで実行します。

```powershell
uv sync
uv run github-repository-search
```

または `uv run python -m github_repository_search` でも起動できます。
検索キーワードの入力例は `playwright python`、`language:Python topic:cli` です。

実行時はEdge起動 → 検索画面表示 → 入力欄へ入力 → Enter → 表示完了待ち → 上位10件取得 → CSV保存 → Edge終了の順に処理します。

`playwright.chromium.launch(channel="msedge", headless=False)` でPC内のEdgeを指定します。
`chromium` は操作エンジン名であり、Playwright付属Chromiumは使用しません。
ブラウザのダウンロードは不要で、`playwright install` は実行しません。
この起動方法は[Playwright公式のブラウザ説明](https://playwright.dev/python/docs/browsers#google-chrome--microsoft-edge)に基づきます。

## 操作間のランダム待機

入力欄の表示後、文字入力後、検索結果の表示後、CSV保存後の終了前に、それぞれ1〜3秒待機します。
毎回ランダムに選び、コンソールへ秒数を表示します。
変更する場合は `src/github_repository_search/main.py` の `OPERATION_DELAY_MIN` と `OPERATION_DELAY_MAX` を変更してください。
0以上で最小値≦最大値に設定します。

表示完了は別途Playwrightの待機機能で確認します。ランダム待機はアクセス制限を防ぐ保証にはなりません。
GitHubのアクセス制限時は繰り返し実行せず、時間を置いて確認してください。自動リトライは行いません。

## 保存されるCSV

実行ディレクトリの `github_repository_search.csv` にUTF-8 BOM付きで保存します。同名ファイルは上書きします。

| 列 | 内容 |
| --- | --- |
| リポジトリ名 | 所有者/リポジトリ名 |
| 説明 | 検索結果に表示される説明（省略されている場合はそのまま） |
| リポジトリURL | GitHubのリポジトリURL |
| 使用言語 | 表示されている言語 |
| Star数 | aria-labelの数値を優先。なければ画面の省略表記 |

任意項目がない場合は空文字です。10件未満なら表示された件数だけ保存し、0件ならヘッダーだけ保存します。

## エラー時

Edge未導入・起動制限、接続失敗、入力欄の変更、検索結果の取得失敗、CSV書き込み失敗は日本語で表示します。
ExcelでCSVを開いている場合は閉じてから再実行してください。正常終了は終了コード0、エラーは1、中断は130です。
取得・保存が失敗した場合も、このプログラムで起動したEdgeを閉じます。

GitHubの画面は変更されることがあります。検索欄、結果カード、説明、言語、Star数のセレクタは2026-09-23に実画面で確認しました。
画面変更時は `search_repositories`、`RESULT_CARD`、`DESCRIPTION`、`EMPTY_MESSAGE`、`read_repository` を確認してください。

## 構成

```text
.
├── AGENTS.md                 # 開発方針
├── PLANS.md                  # 段階的な実装計画・検証記録
├── REQUEST.md                # 元の要件
├── README.md
├── .python-version           # 3.14
├── .gitignore
├── pyproject.toml            # uv用依存関係・CLI定義
├── uv.lock                   # 依存バージョンの固定
├── requirements.txt          # pip用の最小依存一覧（通常は不要）
├── src/github_repository_search/
│   ├── __init__.py
│   ├── __main__.py
│   └── main.py               # 検索・CSV出力
└── tests/
    ├── conftest.py
    ├── test_main.py
    └── test_dom.py
```

REQUEST.mdのフラットな構成例より、追加指定のsrcレイアウト・uv・Python 3.14を優先しています。

## テスト

pytestは開発用依存関係に含まれ、`uv sync` でインストールされます。

```powershell
uv run pytest -q
uv run pytest --run-edge -q
```

通常はブラウザなしのテストを実行し、Edgeの5テストをスキップします。
`--run-edge` はPC内のEdgeを画面表示付きで起動し、外部通信なしのHTMLで欠損項目・上限10件・0件・構造変更を検証します。
テスト中は操作間のランダム待機だけを省きます。
実GitHubの確認はCLIから手動実行してください。
