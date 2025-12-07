"""設定ファイル読み込み機能のテスト。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from python_common_sample.config import load_config, load_config_as
from python_common_sample.errors import OcSampleError, OcSampleUserError


def _write(path: Path, content: str, binary: bool = False) -> None:
    """テスト用に一時ファイルへ書き込む。"""

    if binary:
        path.write_bytes(content.encode("utf-8"))
    else:
        path.write_text(content, encoding="utf-8")


@pytest.mark.parametrize(
    ("extension", "content", "expected"),
    [
        (
            ".yaml",
            "name: demo\nretries: 3\nenabled: true\n",
            {"name": "demo", "retries": 3, "enabled": True},
        ),
        (
            ".yml",
            "name: demo\nretries: 3\nenabled: true\n",
            {"name": "demo", "retries": 3, "enabled": True},
        ),
        (
            ".json",
            json.dumps({"name": "demo", "retries": 3, "enabled": True}),
            {"name": "demo", "retries": 3, "enabled": True},
        ),
        (
            ".toml",
            "name = 'demo'\nretries = 3\nenabled = true\n",
            {"name": "demo", "retries": 3, "enabled": True},
        ),
    ],
)
def test_load_config_supports_multiple_formats(tmp_path, extension, content, expected):
    # 対応拡張子であれば同一の dict として読み込めることを確認
    path = tmp_path / f"config{extension}"
    _write(path, content)

    assert load_config(path) == expected


def test_load_config_errors_on_missing_file(tmp_path):
    # ファイルが存在しない場合はユーザーエラーになる
    missing = tmp_path / "missing.yaml"

    with pytest.raises(OcSampleUserError) as excinfo:
        load_config(missing)

    assert "見つかりません" in str(excinfo.value)


def test_load_config_permission_error(monkeypatch, tmp_path):
    # Path.open が PermissionError を投げた際のラップを確認
    path = tmp_path / "config.yaml"
    _write(path, "name: demo")

    def fake_open(self, *_args, **_kwargs):  # noqa: ANN001
        raise PermissionError("denied")

    monkeypatch.setattr("python_common_sample.config.Path.open", fake_open)

    with pytest.raises(OcSampleUserError) as excinfo:
        load_config(path)

    assert "権限" in str(excinfo.value)


def test_load_config_invalid_format(tmp_path):
    # フォーマットエラーはユーザーエラーになる
    path = tmp_path / "broken.json"
    _write(path, '{"name": "demo",}')

    with pytest.raises(OcSampleUserError) as excinfo:
        load_config(path)

    assert "JSON" in str(excinfo.value)


def test_load_config_rejects_unsupported_extension(tmp_path):
    # 未対応拡張子は即座に拒否する
    path = tmp_path / "config.ini"
    _write(path, "[section]\nkey=value\n")

    with pytest.raises(OcSampleUserError) as excinfo:
        load_config(path)

    assert ".ini" in str(excinfo.value)


def test_load_config_as_validates_with_pydantic(tmp_path):
    # load_config_as で pydantic による型チェックを行う

    class AppSettings(BaseModel):
        name: str
        retries: int
        enabled: bool = True

    path = tmp_path / "config.yaml"
    _write(path, "name: demo\nretries: 2\nenabled: false\n")

    settings = load_config_as(path, AppSettings)
    assert isinstance(settings, AppSettings)
    assert settings.name == "demo"
    assert settings.retries == 2
    assert settings.enabled is False


def test_load_config_as_reports_validation_errors(tmp_path):
    # pydantic バリデーションの失敗はユーザーエラーになる

    class AppSettings(BaseModel):
        name: str
        retries: int

    path = tmp_path / "config.yaml"
    _write(path, "name: demo\nretries: invalid\n")

    with pytest.raises(OcSampleUserError):
        load_config_as(path, AppSettings)


def test_load_config_wraps_unexpected_errors(monkeypatch, tmp_path):
    # 想定外の例外は OcSampleError に昇格させる
    path = tmp_path / "config.json"
    _write(path, "{}")

    import python_common_sample.config as config_module

    def boom(_path):  # noqa: ANN001
        raise RuntimeError("boom")

    monkeypatch.setitem(config_module._PARSERS, ".json", boom)

    with pytest.raises(OcSampleError):
        config_module.load_config(path)
