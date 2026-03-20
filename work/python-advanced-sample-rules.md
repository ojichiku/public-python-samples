# python-advanced 用サンプル保存ルール

## 方針

`content/python-advanced` の記事でコードが長くなる場合は、
完成版コードを `public-python-samples` に保存し、記事本文では要点だけを抜粋します。

保存先は `samples/` 配下に統一し、記事ごとに独立したミニプロジェクトとして管理します。

## 基本ルール

* 保存先は `samples/python-advanced-<topic>-<slug>` を基本にする
* 1記事につき1ディレクトリを原則とする
* 記事タイトルではなく、テーマと slug が分かる名前を使う
* 実行可能なコードを置く
* 記事から GitHub の該当ディレクトリへリンクする

## ディレクトリ命名ルール

推奨形式:

```text
samples/python-advanced-<series>-<slug>
```

例:

```text
samples/python-advanced-practice-function-splitting
samples/python-advanced-practice-file-csv-reader
samples/python-advanced-development-argparse-cli
samples/python-advanced-library-pandas-read-csv
```

補足:

* `series` は `practice` `development` `library` など短くする
* `slug` は記事のスラッグと近い形にそろえる
* 記事URLとディレクトリ名が完全一致でなくてもよいが、対応関係は見てすぐ分かるようにする

## 推奨構成

通常は次の構成を使います。

```text
samples/python-advanced-<series>-<slug>/
  README.md
  pyproject.toml
  src/
    <package_name>/
      __init__.py
      __main__.py
      main.py
  tests/
    test_main.py
```

## 軽量サンプルの例外

10〜30行程度の本当に短い補足コードなら、直下 `.py` だけでも許容します。
ただし `python-advanced` は実践・発展が中心なので、基本はミニプロジェクト構成を優先します。

## README の最低限の内容

* 何のサンプルか
* 対応するブログ記事
* 実行方法
* 主要ファイルの説明

## 記事からのリンク方針

記事本文では、長いコードを全部貼らずに次のように扱います。

* 本文には要点となる抜粋コードを載せる
* 完成版コードは GitHub リンクを案内する
* 可能なら「完成版はこちら」で終わらせず、本文で主要ロジックは説明する

## 運用フロー

1. `content/python-advanced` 側で記事を書く
2. 長いコードが必要なら、このリポジトリにサンプルを作る
3. サンプルをコミットして push する
4. 記事本文に GitHub リンクを入れる
5. 記事を投稿・更新する
