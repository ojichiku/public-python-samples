"""generator モジュールのユニットテスト。

ランダム値そのものの一致は要求せず、出力仕様（長さ・文字集合・例外）を検証する。
"""

from __future__ import annotations

import string

import pytest

from password_gui import generator


class TestGeneratePasswords:
    """`generate_passwords()` の期待動作をまとめて検証する。

    - 入力バリデーション（不正値で ValueError）
    - 出力の形式（件数、長さ）
    - 文字種の制約（許可文字のみ、各文字種を最低1文字含む）
    - 紛らわしい文字除外の挙動
    """

    def test_kinds_empty_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            generator.generate_passwords(length=16, kinds=[], count=1)

    def test_kinds_invalid_value_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            generator.generate_passwords(
                length=16, kinds=["digits", "unknown"], count=1
            )

    @pytest.mark.parametrize("length,count", [(0, 1), (-1, 1), (16, 0), (16, -1)])
    def test_invalid_length_or_count_raises_value_error(
        self, length: int, count: int
    ) -> None:
        with pytest.raises(ValueError):
            generator.generate_passwords(length=length, kinds=["digits"], count=count)

    def test_too_short_length_for_selected_kinds_raises_value_error(self) -> None:
        # 4種類選ぶと各種類から最低1文字入れるため、length<4 はエラーになる
        with pytest.raises(ValueError):
            generator.generate_passwords(
                length=3,
                kinds=["digits", "lower", "upper", "symbols"],
                count=1,
            )

    @pytest.mark.parametrize("length,count", [(4, 1), (20, 3), (128, 50)])
    def test_returns_expected_count_and_length(self, length: int, count: int) -> None:
        passwords = generator.generate_passwords(
            length=length,
            kinds=["digits", "lower", "upper", "symbols"],
            count=count,
        )

        assert len(passwords) == count
        assert all(len(pw) == length for pw in passwords)

    def test_passwords_use_only_selected_kinds_and_include_each_kind(self) -> None:
        kinds = ["digits", "lower", "upper", "symbols"]
        passwords = generator.generate_passwords(length=32, kinds=kinds, count=10)

        symbols = "".join(dict.fromkeys(generator.DEFAULT_SYMBOLS))
        allowed = set(
            string.digits + string.ascii_lowercase + string.ascii_uppercase + symbols
        )
        digits = set(string.digits)
        lowers = set(string.ascii_lowercase)
        uppers = set(string.ascii_uppercase)
        sym_set = set(symbols)

        for pw in passwords:
            assert set(pw) <= allowed
            assert any(ch in digits for ch in pw)
            assert any(ch in lowers for ch in pw)
            assert any(ch in uppers for ch in pw)
            assert any(ch in sym_set for ch in pw)

    def test_exclude_ambiguous_never_outputs_ambiguous_chars(self) -> None:
        ambiguous = set("0O1Il")
        passwords = generator.generate_passwords(
            length=32,
            kinds=["digits", "lower", "upper", "symbols"],
            count=20,
            exclude_ambiguous=True,
        )

        for pw in passwords:
            assert not (set(pw) & ambiguous)

    def test_exclude_ambiguous_raises_when_pool_becomes_empty(self) -> None:
        with pytest.raises(ValueError):
            generator._exclude_ambiguous({"digits": "01"})
