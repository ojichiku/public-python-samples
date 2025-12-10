"""YAML ファイルへの保存を行うユーティリティ。"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from .errors import OcSampleError, OcSampleUserError

__all__ = ["save_yaml"]


def save_yaml(path: str | Path, data: Mapping[str, Any]) -> None:
    """Mapping を YAML ファイルに保存する。

    Args:
        path: 保存先ファイルパス。
        data: YAML に変換する Mapping データ。

    Raises:
        OcSampleUserError: パスが書き込み不可などユーザ起因のエラー。
        OcSampleError: YAML 非対応データやその他の予期しないエラー。
    """

    if not isinstance(data, Mapping):
        msg = "YAML に保存できるのは Mapping 型のデータです。"
        raise OcSampleError(msg)

    dest = Path(path)
    parent = dest.parent
    if parent and not parent.exists():
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as exc:
            raise OcSampleUserError(
                f"保存先ディレクトリ '{parent}' を作成できません。",
                user_message="ディレクトリの書き込み権限を確認してください。",
            ) from exc
        except OSError as exc:
            raise OcSampleError(
                f"保存先ディレクトリ '{parent}' の作成中にエラーが発生しました。",
            ) from exc

    try:
        with dest.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(
                data,
                fh,
                sort_keys=False,
                allow_unicode=True,
            )
    except PermissionError as exc:
        raise OcSampleUserError(
            f"ファイル '{dest}' に書き込めません。",
            user_message="ファイルの書き込み権限やロック状態を確認してください。",
        ) from exc
    except yaml.YAMLError as exc:
        raise OcSampleError(
            "データを YAML として保存できません。",
        ) from exc
    except OSError as exc:
        raise OcSampleError(
            f"ファイル '{dest}' の書き込み中にエラーが発生しました。",
        ) from exc
