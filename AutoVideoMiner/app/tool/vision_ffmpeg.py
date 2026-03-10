from __future__ import annotations

import subprocess
from pathlib import Path

import ffmpeg
import imageio_ffmpeg


class VisionFFmpegTool:
    """FFmpeg wrapper using python dependencies instead of manual local path config."""

    def __init__(self) -> None:
        self.ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

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
        """Split video into one placeholder segment via ffmpeg-python dependency pipeline."""
        source = Path(video_path)
        if not source.exists():
            raise FileNotFoundError(f"输入视频不存在: {video_path}")

        output = source.with_suffix(source.suffix + ".event_001.mp4")

        # Placeholder transcode operation to validate dependency-based ffmpeg invocation.
        (
            ffmpeg.input(str(source))
            .output(str(output), c="copy")
            .overwrite_output()
            .run(cmd=self.ffmpeg_bin, quiet=True)
        )

        del scene_threshold
        return [str(output)]
