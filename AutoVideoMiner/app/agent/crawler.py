from __future__ import annotations

from typing import Any


class CrawlerAgent:
    """Platform crawler with micro ReAct-like retry loop."""

    def __init__(self, browser_tool: Any, ask_human_tool: Any, max_retry: int = 3) -> None:
        self.browser_tool = browser_tool
        self.ask_human_tool = ask_human_tool
        self.max_retry = max_retry

    def run(self, platform: str, keyword: str) -> list[dict[str, Any]]:
        for attempt in range(1, self.max_retry + 1):
            items = self.browser_tool.search(platform=platform, keyword=keyword)
            if items:
                return items
            if attempt == self.max_retry:
                self.ask_human_tool.request_help(f"{platform}:{keyword} 遇到验证码或死循环")
        return []
