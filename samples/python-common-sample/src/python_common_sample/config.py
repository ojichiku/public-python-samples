"""設定ファイル読み込み機能を提供するモジュール。"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any, Callable

import yaml
from pydantic import BaseModel, ValidationError

from .errors import OcSampleError, OcSampleUserError

__all__ = [
    "load_config",
    "load_config_as",
]

ConfigDict = dict[str, Any]
_Parser = Callable[[Path], ConfigDict]


def load_config(path: str | Path) -> ConfigDict:
    """設定ファイルを読み込み dict として返す。

    Args:
        path: 読み込む設定ファイルのパス。

    Returns:
        設定内容の辞書。

    Raises:
        OcSampleUserError: ファイルが存在しない、読み込めない、拡張子が不正など。
        OcSampleError: 予期しない例外が発生した場合。
    """

    file_path = Path(path)
    if not file_path.exists():
        raise OcSampleUserError(
            f"設定ファイル '{file_path}' が見つかりません。",
            user_message="設定ファイルのパスを確認してください。",
        )
    if not file_path.is_file():
        raise OcSampleUserError(
            f"設定ファイル '{file_path}' はファイルではありません。",
            user_message="設定ファイルのパスを確認してください。",
        )

    suffix = file_path.suffix.lower()
    parser = _PARSERS.get(suffix)
    if parser is None:
        raise OcSampleUserError(
            f"設定ファイル '{file_path}' の拡張子 '{suffix}' には対応していません。",
            user_message="yaml/json/toml のいずれかを指定してください。",
        )

    try:
        return parser(file_path)
    except OcSampleUserError:
        raise
    except PermissionError as exc:
        raise OcSampleUserError(
            f"設定ファイル '{file_path}' を読み込む権限がありません。",
            user_message="設定ファイルの権限を確認してください。",
        ) from exc
    except OSError as exc:
        raise OcSampleUserError(
            f"設定ファイル '{file_path}' を読み込めません: {exc}",
            user_message="設定ファイルを読み取れる状態か確認してください。",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise OcSampleError(
            f"設定ファイル '{file_path}' の読み込み中に予期しないエラーが発生しました。",
            fatal=True,
        ) from exc


def load_config_as(path: str | Path, model: type[BaseModel]) -> BaseModel:
    """設定ファイルを読み込み、指定された pydantic モデルで検証して返す。

    Args:
        path: 読み込む設定ファイルのパス。
        model: バリデーション先の pydantic モデルクラス。

    Returns:
        検証済みのモデルインスタンス。

    Raises:
        OcSampleUserError: 設定内容がモデルのスキーマと一致しない場合。
    """

    data = load_config(path)
    try:
        return model(**data)
    except ValidationError as exc:
        raise OcSampleUserError(
            f"設定ファイル '{path}' の内容がモデル '{model.__name__}' と一致しません。",
            user_message="設定ファイルの構造や型を確認してください。",
        ) from exc


def _ensure_mapping(data: Any, path: Path) -> ConfigDict:
    """トップレベルが dict であることを保証する。

    Args:
        data: ファイルから読み取ったオブジェクト。
        path: 読み込み対象ファイルのパス。

    Returns:
        dict 型に正規化したデータ。

    Raises:
        OcSampleUserError: トップレベルが dict でない場合。
    """

    if not isinstance(data, dict):
        raise OcSampleUserError(
            f"設定ファイル '{path}' の内容はオブジェクト形式（dict）である必要があります。",
            user_message="設定ファイルのルート要素をオブジェクトにしてください。",
        )
    return data


def _load_yaml(path: Path) -> ConfigDict:
    """YAML ファイルを読み込む。

    Args:
        path: YAML ファイルのパス。

    Returns:
        読み込んだ内容の dict。

    Raises:
        OcSampleUserError: YAML の構文が不正な場合。
    """

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise OcSampleUserError(
            f"設定ファイル '{path}' の YAML 形式が不正です: {exc}",
            user_message="設定ファイルの内容を確認してください。",
        ) from exc
    return _ensure_mapping(data, path)


def _load_json(path: Path) -> ConfigDict:
    """JSON ファイルを読み込む。

    Args:
        path: JSON ファイルのパス。

    Returns:
        読み込んだ内容の dict。

    Raises:
        OcSampleUserError: JSON の構文が不正な場合。
    """

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise OcSampleUserError(
            f"設定ファイル '{path}' の JSON 形式が不正です: {exc}",
            user_message="設定ファイルの内容を確認してください。",
        ) from exc
    return _ensure_mapping(data, path)


def _load_toml(path: Path) -> ConfigDict:
    """TOML ファイルを読み込む。

    Args:
        path: TOML ファイルのパス。

    Returns:
        読み込んだ内容の dict。

    Raises:
        OcSampleUserError: TOML の構文が不正な場合。
    """

    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise OcSampleUserError(
            f"設定ファイル '{path}' の TOML 形式が不正です: {exc}",
            user_message="設定ファイルの内容を確認してください。",
        ) from exc
    return _ensure_mapping(data, path)


_PARSERS: dict[str, _Parser] = {
    ".yaml": _load_yaml,
    ".yml": _load_yaml,
    ".json": _load_json,
    ".toml": _load_toml,
}
