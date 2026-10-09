"""Reproducible Windows build and artifact verification."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "src" / "backend"
FRONTEND = ROOT / "src" / "frontend"
BUILD = ROOT / ".build"
DIST = ROOT / "dist"
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
NPM = "npm.cmd" if os.name == "nt" else "npm"


def run(args: list[str], cwd: Path = ROOT) -> None:
    print(f"> {' '.join(map(str, args))}")
    subprocess.run([str(item) for item in args], cwd=cwd, check=True)


def ensure_tools() -> Path:
    python = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)
    run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(BACKEND / "requirements.txt")])
    run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "pyinstaller==6.19.0"])
    run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "pillow==12.1.1"])
    return python


def build_backend(python: Path) -> Path:
    destination = BUILD / "backend"
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    run(
        [
            str(python), "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile",
            "--name", "backend", "--distpath", str(destination),
            "--workpath", str(BUILD / "pyinstaller-backend"),
            "--specpath", str(BUILD / "spec"),
            str(BACKEND / "main.py"),
        ],
        cwd=BACKEND,
    )
    artifact = destination / "backend.exe"
    if not artifact.is_file() or artifact.stat().st_size < 1_000_000:
        raise RuntimeError("后端打包产物异常")
    return artifact


def prepare_ffmpeg_runtime() -> list[Path]:
    """Bundle the exact FFmpeg runtime used by the verified build machine."""
    destination = BUILD / "ffmpeg"
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    copied: list[Path] = []
    for name in ("ffmpeg", "ffprobe"):
        source_value = shutil.which(name)
        if not source_value:
            raise RuntimeError(f"找不到 {name}，无法生成可独立运行的客户安装包")
        source = Path(source_value).resolve()
        target = destination / source.name
        shutil.copy2(source, target)
        copied.append(target)
    distribution_root = Path(shutil.which("ffmpeg")).resolve().parent.parent
    license_file = distribution_root / "LICENSE"
    if not license_file.is_file():
        raise RuntimeError("FFmpeg 发行包缺少 LICENSE，停止构建以避免不合规分发")
    shutil.copy2(license_file, destination / "LICENSE-FFMPEG.txt")
    (destination / "SOURCE-AND-NOTICE.txt").write_text(
        "FFmpeg runtime selected from the local PATH. Verify its specific build and license.\n"
        "FFmpeg project source and license: https://ffmpeg.org/legal.html\n"
        "This program invokes FFmpeg and ffprobe as separate executables.\n"
        "See LICENSE-FFMPEG.txt for the license of the selected runtime.\n",
        encoding="utf-8",
    )
    return copied


def build_renderer() -> None:
    run([NPM, "ci", "--no-audit", "--no-fund"], cwd=FRONTEND)
    run([NPM, "run", "build"], cwd=FRONTEND)
    if not (FRONTEND / "dist" / "index.html").is_file():
        raise RuntimeError("前端构建产物缺失")


def build_desktop() -> list[Path]:
    run([NPM, "ci", "--no-audit", "--no-fund"], cwd=ROOT)
    run([NPM, "run", "dist"], cwd=ROOT)
    installers = sorted(DIST.glob("*安装程序.exe"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not installers:
        raise RuntimeError("未生成 NSIS 安装程序")
    return installers


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-desktop", action="store_true")
    args = parser.parse_args()
    python = ensure_tools()
    run([str(python), str(ROOT / "scripts" / "generate_assets.py")])
    prepare_ffmpeg_runtime()
    artifacts = [build_backend(python)]
    build_renderer()
    if not args.skip_desktop:
        artifacts.extend(build_desktop())
    print("\n构建完成：")
    for artifact in artifacts:
        print(f"- {artifact} ({artifact.stat().st_size:,} bytes) SHA256={sha256(artifact)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

