from __future__ import annotations

from typing import Any, TypedDict


class SubGraphState(TypedDict, total=False):
    platform: str
    keyword: str
    retry_count: int
    crawler_results: list[dict[str, Any]]
    filtered_results: list[dict[str, Any]]
    evaluation: dict[str, Any]


class GlobalState(TypedDict, total=False):
    messages: list[dict[str, Any]]
    logs: list[str]
    next: str
    stop_requested: bool
    ask_human_payload: dict[str, Any] | None
    current_time: str
    start_time: str
    end_time: str
    scene_target: str
    task_queue: list[dict[str, str]]
    search_history: list[dict[str, Any]]
    downloaded_video_paths: list[str]
    clean_event_paths: list[str]
    token_estimate: int
    daily_video_count: int
    cycle_count: int
