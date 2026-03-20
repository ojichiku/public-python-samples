# python-advanced-template

`content/python-advanced` 向け記事で使う公開サンプルの雛形です。

## 対応するブログ記事

公開後に追記

## 構成

* `src/python_advanced_template/main.py`: サンプルの本体処理
* `src/python_advanced_template/__main__.py`: `python -m` 実行用エントリポイント
* `tests/test_main.py`: 最低限のテスト

## 実行方法

```bash
uv venv
uv pip install -e ".[test]"
pytest -q
python -m python_advanced_template
```

## 使い方

このディレクトリを複製して、記事テーマに合わせて次を変更します。

* ディレクトリ名
* パッケージ名
* `pyproject.toml` の `project.name`
* README の説明と記事URL
