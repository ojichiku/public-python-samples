# 共通機能：Datetime ユーティリティ仕様書

## 1. 目的

本仕様は、Python アプリケーションで共通して利用する **日時ユーティリティ** の仕様を定める。

- 「現在時刻」「現在日付」を、**統一されたフォーマット**で取得する
- ファイル名に安全に使える **タイムスタンプ文字列** を提供する
- 処理時間計測用の **Timer コンテキストマネージャ** を提供する

ログ用のフォーマットとは切り離し、

- 表示用
- ファイル名用

でよく使うパターンを共通化することを目的とする。

---

## 2. 成果物

### 2.1 モジュール

- `src/common/datetime.py`

### 2.2 テスト

- `tests/test_datetime.py`

---

## 3. 想定ユースケース

- CLI や GUI で「現在時刻」「今日の日付」を表示する
  - 例：`2025/12/08 22:30:01`
  - 例：`2025-12-08`
- 出力ファイル名にタイムスタンプを付ける
  - 例：`report_20251208_223001.csv`
- 処理時間の測定
  - 例：`with Timer() as t: ...` のあと `t.elapsed` で秒数を取得

---

## 4. 共通フォーマット（定数）

モジュール内で、よく使うフォーマットは定数として定義する。

```python
DISPLAY_DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"   # 表示用 日時
DISPLAY_DATE_FORMAT     = "%Y-%m-%d"           # 表示用 日付
FILENAME_DATETIME_FORMAT = "%Y%m%d_%H%M%S"     # ファイル名用
```

* **表示用（日時）**：`YYYY/MM/DD HH:MM:SS`
* **表示用（日付）**：`YYYY-MM-DD`
* **ファイル名用**：`YYYYMMDD_HHMMSS`（拡張子やプレフィックスは呼び出し側が付ける）

---

## 5. 提供する関数・クラス

### 5.1 `now_str()`

```python
def now_str(fmt: str | None = None) -> str:
    """
    現在のローカル日時を文字列で返す。

    デフォルトでは DISPLAY_DATETIME_FORMAT ("%Y/%m/%d %H:%M:%S") を使用する。
    fmt が指定された場合は、そのフォーマットで返す。
    """
```

* 返り値例（デフォルト）：`"2025/12/08 22:30:01"`
* タイムゾーンは考慮せず、`datetime.now()` のローカル時刻を使用する。

---

### 5.2 `today_str()`

```python
def today_str(fmt: str | None = None) -> str:
    """
    本日の日付を文字列で返す。

    デフォルトでは DISPLAY_DATE_FORMAT ("%Y-%m-%d") を使用する。
    fmt が指定された場合は、そのフォーマットで返す。
    """
```

* 返り値例（デフォルト）：`"2025-12-08"`

---

### 5.3 `now_for_filename()`

```python
def now_for_filename() -> str:
    """
    ファイル名に使用しやすい現在日時文字列を返す。

    フォーマットは FILENAME_DATETIME_FORMAT ("%Y%m%d_%H%M%S") とする。
    """
```

* 返り値例：`"20251208_223001"`
* 拡張子やプレフィックスは呼び出し側で連結して利用する。

---

### 5.4 `parse_datetime()`

```python
from datetime import datetime

def parse_datetime(value: str, fmt: str | None = None) -> datetime:
    """
    日時文字列を datetime に変換する。

    fmt が None の場合は DISPLAY_DATETIME_FORMAT ("%Y/%m/%d %H:%M:%S") を既定とする。
    fmt が指定されていれば、そのフォーマットで datetime.strptime() を用いて変換する。

    形式が一致しない場合は ValueError を送出する。
    """
```

* 例：`parse_datetime("2025/12/08 22:30:01")` → `datetime(2025, 12, 8, 22, 30, 1)`

---

### 5.5 `parse_date()`

```python
from datetime import date

def parse_date(value: str, fmt: str | None = None) -> date:
    """
    日付文字列を date に変換する。

    fmt が None の場合は DISPLAY_DATE_FORMAT ("%Y-%m-%d") を既定とする。
    fmt が指定されていれば、そのフォーマットで datetime.strptime() を用いて変換する。

    形式が一致しない場合は ValueError を送出する。
    """
```

* 例：`parse_date("2025-12-08")` → `date(2025, 12, 8)`

---

### 5.6 `Timer` クラス（処理時間計測）

```python
import contextlib
from typing import Optional

class Timer:
    """
    処理時間を計測するためのコンテキストマネージャ。

    使用例:
        with Timer() as t:
            処理...
        print(t.elapsed)  # 経過秒数 (float)

    内部的には time.perf_counter() を使って計測する。
    """

    start: float
    end: float
    elapsed: float
```

#### 5.6.1 `Timer` の仕様

* `with Timer() as t:` の形で使用する。
* `__enter__` で開始時刻を記録。
* `__exit__` で終了時刻を記録し、`elapsed` に経過秒数（float）を格納する。
* コンテキストを出た後、`t.elapsed` で秒数を参照できる。
* 例外が発生しても計測は行われるが、例外はそのまま外に伝播する。

---

## 6. テスト観点（tests/test_datetime.py）

* `now_str()` が指定フォーマットで文字列を返すこと

  * デフォルトフォーマット
  * 任意フォーマットを渡した場合
* `today_str()` が今日の日付文字列を返すこと
* `now_for_filename()` が `YYYYMMDD_HHMMSS` 形式の文字列を返すこと

  * 数字＋`_` だけで構成されていること
  * 長さが期待通りであること（例：15文字）
* `parse_datetime()` が有効な文字列を正しく `datetime` に変換すること

  * 不正な文字列に対して `ValueError` を送出すること
* `parse_date()` が有効な文字列を正しく `date` に変換すること

  * 不正な文字列に対して `ValueError` を送出すること
* `Timer` が 0 以上の経過秒数を `elapsed` に格納すること

  * ごく短い処理の場合でも `elapsed >= 0.0` であること
  * 実時間との差が極端に大きくないこと（sleep を使った簡単な検証など）

※ 時刻そのものの「値」が変化するため、テストでは **フォーマットの妥当性と型** を重視し、
厳密な秒単位の一致を要求しない。

---

## 7. 注意点・非機能要件

* タイムゾーンは扱わない（全てローカル時刻 `datetime.now()` に依存）。

  * タイムゾーン対応が必要になった場合は、別途 spec を拡張する。
* 外部ライブラリ（`pytz`, `python-dateutil` など）は利用しない。
* フォーマット文字列を呼び出し側で乱立させず、原則として

  * `DISPLAY_DATETIME_FORMAT`
  * `DISPLAY_DATE_FORMAT`
  * `FILENAME_DATETIME_FORMAT`

  を使うようにする。

---

## 8. 実装ガイド（Codex 向けメモ）

* `datetime`, `date`, `time`, `timedelta` は標準ライブラリ `datetime` を使用する。
* 時間計測には `time.perf_counter()` を使用する。
* 関数・クラスには日本語の docstring を付ける。
* 型ヒントはすべての公開関数・クラスに付与する。
* モジュール名は `common.datetime` とし、他モジュールからは

  ```python
  from common import datetime as dt_util
  dt_util.now_str()
  ```

  のように呼び出せることを前提とする。
