from __future__ import annotations

from pathlib import Path

import pytest

import python_common_sample.yaml_store as yaml_store
from python_common_sample import (
    OcSampleError,
    OcSampleUserError,
    load_config,
    save_yaml,
)


def test_save_yaml_persists_simple_dict(tmp_path: Path) -> None:
    """単純な dict が保存され config.load_config で復元できるか。"""
    path = tmp_path / "settings.yaml"
    data = {"app": "demo", "enabled": True, "count": 3}
    save_yaml(path, data)

    loaded = load_config(path)
    assert loaded == data


def test_save_yaml_creates_parent_and_saves_nested(tmp_path: Path) -> None:
    """親ディレクトリの自動作成とネストしたデータ保存を確認。"""
    path = tmp_path / "config" / "nested" / "gui.yaml"
    nested = {
        "window": {"width": 1200, "height": 800},
        "recent": ["input", "output"],
    }
    save_yaml(path, nested)

    assert path.exists()
    assert (tmp_path / "config" / "nested").is_dir()
    assert load_config(path) == nested


def test_save_yaml_permission_error_raises_user_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """書き込み権限がない場合に OcSampleUserError となるか。"""
    target = tmp_path / "locked.yaml"
    original_open = Path.open

    def fake_open(self: Path, mode: str = "r", *args, **kwargs):
        if self == target and "w" in mode:
            raise PermissionError("denied")
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(yaml_store.Path, "open", fake_open, raising=False)

    with pytest.raises(OcSampleUserError):
        save_yaml(target, {"value": 1})


def test_save_yaml_with_unserializable_data_raises_error(tmp_path: Path) -> None:
    """YAML 化できないオブジェクトを含む場合に OcSampleError となるか。"""
    path = tmp_path / "invalid.yaml"
    data = {"object": object()}

    with pytest.raises(OcSampleError):
        save_yaml(path, data)


def test_save_yaml_os_error_is_wrapped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """OS 由来のエラー発生時に OcSampleError へラップされるか。"""
    target = tmp_path / "ioerror.yaml"
    original_open = Path.open

    def fake_open(self: Path, mode: str = "r", *args, **kwargs):
        if self == target and "w" in mode:
            raise OSError("disk full")
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(yaml_store.Path, "open", fake_open, raising=False)

    with pytest.raises(OcSampleError):
        save_yaml(target, {"value": 1})
