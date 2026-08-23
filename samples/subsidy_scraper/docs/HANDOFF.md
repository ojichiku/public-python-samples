# Phase 3 引継ぎ

## 現在の目標とフェーズ

- Phase 1「実サイトのHTML構造調査」: 完了
- Phase 2「最小プロジェクトとHTML解析」: 完了
- Phase 3「Web取得とCSV保存」: 完了
- Phase 4「CLI統合とREADME」: 設計レビュー中、実装未着手
- 状態: `docs/design.md` のユーザーレビュー待ち

## 完了した作業

- Python 3.14系に限定した `pyproject.toml` を作成した。
- 実行時依存を `requests` と `beautifulsoup4` に限定した。
- `src/subsidy_scraper/app.py` にHTML解析を実装した。
- 2026年度見出しから次年度見出しまでを対象範囲として判定する。
- `<dt>` と `<dd><a>` の組から公開日、補助金名、申請受付期間、詳細URLを取得する。
- 公開日を `YYYY年M月D日` から `YYYY/MM/DD` へ変換する。
- `申請受付期間：`、`申請受付：`、`公募期間：` の3表記を補助金名から分離する。
- 期間がない場合は空文字とする。
- 相対URLを絶対URLへ変換する。
- 公開日、補助金名、詳細URLが同じレコードを重複除外する。
- 対象年度なし、一覧なし、`dt` / `dd` 不整合、詳細リンクなし、不正な公開日を構造エラーとして扱う。
- 最小HTMLを使った11件のテストを作成した。
- `docs/requirements.md`、`AGENTS.md`、`PLANS.md` にPython 3.14の確定事項とPhase 2の結果を反映した。
- HTTPアクセス直前に3秒待機し、一覧ページを1回だけ取得する `fetch_html()` を実装した。
- 固定Chrome相当User-Agentと30秒タイムアウトを設定した。
- HTTPエラー、403、429、500系、タイムアウト、DNS／接続エラーを、日本語メッセージを持つ `WebFetchError` に統一した。
- 4列のヘッダーとレコードをUTF-8 BOM付きで保存する `save_subsidies_csv()` を実装した。
- CSVはユーザー確認に基づき、出力先へ直接書き込む方式にした。
- 0件時は `NoSubsidiesError` とし、CSVを作成しないようにした。
- 取得条件、HTTP異常系、BOM、CSV内容、0件、保存失敗を含むテストを追加した。
- Phase 4を対象とする `docs/design.md` を作成し、未確定の設計判断をD-01〜D-07として整理した。

## 次の1手

`docs/design.md` のD-01〜D-07についてユーザーレビューを受ける。承認内容を設計書へ反映し、状態を「承認済み」に更新する。設計承認後も、Phase 4の開始指示を受けるまでは実装しない。

Phase 4では、`fetch_html()`、`parse_subsidies()`、`save_subsidies_csv()` をルートの `main.py` で統合し、仕様どおりの日本語表示と終了処理を追加する。対象年度なし、HTML構造エラー、0件、取得失敗、CSV保存失敗のCLIテストも追加する。

## 確定した判断

- Pythonは3.14系を使用する。
- Ruffの解析対象Pythonは、`project.requires-python` の3.14系指定から自動判定する。
- 本実装では、切り分けでHTTP 200を確認した固定Chrome相当User-Agentを使用する。
- HTTPアクセス直前に必ず3秒以上待機し、詳細ページにはアクセスしない。
- 公開日はゼロ埋めした `YYYY/MM/DD` 形式にする。
- HTML解析は `src/subsidy_scraper/app.py` に集約し、Phase 2ではファイルを追加分割しない。
- 自動テストは実サイトへアクセスせず、最小HTMLを使用する。
- 取得・保存処理も `src/subsidy_scraper/app.py` に置き、ファイルを追加分割しない。
- HTTPアクセスと待機は引数で差し替え可能にするが、本番の待機を省略するCLI設定は作らない。
- 取得・保存時の詳細な日本語エラーは専用例外に保持し、コンソール表示と終了コードはPhase 4のCLIで統合する。
- CSV保存は出力先へ直接書き込み、一時ファイルを経由した置換は行わない。
- ユーザーが設計書の作成を指示した場合だけ `docs/design.md` を作成し、レビューと承認を経てから対象フェーズを実装する。設計承認と実装開始指示は分けて扱う。
- Phase 4の設計書は「レビュー中」であり、D-01〜D-07は未承認である。

## 変更したファイル

- `samples/subsidy_scraper/AGENTS.md`
- `samples/subsidy_scraper/PLANS.md`
- `samples/subsidy_scraper/docs/HANDOFF.md`
- `samples/subsidy_scraper/docs/design.md`
- `samples/subsidy_scraper/docs/requirements.md`
- `samples/subsidy_scraper/main.py`
- `samples/subsidy_scraper/pyproject.toml`
- `samples/subsidy_scraper/requirements.txt`
- `samples/subsidy_scraper/src/subsidy_scraper/__init__.py`
- `samples/subsidy_scraper/src/subsidy_scraper/app.py`
- `samples/subsidy_scraper/tests/test_app.py`
- `samples/subsidy_scraper/uv.lock`

## 検証結果

- Python: 3.14.7
- `uv run pytest`: 21件成功
- ステートメントカバレッジ: 100%
- 分岐カバレッジ: 100%
- `uv run ruff check .`: 成功
- `uv run ruff format --check .`: 成功
- Phase 1で保存した実HTMLのオフライン解析: 13件取得
- 先頭レコードの公開日: `2026/08/20`
- 最終レコードの公開日: `2026/04/15`
- HTTPアクセス: Phase 3では実サイトへアクセスせず、モックで1回のアクセス条件と異常系を確認
- CSV保存: 一時ディレクトリへの直接書き込みでBOM、ヘッダー、4列、CSV引用、0件時の非生成、保存エラー変換を確認
- CLI統合: Phase 4のため未実施

## ブロッカーと注意点

- 現在のブロッカーはない。
- ルートの `main.py` は配置だけ済んでおり、実行処理はPhase 4で追加する。
- 403、429などが返った場合、アクセス制限を回避する処理を追加しないこと。
- 通常の `uv run` はホーム配下のuvキャッシュが読み取り専用で失敗するため、検証では `UV_CACHE_DIR=/tmp/uv-cache UV_OFFLINE=1` を付けた。

## Git状態

- ブランチ: `main`
- Phase 3の変更は未コミット
