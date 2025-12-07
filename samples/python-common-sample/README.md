python-common-sample
====================

共通機能の設定ファイルやサンプルコード、テストをまとめるリポジトリです。現在は logging の設定を提供していますが、今後はエラー処理や通知など、他の共通機能も順次追加される想定です。

## 共通機能の概要

- **Logging（ログ出力）**  
  - 仕様: `specs/logging.md` に詳細を記載。  
  - 設定ファイル: `config/logging.ini`。`logging.config.fileConfig()` で読み込み、標準出力とファイルの 2 系統に INFO レベルで出力。  
  - テスト: `tests/test_logging.py` で設定ファイルの整合性を検証。新たな項目を追加した場合はテストも更新してください。
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

## 構成ファイル一覧

```
samples/python-common-sample/
├── config/
│   └── logging.ini          # logging 設定ファイル
├── specs/
│   ├── logging.md           # logging 仕様
│   └── errors.md            # 今後の共通機能仕様テンプレート
├── tests/
│   └── test_logging.py      # logging 設定の検証
├── README.md                # 本ドキュメント
└── pyproject.toml           # 依存管理
```

共通機能を追加する場合は、上記のディレクトリ構成に従ってファイルを増やし、README に概要と手順を追記してください。
