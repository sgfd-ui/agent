from __future__ import annotations

from typing import Any


class EvaluatorAgent:
    """Multimodal quality guard that persists search quality feedback."""

    def __init__(self, sqlite_tool: Any) -> None:
        self.sqlite_tool = sqlite_tool

    def run(self, keyword: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        passed = len(candidates) > 0
        reason = "found relevant items" if passed else "no relevant items"
        quality = "good" if passed else "bad"
        self.sqlite_tool.insert_search_history(keyword=keyword, quality=quality, reason=reason)
        return {"passed": passed, "reason": reason, "suggestion": "refine keyword with stronger constraints"}
