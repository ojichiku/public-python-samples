"""Python初心者向けに整理した合計計算のサンプル。"""


def main() -> None:
    # 商品の金額をリストにまとめます。
    prices = [120, 300, 180]

    # 合計金額を入れるための変数を用意します。
    total = 0

    # リストから金額を1つずつ取り出して、合計に足していきます。
    for price in prices:
        total += price

    # 計算した合計金額を表示します。
    print(total)


if __name__ == "__main__":
    main()
