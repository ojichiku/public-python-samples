# ファイルリネーマーCLI

ファイル名をまとめて整形したいときに使えるシンプルなCLIです。指定ディレクトリ内のファイルを、連番プレフィックス付きに並び替えたり、特定の文字列を別の文字列に置換したりできます。標準ライブラリのみで実装されているため、追加の依存関係を気にせず動かせます。

コマンドは `python -m file_renamer` の形式で呼び出し、サブコマンドに応じてリネーム方法を選びます。操作結果は `旧ファイル名 -> 新ファイル名` の形式で表示されるので、反映内容をすぐに確認できます。

## 主な機能
- `rename`: 連番とプレフィックスを用いた一括リネーム
- `replace`: ファイル名の一部文字列の検索・置換
- エラー時は日本語メッセージを標準エラーに表示し、終了コード1で終了

## 前提
- Python 3.14 以上
- [uv](https://github.com/astral-sh/uv)（任意、依存ライブラリの取得に使用）

## セットアップ
```bash
# 依存インストール (uvを利用)
cd samples/file-renamer-cli
uv sync
```

```bash
# uvがない場合は、標準のvenvを使ってもOK (依存は標準ライブラリのみ)
cd samples/file-renamer-cli
python3 -m venv .venv
source .venv/bin/activate
```

## 使い方

### uv経由での実行例
```bash
# 連番リネーム
uv run python -m file_renamer rename --dir ./samples --prefix blog_ --digits 3

# 文字列置換
uv run python -m file_renamer replace --dir ./samples --find draft_ --replace final_
```

### Pythonコマンドで直接実行
```python
# 連番リネーム
python -m file_renamer rename --dir ./samples --prefix blog_ --digits 3

# 文字列置換
python -m file_renamer replace --dir ./samples --find draft_ --replace final_
```

## 注意事項
- ディレクトリ内のファイルを上書きする可能性があるため、実行前にバックアップを推奨します。
- `rename` では同名ファイルが存在すると失敗します。処理前にディレクトリの状態を確認してください。
- `replace` で検索文字列を空にすることはできません。

## ライセンス
本プロジェクトは MIT ライセンスで提供されます。
