import os

import requests
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    site_url = os.getenv("WP_SITE_URL")
    username = os.getenv("WP_USERNAME")
    app_password = os.getenv("WP_APP_PASSWORD")

    if not site_url or not username or not app_password:
        raise ValueError(".envに必要な接続情報が設定されていません。")

    url = f"{site_url.rstrip('/')}/wp-json/wp/v2/users/me"

    response = requests.get(
        url,
        auth=(username, app_password),
        timeout=10,
    )

    print(f"status_code: {response.status_code}")

    if response.ok:
        user = response.json()
        print("WordPressRESTAPIへの接続に成功しました。")
        print(f"user_id: {user.get('id')}")
        print(f"name: {user.get('name')}")
        return

    print("WordPressRESTAPIへの接続に失敗しました。")
    print(response.text)


if __name__ == "__main__":
    main()
