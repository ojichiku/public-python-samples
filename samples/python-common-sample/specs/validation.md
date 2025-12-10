# 共通機能：validation（pydantic ベース検証）仕様書

## 1. 目的

本仕様は、アプリケーション内で共通して利用する **入力検証レイヤ（validation）** の仕様を定める。

- pydantic ベースの共通 `AppModel` を用意する
- 設定ファイルや CLI パラメータなどの **「最終チェック」** を一元化する
- pydantic の検証エラーを、共通の `ValidationError`（共通エラーマネージャ）に変換し、扱いやすくする

これにより、

- 「辞書を渡す → 型＋必須項目＋値の妥当性を一括チェック」
- エラー時には **人間が読めるメッセージ1本** にして扱える

という形を標準化する。

---

## 2. 成果物

### 2.1 モジュール

- `src/common/validation.py`

### 2.2 テスト

- `tests/test_validation.py`

---

## 3. 想定ユースケース

- 設定ファイル（YAML/JSON/TOML）読込後のチェック  
  → `dict` になった設定値を AppModel に通して検証する
- CLI 引数＋設定ファイルをマージした後の「最終形」を検証
- 他の共通機能（例：paths, logging 設定など）の入力値チェック

イメージ：

```python
from common.validation import AppModel, validate_model

class AppConfig(AppModel):
    input_dir: str
    output_dir: str
    dry_run: bool = False

data = {"input_dir": "in", "output_dir": "out"}
cfg = validate_model(AppConfig, data)  # 成功すれば AppConfig インスタンス
```

---

## 4. pydantic 利用方針（ざっくり）

* pydantic は **型付きデータクラス＋バリデーション** のような位置づけで使う。
* 呼び出し側は基本的に「クラスを定義して `validate_model()` に投げるだけ」にする。
* pydantic が投げる `pydantic.ValidationError` は、
  全て共通エラー `common.errors.ValidationError` に変換して扱う。

> 呼び出し側は「pydantic そのもの」ではなく、
> **AppModel と validate_model の使い方さえ覚えればよい**という設計にする。

---

## 5. 提供するクラス・関数

### 5.1 `AppModel`（共通基底クラス）

```python
from pydantic import BaseModel

class AppModel(BaseModel):
    """
    アプリケーション内で使用する pydantic モデルの共通基底クラス。

    - 型ヒントを利用してバリデーションを行う。
    - 余分なキー（想定していない設定・パラメータ）は基本的に許可しない。
    """

    class Config:
        extra = "forbid"  # 想定外のフィールドを許可しない
```

#### 仕様

* 全ての検証用モデルは `AppModel` を継承して定義する。
* `extra = "forbid"` により、
  設定ファイルに「書いたけど code 側で定義していないキー」があればエラーにする。
* デフォルト値は pydantic の機能を使って通常通り指定できる。

---

### 5.2 `validate_model()`

```python
from typing import Type, TypeVar, Mapping, Any
from pydantic import ValidationError as PydanticValidationError
from .errors import ValidationError  # 共通エラーマネージャの ValidationError

T = TypeVar("T", bound=AppModel)

def validate_model(model_cls: Type[T], data: Mapping[str, Any]) -> T:
    """
    dict 等のデータを受け取り、指定された AppModel サブクラスで検証する。

    - 検証成功 → モデルインスタンス（model_cls のオブジェクト）を返す
    - 検証失敗 → common.errors.ValidationError を送出する

    ValidationError には、ユーザー向けに読みやすいメッセージを設定する。
    詳細なエラー情報（フィールド名と理由）は detail に含める。
    """
```

#### 仕様

* `model_cls`: `AppModel` を継承したクラス（例：`AppConfig`）
* `data`: `dict` や `Mapping[str, Any]`（設定ファイル読込結果など）
* 正常時：
  → `model_cls(**data)` と同等の結果（pydantic が型変換・デフォルト補完を行う）
* 異常時：

  * pydantic の `ValidationError` を捕捉
  * `common.errors.ValidationError` に変換して送出
  * メッセージは日本語でわかりやすく整形する

