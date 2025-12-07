import pytest

import python_common_sample.messages as messages_module
from python_common_sample import OcSampleUserError, get_message


def test_get_message_without_placeholders() -> None:
    assert get_message("MSG_UNKNOWN_ERROR") == "予期しないエラーが発生しました。"


def test_get_message_with_placeholders() -> None:
    message = get_message("MSG_INVALID_PARAM", "port", "65536")
    assert message == "パラメータ port の値「65536」は不正です。"


def test_repeated_placeholder_is_filled_with_same_value() -> None:
    message = get_message("MSG_DUPLICATE_ARGS", "config.ini")
    assert message == "config.ini を config.ini にコピーしました。"


def test_placeholder_remains_when_argument_is_missing() -> None:
    message = get_message("MSG_INVALID_PARAM", "timeout")
    assert message == "パラメータ timeout の値「{1}」は不正です。"


def test_extra_arguments_are_ignored() -> None:
    message = get_message("MSG_CONFIG_NOT_FOUND", "app.yaml", "unused")
    assert message == "設定ファイル app.yaml が見つかりません。"


def test_invalid_placeholder_is_left_as_is() -> None:
    message = get_message("MSG_INVALID_PLACEHOLDER", "config.ini")
    assert message == "タグ {tag} は config.ini に存在しません。"


def test_unknown_message_id_returns_fallback() -> None:
    assert get_message("MSG_DOES_NOT_EXIST") == "[MSG_DOES_NOT_EXIST]"


def test_missing_locale_file_raises_user_error(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(messages_module, "_MESSAGES_DIR", tmp_path)
    monkeypatch.setattr(messages_module, "_CACHE", {}, raising=False)
    with pytest.raises(OcSampleUserError):
        messages_module.get_message("MSG_UNKNOWN_ERROR", locale="tmp")
