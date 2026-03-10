from __future__ import annotations

from pathlib import Path


class YtDownloadTool:
    def download(self, url: str, workspace: str = "data/workspace") -> str:
        workspace_path = Path(workspace)
        workspace_path.mkdir(parents=True, exist_ok=True)
        output_path = workspace_path / f"{abs(hash(url))}.mp4"
        output_path.touch(exist_ok=True)
        return str(output_path)
