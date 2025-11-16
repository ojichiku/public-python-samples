# Password Generator CLI（PyInstallerサンプル）

このディレクトリは、パスワード生成ツールと PyInstaller を使った  **Pythonコード → EXE化** の最小構成サンプルです。  
コードはChatGPTで生成しており、Codexは使っていません。  
このサンプルでPython なしの環境でも実行できる形式を作るところまで確認できます。

---

## サンプル概要

- 数字・英大文字・英小文字・記号を指定可能  
- 文字数・生成数の指定に対応  
- `argparse` による CLI 実装  
- EXE化のための PyInstaller 使用例つき

コード本体：`password_gen.py`  
ブログ記事：（https://www.wanchiku.com/pyinstaller-chatgpt-password/）

---

## 環境構築

### A. uv を使う場合

```bash
uv venv
uv pip install pyinstaller
```

### B. pip + venv を使う場合

```bash
python -m venv .venv
# Linxuの場合
source .venv/bin/activate  
# Windowsの場合 
.venv\Scripts\activate
pip install pyinstaller
```

`.venv/` や `dist/`、`build/` は Git に含めません。

---

## パスワード生成ツールの実行

Python スクリプトとして動かす場合の実行方法です。

```bash
python password_gen.py -l 20 -k digits lower upper symbols -n 3
```

* `-l / --length` : パスワード長（上記例では 20 文字）
* `-k / --kinds`  : 使用する文字種

  * `digits`   : 数字
  * `lower`    : 英小文字
  * `upper`    : 英大文字
  * `symbols`  : 記号
* `-n / --count`  : 生成するパスワード個数（上記例では 3 個）

実行すると、例えば次のような出力が得られます（毎回変わります）。

```text
Gb}b@Edp0m?&_oSJD($W
#8z^=mw,f6OKi1jYMMOH
T3p:74ep0?3&^V!yLjoc
```
---

## PyInstaller で EXE を作る（最小手順）

### onedir（推奨：安定しやすい配布形式）

onedir形式は「EXE本体＋必要なDLLなどをまとめたフォルダ」を作る方式です。

```bash
pyinstaller --name passgen password_gen.py
```

実行後、以下のような構成になります。

```text
dist/
└─ passgen/
   ├─ passgen.exe
   └─ そのほかDLLや依存ファイル
```

実行するときは、`dist/passgen/` に移動して次のように実行します。

```bash
cd dist/passgen
passgen.exe -l 20 -k digits lower upper symbols -n 3
```

### onefile（単一ファイル、ただし誤検知が起きやすい）

onefile形式は、単一のEXEファイルにすべてをまとめる方式です。

```bash
pyinstaller --name passgen -F password_gen.py
```

実行後は、次のファイルが生成されます。

```text
dist/
└─ passgen.exe
```

実行方法は onedir のときと同じです。

```bash
cd dist
passgen.exe -l 20 -k digits lower upper symbols -n 3
```

---

## 配布時の最小ポイント

* onedir → フォルダごと ZIP にして配布
* onefile → 起動は遅め、誤検知に注意
* 可能であれば ZIP の SHA256 を併記しておくと安心

---

## まとめ

* `password_gen.py` は CLI として単体で動作
* PyInstaller により EXE を簡単に作成可能
* onedir が安定、onefile は軽量だが環境依存の差が出やすい
* 詳細手順と説明は次のブログ記事にて補足  
  https://www.wanchiku.com/pyinstaller-chatgpt-password/

