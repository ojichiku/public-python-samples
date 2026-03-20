from python_advanced_template.main import build_message


def test_build_message() -> None:
    assert build_message() == "python-advanced sample template"
