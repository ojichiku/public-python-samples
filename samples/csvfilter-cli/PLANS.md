# csvfilter-cli 実行手順メモ

## 使い方（代表例）
- 実行前に `python -m pip install -e .`（または `PYTHONPATH=src` を通す）を推奨。
- 基本: `python -m csvfilter_cli --input data.csv --and name:contains:Alice --and status:regex:^active$`
- 出力先指定: `python -m csvfilter_cli --input data.csv --output filtered.csv --and city:contains:Tokyo`
- ヘッダーなし（1 始まり列番号）: `python -m csvfilter_cli --input data.csv --no-header --and 2:contains:Alice`
- 区切り変更（TSVなど）: `python -m csvfilter_cli --input data.tsv --delimiter "\t" --and 1:regex:^[0-9]+$`
- 詳細ログ: `python -m csvfilter_cli --input data.csv --and name:contains:Bob -v`

## 実装後の動作確認フロー（pytest 前提）
1. 依存なし、Python 3.13+ が前提。
2. `python -m csvfilter_cli --help` でヘルプ表示確認。
3. 簡易動作: サンプル CSV を用意し、contains / regex / AND 条件 / --no-header / 区切り変更を手動実行で確認。
4. pytest で自動テスト実行（予定の tests/test_cli.py 等）。
5. 0 件マッチ時に stderr へメッセージが出て終了コード 0 になることを確認。
6. 無効演算子、正規表現エラー、カラム未存在で非 0 終了になることを確認。

## 実装タスクの目安（src 配下で機能ごとに分割）
- `src/csvfilter_cli/cli.py`: argparse で引数を受け取り、実行パイプラインを組み立てるメイン処理。
- `src/csvfilter_cli/filters.py`: contains / regex のフィルター実装と AND 結合ロジック。
- `src/csvfilter_cli/io.py`: CSV の読み書き（ヘッダー処理、区切り・クオート指定、行スキップ、出力）。
- `src/csvfilter_cli/__main__.py`: `python -m csvfilter_cli` で cli.main() を呼ぶエントリポイント。
- `tests/`: pytest でフィルター挙動・エラー系・`-v` 出力をカバーするテスト。
- README: 概要、オプション、例、エラー挙動、テスト方法を記載。
