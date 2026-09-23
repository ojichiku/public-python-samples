# 開発方針

- 要件はREQUEST.mdを参照する。ユーザーの追加指定を優先する。
- Python 3.14、uv、srcレイアウトを使用する。
- 実装はsrc/github_repository_search/main.pyを中心とした小さな関数構成にする。
- Playwrightの同期APIで、channel="msedge", headless=Falseを指定する。
- GitHubの検索欄にfillで入力し、Enterで検索する。検索語付きURLへの直接移動、GitHub API、requestsへの置換は禁止。
- Playwright付属ブラウザのインストールは行わない。
- 表示完了にはPlaywrightの待機機能を使用する。操作間はユーザー指定により1〜3秒のランダム待機を入れる。複雑なXPathは避ける。
- コメント、利用者向けメッセージ、ドキュメントは日本語で書く。
- CSVはUTF-8 BOM付き、取得上限10件。存在しない任意項目は空文字にする。
- テストはpytestを使用し、uv run pytestで検証する。実EdgeのDOM検証はuv run pytest --run-edgeで行う。
- 実サイトの検証結果と未検証項目をPLANS.mdに記録する。実サイトの制限を回避する処理は加えない。
