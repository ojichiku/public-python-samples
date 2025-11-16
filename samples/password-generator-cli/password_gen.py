# password_gen.py
import argparse
import string
import secrets
import sys

DEFAULT_SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/\\"


def build_pool(kinds, symbols):
    pools = {}
    if "digits" in kinds:
        pools["digits"] = string.digits
    if "lower" in kinds:
        pools["lower"] = string.ascii_lowercase
    if "upper" in kinds:
        pools["upper"] = string.ascii_uppercase
    if "symbols" in kinds:
        pools["symbols"] = "".join(dict.fromkeys(symbols))
    if not pools:
        raise ValueError("少なくとも1種類を指定してください")
    return pools


def generate_one(length, pools):
    password_chars = [secrets.choice(chars) for chars in pools.values()]
    all_chars = "".join(pools.values())

    if length < len(password_chars):
        raise ValueError("長さが短すぎます")

    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(all_chars))

    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    return "".join(password_chars)


def main():
    parser = argparse.ArgumentParser(description="パスワード生成ツール")
    parser.add_argument("-l", "--length", type=int, default=16, help="パスワード長")
    parser.add_argument(
        "-k",
        "--kinds",
        nargs="+",
        choices=["digits", "lower", "upper", "symbols"],
        default=["digits", "lower", "upper", "symbols"],
        help="使用する文字種",
    )
    parser.add_argument("-n", "--count", type=int, default=1, help="生成数")
    parser.add_argument(
        "--symbols", type=str, default=DEFAULT_SYMBOLS, help="記号セット"
    )

    args = parser.parse_args()

    try:
        pools = build_pool(args.kinds, args.symbols)
        for _ in range(args.count):
            print(generate_one(args.length, pools))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
