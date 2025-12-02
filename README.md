# public-python-samples

このリポジトリは、ブログ連動の **公開Pythonサンプル集** です。  
各ディレクトリ（`samples/*`）は独立したミニプロジェクトとして構成し、`uv` または `pip + venv` で環境を構築できます。

サンプルには以下の特徴があります。
- ディレクトリ単位で環境を分離
- `pyproject.toml` と必要に応じて `uv.lock` をコミット（`.venv` 本体はコミットしない）
- Codex（各ミニプロジェクト直下の `AGENTS.md`, `PLANS.md`）による自動生成対応のものと、非対応のものが混在
- ブログ記事との相互リンクによって内容を補足

ブログ: （https://www.wanchiku.com/）  
ライセンス: MIT（詳細は [LICENSE](./LICENSE)）

---

## サンプル一覧

| ディレクトリ                                                       | 概要                                                                                                          | ブログ記事                                                |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| [samples/password-generator-cli](./samples/password-generator-cli) | パスワード生成ツールと PyInstaller を使ったPythonコード → EXE化のサンプルです。                               | https://www.wanchiku.com/pyinstaller-chatgpt-password/    |
| [samples/file-renamer-cli](./samples/file-renamer-cli)             | Codexを使ってコーディングしないで作った「ファイル名一括リネーマーツール」です。                               | https://www.wanchiku.com/codex-uv-python-cli-sample/      |
| [samples/logfilter-cli](./samples/logfilter-cli)                   | ChatGPT+CodexでAGENTS.md、PLANS.mdを使ってコーディングしないで作った「ログフィルターCLIツール」です。         | https://www.wanchiku.com/agents-md-autogen-logfilter-cli/ |
| [samples/logfilter-cli](./samples/logfilter-cli)                   | ChatGPTなし、CodexのみでAGENTS.md、PLANS.mdを使ってコーディングしないで作った「CSVフィルターCLIツール」です。 | https://www.wanchiku.com/codex-csvfilter-cli-report/      |

---

## 環境構築（uv または pip + venv のいずれかを使用）

### 方法A: uvを使用する場合

```bash
cd samples/xxxx
uv venv
uv pip install -e ".[dev]"
pytest -q
python -m <package> --help
```

* `.venv/` はリポジトリにコミットしません。
* `uv.lock` を生成してコミットすると、依存関係を再現できます。

### 方法B: pip + venvを使用する場合

```bash
cd samples/xxxx
python -m venv .venv

# Linuxの場合
source .venv/bin/activate
# Windowsの場合
.venv\Scripts\activate

pip install -e ".[dev]"
pytest -q
python -m <package> --help
```

`pip freeze > requirements.txt` で依存を固定したい場合は、各サンプルディレクトリに出力して管理します。

---

## 開発規約（共通）

* ディレクトリ構成: `src/<package>/`, `tests/`, `pyproject.toml`
* 品質維持: `ruff` + `black` + `pytest` を基本セットとして使用
* CLI形式を推奨。`python -m <package>` で `src/<package>/__main__.py` を実行するか、`pyproject.toml` の `[project.scripts]` にエントリポイントを登録して `pip install -e .` 後にCLI名で呼び出します。
* 実行ファイル（PyInstallerなどで作るバイナリ）はリポジトリに含めません。

---

## Codex の扱いについて

本リポジトリには、Codex を利用して自動生成・拡張を行うサンプルと、手動で作成した通常のPythonサンプルの両方が含まれます。

Codex対応サンプルでは、プロジェクト直下に以下の2ファイルを置いて運用します。

* `AGENTS.md` : 実装ポリシー（命名規則、例外、関数長など）
* `PLANS.md` : 各サンプルの進行手順（テスト→実装→CLI→ドキュメント）

専用の `codex/` ディレクトリは作成していません。  
Codexを使用しないサンプルでは、これらのファイルは含まれません。

---

## 推奨ツール

各サンプルディレクトリで、以下のツールを基本セットとして利用します。

```bash
uv pip install pre-commit ruff black pytest
pre-commit install
```

`.pre-commit-config.yaml` はリポジトリ直下に置き、ルートで `pre-commit install` を実行して共有設定を適用します。  
pre-commitの詳しい説明は下記のブログ記事を見てください。
https://www.wanchiku.com/python-monorepo-precommit/  

---

## ブログとの連携

* 各サンプルのREADME冒頭に、対応するブログ記事のURLを明記します。
* ブログ側にもGitHub該当ディレクトリへのリンクを設置します。
* 更新内容はブログの記事末尾の更新履歴に反映します。

---

## ライセンス

MIT（[LICENSE](./LICENSE) を参照）
