# 共通機能：YAML 保存ユーティリティ仕様書

---

## 1. 目的

本仕様は、アプリケーション内で利用される任意のデータ（dict / Mapping）を
**YAML 形式で保存する汎用ユーティリティ機能**の仕様を定義する。

* GUI 設定保存（ウィンドウ状態・ユーザー設定 等）
* CLI / バッチツールの実行結果保存
* 一時的な保存データの出力
* 手動編集可能な設定の書き戻し

など、**読み込みを伴わず「書く（保存する）」** ことに特化した軽量な共通機能とする。

YAML の読み込みは既存の `config` 機能で行うため、本仕様では扱わない。

---

## 2. 機能範囲

### 2.1 この機能が行うこと

* YAMLファイルへの保存（dict → YAML）
* 保存先パス（ファイルパス）は呼び出し側が指定する
* ディレクトリが存在しない場合、必要であれば自動作成する（仕様で後述）
* 保存時の文字コードは UTF-8 固定とする

### 2.2 この機能が行わないこと

* YAML の読み込み
  → 既存の `config` 機能を使う
* get/set のラッパ機能
  → YAML 読み込み後は dict として扱えるため不要
* GUI 専用のロジック（ウィンドウ座標・サイズ保存など）
  → 将来必要であれば別 spec を作成する

---

## 3. 使用想定例（仕様レベル）

```python
from common.yaml_store import save_yaml
from pathlib import Path

data = {
    "window": {"width": 1200, "height": 800},
    "recent_paths": ["input/", "output/"],
}

save_yaml(Path("config/gui_settings.yaml"), data)
```

---

## 4. 提供する API（仕様）

### 4.1 モジュール

```
src/common/yaml_store.py
```

### 4.2 関数

```python
def save_yaml(path: str | Path, data: Mapping[str, Any]) -> None:
    """
    渡された dict / Mapping を YAML ファイルとして保存する。

    - path は保存先ファイルパス（絶対/相対どちらでも可）
    - 親ディレクトリが存在しない場合は自動で作成してよい
    - 既存ファイルがある場合は上書き
    - YAML の書き込みには yaml.safe_dump を使用する
    - 文字コードは UTF-8 固定とする

    エラー時は共通エラークラス（OcSampleError / OcSampleUserError）を使用する。
    """
```

---

## 5. 入出力仕様

### 5.1 入力：`data`

* 型：`Mapping[str, Any]`（dict を想定）
* YAML で表現できる型のみ扱う

  * str / int / float / bool / list / dict / None
  * YAML で表現できないオブジェクトは例外とする

### 5.2 入力：`path`

* 任意の場所を指定できる（アプリ側で管理）
* 絶対パス / 相対パスのどちらも許可
* 親ディレクトリが存在しない場合の扱い
  → **自動作成する**（使う側の利便性を優先）

### 5.3 出力

* 指定パスに YAML ファイルを作成する
* インデントやフォーマットは yaml.safe_dump の標準動作に従う
* 文字コード：UTF-8

---

## 6. エラー処理

本機能は共通エラーモジュールの例外を用いる。

| ケース                           | 投げる例外          |
| -------------------------------- | ------------------- |
| ファイルが書き込み不可           | `OcSampleUserError` |
| データが YAML として保存できない | `OcSampleError`     |
| 予期せぬエラー                   | `OcSampleError`     |

エラーメッセージは可能な範囲でユーザー向けに簡潔にする。

---

## 7. テスト仕様（tests/test_yaml_store.py）

以下の観点を必ず含める：

### 7.1 正常系

* シンプルな dict を保存できる
* ネストした dict / list を含む構造で保存できる
* 親ディレクトリが無い場合、作成される
* 保存した YAML を読み込むと元の dict と同等になる
  ※ 読み込みは `config.load_config()` を使用

### 7.2 異常系

* 書き込み権限がないパスを指定した場合に `OcSampleUserError`
* YAML として保存できないオブジェクトを含む場合に `OcSampleError`
* ファイルシステム例外（I/O エラー）発生時に `OcSampleError` になる

---

## 8. モジュール配置

```
src/
  common/
    yaml_store.py

tests/
  test_yaml_store.py

specs/
  yaml_store.md  ← このファイル
```

---

## 9. 今後の拡張

必要に応じて以下を追加してよい：

* YAML のオプション指定

  * インデント数
  * ソートキー ON/OFF
* スキーマ検証（pydantic や JSON schema）
* 保存専用ではなく read/write の統合バージョン
* GUI アプリ用設定ヘルパ関数（別 spec で管理）

---

## 10. 注意事項

* `load` は本機能には含めない
  → 読み込みは config モジュールで統一して扱う
* GUI 専用の機能は追加しない
  → 汎用ユーティリティとして設計する
* 保存形式を後から変更（JSON 等）したくなる場合を想定し、
  機能名は「yaml_store」に固定して迷いを防ぐ

---
