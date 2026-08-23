# Phase 1で実行したcurlコマンド

実行日: 2026-08-23

```bash
sleep 3
curl --max-time 30 \
  --user-agent 'subsidy_scraper/1.0 (+public Python sample; contact via repository)' \
  --dump-header /tmp/subsidy_scraper_headers.txt \
  --output /tmp/subsidy_kobo.html \
  --write-out 'http_code=%{http_code}\nredirect_url=%{redirect_url}\nsize_download=%{size_download}\nnum_redirects=%{num_redirects}\n' \
  'https://www.chusho.meti.go.jp/koukai/hojyokin/kobo.html'
```

## オプションの用途

- `sleep 3`: HTTPアクセス直前に3秒待機する。
- `--max-time 30`: curl全体のタイムアウトを30秒にする。
- `--user-agent`: このサンプルツールからのアクセスであることを示す。
- `--dump-header`: レスポンスヘッダーを一時ファイルへ保存する。
- `--output`: レスポンス本文を一時ファイルへ保存する。
- `--write-out`: HTTPステータス、リダイレクト先、取得サイズ、リダイレクト回数を表示する。

## 実行結果

```text
http_code=403
redirect_url=
size_download=2950
num_redirects=0
```

保存先はいずれも `/tmp` 配下であり、取得したレスポンス自体はリポジトリに追加していません。

## User-Agent切り分けテスト

ユーザーの承認後、ほかの条件を変えず、User-AgentだけをChrome相当へ変更して実行しました。

```bash
sleep 3
curl --max-time 30 \
  --user-agent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
  --dump-header /tmp/subsidy_scraper_chrome_headers.txt \
  --output /tmp/subsidy_kobo_chrome.html \
  --write-out 'http_code=%{http_code}\nredirect_url=%{redirect_url}\nsize_download=%{size_download}\nnum_redirects=%{num_redirects}\n' \
  'https://www.chusho.meti.go.jp/koukai/hojyokin/kobo.html'
```

実行結果:

```text
http_code=200
redirect_url=
size_download=17238
num_redirects=0
```

URL、タイムアウト、保存・表示条件は1回目と同じです。変更したリクエスト条件はUser-Agentだけでした。
