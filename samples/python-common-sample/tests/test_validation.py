from __future__ import annotations

import pytest

from python_common_sample import (
    AppModel,
    ValidationError,
    validate_model,
)


class SampleConfig(AppModel):
    name: str
    count: int = 0


def test_validate_model_success() -> None:
    """必須項目とデフォルト値が正しく適用されるか。"""

    model = validate_model(SampleConfig, {"name": "test"})
    assert model.name == "test"
    assert model.count == 0


def test_validate_model_missing_field() -> None:
    """必須項目欠落時に ValidationError となるか。"""

    with pytest.raises(ValidationError) as excinfo:
        validate_model(SampleConfig, {"count": 1})
    assert "設定の検証に失敗しました" in str(excinfo.value)
    assert excinfo.value.detail is not None
    assert "name" in excinfo.value.detail


def test_validate_model_type_error() -> None:
    """型不正時に detail にフィールド名が含まれるか。"""

    with pytest.raises(ValidationError) as excinfo:
        validate_model(SampleConfig, {"name": "test", "count": "abc"})
    assert "count" in (excinfo.value.detail or "")


def test_validate_model_extra_field() -> None:
    """余分なフィールドでエラーになるか。"""

    with pytest.raises(ValidationError) as excinfo:
        validate_model(SampleConfig, {"name": "test", "extra": 1})
    assert "extra" in (excinfo.value.detail or "")


def test_format_pydantic_errors_outputs_lines() -> None:
    """format_pydantic_errors が行単位の文字列を返すか。"""

    with pytest.raises(ValidationError) as excinfo:
        validate_model(SampleConfig, {"count": "abc"})
    detail = excinfo.value.detail
    assert detail is not None
    lines = detail.splitlines()
    assert any("name" in line or "count" in line for line in lines)
