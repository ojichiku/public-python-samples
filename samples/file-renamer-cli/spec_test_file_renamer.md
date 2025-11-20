tests/test_file_renamer.py を作りたいです。
src/file_renamer.py に定義されている関数 rename_files と
replace_in_filenames を pytest でテストしてください。

【テストの目的】
- rename サブコマンド相当の関数の動作確認
- replace サブコマンド相当の関数の動作確認

【条件】
- pytest を使用すること
- tmp_path フィクスチャを使い、一時ディレクトリにテスト用ファイルを作成すること
- 実際にファイルをリネームして、ファイル名が期待通りになっていることを assert すること
- コマンドライン実行ではなく、rename_files(), replace_in_filenames() のような関数を直接テストすること
- テストコードは tests/test_file_renamer.py 用に生成すること

src/file_renamer.py を読んで、テストコードを書いてください。
