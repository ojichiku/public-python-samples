"""共通エラーハンドラの単体テスト。"""

from python_common_sample.errors import OcSampleError, OcSampleUserError


def test_oc_sample_error_basic_attributes():
    # OcSampleError のデフォルト属性が仕様通りであることを確認
    err = OcSampleError("broken config")

    assert isinstance(err, Exception)
    assert err.message == "broken config"
    assert err.code is None
    assert err.user_message is None
    assert err.fatal is True
    assert err.args[0] == "broken config"


def test_oc_sample_error_optional_metadata():
    # 任意メタデータと to_dict() の出力を検証
    err = OcSampleError(
        "file I/O failed",
        code="IO_ERROR",
        user_message="Cannot open file.",
        fatal=False,
    )

    assert err.code == "IO_ERROR"
    assert err.user_message == "Cannot open file."
    assert err.fatal is False
    assert err.to_dict() == {
        "message": "file I/O failed",
        "code": "IO_ERROR",
        "user_message": "Cannot open file.",
        "fatal": False,
    }


def test_oc_sample_user_error_defaults_to_non_fatal():
    # ユーザーエラーは非致命扱いになることを確認
    err = OcSampleUserError("invalid range", code="RANGE_ERROR")

    assert isinstance(err, OcSampleError)
    assert err.fatal is False
    assert err.code == "RANGE_ERROR"


def test_oc_sample_user_error_allows_overriding_fatal_flag():
    # fatal 引数で挙動を上書きできることを確認
    err = OcSampleUserError("misconfigured profile", fatal=True)

    assert err.fatal is True
