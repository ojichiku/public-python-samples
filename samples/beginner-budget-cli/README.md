# beginner-budget-cli

Python beginner向けの基本サンプルです。1か月の予算と支出を入力すると、残額と使いすぎ判定を表示します。

このサンプルで触れられる内容:

- `input()` による入力
- `split()` と `for` を使った繰り返し
- `int` への変換
- 関数分割
- `if` / `elif` / `else` による条件分岐

## 実行方法

```bash
cd samples/beginner-budget-cli
python -m beginner_budget_cli
```

## テスト

このサンプルではpytestを使用します。

```bash
uv run pytest
```

## 入力例

```text
1か月の予算を入力してください: 30000
支出をカンマ区切りで入力してください (例: 1200,850,3000): 1200,850,3000
```

## 出力例

```text
家計レポート
支出件数: 3
合計支出: 5050円
残額: 24950円
判定: 余裕あり
```
