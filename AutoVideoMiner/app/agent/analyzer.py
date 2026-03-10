from __future__ import annotations

from typing import Any


class AnalyzerAgent:
    """Video segmentation controller for split-merge workflow."""

    def __init__(self, vision_ffmpeg_tool: Any, ask_human_tool: Any) -> None:
        self.vision_ffmpeg_tool = vision_ffmpeg_tool
        self.ask_human_tool = ask_human_tool

    def run(self, video_path: str) -> list[str]:
        segments = self.vision_ffmpeg_tool.segment(video_path=video_path, scene_threshold=0.1)
        if not segments:
            self.ask_human_tool.request_help(f"无法切分: {video_path}")
            return []
        return segments
