"""パスワード生成ロジック（GUI非依存）。

このモジュールは CLI 実装 `samples/password-generator-cli/password_gen.py` の生成処理を
できるだけそのまま移植し、GUI 側から使いやすい形（`generate_passwords`）で提供する。
"""

from __future__ import annotations

import secrets
import string

DEFAULT_SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/\\"
AMBIGUOUS_CHARS = set("0O1Il")


def build_pool(kinds, symbols):
    """指定した文字種から候補文字プールを構築する（CLI 実装相当）。

    Args:
        kinds: 使用する文字種のリスト（"digits", "lower", "upper", "symbols"）。
        symbols: 記号セット（重複は除去される）。

    Returns:
        文字種名 -> 候補文字列 の辞書。

    Raises:
        ValueError: 1種類も指定されていない場合。
    """
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
    """1つ分のパスワードを生成する（CLI 実装相当）。

    各文字種から最低1文字ずつ含むようにし、残りは全候補からランダムに選ぶ。
    最後に Fisher–Yates シャッフルで並びをランダム化する。

    Args:
        length: 生成するパスワード長。
        pools: 文字種名 -> 候補文字列 の辞書。

    Returns:
        生成されたパスワード文字列。

    Raises:
        ValueError: `length` が文字種数より短い場合。
    """
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


def _exclude_ambiguous(pools: dict[str, str]) -> dict[str, str]:
    """紛らわしい文字を候補から除外する。

    Args:
        pools: 文字種名 -> 候補文字列 の辞書。

    Returns:
        紛らわしい文字を除外した辞書。

    Raises:
        ValueError: 除外により候補文字が空になる場合。
    """
    filtered = {
        k: "".join(ch for ch in v if ch not in AMBIGUOUS_CHARS)
        for k, v in pools.items()
    }
    if not filtered:
        raise ValueError("少なくとも1種類を指定してください")
    if any(not v for v in filtered.values()):
        raise ValueError("候補文字が空です")
    if not "".join(filtered.values()):
        raise ValueError("候補文字が空です")
    return filtered


def generate_passwords(
    length: int,
    kinds: list[str],
    count: int,
    exclude_ambiguous: bool = False,
) -> list[str]:
    """指定条件でパスワードを複数生成する（GUI からの公開 API）。

    CLI 実装 `samples/password-generator-cli/password_gen.py` の生成処理を流用し、
    GUI から扱いやすいように引数を明確化したラッパー関数。

    Args:
        length: パスワード長。
        kinds: 使用する文字種（"digits", "lower", "upper", "symbols"）。
        count: 生成数。
        exclude_ambiguous: True の場合、紛らわしい文字（0 O 1 I l）を除外する。

    Returns:
        生成されたパスワードのリスト（各要素は 1 行分）。

    Raises:
        ValueError: 入力が不正な場合、または候補文字が空になる場合。
    """

    if not isinstance(length, int) or not isinstance(count, int):
        raise ValueError("length/count は int を指定してください")
    if length <= 0:
        raise ValueError("length は 1 以上を指定してください")
    if count <= 0:
        raise ValueError("count は 1 以上を指定してください")

    if not isinstance(kinds, list) or not kinds:
        raise ValueError("少なくとも1種類を指定してください")

    allowed = {"digits", "lower", "upper", "symbols"}
    if any(kind not in allowed for kind in kinds):
        raise ValueError("kinds が不正です")

    pools = build_pool(kinds, DEFAULT_SYMBOLS)
    if exclude_ambiguous:
        pools = _exclude_ambiguous(pools)

    return [generate_one(length, pools) for _ in range(count)]
