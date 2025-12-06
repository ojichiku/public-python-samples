# 共通機能：Logging 仕様書

## 1. 目的

本仕様は、Python アプリケーションで統一的に利用できる **共通ログ基盤**を定義する。
CLI / GUI / バッチ処理など、どの形式のアプリケーションでも同じログ設定・ログフォーマットを利用できるようにし、コードの重複を防ぐ。

logging の詳細な実装ではなく、**外部設定・API・フォーマット・成果物**などの仕様レベルをまとめたものである。

---

## 2. 基本要件

### 2.1 出力先

ログは以下の2つに出力する：

1. **標準出力（stdout）**
2. **ログファイル**

これらの有効・無効は **外部設定ファイル**で指定できる。

---

### 2.2 ログフォーマット（必須）

使用するフォーマットは以下の通りとする：

```
yyyy/MM/dd HH:mm:ss.fff [LEVEL] メッセージ
```

Python logging のフォーマット例：

```
"%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s"
```

日付フォーマット：

```
"%Y/%m/%d %H:%M:%S"
```

---

### 2.3 ログレベル

* 既定値：**INFO**
* 外部設定で変更可能（DEBUG / INFO / WARNING / ERROR / CRITICAL）

---

## 3. 外部設定ファイル

logging の設定は、外部設定ファイル（YAML / JSON / TOML）で指定する。

### 3.1 設定項目（仕様）

| 項目             | 型       | 説明                                                  |
| ---------------- | -------- | ----------------------------------------------------- |
| `level`          | str      | ログレベル                                            |
| `stdout.enabled` | bool     | 標準出力へログを出すか                                |
| `file.enabled`   | bool     | ファイルへログを出すか                                |
| `file.path`      | str      | ログファイルの保存先                                  |
| `file.rotation`  | str/null | ローテーション設定（例："1MB", "1day"）※MVPでは未実装 |
| `file.max_files` | int      | ローテーション時の保持数                              |
| `format`         | str      | ログのフォーマット文字列。未指定ならデフォルトを使用  |
| `date_format`    | str      | 日付フォーマット文字列                                |

### 3.2 標準の設定ファイル（ひな形：YAML）

`config/logging.yaml` をデフォルト設定ファイルとする。

```yaml
# config/logging.yaml

level: INFO

stdout:
  enabled: true

file:
  enabled: true
  path: logs/app.log
  rotation: null
  max_files: 5

format: "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s"
date_format: "%Y/%m/%d %H:%M:%S"
```

---

## 4. 提供するAPI（仕様レベル）

本 logging 機能は以下の API を提供する。

```python
def setup_logging_from_file(path: str | Path) -> None:
    """
    外部設定ファイル（YAML/JSON/TOML）を読み込み、
    ログ設定を初期化する。
    """

def setup_logging(config: LoggingConfig) -> None:
    """
    LoggingConfig（pydantic モデル）を元にログ設定を適用する。
    """

def get_logger(name: str | None = None) -> logging.Logger:
    """
    共通ロガーの取得関数。
    各モジュールは本関数を必ず経由してロガーを取得する。
    """
```

---

## 5. 実装方針（メモ）

* 設定ファイルは `common.config` のロード機能で読み込み、pydantic により検証してから `setup_logging` に渡す。
* ログの初期化処理は、アプリ起動時に **1 回**のみ実行される。
* `get_logger()` は logging の標準ロガーを返しつつ、設定反映済みであることを保証する。
* ハンドラの重複を避けるため、 `setup_logging()` 内で既存ハンドラをクリアするか、二重登録チェックを行う。

---

## 6. 成果物（必須）

logging 共通機能を実装する際、以下の成果物を作る。

### 6.1 ソースファイル

**`src/common/logging.py`**

* 外部設定ファイルの読み込み → logging 初期化
* フォーマット・ハンドラ（stdout / file）の設定
* ロガー取得関数の提供
* `LoggingConfig`（pydantic モデル）の定義

---

### 6.2 テストファイル（pytest）

**`tests/test_logging.py`**

テスト観点：

* 標準出力にログが正しく出るか（フォーマット含む）
* ログファイルが生成されるか
* ログレベル設定が反映されるか
* ログフォーマット変更が反映されるか
* ファイル出力 ON/OFF の反映
* `get_logger()` の動作確認
* 初期化を複数回行ってもハンドラが重複しない

---

### 6.3 外部設定ファイル（標準ひな形）

**`config/logging.yaml`**

* 標準設定の YAML ファイル
* テストおよびサンプルとして利用
* 各アプリケーションは必要に応じてこのファイルをコピーして利用

---

## 7. 今後の拡張（将来項目）

* ログの色付け（rich の対応）
* ローテーション（TimedRotatingFileHandler / RotatingFileHandler）
* JSON 形式ログ
* 非同期ログ（QueueHandler）

---

## 8. 補足

本 spec に書かれている “設定項目” や “API 仕様” は最小構成であり、必要に応じて拡張する。
いずれの変更も、**AGENTS.md → spec 更新 → 実装 → テスト追加**の順で進める。

