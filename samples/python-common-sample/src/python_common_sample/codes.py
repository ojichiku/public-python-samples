"""コード管理機能を提供するモジュール。"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

from .errors import OcSampleUserError

__all__ = [
    "CodeItem",
    "FileCodeSource",
    "get_codes",
    "get_value",
    "reload_codes",
]


@dataclass(slots=True)
class CodeItem:
    """コード1件分の情報。"""

    code_group: str
    code: str
    value: str
    sort_order: int
    enabled: bool = True
    extra: str | None = None


class CodeSource(Protocol):
    """コードを取得するソースのインターフェイス。"""

    def load_all(self) -> list[CodeItem]:
        """すべてのコードを読み込んで返す。"""


class FileCodeSource:
    """CSV ファイルからコードを読み込むソース実装。"""

    def __init__(self, path: str | Path | None = None) -> None:
        """ファイルパスを受け取りソースを初期化する。

        Args:
            path: CSV ファイルのパス。省略時は `config/codes.csv`。
        """

        if path is None:
            path = Path(__file__).resolve().parents[2] / "config" / "codes.csv"
        self.path = Path(path)

    def load_all(self) -> list[CodeItem]:
        """CSV を読み込み CodeItem の一覧を構築する。

        Returns:
            CSV から読み出した CodeItem のリスト。

        Raises:
            OcSampleUserError: CSV が存在しない、読めない、不正な場合。
        """

        if not self.path.exists():
            msg = f"コードファイル '{self.path}' が見つかりません。"
            raise OcSampleUserError(
                msg,
                user_message="codes.csv のパスと配置を確認してください。",
            )

        try:
            with self.path.open("r", encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                if reader.fieldnames is None:
                    raise OcSampleUserError(
                        "コードファイルにヘッダ行がありません。",
                        user_message="codes.csv の 1 行目にヘッダを記述してください。",
                    )
                self._validate_columns(reader.fieldnames)
                items = [self._to_item(row, reader.fieldnames) for row in reader]
        except OSError as exc:
            msg = f"コードファイル '{self.path}' を読み込めません: {exc}"
            raise OcSampleUserError(
                msg,
                user_message="codes.csv を読み取れる状態か確認してください。",
            ) from exc
        return items

    @staticmethod
    def _validate_columns(fieldnames: Sequence[str]) -> None:
        """CSV の必須カラムを検証する。"""

        required = {"code_group", "code", "value", "sort_order"}
        missing = required.difference(fieldnames)
        if missing:
            missing_list = ", ".join(sorted(missing))
            msg = f"コードファイルに必須カラムが不足しています: {missing_list}"
            raise OcSampleUserError(
                msg,
                user_message="code_group/code/value/sort_order の各列を定義してください。",
            )

    @staticmethod
    def _to_item(row: dict[str, str | None], fieldnames: Sequence[str]) -> CodeItem:
        """DictReader の1行を CodeItem に変換する。"""

        try:
            sort_order = int(row["sort_order"] or 0)
        except (TypeError, ValueError) as exc:
            msg = f"sort_order の値が不正です: {row.get('sort_order')!r}"
            raise OcSampleUserError(
                msg,
                user_message="sort_order には整数を指定してください。",
            ) from exc

        enabled_value = row.get("enabled") if "enabled" in fieldnames else None
        enabled = _parse_enabled(enabled_value)
        extra = row.get("extra") if "extra" in fieldnames else None
        extra = extra or None

        code_group = (row.get("code_group") or "").strip()
        code_value = (row.get("code") or "").strip()
        display_value = row.get("value") or ""
        if not code_group or not code_value or display_value == "":
            msg = f"必須項目が不足しています: {row!r}"
            raise OcSampleUserError(
                msg,
                user_message="code_group/code/value の各列に値を入力してください。",
            )

        return CodeItem(
            code_group=code_group,
            code=code_value,
            value=display_value,
            sort_order=sort_order,
            enabled=enabled,
            extra=extra,
        )


_source: CodeSource = FileCodeSource()
_cache: dict[str, list[CodeItem]] = {}
_loaded = False


def get_codes(code_group: str, *, only_enabled: bool = True) -> list[CodeItem]:
    """指定グループに属するコード一覧を取得する。

    Args:
        code_group: 取得対象のコードグループ。
        only_enabled: True の場合、enabled=False を除外する。

    Returns:
        sort_order 昇順で並んだ CodeItem のリスト（該当無しなら空リスト）。
    """

    _ensure_loaded()
    items = _cache.get(code_group, [])
    if only_enabled:
        return [item for item in items if item.enabled]
    return list(items)


def get_value(
    code_group: str,
    code: str,
    *,
    default: str | None = None,
    only_enabled: bool = True,
) -> str | None:
    """指定されたコードの value を取得する。

    Args:
        code_group: 対象のコードグループ。
        code: 取得したいコード値。
        default: 該当が無い場合に返すデフォルト値。
        only_enabled: True の場合、enabled=False のコードを除外する。

    Returns:
        見つかった value。該当なしは default（既定では None）。
    """

    codes = get_codes(code_group, only_enabled=only_enabled)
    for item in codes:
        if item.code == code:
            return item.value
    return default


def reload_codes() -> None:
    """コード情報を取得元から再読み込みする。"""

    global _cache, _loaded
    items = _source.load_all()
    grouped: dict[str, list[CodeItem]] = {}
    for item in items:
        grouped.setdefault(item.code_group, []).append(item)
    for values in grouped.values():
        values.sort(key=lambda item: item.sort_order)
    _cache = grouped
    _loaded = True


def _ensure_loaded() -> None:
    """キャッシュが初期化済みか確認し、必要なら読み込む。"""

    if not _loaded:
        reload_codes()


def _parse_enabled(value: str | None) -> bool:
    """CSV の enabled フィールドを bool に変換する。"""

    if value is None or value == "":
        return True

    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y"}:
        return True
    if normalized in {"0", "false", "f", "no", "n"}:
        return False
    return True
