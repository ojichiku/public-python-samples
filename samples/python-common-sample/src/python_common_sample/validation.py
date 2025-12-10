"""pydantic を使った入力検証ユーティリティ。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic import ValidationError as PydanticValidationError

from .errors import ValidationError

__all__ = [
    "AppModel",
    "format_pydantic_errors",
    "validate_model",
]

T = TypeVar("T", bound="AppModel")


class AppModel(BaseModel):
    """アプリケーション内で利用する pydantic モデルの基底クラス。"""

    model_config = ConfigDict(extra="forbid")


def format_pydantic_errors(exc: PydanticValidationError) -> str:
    """pydantic の ValidationError を読みやすい文字列に変換する。

    Args:
        exc: pydantic の ValidationError。

    Returns:
        各エラーを行単位で連結した文字列。
    """

    messages: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", ()))
        message = error.get("msg", "")
        if location:
            messages.append(f"{location}: {message}")
        else:
            messages.append(message)
    return "\n".join(messages)


def validate_model(model_cls: type[T], data: Mapping[str, Any]) -> T:
    """AppModel サブクラスを使ってデータを検証する。

    Args:
        model_cls: AppModel を継承したモデルクラス。
        data: 検証対象のマッピング。

    Returns:
        検証済みモデルのインスタンス。

    Raises:
        ValidationError: 検証に失敗した場合。
    """

    try:
        return model_cls(**data)
    except PydanticValidationError as exc:
        detail = format_pydantic_errors(exc)
        raise ValidationError(
            "設定の検証に失敗しました。項目を確認してください。",
            detail=detail,
        ) from exc
