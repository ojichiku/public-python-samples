# 共通機能：Errors（共通エラーマネージャ）仕様書

## 1. 目的

本仕様は、Python アプリケーションで利用する **共通エラーマネージャ（例外クラス群）** の設計方針と仕様を定める。

目的は以下の通り。

- 共通機能（logging / config / paths / など）が投げる例外クラスを **統一** すること
- 呼び出し側（CLI / GUI / バッチ）が、例外を「どのように扱うべきか」を判断しやすくすること
- 例外クラスの種類を増やしすぎず、シンプルな設計を維持すること

本仕様では例外クラスの設計のみを対象とし、  
例外ハンドリングロジック（CLI での終了コードや GUI でのダイアログ表示など）は、  
`cli` 共通機能やアプリケーション側の責務とする。

---

## 2. 設計方針

### 2.1 例外クラスの命名

- 例外クラスのプレフィックスは **`OcSample`** とする。
  - `Oc` は OjiChiku の略。
- 例外クラスは Python 標準の `Exception` を継承する。

### 2.2 例外クラスの種類

例外クラスの種類は **最小限に抑える**。

初期バージョンでは、以下の 2 クラスのみを定義する。

1. `OcSampleError`  
   - 全ての共通機能が投げる例外のベースクラス  
   - 主に **システム的・致命的なエラー** を表現する

2. `OcSampleUserError`  
   - `OcSampleError` のサブクラス  
   - 主に **ユーザの入力や設定の修正によって解消可能なエラー** を表現する

これにより、呼び出し側は

- 「致命的エラーとして処理すべきか」
- 「ユーザに修正を促すエラーとして処理すべきか」

を簡単に判別できる。

### 2.3 Validation（バリデーションエラー）の扱い

- バリデーションエラーを **すべて例外で返す方針にはしない**。
- よくあるパターンとして、以下を使い分ける。

  1. **True / False や結果オブジェクトで返す**  
     - 業務ロジック的な検証（例：値が範囲内か、パスが存在するか）  
     - 失敗が日常的に起こりうるチェックでは、例外ではなく戻り値で扱う

  2. **例外（`OcSampleUserError`）で返す**  
     - 「ここで通らないと処理続行が危険」「後続処理を止めたい」ような場合  
     - 例：設定ファイルの構造が根本的におかしい、入力値が前提と大きく異なる など

- 将来的に必要になった場合にのみ、`OcSampleUserError` のサブクラスとして `OcSampleValidationError` 等を追加することは許容するが、**初期段階では定義しない**。

---

## 3. 例外クラス仕様

### 3.1 OcSampleError

**役割**

- 共通機能が投げる例外のベースクラス
- 主に **致命的・システム寄りのエラー**（設定ファイル破損、I/O エラーなど）を表現する

**想定プロパティ**

- `message: str`  
  - 人間が読めるエラーメッセージ（ログ出力・デバッグ用）
- `code: str | None`  
  - エラーコード（例：`"CONFIG_NOT_FOUND"`, `"IO_ERROR"`）  
  - ログやメッセージカタログと連携するための識別子
- `user_message: str | None`  
  - ユーザ表示向けメッセージ（任意）  
  - CLI / GUI でそのまま表示できる短いメッセージ
- `fatal: bool`  
  - `True` = 致命的エラー（デフォルト）  
  - `False` = 致命的ではない（後続処理でリカバリ可能）

**コンストラクタのイメージ（仕様レベル）**

```python
OcSampleError(
    message: str,
    code: str | None = None,
    user_message: str | None = None,
    fatal: bool = True,
    *args,
)
```

※ 正確なシグネチャや引数順は実装時に微調整してよい。

---

### 3.2 OcSampleUserError

**役割**

* ユーザの操作や入力、設定内容の修正によって解決可能なエラーを表現する。
* 例：

  * 存在しないファイルパスを指定した
  * 設定値が許可範囲外（例：1〜10のところに 100 を指定した）
  * 組み合わせとして無効なオプションを渡した など

**クラス構造**

* `OcSampleError` を継承するサブクラス。
* `fatal` のデフォルト値は `False`。

**コンストラクタのイメージ**

```python
OcSampleUserError(
    message: str,
    code: str | None = None,
    user_message: str | None = None,
    fatal: bool = False,
    *args,
)
```

---

## 4. 使い分けの指針

### 4.1 共通機能側（ライブラリ側）の例外送出

* **システム・環境起因のエラー**（設定ファイルの破損、I/O エラー、想定外の例外など）
  → `OcSampleError` を送出（`fatal=True` のまま）

* **ユーザ入力や設定の誤り**であり、修正すれば実行可能な場合
  → `OcSampleUserError` を送出（`fatal=False` が基本）

### 4.2 呼び出し側（CLI / GUI / バッチ）の扱いイメージ

この spec ではコードは書かないが、想定するパターンは以下の通り：

* `OcSampleUserError`:

  * CLI → エラーメッセージを表示し、終了コード 1 で終了するなど
  * GUI → メッセージボックスでユーザに通知し、画面は継続
* `OcSampleError`:

  * CLI → ログに詳細を出力し、終了コード 2 などで異常終了
  * GUI → エラーダイアログ表示後、必要に応じてアプリ終了 or 機能停止

実際のハンドリングロジックは `cli` 共通機能や GUI 基底クラス等で定義する。

---

## 5. バリデーションの設計ポリシー

このプロジェクトにおけるバリデーションの方針：

1. **頻発する・想定内の NG**

   * True/False や Result オブジェクトで返す
   * 例：値が範囲内かどうかの確認、文字列フォーマットチェックなど
2. **ここを通過しないと後続処理が破綻する NG**

   * `OcSampleUserError` を送出
   * 例：設定ファイル全体の構造が無効、必須キーが抜けている 等
3. pydantic など外部ライブラリの `ValidationError` が発生した場合

   * 例外をキャッチし、必要に応じて `OcSampleUserError` にラップして再送出する
   * 呼び出し側が OcSample 系のみを意識すればよいようにする

`OcSampleValidationError` のような専用クラスは、必要性が明確になるまで定義しない。

---

## 6. 成果物

本仕様に基づき、以下を作成する。

### 6.1 ソースファイル

* `src/common/errors.py`

内容：

* `OcSampleError` クラス定義
* `OcSampleUserError` クラス定義
* （必要に応じて）補助関数（ログ出力やメッセージフォーマット用）があれば追加可
  ※ ただし共通エラーメッセージの管理（メッセージカタログ）は、別の `messages` 機能として切り出すことを検討する。

### 6.2 テストファイル

* `tests/test_errors.py`

テスト観点：

* 継承関係が正しいこと

  * `OcSampleError` が `Exception` を継承している
  * `OcSampleUserError` が `OcSampleError` を継承している
* コンストラクタで `message` / `code` / `user_message` / `fatal` が正しくセットされること
* `OcSampleUserError` の `fatal` デフォルト値が `False` であること
* `raise` / `except` で正しく捕捉できること

  * `except OcSampleError:` で両方拾える
  * `except OcSampleUserError:` でユーザエラーのみ拾える

---

## 7. 今後の拡張について

* 具体的な要件が出てきた場合のみ、以下のような派生クラス追加を検討する：

  * `OcSampleTimeoutError`
  * `OcSampleValidationError`
  * `OcSampleConfigError`
* 追加する場合は：

  1. 本 spec (`specs/errors.md`) にクラスを追記
  2. 実装 (`src/common/errors.py`) を追加
  3. テスト (`tests/test_errors.py`) を追加
     の順で行う。

---
