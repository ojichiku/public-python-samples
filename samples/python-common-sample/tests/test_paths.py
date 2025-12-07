from __future__ import annotations

import sys
from pathlib import Path

import python_common_sample.paths as paths


def test_to_path_and_resolve_path(tmp_path: Path) -> None:
    """str/Path を正しく Path に変換し絶対パスへ解決できるか。"""

    file_path = tmp_path / "data.txt"
    file_path.write_text("hi", encoding="utf-8")
    assert paths.to_path(str(file_path)) == file_path
    assert paths.resolve_path(file_path) == file_path


def test_get_cwd_returns_path_object() -> None:
    """現在のカレントディレクトリが Path で返却されるか。"""

    assert isinstance(paths.get_cwd(), Path)


def test_get_app_dir_frozen(monkeypatch) -> None:
    """EXE 実行扱い（sys.frozen）時に実行ファイルの親を返すか。"""

    fake_exe = Path("/tmp/fake/app.exe")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(fake_exe))
    assert paths.get_app_dir() == fake_exe.resolve().parent


def test_get_app_dir_main_module(monkeypatch, tmp_path: Path) -> None:
    """__main__.__file__ がある場合にその親ディレクトリを返すか。"""

    script = tmp_path / "app.py"
    script.write_text("print('hi')", encoding="utf-8")
    module = type(sys)("dummy")
    module.__file__ = str(script)
    monkeypatch.setitem(sys.modules, "__main__", module)
    assert paths.get_app_dir() == script.parent


def test_get_user_home_dir_matches_path_home() -> None:
    """ホームディレクトリ取得が Path.home と一致するか。"""

    assert paths.get_user_home_dir() == Path.home()


def test_get_temp_dir_creates_subdir() -> None:
    """サブディレクトリ指定で一時ディレクトリ配下に作成されるか。"""

    base = Path(paths.tempfile.gettempdir())
    subdir = paths.get_temp_dir("logs")
    assert subdir.exists()
    assert subdir.parent == base


def test_create_temp_file_and_delete() -> None:
    """一時ファイル作成と delete フラグの挙動を確認する。"""

    path = paths.create_temp_file(delete=False)
    assert path.exists()
    path.unlink()
    path2 = paths.create_temp_file(delete=True)
    assert not path2.exists()


def test_temporary_directory_cleans_up() -> None:
    """コンテキスト終了時に一時ディレクトリが削除されるか。"""

    with paths.temporary_directory(prefix="paths-test-") as temp_dir:
        created = temp_dir / "file.txt"
        created.write_text("tmp", encoding="utf-8")
        assert created.exists()
    assert not temp_dir.exists()


def test_exists_and_type_checks(tmp_path: Path) -> None:
    """存在判定・ファイル/ディレクトリ判定の結果を確認する。"""

    file_path = tmp_path / "file.txt"
    file_path.write_text("data", encoding="utf-8")
    dir_path = tmp_path / "folder"
    dir_path.mkdir()
    assert paths.exists(file_path)
    assert paths.is_file(file_path)
    assert paths.is_dir(dir_path)


def test_list_files_and_dirs(tmp_path: Path) -> None:
    """glob オプションと再帰指定で期待通り列挙できるか。"""

    (tmp_path / "a.txt").write_text("", encoding="utf-8")
    (tmp_path / "b.log").write_text("", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.txt").write_text("", encoding="utf-8")
    assert [p.name for p in paths.list_files(tmp_path, "*.txt")] == ["a.txt"]
    assert [p.name for p in paths.list_files(tmp_path, "*.txt", recursive=True)] == [
        "a.txt",
        "c.txt",
    ]
    assert [p.name for p in paths.list_dirs(tmp_path)] == ["sub"]


def test_safe_filename_and_suffix_utils() -> None:
    """ファイル名ユーティリティ各種の出力を検証する。"""

    unsafe = 'inva<>:"/\\|?*lid'
    assert paths.safe_filename(unsafe) == "invalid"
    assert paths.safe_filename("", max_length=10) == "untitled"
    assert paths.add_suffix_before_extension("report.csv", "_backup") == Path(
        "report_backup.csv"
    )
    assert paths.add_suffix_before_extension("README", "_v2") == Path("README_v2")
    assert paths.change_extension("archive.tar.gz", ".zip") == Path("archive.tar.zip")
    assert paths.change_extension("notes", "md") == Path("notes.md")
    assert paths.change_extension("file.txt", "") == Path("file")
