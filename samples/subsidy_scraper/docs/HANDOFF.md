# Phase 2 引継ぎ

## 現在の目標とフェーズ

- Phase 1「実サイトのHTML構造調査」: 完了
- Phase 2「最小プロジェクトとHTML解析」: 完了
- Phase 3「Web取得とCSV保存」: 未着手
- 状態: ユーザーからのPhase 3開始指示待ち

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

## 次の1手

ユーザーから開始指示を受けた後、`PLANS.md` のPhase 3「Web取得とCSV保存」に着手する。

Phase 3では、Phase 2の `parse_subsidies()` を変更せずに利用し、3秒待機、固定Chrome相当User-Agent、30秒タイムアウト、HTTPエラー処理、UTF-8 BOM付きCSV保存を追加する。

## 確定した判断

- Pythonは3.14系を使用する。
- リポジトリのpre-commit Ruff v0.6.1との互換性のため、Ruffの解析ターゲットだけは `py313` とする。実行Python要件は3.14系のまま維持する。
- 本実装では、切り分けでHTTP 200を確認した固定Chrome相当User-Agentを使用する。
- HTTPアクセス直前に必ず3秒以上待機し、詳細ページにはアクセスしない。
- 公開日はゼロ埋めした `YYYY/MM/DD` 形式にする。
- HTML解析は `src/subsidy_scraper/app.py` に集約し、Phase 2ではファイルを追加分割しない。
- 自動テストは実サイトへアクセスせず、最小HTMLを使用する。

## 変更したファイル

- `samples/subsidy_scraper/AGENTS.md`
- `samples/subsidy_scraper/PLANS.md`
- `samples/subsidy_scraper/docs/HANDOFF.md`
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
- `uv run pytest`: 11件成功
- ステートメントカバレッジ: 100%
- 分岐カバレッジ: 100%
- `uv run ruff check .`: 成功
- `uv run ruff format --check .`: 成功
- Phase 1で保存した実HTMLのオフライン解析: 13件取得
- 先頭レコードの公開日: `2026/08/20`
- 最終レコードの公開日: `2026/04/15`
- HTTPアクセス: Phase 2では未実施
- CSV保存: Phase 3のため未実施
- CLI統合: Phase 4のため未実施

## ブロッカーと注意点

- 現在のブロッカーはない。
- ルートの `main.py` はPhase 2で配置だけ行い、実行処理はPhase 4まで追加しない。
- Phase 3でHTML解析の責務とネットワーク／CSVの責務を混在させすぎないこと。
- 403、429などが返った場合、アクセス制限を回避する処理を追加しないこと。

## Git状態

- ブランチ: `main`
- Phase 2開始時の作業ツリー: クリーン
- Phase 2の変更は未コミット
