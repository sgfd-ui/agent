from __future__ import annotations

from typing import Any


class ExplorerAgent:
    """Summarize events and merge/split categories in SQLite assets."""

    def __init__(self, sqlite_tool: Any, embeddings: Any) -> None:
        self.sqlite_tool = sqlite_tool
        self.embeddings = embeddings

    def run(self, event_video_path: str, summary: str) -> dict[str, Any]:
        vector = self.embeddings.embed_query(summary)
        category = self.sqlite_tool.upsert_event_category(summary=summary, vector=vector, threshold=0.85)
        video_id = self.sqlite_tool.insert_video(path=event_video_path, category_id=category["id"])
        return {"video_id": video_id, "category_id": category["id"]}
