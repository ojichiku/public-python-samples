# 共通機能：Config（設定ファイル読み込み）仕様書

## 1. 目的

本仕様は、Python アプリケーションで共通して利用できる  
**設定ファイル読み込み機能（config loader）** の挙動を定義する。

- YAML / JSON / TOML などの設定ファイルを読み込む
- ファイル形式ごとの差異を吸収して、`dict` として利用できるようにする
- 必要な場合のみ pydantic で構造・型チェックを行えるようにする
- エラー時は共通の例外クラス（`OcSampleError`, `OcSampleUserError`）で表現する

ことを目的とする。

> ※ この spec は「設定ファイルをどう読むか」の仕様のみを扱う。  
> 設定ファイルの中身（項目構造）や CLI の `--config` オプションなどは対象外とする。

---

## 2. 対応するファイル形式

Config 共通機能は、以下の拡張子を持つファイルに対応する。

- `.yaml` / `.yml`
- `.json`
- `.toml`

拡張子から自動判別し、適切なパーサで読み込む。

---

## 3. 提供機能

### 3.1 基本機能：設定ファイルを dict として読み込む

**役割**

- 指定された設定ファイルを読み込み、`dict` として返す。
- ファイル形式の違い（YAML / JSON / TOML）はこの共通機能の内部で吸収する。

**想定 API（仕様レベル）**

```python
def load_config(path: str | Path) -> dict:
    """
    設定ファイルを読み込み、dict として返す。

    対応形式:
        - .yaml / .yml
        - .json
        - .toml
    """
```

> 実際の関数名・モジュール名は `src/common/config.py` で定義するが、
> 基本的な責務は「ファイルパス → dict」変換である。

---

### 3.2 オプション機能：pydantic による構造・型チェック

**役割**

* 必要な場合のみ、pydantic モデルを使って設定内容の構造・型チェックを行う。
* 共通機能として「pydantic を使った検証もできる」が、**pydantic 利用は必須ではない**。

**想定 API（仕様レベル）**

```python
def load_config_as(path: str | Path, model: type[BaseModel]) -> BaseModel:
    """
    指定された設定ファイルを読み込み、pydantic モデルで検証して返す。

    - まず load_config() で dict として読み込む
    - 次に model(**data) でバリデーションする
    """
```

pydantic を使うかどうかは「利用側（各アプリ）」の判断とし、
この spec では **「サポート機能」として提供するにとどめる**。

---

## 4. 例外仕様（共通例外クラスの利用）

Config 共通機能では、エラー時に
`OcSampleError` / `OcSampleUserError` を利用する。

### 4.1 使用する例外クラス

* `OcSampleError`

  * 共通機能が送出する致命的エラーを表す。
* `OcSampleUserError`

  * ユーザの修正で解決できるエラーを表す。

### 4.2 想定されるエラーと例外の使い分け

#### 4.2.1 ファイルが存在しない・読み込めない

* 例：パスのタイプミス、権限不足など
* 原則：**ユーザの修正で解決できるため `OcSampleUserError` を送出する。**

メッセージ例（`message` / `user_message` のイメージ）：

* `message`（内部・ログ向け）

  * `設定ファイル 'config/app.yaml' が見つかりません。`
* `user_message`（ユーザ向け、必要なら）

  * `設定ファイルのパスを確認してください。`

#### 4.2.2 ファイル形式が不正（パースエラー）

* 例：YAML/JSON/TOML の構文エラー
* 原則：**ユーザ修正可能なため `OcSampleUserError` を送出する。**

メッセージ例：

* `設定ファイル 'config/app.yaml' の内容が不正です。形式や構文を確認してください。`

#### 4.2.3 未対応の拡張子

* 例：`config/app.ini` など、この機能が対応していない形式
* 原則：**ユーザの指定ミスなので `OcSampleUserError` を送出する。**

メッセージ例：

* `設定ファイル 'config/app.ini' の拡張子 '.ini' には対応していません。yaml/json/toml を使用してください。`

#### 4.2.4 内部的な予期せぬエラー

* 例：内部で想定外の例外が発生した場合（バグなど）
* 原則：**`OcSampleError` を送出する。**

メッセージ例：

* `設定ファイル読み込み中に予期しないエラーが発生しました。`

---

### 4.3 メッセージに関する方針

* `message` は **ログ用／開発者向け** として、

  * どのファイルで何が起きたか
  * 原因の概要
    を日本語でわかりやすく書く。
* `user_message` を使う場合は、CLI や GUI でそのまま表示できる、
  **簡潔な日本語メッセージ** とする。
* `code` フィールドの具体的な値（例：`"CONFIG_NOT_FOUND"` など）は、
  必要になった時点で別 spec（messages など）で定義する。

---

## 5. 成果物

Config 共通機能を実装する際に作成すべき成果物は以下の通り。

### 5.1 ソースファイル

* `src/common/config.py`

主な責務：

* ファイルの存在確認
* 拡張子の判定
* YAML / JSON / TOML のパース
* エラー発生時に `OcSampleError` / `OcSampleUserError` を送出する

提供関数（仕様レベル）：

* `load_config(path: str | Path) -> dict`
* `load_config_as(path: str | Path, model: type[BaseModel]) -> BaseModel`（オプション機能）

---

### 5.2 テストファイル（pytest）

* `tests/test_config.py`

テスト観点：

1. 正常系

   * YAML / JSON / TOML の各形式で、期待通りの dict が返る
2. 異常系

   * ファイルが存在しない → `OcSampleUserError` が送出される
   * ファイルの読み込み権限がない → `OcSampleUserError` を想定
   * フォーマットが不正（構文エラー） → `OcSampleUserError`
   * 未対応拡張子 → `OcSampleUserError`
   * 内部的な例外を擬似的に発生させ、`OcSampleError` が使われるパスもテストできると望ましい
3. pydantic 利用（任意）

   * `load_config_as()` に簡単な pydantic モデルを渡してバリデーション成功/失敗を確認する

---

### 5.3 サンプル設定ファイル（任意）

* `config/sample.yaml`
* `config/sample.json`
* `config/sample.toml`

など、README やテストで利用するサンプルを用意してもよい（必須ではない）。

---

## 6. 今後の拡張（設定読み込み側）

将来的に必要になった場合、以下の機能を追加する可能性がある。

* 環境変数による上書き（例：`APP_FOO=bar` を config にマージ）
* 複数ファイルのマージ（デフォルト設定 + 環境別設定など）
* 設定のスキーマバージョン管理
* ディレクトリを渡して「見つかったファイルを順に読み込む」仕組み

これらを追加する場合は、本 spec を更新し、
AGENTS.md・README・実装・テストを合わせて修正する。

---
