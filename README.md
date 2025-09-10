# public-python-samples

ブログや学習用に公開する **Python サンプル集** です。  
各サンプルは最小構成・最小依存を心がけ、README と実行手順を同梱します。

## 収録ポリシー
- 小さく動くこと、再現性（requirements 最小化）を優先
- データや生成物は基本的にリポジトリに含めない（必要なら取得手順を記載）
- 外部の著作物・商標・個人情報を含めない

## ディレクトリ構成（例）
```

samples/
image/
resize\_basic/
main.py
requirements.txt
README.md
csv/
merge\_and\_clean/
main.py
requirements.txt
README.md
algo/
diff\_calc/
main.py
README.md
```

## 使い方（共通手順）
各サンプルのフォルダに移動して実行します。仮想環境は任意です。
```bash
# 任意：仮想環境を作る場合
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac/WSL:
. .venv/bin/activate

# 依存があれば
pip install -r requirements.txt

# 実行
python main.py
````

## 開発メモ

* 依存がある場合は **そのサンプル直下**に `requirements.txt` を置く
* データは `data/`（空ディレクトリは `.gitkeep`）を用意し、取得方法を README に記載
* 生成物は `outputs/` を推奨し、Git 管理対象外（.gitignore 参照）

## ライセンス

MIT License © 2025 Ojichiku

````
