from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class SQLiteDBTool:
    def __init__(self, db_path: str = "data/db/autovidminer.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT,
                    quality TEXT,
                    reason TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS event_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary TEXT,
                    weight INTEGER DEFAULT 1
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT,
                    category_id INTEGER
                )
                """
            )

    def insert_search_history(self, keyword: str, quality: str, reason: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO search_history (keyword, quality, reason) VALUES (?, ?, ?)",
                (keyword, quality, reason),
            )

    def upsert_event_category(self, summary: str, vector: list[float], threshold: float) -> dict[str, Any]:
        del vector, threshold
        with self._connect() as conn:
            row = conn.execute("SELECT id, summary, weight FROM event_categories LIMIT 1").fetchone()
            if row:
                category_id, _, weight = row
                conn.execute(
                    "UPDATE event_categories SET summary = ?, weight = ? WHERE id = ?",
                    (summary, weight + 1, category_id),
                )
                return {"id": category_id, "summary": summary}
            cursor = conn.execute("INSERT INTO event_categories (summary) VALUES (?)", (summary,))
            return {"id": cursor.lastrowid, "summary": summary}

    def insert_video(self, path: str, category_id: int) -> int:
        with self._connect() as conn:
            cursor = conn.execute("INSERT INTO videos (path, category_id) VALUES (?, ?)", (path, category_id))
            return int(cursor.lastrowid)
