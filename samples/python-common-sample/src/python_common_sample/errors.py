"""共通機能で利用する例外クラス群。"""

from __future__ import annotations

from typing import Any

__all__ = [
    "OcSampleError",
    "OcSampleUserError",
]


class OcSampleError(Exception):
    """共通機能が送出する致命的エラーを表す。"""

    def __init__(
        self,
        message: str,
        *details: Any,
        code: str | None = None,
        user_message: str | None = None,
        fatal: bool = True,
    ) -> None:
        super().__init__(message, *details)
        self.message = message
        self.code = code
        self.user_message = user_message
        self.fatal = fatal

    def to_dict(self) -> dict[str, Any]:
        """ログや通知向けに属性を辞書化する。"""

        payload: dict[str, Any] = {
            "message": self.message,
            "code": self.code,
            "user_message": self.user_message,
            "fatal": self.fatal,
        }
        return payload


class OcSampleUserError(OcSampleError):
    """ユーザの修正で解決できるエラーを表す。"""

    def __init__(
        self,
        message: str,
        *details: Any,
        code: str | None = None,
        user_message: str | None = None,
        fatal: bool = False,
    ) -> None:
        super().__init__(
            message,
            *details,
            code=code,
            user_message=user_message,
            fatal=fatal,
        )
