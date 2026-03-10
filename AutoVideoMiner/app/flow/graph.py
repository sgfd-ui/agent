from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from math import sqrt
from typing import Any

from app.agent.analyzer import AnalyzerAgent
from app.agent.crawler import CrawlerAgent
from app.agent.evaluator import EvaluatorAgent
from app.agent.explorer import ExplorerAgent
from app.agent.planner import PlannerAgent
from app.flow.memory_manager import MemoryManager
from app.flow.state import GlobalState
from app.tool.ask_human import AskHumanTool
from app.tool.browser_use import BrowserTool
from app.tool.sqlite_db import SQLiteDBTool
from app.tool.vision_ffmpeg import VisionFFmpegTool
from app.tool.yt_download import YtDownloadTool


class LocalEmbeddings:
    def embed_query(self, text: str) -> list[float]:
        tokens = text.lower().split()
        return [float(len(tokens)), float(len(text)), float(sum(ord(c) for c in text) % 997)]


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


@dataclass
class GraphRuntime:
    planner: PlannerAgent
    crawler: CrawlerAgent
    evaluator: EvaluatorAgent
    analyzer: AnalyzerAgent
    explorer: ExplorerAgent
    sqlite_tool: SQLiteDBTool
    download_tool: YtDownloadTool
    memory_manager: MemoryManager
    state: GlobalState

    def log(self, message: str) -> None:
        self.state.setdefault("logs", []).append(message)
        self.state["token_estimate"] = int(self.state.get("token_estimate", 0)) + max(1, len(message) // 4)

    def get_state(self) -> GlobalState:
        return self.state

    def update_state(self, patch: dict[str, Any]) -> None:
        self.state.update(patch)


def _parse_hhmm(value: str) -> time:
    hh, mm = value.split(":", 1)
    return time(hour=int(hh), minute=int(mm))


def _check_time_node(state: GlobalState) -> bool:
    now = datetime.now().time()
    start_t = _parse_hhmm(str(state.get("start_time", "09:00")))
    end_t = _parse_hhmm(str(state.get("end_time", "18:00")))
    if now < start_t or now > end_t:
        return False
    return True


def _embedding_filter_node(scene_target: str, candidates: list[dict[str, Any]], threshold: float = 0.6) -> list[dict[str, Any]]:
    scene_tokens = set(scene_target.lower().split())
    filtered: list[dict[str, Any]] = []
    for item in candidates:
        title_tokens = set(str(item.get("title", "")).lower().split())
        if not scene_tokens:
            score = 0.0
        else:
            overlap = len(scene_tokens.intersection(title_tokens))
            score = overlap / max(1, len(scene_tokens))
        if score >= threshold:
            item["similarity"] = score
            filtered.append(item)
    return filtered


def build_graph(scene_target: str = "室外 监控", start_time: str = "09:00", end_time: str = "18:00") -> GraphRuntime:
    try:
        from app.llm import init_bedrock

        llm, embeddings = init_bedrock()
        del llm
    except Exception:
        embeddings = LocalEmbeddings()

    browser_tool = BrowserTool()
    ask_human_tool = AskHumanTool()
    sqlite_tool = SQLiteDBTool()
    try:
        vision_ffmpeg_tool = VisionFFmpegTool()
    except Exception:
        class _FallbackVisionTool:
            def segment(self, video_path: str, scene_threshold: float = 0.1) -> list[str]:
                del scene_threshold
                return [video_path]

        vision_ffmpeg_tool = _FallbackVisionTool()
    download_tool = YtDownloadTool()
    memory_manager = MemoryManager()

    planner_agent = PlannerAgent()
    crawler_agent = CrawlerAgent(browser_tool=browser_tool, ask_human_tool=ask_human_tool)
    evaluator_agent = EvaluatorAgent(sqlite_tool=sqlite_tool)
    analyzer_agent = AnalyzerAgent(vision_ffmpeg_tool=vision_ffmpeg_tool, ask_human_tool=ask_human_tool)
    explorer_agent = ExplorerAgent(sqlite_tool=sqlite_tool, embeddings=embeddings)

    state: GlobalState = {
        "messages": [],
        "logs": [],
        "next": "CheckTimeNode",
        "stop_requested": False,
        "ask_human_payload": None,
        "start_time": start_time,
        "end_time": end_time,
        "scene_target": scene_target,
        "task_queue": [],
        "search_history": [],
        "downloaded_video_paths": [],
        "clean_event_paths": [],
        "token_estimate": 0,
        "daily_video_count": sqlite_tool.get_daily_video_count(),
        "cycle_count": 0,
    }

    return GraphRuntime(
        planner=planner_agent,
        crawler=crawler_agent,
        evaluator=evaluator_agent,
        analyzer=analyzer_agent,
        explorer=explorer_agent,
        sqlite_tool=sqlite_tool,
        download_tool=download_tool,
        memory_manager=memory_manager,
        state=state,
    )


def _crawler_subgraph(runtime: GraphRuntime, task: dict[str, str]) -> list[str]:
    max_retry = 3
    retry_count = 0
    saved_paths: list[str] = []

    while retry_count < max_retry:
        runtime.log(f"CrawlerNode: platform={task['platform']} keyword={task['keyword']} retry={retry_count}")
        candidates = runtime.crawler.run(platform=task["platform"], keyword=task["keyword"])

        runtime.log("EmbeddingFilterNode: computing similarity threshold=0.6")
        filtered = _embedding_filter_node(str(runtime.state.get("scene_target", "")), candidates, threshold=0.6)
        if not filtered:
            retry_count += 1
            runtime.log("EmbeddingFilterNode: no candidate passed, retrying crawler")
            continue

        runtime.log("EvaluatorNode: visual quality check")
        verdict = runtime.evaluator.run(keyword=task["keyword"], candidates=filtered)
        if not verdict.get("passed", False):
            retry_count += 1
            suggestion = verdict.get("suggestion", "")
            runtime.log(f"EvaluatorNode rejected. suggestion={suggestion}")
            task["keyword"] = f"{task['keyword']} {suggestion}".strip()
            continue

        for item in filtered:
            url = str(item.get("url", ""))
            if not url or runtime.sqlite_tool.is_visited_url(url):
                continue
            runtime.sqlite_tool.mark_visited_url(url)
            path = runtime.download_tool.download(url)
            saved_paths.append(path)
            runtime.log(f"DownloadTool saved: {path}")
        break

    return saved_paths


def run_cycle(runtime: GraphRuntime) -> GlobalState:
    state = runtime.state
    state["cycle_count"] = int(state.get("cycle_count", 0)) + 1

    runtime.log("START -> CheckTimeNode")
    if state.get("stop_requested") or not _check_time_node(state):
        runtime.log("CheckTimeNode: overtime/stop detected -> END")
        runtime.memory_manager.save_shutdown_snapshot(state.get("logs", []))
        state["next"] = "END"
        return state

    state["next"] = "PlannerNode"
    runtime.log("CheckTimeNode passed -> PlannerNode")

    tasks = runtime.planner.run(
        time_range=f"{state.get('start_time')}~{state.get('end_time')}",
        target_scene=str(state.get("scene_target", "")),
        md_memory="",
        search_history=state.get("search_history", []),
    )
    state["task_queue"] = tasks
    runtime.log(f"PlannerNode produced {len(tasks)} tasks")

    # Map-Reduce fan-out/fan-in
    all_downloaded_paths: list[str] = []
    for task in tasks:
        all_downloaded_paths.extend(_crawler_subgraph(runtime, task))

    state["downloaded_video_paths"] = all_downloaded_paths
    runtime.log(f"Fan-in complete: downloaded={len(all_downloaded_paths)}")

    state["next"] = "AnalyzerNode"
    clean_segments: list[str] = []
    for path in all_downloaded_paths:
        try:
            clean_segments.extend(runtime.analyzer.run(video_path=path))
        except Exception as exc:
            state["ask_human_payload"] = {
                "reason": f"analyzer failed: {exc}",
                "images": [],
            }
            state["next"] = "ask_human"
            runtime.log(f"AnalyzerNode requires HITL: {exc}")
            return state

    state["clean_event_paths"] = clean_segments
    runtime.log(f"AnalyzerNode completed: segments={len(clean_segments)}")

    state["next"] = "ExplorerNode"
    for segment in clean_segments:
        runtime.explorer.run(event_video_path=segment, summary="单事件摘要")
    runtime.log("ExplorerNode completed and persisted")

    state["daily_video_count"] = runtime.sqlite_tool.get_daily_video_count()
    state["next"] = "CheckTimeNode"
    runtime.log("Loop back -> CheckTimeNode")
    return state


def run_once(runtime: GraphRuntime, target_scene: str, time_range: str, md_memory: str) -> dict[str, Any]:
    del md_memory
    if "~" in time_range:
        start, end = time_range.split("~", 1)
        runtime.update_state({"start_time": start.strip(), "end_time": end.strip()})
    runtime.update_state({"scene_target": target_scene})
    state = run_cycle(runtime)
    return {"task_queue": state.get("task_queue", []), "saved": state.get("clean_event_paths", [])}
