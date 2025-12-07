python-common-sample
====================

共通機能の設定ファイルやサンプルコード、テストをまとめるリポジトリです。現在は logging の設定を提供していますが、今後はエラー処理や通知など、他の共通機能も順次追加される想定です。

## 共通機能の概要

- **Logging（ログ出力）**  
  - 仕様: `specs/logging.md` に詳細を記載。  
  - 設定ファイル: `config/logging.ini`。`logging.config.fileConfig()` で読み込み、標準出力とファイルの 2 系統に INFO レベルで出力。  
  - テスト: `tests/test_logging.py` で設定ファイルの整合性を検証。新たな項目を追加した場合はテストも更新してください。
- **Config（設定ファイル読み込み）**  
  - 仕様: `specs/config.md` を参照。  
  - 実装: `src/python_common_sample/config.py` が YAML/JSON/TOML を吸収して `dict` を返します。  
  - テスト: `tests/test_config.py` で対応拡張子やエラー時の挙動、pydantic 連携をカバーしています。
- **Errors（共通エラーマネージャ）**  
  - 仕様: `specs/errors.md` を参照。  
  - 実装: `src/python_common_sample/errors.py` で `OcSampleError` / `OcSampleUserError` を提供。  
  - テスト: `tests/test_errors.py` で基本的な属性と `to_dict()` の挙動を担保しています。共通機能が新たなメタデータを扱う場合はテストを拡張してください。
- **Messages（メッセージ取得）**  
  - 仕様: `specs/messages.md`。  
  - 設定: `config/messages_ja.ini` に ID と本文を INI 形式で定義。  
  - 実装: `src/python_common_sample/messages.py` の `get_message()` がロケールごとのファイルを読み込み、`{0}` 形式のプレースホルダーを引数で置換します。  
  - テスト: `tests/test_messages.py` で引数不足・余剰、未知 ID、プレースホルダーの挙動を確認しています。
- **今後追加される機能**  
  - 例: エラー共通処理、通知、ジョブ管理等。追加時は spec → 設定ファイル → テスト → README の順で反映します。

## 利用方法

1. **仮想環境の準備**  
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install .
   uv pip install --group test  # テストが必要な場合
   ```
2. **Logging 設定の利用**  
   ```python
   from logging.config import fileConfig
   from pathlib import Path

   config_path = Path(__file__).resolve().parent / "config" / "logging.ini"
   fileConfig(config_path, encoding="utf-8")
   logger = logging.getLogger(__name__)
   logger.info("ready")
   ```
   必要に応じて `logging.ini` をコピーし、`fileHandler` のパスやレベルを変更してください。
3. **テスト実行**  
   ```bash
   uv run pytest samples/python-common-sample/tests
   ```
   新しい共通機能を追加した際は、設定ファイルと spec に合わせてテストを追加することを推奨します。
4. **エラークラスの利用**  
   ```python
   from python_common_sample import OcSampleError, OcSampleUserError

   raise OcSampleUserError(
       "invalid range",
       code="RANGE_ERROR",
       user_message="1〜10 の範囲で入力してください。",
   )
   ```
   `OcSampleError` は致命的な共通エラーのベース、`OcSampleUserError` はユーザ修正可能なエラーを表します。呼び出し側は `fatal` フラグや `user_message` を用いて適切に通知してください。
5. **設定ファイル読み込み**  
   ```python
   from python_common_sample import load_config, load_config_as, OcSampleUserError
   from pydantic import BaseModel

   config_dict = load_config("config/app.yaml")

   class AppConfig(BaseModel):
       name: str
       retries: int

   try:
       app_config = load_config_as("config/app.yaml", AppConfig)
   except OcSampleUserError as exc:
       print(exc.user_message or exc)
   ```
   YAML/JSON/TOML の拡張子を自動判別し、必要に応じて `load_config_as()` で構造チェックも実施できます。

## 構成ファイル一覧

```
samples/python-common-sample/
├── config/
│   ├── logging.ini          # logging 設定ファイル
│   └── messages_ja.ini      # メッセージ定義（日本語）
├── specs/
│   ├── config.md            # 設定ファイル読み込み仕様
│   ├── logging.md           # logging 仕様
│   ├── errors.md            # エラー共通機能仕様
│   └── messages.md          # メッセージ取得仕様
├── src/
│   └── python_common_sample/
│       ├── __init__.py      # 公開インターフェイス
│       ├── config.py        # 設定ファイル読み込み実装
│       ├── errors.py        # エラークラス実装
│       └── messages.py      # メッセージ取得実装
├── tests/
│   ├── test_config.py       # 設定読み込みの検証
│   ├── test_errors.py       # エラークラスの検証
│   ├── test_logging.py      # logging 設定の検証
│   └── test_messages.py     # メッセージ取得の検証
├── README.md                # 本ドキュメント
└── pyproject.toml           # 依存管理
```

共通機能を追加する場合は、上記のディレクトリ構成に従ってファイルを増やし、README に概要と手順を追記してください。
