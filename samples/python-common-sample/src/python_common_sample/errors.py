"""共通機能で利用する例外クラス群。"""

from __future__ import annotations

from typing import Any

__all__ = [
    "OcSampleError",
    "OcSampleUserError",
    "ValidationError",
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
        """エラーのメタデータを保持しやすいよう属性を初期化する。

        Args:
            message: 例外のメインメッセージ。
            *details: 任意の追加情報（Exception 継承元に渡す）。
            code: エラーを識別するコード。
            user_message: ユーザ向けのメッセージ。
            fatal: 致命的かどうかのフラグ。
        """

        super().__init__(message, *details)
        self.message = message
        self.code = code
        self.user_message = user_message
        self.fatal = fatal

    def to_dict(self) -> dict[str, Any]:
        """ログや通知向けに属性を辞書化する。

        Returns:
            message/code/user_message/fatal を含む辞書。
        """

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
        """ユーザ向けエラーの属性を初期化する。

        Args:
            message: 例外のメインメッセージ。
            *details: 任意の追加情報。
            code: エラーコード。
            user_message: ユーザ向けメッセージ。
            fatal: 原則 False（必要なら True にもできる）。
        """

        super().__init__(
            message,
            *details,
            code=code,
            user_message=user_message,
            fatal=fatal,
        )


class ValidationError(OcSampleUserError):
    """入力値や設定内容の検証に失敗した際に使用する例外。"""

    def __init__(
        self,
        message: str,
        *,
        detail: str | None = None,
        code: str | None = None,
    ) -> None:
        """検証失敗時の情報を保持する。

        Args:
            message: ユーザー向けメッセージ。
            detail: ログなどで参照する詳細情報。
            code: エラーコード。
        """

        super().__init__(message, code=code, user_message=message, fatal=False)
        self.detail = detail
