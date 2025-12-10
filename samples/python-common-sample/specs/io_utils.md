# 共通機能：io_utils（ファイル入出力）仕様書

## 1. 目的

本仕様は、「設定ファイル以外の汎用的なファイル入出力処理」を  
`common.io_utils` モジュールとして提供するための仕様を定義する。

本モジュールは以下の入出力を対象とする：

- テキストファイル（全文読み書き）
- 行単位読み書き
- CSV（dict形式）読み書き
- **追記モード（append）での書き込み**

設定ファイル（YAML/JSON/TOML/INI）の読み込みは **`common.config`** 側の責務とし、  
本モジュールには含めない。

---

## 2. 対象範囲と非対象範囲

### 2.1 対象とする処理

- テキストファイル全文読み書き
- テキスト行単位読み書き
- CSV 読み書き（dict 形式）
- 追記モード（append）による書き込み

### 2.2 非対象とする処理

- 設定ファイルの読み書き（common.configに委譲）
- バイナリファイルの特殊処理（バイナリ編集・画像処理など）
- 大規模ファイルのストリーム処理（必要時は拡張）
- 特定用途に依存する処理（例：特定レポート生成、独自ログ形式の解析出力など）

---

## 3. 設計方針

- パスは `str` か `pathlib.Path` を受け取り、内部では必ず `Path` に変換する。
- 文字コードは **原則 UTF-8 をデフォルト**とする。
- 例外（`FileNotFoundError`, `IOError`, `OSError` 等）は基本的にラップせずそのまま送出する。
- 書き込み関数は、親ディレクトリが存在しない場合はエラーとする（自動作成しない）。
  - 必要であれば呼び出し側で `common.paths.ensure_dir()` を利用する。

---

## 4. 提供する API（仕様）

モジュール名：`common.io_utils`

---

### 4.1 テキストファイル読み書き

#### 4.1.1 テキスト読み込み

```python
def read_text(path: str | Path, encoding: str = "utf-8") -> str:
    """
    指定パスのテキストファイルを読み込み、文字列として返す。
    """
```

#### 4.1.2 テキスト書き込み（上書き）

```python
def write_text(path: str | Path, text: str, encoding: str = "utf-8") -> None:
    """
    テキストをファイルに上書き保存する。
    既存ファイルがあれば上書き、無ければ新規作成。
    """
```

#### 4.1.3 テキスト書き込み（追記）

```python
def append_text(path: str | Path, text: str, encoding: str = "utf-8") -> None:
    """
    テキストを追記モードで書き込む。
    既存ファイルの末尾に text を追加する。
    """
```

---

### 4.2 行単位の読み書き

#### 4.2.1 行読み込み

```python
def read_lines(path: str | Path, encoding: str = "utf-8", keep_newline: bool = False) -> list[str]:
    """
    テキストファイルを行単位で読み込み、リストで返す。
    keep_newline=True の場合、行末の改行を保持する。
    """
```

#### 4.2.2 行書き込み（上書き）

```python
def write_lines(
    path: str | Path,
    lines: Iterable[str],
    encoding: str = "utf-8",
    newline: str = "\n",
) -> None:
    """
    行のリストをテキストファイルとして上書き保存する。
    各行の末尾に newline を付加して書き込む。
    """
```

#### 4.2.3 行書き込み（追記）

```python
def append_lines(
    path: str | Path,
    lines: Iterable[str],
    encoding: str = "utf-8",
    newline: str = "\n",
) -> None:
    """
    行のリストをファイル末尾へ追記する。
    各行の末尾に newline を付加して追記する。
    """
```

---

### 4.3 CSV 読み書き（dict形式）

#### 4.3.1 CSV 読み込み

```python
def read_csv_dict(
    path: str | Path,
    encoding: str = "utf-8",
    dialect: str = "excel",
) -> list[dict[str, str]]:
    """
    CSV を dict のリストとして読み込む。
    1 行目をヘッダとして扱う。
    """
```

#### 4.3.2 CSV 書き込み（上書き）

```python
def write_csv_dict(
    path: str | Path,
    rows: list[dict[str, str]],
    fieldnames: list[str],
    encoding: str = "utf-8",
    dialect: str = "excel",
    newline: str = "",
) -> None:
    """
    dict のリストを CSV として上書き保存する。
    fieldnames の順序で列を出力する。
    """
```

#### 4.3.3 CSV 書き込み（追記）

```python
def append_csv_dict(
    path: str | Path,
    rows: list[dict[str, str]],
    fieldnames: list[str],
    encoding: str = "utf-8",
    dialect: str = "excel",
    newline: str = "",
) -> None:
    """
    dict のリストを CSV の末尾に追記する。

    - 既存ファイルが存在しない場合はヘッダ付きで新規作成する。
    - 存在する場合はヘッダを出力せず、rows のみ追記する。
    """
```

---

## 5. 成果物

### 5.1 ソースファイル

```
src/common/io_utils.py
```

実装内容：

* 本仕様で定義した関数群すべてを実装する。
* UTF-8 をデフォルトとし、例外は上位に送出する。
* パスの扱いは内部で Path に統一する。

### 5.2 テストファイル

```
tests/test_io_utils.py
```

テスト観点（例）：

* テキスト読み書き（上書き・追記）が正しく行われる
* 行単位読み書きの挙動（改行保持の有無）
* CSV 読み書き（上書き）
* CSV 追記（append）が正しく動作し、ヘッダの扱いが仕様通りか
* Path と str の混在が問題なく扱えるか
* 不正パスで適切に例外が発生するか

---

## 6. 今後の拡張（必要に応じて）

* TSV / 任意区切り文字への対応
* 一時ファイル作成ヘルパ
* ストリーミング処理（大規模ファイル）
* JSON Lines（NDJSON）の読み書き

これらを追加する場合は、本 spec を更新し、
AGENTS.md → spec 変更 → 実装 → テスト追加の流れで進める。

---
