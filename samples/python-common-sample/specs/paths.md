# 共通機能：paths（パス操作ユーティリティ）仕様書

## 1. 目的

本仕様は、Python アプリケーション・CLIツール・GUIツール・実行ファイル（EXE化含む）に共通して利用できる  
**汎用的なパス操作ユーティリティ** の仕様を定義する。

対象とする機能は以下：

- パスを `pathlib.Path` へ統一
- 実行形態（スクリプト / モジュール / EXE）に依存しない「アプリ起点ディレクトリ」の取得
- ユーザーホームディレクトリの取得
- 一時ディレクトリ・一時ファイルの生成
- 汎用的なファイル／ディレクトリ操作（存在判定・列挙・ファイル名ユーティリティ）

プロジェクト固有（logs / data / project_root など）の扱いは **paths の責務外** とする。

---

## 2. スコープ

### 2.1 この共通機能が扱うもの

- `str | Path` → `Path` の統一変換
- カレントディレクトリ取得
- **アプリケーション起点ディレクトリ取得（EXE対応）**
- **ユーザーホームディレクトリ取得**
- 一時ディレクトリ・一時ファイル作成
- ファイル／ディレクトリ列挙（glob）
- OS依存の禁止文字を除去するファイル名ユーティリティ

### 2.2 この共通機能が扱わないもの

- 特化用途ディレクトリ（logs/, data/ など）
- project_root（pyproject.toml, .git）依存のルート判定
- 再帰削除などの破壊的ファイル操作
- 圧縮／展開／同期など高度な操作

---

## 3. 基本方針

- **すべてのパス処理は `pathlib.Path` に統一する。**
- Public API では `str | Path` を受け、内部で Path に変換する。
- Public API の戻り値は基本 Path。
- 実行形態の違いは `get_app_dir()` で吸収する。
- 削除系は範囲外とし、安全を優先。

---

## 4. 提供機能（API仕様）

モジュール名：`src/common/paths.py`

---

### 4.1 パス変換ユーティリティ

```python
def to_path(path: str | Path) -> Path:
    """
    引数を pathlib.Path に変換して返す。
    """
```

```python
def resolve_path(path: str | Path) -> Path:
    """
    Path に変換し、絶対パスに解決して返す。
    """
```

---

### 4.2 カレントディレクトリ

```python
def get_cwd() -> Path:
    """
    現在の作業ディレクトリ（カレントディレクトリ）を Path で返す。
    """
```

---

### 4.3 アプリケーション起点ディレクトリ（スクリプト & EXE 対応）

```python
def get_app_dir() -> Path:
    """
    アプリケーションの起点ディレクトリを返す。

    優先順位:
    1. frozen 実行ファイル（EXE化された場合）
       → sys.executable の親ディレクトリ
    2. スクリプト実行 (__main__.__file__ がある場合)
       → __main__.__file__ の親ディレクトリ
    3. ライブラリとして使用されている場合
       → このモジュール (paths.py) の親ディレクトリ

    この関数は logs や data などを「呼び出し側が自由に決める」ための基点を返すだけであり、
    特定用途のディレクトリは生成しない。
    """
```

---

### 4.4 ユーザーホームディレクトリ取得（★新規追加）

```python
def get_user_home_dir() -> Path:
    """
    現在のユーザーのホームディレクトリを Path で返す。

    Path.home() を内部で使用する。
    OS（Windows / macOS / Linux）を問わず共通で利用可能。
    """
```

---

### 4.5 一時ディレクトリ・一時ファイル

```python
def get_temp_dir(subdir: str | None = None) -> Path:
    """
    OS の一時ディレクトリへの Path を返す。

    subdir が指定されている場合は配下にディレクトリを作成して返す。
    """
```

```python
def create_temp_file(
    prefix: str = "tmp",
    suffix: str = "",
    dir: str | Path | None = None,
    delete: bool = False,
) -> Path:
    """
    一時ファイルを作成し、そのパスを返す。
    delete=False の場合、呼び出し側が明示的に削除する必要がある。
    """
```

```python
@contextmanager
def temporary_directory(prefix: str = "tmp") -> Iterator[Path]:
    """
    with ブロック終了時に削除される一時ディレクトリを提供する。
    """
```

---

### 4.6 存在・種別チェック

```python
def exists(path: str | Path) -> bool:
    """パスが存在するかどうかを返す。"""
```

```python
def is_file(path: str | Path) -> bool:
    """通常ファイルであるかどうかを返す。"""
```

```python
def is_dir(path: str | Path) -> bool:
    """ディレクトリであるかどうかを返す。"""
```

---

### 4.7 ファイル／ディレクトリ列挙

```python
def list_files(dir_path: str | Path, pattern: str = "*", recursive: bool = False) -> list[Path]:
    """
    指定ディレクトリ配下のファイル一覧を返す。
    """
```

```python
def list_dirs(dir_path: str | Path, recursive: bool = False) -> list[Path]:
    """
    指定ディレクトリ配下のサブディレクトリ一覧を返す。
    """
```

---

### 4.8 ファイル名ユーティリティ

```python
def safe_filename(name: str, max_length: int = 255) -> str:
    """
    OS依存の禁止文字を除去した安全なファイル名に変換する。
    """
```

```python
def add_suffix_before_extension(path: str | Path, suffix: str) -> Path:
    """
    拡張子の直前に suffix を付与する。
    """
```

```python
def change_extension(path: str | Path, new_ext: str) -> Path:
    """
    ファイル拡張子を new_ext に変更した Path を返す。
    """
```

---

## 5. 非対象（明確に扱わないもの）

* logs_dir、data_dir のような用途特化関数
* プロジェクトルート推定（pyproject.toml / .git）
* 破壊的な一括削除（rm -rf 相当）
* 圧縮 / 展開 / ディレクトリ同期など高レベル操作

---

## 6. 成果物

### 6.1 ソースファイル

* `src/common/paths.py`

### 6.2 テストファイル（pytest）

* `tests/test_paths.py`

テスト観点例：

* EXE / スクリプト / ライブラリ状況での `get_app_dir()` の動作
* `get_user_home_dir()` が `Path.home()` を返すこと
* 一時ファイル／一時ディレクトリが正しく生成／削除されること
* list_files / list_dirs の挙動
* safe_filename の禁止文字除去
* add_suffix_before_extension / change_extension の変換結果

---

## 7. 将来拡張（候補）

* ユーザー毎の設定ディレクトリ（`~/.config/app_name`）取得
* OS別の標準ドキュメントフォルダ取得
* パス監視（watchdog ラッパー）
* 仮想環境関連のパス補助関数

---
