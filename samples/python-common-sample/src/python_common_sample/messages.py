"""メッセージカタログを読み込んで提供するモジュール。"""

from __future__ import annotations

import configparser
import re
from pathlib import Path
from typing import Any

from .errors import OcSampleUserError

__all__ = [
    "get_message",
]

_SECTION = "messages"
_MESSAGES_DIR = Path(__file__).resolve().parents[2] / "config"
_CACHE: dict[str, dict[str, str]] = {}
_PLACEHOLDER_PATTERN = re.compile(r"\{(\d+)\}")


def get_message(msg_id: str, *args: Any, locale: str = "ja") -> str:
    """メッセージ本文を取得し、`{n}` プレースホルダーを置換する。

    Args:
        msg_id: INI ファイルに定義されたメッセージ ID。
        *args: `{0}`, `{1}` ... に対応する位置指定引数。
        locale: 利用する `messages_<locale>.ini` のロケール。

    Returns:
        フォーマット済みの文字列。ID が存在しない場合は `"[{msg_id}]"` を返す。
    """

    template = _load_locale(locale).get(msg_id)
    if template is None:
        return f"[{msg_id}]"
    return _fill_placeholders(template, args)


def _load_locale(locale: str) -> dict[str, str]:
    """ロケール別のメッセージ定義を読み込み、キャッシュする。

    Args:
        locale: `messages_<locale>.ini` に対応するロケール。

    Returns:
        該当ロケールのメッセージ ID とテンプレートの dict。

    Raises:
        OcSampleUserError: ファイルが存在しない、不正といったユーザ起因のエラー。
    """

    if locale in _CACHE:
        return _CACHE[locale]

    config_path = _MESSAGES_DIR / f"messages_{locale}.ini"
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str  # preserve message IDs as-is
    read_files = parser.read(config_path, encoding="utf-8")
    if not read_files:
        msg = f"メッセージファイル '{config_path}' を読み込めません。"
        raise OcSampleUserError(
            msg,
            user_message=f"{config_path.name} を配置し、アクセスできることを確認してください。",
        )
    if _SECTION not in parser:
        msg = f"メッセージファイル '{config_path}' にセクション '{_SECTION}' がありません。"
        raise OcSampleUserError(
            msg,
            user_message="[messages] セクションを追加してください。",
        )

    messages = dict(parser[_SECTION])
    _CACHE[locale] = messages
    return messages


def _fill_placeholders(template: str, args: tuple[Any, ...]) -> str:
    """テンプレート内の `{n}` プレースホルダーを位置引数で置換する。

    Args:
        template: `{0}`, `{1}` ... を含むテンプレート文字列。
        args: インデックスに応じて埋め込む値のタプル。

    Returns:
        置換済みの文字列。
    """

    def replace(match: re.Match[str]) -> str:
        index = int(match.group(1))
        if index < len(args):
            return str(args[index])
        return match.group(0)

    return _PLACEHOLDER_PATTERN.sub(replace, template)
