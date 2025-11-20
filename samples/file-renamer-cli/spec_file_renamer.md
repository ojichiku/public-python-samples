CLIツールを実装します。
このファイルは既存GitHubリポジトリ内の samples/file-renamer-cli サブプロジェクトです。
Gitの操作やgit initは行わないでください。Pythonコードだけを書いてください。
ファイル名はsrc/file_renamer.pyにしてください。

【作りたいツール】
- ファイル名の一括リネームツール (file_renamer.py)
- 対象ディレクトリ内のファイルをルールに従ってリネームする

【仕様】
- Python 3.14系を想定、標準ライブラリのみ使用すること
- コマンドの呼び出し例:
  - python -m file_renamer rename --dir ./samples --prefix blog_ --digits 3
  - python -m file_renamer replace --dir ./samples --find draft_ --replace final_
- サブコマンド:
  1. rename:
     - 連番でリネームする
     - オプション:
       - --dir: 対象ディレクトリ (必須)
       - --prefix: 新しいファイル名の先頭文字列 (必須)
       - --digits: 連番の桁数 (デフォルト3)
  2. replace:
     - ファイル名の一部文字列を置換する
     - オプション:
       - --dir: 対象ディレクトリ (必須)
       - --find: 探す文字列 (必須)
       - --replace: 置き換える文字列 (必須)

【要件】
- argparse を使って CLI を実装すること
- pathlib を使ってファイルパスを扱うこと
- リネーム前後のファイル名を標準出力に表示すること
- エラー時は例外をそのまま表示せず、わかりやすいメッセージを表示して終了コード1で終了すること
- 後からpytestでテストしやすいように、純粋な処理は関数に分けること
  - 例: rename_files(), replace_in_filenames() など
- モジュールとしても使えるように、main() 関数を用意し、if __name__ == "__main__": から呼び出す構成にすること。
- コードに日本語コメントを追加してください。
  - 処理の意図が分かるように
  - 関数の先頭にはdocstringも追加してください
  