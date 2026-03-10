from __future__ import annotations


class YtDownloadTool:
    def download(self, url: str) -> str:
        return f"data/workspace/{abs(hash(url))}.mp4"
