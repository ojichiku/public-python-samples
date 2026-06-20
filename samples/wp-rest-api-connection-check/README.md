# wp-rest-api-connection-check

WordPress REST API にアプリケーションパスワードで接続できるかを確認する最小サンプルです。

`/wp-json/wp/v2/users/me` にアクセスし、認証に成功した場合はステータスコード、ユーザー ID、表示名を出力します。

## 必要環境

- Python 3.13 以上
- [uv](https://docs.astral.sh/uv/) または pip が利用可能であること
- WordPress 側でアプリケーションパスワードを発行済みであること

## セットアップ

### uv を使う場合

```bash
cd samples/wp-rest-api-connection-check
uv sync
```

### pip を使う場合

```bash
cd samples/wp-rest-api-connection-check
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install requests python-dotenv
```

Windows の PowerShell で仮想環境を有効化する場合は、次のコマンドを使います。

```powershell
.\.venv\Scripts\Activate.ps1
```

`.env.example` をコピーして `.env` を作成します。

```bash
cp .env.example .env
```

`.env` に接続先の WordPress 情報を設定します。

```ini
WP_SITE_URL=https://example.com
WP_USERNAME=your_username
WP_APP_PASSWORD=your_application_password
```

`WP_APP_PASSWORD` には、WordPress のユーザープロフィール画面で発行したアプリケーションパスワードを設定します。通常のログインパスワードは使いません。

## 使い方

uv を使う場合:

```bash
uv run python check_connection.py
```

pip を使う場合:

```bash
python check_connection.py
```

成功時の出力例:

```text
status_code: 200
WordPressRESTAPIへの接続に成功しました。
user_id: 1
name: Example User
```

失敗時はステータスコードと WordPress REST API から返されたレスポンス本文を表示します。

## ファイル構成

```text
samples/wp-rest-api-connection-check/
  .env.example          # 環境変数の記入例
  README.md             # 本ドキュメント
  check_connection.py   # 接続確認スクリプト
  pyproject.toml        # uv 用の依存関係定義
```

## ライセンス

MIT License
