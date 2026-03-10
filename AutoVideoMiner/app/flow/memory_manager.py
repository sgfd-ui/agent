from __future__ import annotations

from pathlib import Path
from typing import Any


class MemoryManager:
    """Three-layer memory manager.

    1) Short-term: keep only latest N turns in in-memory state.
    2) Mid-term: compress evicted logs and append to markdown snapshot.
    3) Long-term: handled by SQLite tools.
    """

    def __init__(self, md_summary_path: str = "data/logs/task_summary.md", window_size: int = 10) -> None:
        self.window_size = window_size
        self.md_summary_path = Path(md_summary_path)
        self.md_summary_path.parent.mkdir(parents=True, exist_ok=True)
        self.md_summary_path.touch(exist_ok=True)

    def trim_messages(self, messages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        if len(messages) <= self.window_size:
            return messages, []
        keep = messages[-self.window_size :]
        evicted = messages[: -self.window_size]
        return keep, evicted

    def append_mid_memory(self, compressed_summary: str) -> None:
        with self.md_summary_path.open("a", encoding="utf-8") as f:
            f.write(f"\n- {compressed_summary}\n")
