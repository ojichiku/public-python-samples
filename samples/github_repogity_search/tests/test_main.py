import csv
import importlib
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from playwright.sync_api import Error as PlaywrightError

app = importlib.import_module("github_repository_search.main")


def test_csv_bom_and_round_trip(tmp_path):
    row = dict(zip(app.HEADERS, ["owner/repo", '日本語,説明\n"引用"', "https://github.com/owner/repo", "", "1234"]))
    path = tmp_path / "output.csv"
    app.save_csv([row], path)
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    with path.open(encoding="utf-8-sig", newline="") as file:
        assert list(csv.DictReader(file)) == [row]


def test_empty_csv_has_header(tmp_path):
    path = tmp_path / "empty.csv"
    app.save_csv([], path)
    assert path.read_text(encoding="utf-8-sig").splitlines() == [",".join(app.HEADERS)]


def test_save_error_is_japanese(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "open", MagicMock(side_effect=PermissionError))
    with pytest.raises(app.SearchError, match="CSVを保存できません"):
        app.save_csv([], tmp_path / "output.csv")


def test_blank_does_not_launch(monkeypatch, capsys):
    runner = MagicMock()
    monkeypatch.setattr("builtins.input", lambda _: "  ")
    monkeypatch.setattr(app, "run", runner)
    assert app.main() == 1
    runner.assert_not_called()
    assert "検索キーワードが空" in capsys.readouterr().err


def test_eof(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", MagicMock(side_effect=EOFError))
    assert app.main() == 130
    assert "中止" in capsys.readouterr().err


def test_missing_edge(monkeypatch):
    factory = MagicMock()
    monkeypatch.setattr(app, "sync_playwright", factory)
    factory.return_value.__enter__.return_value.chromium.launch.side_effect = PlaywrightError("missing")
    with pytest.raises(app.SearchError, match="Microsoft Edgeを起動できません"):
        app.run("python")


@pytest.mark.parametrize("target", ["search_repositories", "save_csv"])
def test_browser_closes_on_failure(monkeypatch, target):
    factory = MagicMock()
    monkeypatch.setattr(app, "sync_playwright", factory)
    browser = factory.return_value.__enter__.return_value.chromium.launch.return_value
    monkeypatch.setattr(app, "search_repositories", MagicMock(return_value=[]))
    monkeypatch.setattr(app, target, MagicMock(side_effect=app.SearchError("テストエラー")))
    with pytest.raises(app.SearchError, match="テストエラー"):
        app.run("python")
    browser.close.assert_called_once()


def test_access_error():
    page = MagicMock()
    page.goto.side_effect = PlaywrightError("network error")
    with pytest.raises(app.SearchError, match="GitHubにアクセスできません"):
        app.search_repositories(page, "python")


def test_input_missing():
    page = MagicMock()
    page.goto.return_value.status = 200
    page.get_by_role.return_value.fill.side_effect = PlaywrightError("missing")
    with pytest.raises(app.SearchError, match="検索入力欄"):
        app.search_repositories(page, "python")


def test_random_operation_delay(monkeypatch, capsys):
    uniform = MagicMock(return_value=2.25)
    sleeper = MagicMock()
    monkeypatch.setattr(app.random, "uniform", uniform)
    monkeypatch.setattr(app.time, "sleep", sleeper)
    app.pause_between_operations()
    uniform.assert_called_once_with(1.0, 3.0)
    sleeper.assert_called_once_with(2.25)
    assert "待機します" in capsys.readouterr().out
