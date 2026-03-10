from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class VisionFFmpegTool:
    """FFmpeg wrapper using python dependencies instead of manual local path config."""

    def __init__(self) -> None:
        self.ffmpeg, self.ffmpeg_bin = self._load_deps()

    @staticmethod
    def _load_deps() -> tuple[Any, str]:
        try:
            import ffmpeg
        except ModuleNotFoundError as exc:
            raise RuntimeError("missing dependency: ffmpeg-python") from exc
        try:
            import imageio_ffmpeg
        except ModuleNotFoundError as exc:
            raise RuntimeError("missing dependency: imageio-ffmpeg") from exc
        return ffmpeg, imageio_ffmpeg.get_ffmpeg_exe()

    def is_available(self) -> bool:
        return bool(self.ffmpeg_bin)

    def version(self) -> str:
        result = subprocess.run(
            [self.ffmpeg_bin, "-version"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.splitlines()[0] if result.stdout else "unknown"

    def segment(self, video_path: str, scene_threshold: float = 0.1) -> list[str]:
        source = Path(video_path)
        if not source.exists():
            raise FileNotFoundError(f"输入视频不存在: {video_path}")

        output = source.with_suffix(source.suffix + ".event_001.mp4")
        (
            self.ffmpeg.input(str(source))
            .output(str(output), c="copy")
            .overwrite_output()
            .run(cmd=self.ffmpeg_bin, quiet=True)
        )

        del scene_threshold
        return [str(output)]