例（エラーメッセージイメージ）：

* ユーザー向けメッセージ：
  `設定ファイルの内容が不正です。詳細を確認してください。`
* detail（ログ向け）：
  `field "input_dir": field required\nfield "retry": value is not a valid integer ...`

---

### 5.3 `format_pydantic_errors()`

```python
from pydantic import ValidationError as PydanticValidationError

def format_pydantic_errors(exc: PydanticValidationError) -> str:
    """
    pydantic の ValidationError から、読みやすい日本語メッセージ文字列を生成する。

    - フィールド名
    - エラー内容

    を1つの文字列にまとめて返す。
    """
```

#### 仕様

* pydantic のエラー構造はリスト形式で複数エラーを含むため、
  それらを「行ごとに1エラー」の形で文字列化する。

* 例：

  ```text
  input_dir: field required
  retry: value is not a valid integer
  ```

* この文字列を `ValidationError.detail` に入れてログ側で使えるようにする。

---

## 6. エラーとの連携（common.errors）

この validation 機能は、共通エラーマネージャの `ValidationError` と連携する。

想定される `common.errors.ValidationError` のイメージ：

```python
class ValidationError(AppError):
    """
    入力値や設定内容が不正な場合に使用する共通例外。
    """
    ...
```

`validate_model()` は、pydantic の `ValidationError` を必ずこのクラスに変換して送出する。

* `ValidationError.message` にはユーザー向けの簡潔なメッセージ（日本語）を入れる。
* `ValidationError.detail` には `format_pydantic_errors()` で整形した詳細情報を入れる。

これにより、CLI/GUI は「ValidationError が来たらこの文言を表示する」という共通処理ができる。

---

## 7. テスト観点（tests/test_validation.py）

* `AppModel` を継承した簡単なモデルで検証する：

  ```python
  class SampleConfig(AppModel):
      name: str
      count: int = 0
  ```

### 7.1 正常系

* `validate_model(SampleConfig, {"name": "test"})` が成功し、

  * `name == "test"`
  * `count == 0`（デフォルト適用）
* 追加フィールドがない場合は問題なく通る。

### 7.2 異常系：必須項目欠落

* `validate_model(SampleConfig, {"count": 1})` で `ValidationError` が送出されること。
* `ValidationError.message` に

  * `"設定の検証に失敗しました。項目を確認してください。"`（例）
* `ValidationError.detail` に `name: field required` が含まれること。

### 7.3 異常系：型不正

* `validate_model(SampleConfig, {"name": "test", "count": "abc"})` で `ValidationError`
* detail に `count` フィールドの型エラー内容が含まれること。

### 7.4 異常系：余分なフィールド

* `validate_model(SampleConfig, {"name": "test", "extra": 1})`
* extra フィールドによるエラーとなること（`extra = "forbid"` の動作確認）

---

## 8. 注意点・方針

* pydantic のバージョンは現時点の安定版を使用する（v1 / v2 のどちらかは pyproject で管理）。

* 呼び出し側は基本的に以下だけ覚えればよい：

  1. `AppModel` を継承したクラスを定義する
  2. `validate_model(MyModel, data)` を呼ぶ
  3. 例外 `ValidationError`（共通）を捕まえて、メッセージを表示 or ログ出力する

* タイプヒントに従って自動で変換・チェックしてくれるので、
  「自前で `if not isinstance(x, int)` とかを書きまくる」必要がなくなる。

---

## 9. Codex への依頼ポイント（メモ）

Codex に実装を依頼する際は、次のように伝える想定：

* ファイル：`src/common/validation.py` に、
  本 spec に書かれた `AppModel`, `validate_model`, `format_pydantic_errors` を実装すること。
* ファイル：`tests/test_validation.py` に、
  7章のテスト観点をカバーする pytest テストを書くこと。
* コメント・docstring は日本語、型ヒントは必須。
* `common.errors.ValidationError` を前提にするが、テストでは簡易ダミー or 実際のクラスを使う形で整合性を取る。

---
