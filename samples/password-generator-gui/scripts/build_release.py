from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], *, cwd: Path) -> None:
    print(">>>", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=cwd)


def _find_dist_dir(dist_root: Path) -> Path:
    candidates = [p for p in dist_root.glob("*.dist") if p.is_dir()]
    if not candidates:
        raise SystemExit(f"[ERROR] distフォルダが見つかりません: {dist_root}")
    if len(candidates) > 1:
        names = ", ".join(p.name for p in candidates)
        raise SystemExit(f"[ERROR] distフォルダが複数あります: {names}")
    return candidates[0]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Nuitka onedirビルドと配布用ZIP作成を行います。",
    )
    parser.add_argument(
        "--app-name",
        default="PasswordGeneratorGUI",
        help="アプリ名（既定: PasswordGeneratorGUI）",
    )
    parser.add_argument(
        "--exe-name",
        default="passgen-gui.exe",
        help="生成する実行ファイル名（既定: passgen-gui.exe）",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Nuitkaビルドをスキップする",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="出力先が存在する場合に削除して作り直す",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    entry = repo_root / "src" / "password_gui"
    ui_file = repo_root / "src" / "resources" / "ui" / "main_window.ui"
    dist_root = repo_root / "dist"
    output_root = repo_root / "release"
    release_dir = output_root / args.app_name
    app_dir = release_dir / "app"

    if not entry.exists():
        raise SystemExit(f"[ERROR] エントリポイントが見つかりません: {entry}")
    if not ui_file.exists():
        raise SystemExit(f"[ERROR] main_window.ui が見つかりません: {ui_file}")

    if release_dir.exists():
        if args.clean:
            shutil.rmtree(release_dir)
        else:
            raise SystemExit(f"[ERROR] 出力先が既に存在します: {release_dir}")

    output_root.mkdir(parents=True, exist_ok=True)
    release_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_build:
        cmd = [
            sys.executable,
            "-m",
            "nuitka",
            "--standalone",
            "--enable-plugin=pyside6",
            "--python-flag=-m",
            f"--output-dir={dist_root}",
            f"--output-filename={args.exe_name}",
            f"--include-data-file={ui_file}=src/resources/ui/main_window.ui",
            str(entry),
        ]
        _run(cmd, cwd=repo_root)

    dist_dir = _find_dist_dir(dist_root)
    shutil.copytree(dist_dir, app_dir)

    readme_src = output_root / "README.txt"
    if not readme_src.exists():
        raise SystemExit(f"[ERROR] README.txtがありません: {readme_src}")
    shutil.copy2(readme_src, release_dir / "README.txt")

    license_file = output_root / "LICENSE"
    if not license_file.exists():
        raise SystemExit(f"[ERROR] LICENSEがありません: {license_file}")
    shutil.copy2(license_file, release_dir / "LICENSE")

    zip_base = output_root / args.app_name
    zip_path = zip_base.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    shutil.make_archive(
        str(zip_base),
        "zip",
        root_dir=output_root,
        base_dir=args.app_name,
    )
    print(f"[OK] ZIP作成: {zip_path}")
    print(f"[OK] リリース出力: {release_dir}")


if __name__ == "__main__":
    main()
