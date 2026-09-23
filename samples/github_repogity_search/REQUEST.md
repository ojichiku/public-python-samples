PythonとPlaywrightを使って、GitHubのリポジトリ検索を行い、検索結果をCSVファイルへ保存するサンプルプログラムを作成してください。

目的は、Playwright付属のChromiumを使用せず、Windows PCにインストール済みのMicrosoft EdgeをPlaywrightから操作できることを確認することです。

GitHub REST APIやrequestsによる取得は使用せず、実際にブラウザを起動して、検索文字の入力、検索実行、検索結果取得までをPlaywrightで操作してください。

## 使用技術

・Python
・Playwright for Python
・Playwrightの同期APIを使用する
・Windows PCにインストール済みのMicrosoft Edgeを使用する
・Playwright付属Chromiumは使用しない
・Microsoft Edgeは channel="msedge" で起動する
・ブラウザ画面が確認できるように headless=False とする

Playwrightのブラウザダウンロードを前提にしないでください。

つまり、以下は実行しない構成にしてください。

playwright install

Pythonライブラリとしてplaywrightをインストールするだけで動かせる構成にしてください。

## GitHub

GitHub Code Searchの紹介ページは以下です。

https://github.com/features/code-search

ただし、今回行いたいのはコード検索ではなく「リポジトリ検索」です。

リポジトリ検索画面として以下を使用してください。

https://github.com/search?type=repositories

## プログラムの動作

プログラムを起動すると、コンソールから検索キーワードを入力できるようにしてください。

例：

検索キーワードを入力してください: playwright python

入力後、以下の順番で処理してください。

1. Microsoft Edgeを起動する
2. GitHubのリポジトリ検索画面を開く
3. GitHub画面上の検索入力欄に、ユーザーが入力した検索キーワードをPlaywrightで入力する
4. Enterキーなどで検索を実行する
5. 検索結果画面が表示されるまで待機する
6. 検索結果の上位10件を取得する
7. CSVファイルへ保存する
8. 保存したファイル名と取得件数をコンソールへ表示する
9. 処理終了後にブラウザを閉じる

検索URLに最初から検索キーワードを付けてアクセスする方法は使用しないでください。

今回の目的はPlaywrightによる入力操作を確認することなので、必ずGitHubの検索入力欄へPlaywrightで文字を入力して検索してください。

## CSVへ保存する項目

可能な範囲で次の項目を取得してください。

・リポジトリ名
・説明
・リポジトリURL
・使用言語
・Star数

検索結果に項目が存在しない場合は空文字にしてください。

CSVの1行目にはヘッダーを出力してください。

WindowsのExcelで開いたときに日本語が文字化けしないよう、UTF-8 BOM付きで保存してください。

ファイル名は以下とします。

github_repository_search.csv

## Playwrightの実装方針

GitHubのHTML構造に過度に依存するXPathはできるだけ避けてください。

可能であれば、

・get_by_role
・get_by_placeholder
・locator

などを使い、意味の分かるセレクタを優先してください。

画面表示待ちには固定秒数のtime.sleepを多用せず、

・wait_for_url
・wait_for_selector
・locator.wait_for

など、Playwrightの待機機能を利用してください。

ただし、GitHubの現在の画面構造に合わせて、実際に動作する方法を優先してください。

検索結果のHTML構造について推測だけで実装せず、必要なら現在のGitHub画面を確認したうえで実装してください。

## エラー処理

最低限、以下を考慮してください。

・Microsoft Edgeが見つからない
・GitHubへアクセスできない
・検索入力欄が見つからない
・検索結果が0件
・GitHubの画面構造変更などで検索結果を取得できない
・CSV保存時のエラー

エラー発生時は、Pythonの長いスタックトレースだけを表示するのではなく、利用者が原因を判断しやすい日本語メッセージも表示してください。

## プログラム構成

最初は学習・検証用の小さなサンプルなので、過度に複雑なクラス設計は不要です。

以下程度の構成にしてください。

main.py
requirements.txt
README.md

main.pyには処理内容が分かる程度の日本語コメントを入れてください。

requirements.txtには必要なPythonライブラリのみ記載してください。

README.mdには以下を書いてください。

・このプログラムの目的
・動作環境
・Microsoft Edgeが必要であること
・Pythonのインストール方法は不要
・必要ライブラリのインストール方法
・実行方法
・検索例
・CSVへ保存される内容
・Playwright付属Chromiumをインストールする必要がないこと

## 実行例

python main.py

検索キーワードを入力してください: playwright python

Microsoft Edgeを起動しました。
GitHubで「playwright python」を検索します。
10件取得しました。
github_repository_search.csv に保存しました。

## 重要

今回の目的はGitHubから効率良くデータを取得することではありません。

「PCに既にインストールされているMicrosoft EdgeをPlaywrightから操作し、Webページに文字を入力し、検索を実行し、画面からデータを取得する」

という一連のブラウザ自動操作を確認することが目的です。

そのため、GitHub APIへの置き換えはしないでください。

まず実装してください。

実装後は、

1. 作成したファイル一覧
2. プログラムの処理の流れ
3. 実行に必要なコマンド
4. Playwright付属Chromiumを使っていないこと
5. Microsoft Edgeをどのコードで指定しているか
6. GitHub画面へ実際に入力しているコード箇所

を簡潔に説明してください。
