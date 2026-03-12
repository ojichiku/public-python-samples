# beginner-score-cli

Python beginner向けの基本サンプルです。テストの点数を入力すると、平均点・最高点・最低点・評価を表示します。

このサンプルで触れられる内容:

- `input()` を使った入力
- `split()` と `for` を使った繰り返し処理
- 関数の分割
- `if` / `elif` / `else` の条件分岐
- 例外処理による入力チェック

## 実行方法

```bash
cd samples/beginner-score-cli
python -m beginner_score_cli
```

## 入力例

```text
名前を入力してください: Aki
点数をカンマ区切りで入力してください (例: 80,75,92): 80,75,92
```

## 出力例

```text
Akiさんの結果
科目数: 3
平均点: 82.3
最高点: 92
最低点: 75
評価: B
```
