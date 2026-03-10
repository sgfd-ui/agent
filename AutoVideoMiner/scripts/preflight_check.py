from __future__ import annotations

import sqlite3
from pathlib import Path


def check_ffmpeg_dependency() -> tuple[bool, str]:
    try:
        import imageio_ffmpeg

        exe = imageio_ffmpeg.get_ffmpeg_exe()
        return True, f"imageio-ffmpeg ready (exe={exe})"
    except Exception as exc:
        return False, f"imageio-ffmpeg unavailable: {exc}"


def check_ffmpeg_python() -> tuple[bool, str]:
    try:
        import ffmpeg  # noqa: F401

        return True, "ffmpeg-python module ready"
    except Exception as exc:
        return False, f"ffmpeg-python unavailable: {exc}"


def check_sqlite() -> tuple[bool, str]:
    version = sqlite3.sqlite_version
    return True, f"sqlite3 module ready (version={version})"


def check_paths() -> tuple[bool, str]:
    workspace = Path("data/workspace")
    db = Path("data/db/autovidminer.db")
    workspace.mkdir(parents=True, exist_ok=True)
    db.parent.mkdir(parents=True, exist_ok=True)
    return True, f"workspace={workspace.resolve()} db={db.resolve()}"


def main() -> int:
    checks = [check_ffmpeg_dependency(), check_ffmpeg_python(), check_sqlite(), check_paths()]
    failed = False
    for ok, msg in checks:
        mark = "OK" if ok else "FAIL"
        print(f"[{mark}] {msg}")
        failed = failed or (not ok)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
