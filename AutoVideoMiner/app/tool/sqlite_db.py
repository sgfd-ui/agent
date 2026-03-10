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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS visited_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE
                )
                """
            )

    def insert_search_history(self, keyword: str, quality: str, reason: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO search_history (keyword, quality, reason) VALUES (?, ?, ?)",
                (keyword, quality, reason),
            )

    def is_visited_url(self, url: str) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT 1 FROM visited_urls WHERE url = ? LIMIT 1", (url,)).fetchone()
            return row is not None

    def mark_visited_url(self, url: str) -> None:
        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO visited_urls (url) VALUES (?)", (url,))

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
            return {"id": int(cursor.lastrowid), "summary": summary}

    def insert_video(self, path: str, category_id: int) -> int:
        with self._connect() as conn:
            cursor = conn.execute("INSERT INTO videos (path, category_id) VALUES (?, ?)", (path, category_id))
            return int(cursor.lastrowid)

    def get_daily_video_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM videos").fetchone()
            return int(row[0]) if row else 0

    def get_event_category_ranking(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT summary, weight FROM event_categories ORDER BY weight DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [{"summary": str(r[0]), "weight": int(r[1])} for r in rows]
