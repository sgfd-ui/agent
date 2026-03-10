from __future__ import annotations

from typing import Any


class BrowserTool:
    def search(self, platform: str, keyword: str) -> list[dict[str, Any]]:
        # Stub implementation for integration tests.
        return [
            {
                "title": f"{platform}::{keyword}",
                "url": "https://example.com/video",
                "duration": "01:00",
                "cover_base64": "",
            }
        ]
