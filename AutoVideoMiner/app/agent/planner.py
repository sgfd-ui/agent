from __future__ import annotations

from typing import Any


class PlannerAgent:
    """Generate platform-keyword tasks with history-aware negative terms."""

    def run(
        self,
        time_range: str,
        target_scene: str,
        md_memory: str,
        search_history: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        negative_hints = [item.get("keyword", "") for item in search_history if item.get("quality") == "bad"]
        negative_suffix = " ".join(f"-{word}" for word in negative_hints[:3] if word)
        base_keyword = f"{target_scene} {time_range}".strip()
        keyword = f"{base_keyword} {negative_suffix}".strip()
        return [
            {"platform": "bilibili", "keyword": keyword},
            {"platform": "youtube", "keyword": keyword},
        ]
