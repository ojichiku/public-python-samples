# 共通機能：コード管理（codes）仕様書

## 1. 目的

画面やバッチ処理で使用する「コード値（マスタ）」を、  
共通の仕組みで取得・利用できるようにする。

- コードグループ単位で一覧を取得し、プルダウン表示などに利用する。
- コードグループ＋コードから単一の値を取得する。
- 取得元は現在は **CSV ファイル**とし、将来 DB や API へ拡張できる構造とする。
- パフォーマンスのため、初回読み込み後は **メモリキャッシュ**から値を返す。

---

## 2. データモデル

### 2.1 CodeItem（論理モデル）

コード1件分の情報を表す。

必須項目：

- `code_group`: str  
  コードグループ名（例：`GENDER`, `STATUS`）
- `code`: str  
  コード値（例：`1`, `0`, `M` など）
- `value`: str  
  表示用の文字列（例：`男性`, `有効` など）
- `sort_order`: int  
  表示順（昇順で並べる）

オプション項目（将来対応を見据え、モデルとしては保持する）：

- `enabled`: bool  
  無効コードを隠したい場合に使うフラグ  
  - `True`（または `1`, `true`, `TRUE` など）→ 有効  
  - `False`（または `0`, `false`, `FALSE` など）→ 無効
- `extra`: dict[str, Any]  
  備考や追加情報を格納するための任意フィールド  
  ※ CSV 上では文字列として保存し、必要に応じて JSON 文字列などにする。

---

## 3. 取得元（ソース）の設計方針

- コード情報の取得元は「**コードソース（CodeSource）**」として抽象化する。
- 現時点では **CSV ファイルから読み込む実装のみ**提供する。
- 将来、DB や API に切り替える場合でも、同じインターフェースで置き換えられるようにする。

（インターフェース例：）

```python
class CodeSource(Protocol):
    def load_all(self) -> list[CodeItem]:
        """すべてのコードを読み込んで返す。"""
```

---

## 4. ファイル形式（CSV）

### 4.1 ファイルパス

* デフォルトパス：`config/codes.csv`

### 4.2 文字コード・区切り

* 文字コード：UTF-8
* 区切り文字：カンマ（`,`）
* ヘッダ行：**あり**

### 4.3 カラム定義

CSV のヘッダ行に定義するカラム：

| カラム名       | 型    | 必須 | 説明                 |
| ---------- | ---- | -- | ------------------ |
| code_group | str  | 必須 | コードグループ名           |
| code       | str  | 必須 | コード                |
| value      | str  | 必須 | 表示用の文字列            |
| sort_order | int  | 必須 | 表示順（昇順でソート）        |
| enabled    | bool | 任意 | 有効フラグ。省略時は True 扱い |
| extra      | str  | 任意 | 追加情報。形式は実装側で自由     |

* `enabled` カラムが存在しない場合：すべて **有効（True）** とみなす。
* `enabled` カラムが存在し、空欄の場合：有効（True）とみなす。
* `extra` は任意文字列。JSON 文字列として扱ってもよい。

### 4.4 囲み文字（クオート）の扱い

* フィールドは **囲み文字（ダブルクォーテーション `"..."`）あり／なしのどちらでもよい**。
* CSV パーサ側は、以下の両方を許容して正しく読み込むこと。

  * 例1：`GENDER,1,男性,1,true,`
  * 例2：`"GENDER","1","男性","1","true","{"note":"サンプル"}"`

つまり仕様としては：

* 区切り文字：`,` 固定
* 囲み文字：`"` を使用可。
  **仕様上は「囲み文字有り無し両対応」とし、どちらか一方に固定しない。**

### 4.5 CSVサンプル

```csv
code_group,code,value,sort_order,enabled,extra
GENDER,1,男性,1,true,
GENDER,2,女性,2,true,
GENDER,9,その他,9,false,{"note":"画面では通常非表示"}
STATUS,1,有効,1,true,
STATUS,0,無効,2,true,
```

---

## 5. 提供機能（API仕様）

モジュール名案：`common.codes`

### 5.1 コード一覧取得（プルダウン用）

```python
def get_codes(code_group: str, *, only_enabled: bool = True) -> list[CodeItem]:
    """
    指定されたコードグループに属するコード一覧を取得する。

    - code_group で絞り込み
    - sort_order 昇順でソートして返す
    - only_enabled=True の場合、enabled=False のコードは除外する

    該当グループが存在しない場合は、空リストを返す。
    """
```

ポイント：

* **該当グループが存在しない場合は空リスト**（例外にしない）。
* プルダウン用途を想定しているので、基本は `only_enabled=True` をデフォルト。

---

### 5.2 値の取得（単一コード）

```python
def get_value(
    code_group: str,
    code: str,
    *,
    default: str | None = None,
    only_enabled: bool = True,
) -> str | None:
    """
    指定されたコードグループとコードに対応する value を取得する。

    - code_group と code で一致するエントリを探す
    - only_enabled=True の場合、enabled=False は候補から除外する

    見つかった場合:
        value を返す

    見つからない場合:
        - default が指定されていれば default を返す
        - default が None の場合は None を返す
    """
```

ご指定のとおり、見つからない場合の挙動は：

* default が指定されていれば default を返す
* default が None の場合は None を返す

で確定。

---

## 6. キャッシュ戦略

### 6.1 基本方針

* コード情報は **初回に CSV ファイルから読み込んでメモリに保持**する。
* `get_codes` / `get_value` は、**常にキャッシュを参照**して動作する。
* 読み込みは通常 1 回のみで、以降はキャッシュを使う。

### 6.2 リロード機能

CSV を編集したあとなどに再読み込みしたいケースに備え、
明示的なリロード関数を用意する。

```python
def reload_codes() -> None:
    """
    コード情報を取得元から再読み込みする。

    - CSV ファイルを再度読み込み
    - メモリキャッシュを更新する
    """
```

* 開発時や管理ツールから呼び出すことを想定。
* 通常運用では頻繁に呼ぶ必要はない。

---

## 7. 成果物

この仕様に基づき、以下の成果物を作成する。

1. **spec ファイル**

   * `specs/codes.md`（本ファイル）

2. **ソースコード**

   * `src/common/codes.py`

     * `CodeItem` データモデル
     * `CodeSource` 相当の抽象（必要であれば Protocol）
     * `FileCodeSource` 実装（`config/codes.csv` の読み込み）
     * キャッシュ管理
     * 公開関数：`get_codes`, `get_value`, `reload_codes`

3. **設定ファイル（コード定義 CSV）**

   * `config/codes.csv`

     * ヘッダ付き UTF-8 CSV
     * 4必須カラム + `enabled` / `extra` のサンプル

4. **テストコード**

   * `tests/test_codes.py`

     * グループ一覧取得（ソート順）の確認
     * 有効/無効フラグの挙動確認
     * 単一値取得（存在する／存在しない／default あり／なし）
     * キャッシュが複数回読み込みを発生させていないこと
     * `reload_codes()` の挙動（更新が反映されること）

---
