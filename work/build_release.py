from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], *, cwd: Path) -> None:
    # 外部コマンドを表示して実行する。
    print(">>>", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=cwd)


def _find_dist_dir(dist_root: Path) -> Path:
    # Nuitkaのonedir出力は単一の*.distディレクトリになる。
    candidates = [p for p in dist_root.glob("*.dist") if p.is_dir()]
    if not candidates:
        raise SystemExit(f"[ERROR] distフォルダが見つかりません: {dist_root}")
    if len(candidates) > 1:
        names = ", ".join(p.name for p in candidates)
        raise SystemExit(f"[ERROR] distフォルダが複数あります: {names}")
    return candidates[0]


def _copy_dir(src: Path, dst: Path) -> None:
    # 既存ディレクトリをコピーし、無ければ即エラーにする。
    if not src.exists():
        raise SystemExit(f"[ERROR] 必要なフォルダが見つかりません: {src}")
    shutil.copytree(src, dst)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Nuitka onedirビルドと販売用ZIP作成を行います。",
    )
    parser.add_argument(
        "--app-name",
        default="ImageUpscale",
        help="アプリ名（既定: ImageUpscale）",
    )
    parser.add_argument(
        "--exe-name",
        default="image-upscale.exe",
        help="生成する実行ファイル名（既定: image-upscale.exe）",
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

    # 作業ルートと出力先を確定する。
    repo_root = Path(__file__).resolve().parents[1]
    entry = repo_root / "src" / "image_upscale" / "cli.py"
    dist_root = repo_root / "dist"
    output_root = repo_root / "release"
    release_dir = output_root / args.app_name
    app_dir = release_dir / "app"

    if release_dir.exists():
        if args.clean:
            shutil.rmtree(release_dir)
        else:
            raise SystemExit(f"[ERROR] 出力先が既に存在します: {release_dir}")

    output_root.mkdir(parents=True, exist_ok=True)
    release_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_build:
        # Nuitkaでonedirビルドを行う。
        cmd = [
            sys.executable,
            "-m",
            "nuitka",
            "--standalone",
            "--include-data-file=src/image_upscale/logging.ini=image_upscale/logging.ini",
            f"--output-dir={dist_root}",
            f"--output-filename={args.exe_name}",
            str(entry),
        ]
        _run(cmd, cwd=repo_root)

    # Nuitka出力をリリースフォルダに配置する。
    dist_dir = _find_dist_dir(dist_root)
    shutil.copytree(dist_dir, app_dir)

    # 既定の入出力フォルダを作成する。
    (release_dir / "input").mkdir(parents=True, exist_ok=True)
    (release_dir / "output").mkdir(parents=True, exist_ok=True)
    (release_dir / "log").mkdir(parents=True, exist_ok=True)

    # Real-ESRGAN は同梱しないため空の resources を用意する。
    (release_dir / "resources" / "models").mkdir(parents=True, exist_ok=True)

    run_bat = output_root / "run.bat"
    if not run_bat.exists():
        raise SystemExit(f"[ERROR] run.batがありません: {run_bat}")
    shutil.copy2(run_bat, release_dir / "run.bat")
    licenses_dir = output_root / "LICENSES"
    if licenses_dir.exists():
        _copy_dir(licenses_dir, release_dir / "LICENSES")
    readme_src = output_root / "README.txt"
    if readme_src.exists():
        shutil.copy2(readme_src, release_dir / "README.txt")

    # リリースフォルダをZIP化する。
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
    print(f"[OK] ZIP作成: {zip_base.with_suffix('.zip')}")

    print(f"[OK] リリース出力: {release_dir}")


if __name__ == "__main__":
    main()
