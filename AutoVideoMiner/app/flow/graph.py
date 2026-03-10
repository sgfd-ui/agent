from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.agent.analyzer import AnalyzerAgent
from app.agent.crawler import CrawlerAgent
from app.agent.evaluator import EvaluatorAgent
from app.agent.explorer import ExplorerAgent
from app.agent.planner import PlannerAgent
from app.llm import init_bedrock
from app.tool.ask_human import AskHumanTool
from app.tool.browser_use import BrowserTool
from app.tool.sqlite_db import SQLiteDBTool
from app.tool.vision_ffmpeg import VisionFFmpegTool


@dataclass
class GraphRuntime:
    planner: PlannerAgent
    crawler: CrawlerAgent
    evaluator: EvaluatorAgent
    analyzer: AnalyzerAgent
    explorer: ExplorerAgent



def build_graph() -> GraphRuntime:
    llm, embeddings = init_bedrock()
    del llm

    browser_tool = BrowserTool()
    ask_human_tool = AskHumanTool()
    sqlite_tool = SQLiteDBTool()
    vision_ffmpeg_tool = VisionFFmpegTool()

    planner_agent = PlannerAgent()
    crawler_agent = CrawlerAgent(browser_tool=browser_tool, ask_human_tool=ask_human_tool)
    evaluator_agent = EvaluatorAgent(sqlite_tool=sqlite_tool)
    analyzer_agent = AnalyzerAgent(vision_ffmpeg_tool=vision_ffmpeg_tool, ask_human_tool=ask_human_tool)
    explorer_agent = ExplorerAgent(sqlite_tool=sqlite_tool, embeddings=embeddings)

    return GraphRuntime(
        planner=planner_agent,
        crawler=crawler_agent,
        evaluator=evaluator_agent,
        analyzer=analyzer_agent,
        explorer=explorer_agent,
    )


def run_once(runtime: GraphRuntime, target_scene: str, time_range: str, md_memory: str) -> dict[str, Any]:
    search_history: list[dict[str, Any]] = []
    task_queue = runtime.planner.run(
        time_range=time_range,
        target_scene=target_scene,
        md_memory=md_memory,
        search_history=search_history,
    )

    accepted_paths: list[str] = []
    for task in task_queue:
        candidates = runtime.crawler.run(platform=task["platform"], keyword=task["keyword"])
        verdict = runtime.evaluator.run(keyword=task["keyword"], candidates=candidates)
        if verdict["passed"]:
            accepted_paths.append("data/workspace/mock_download.mp4")

    cleaned_segments: list[str] = []
    for path in accepted_paths:
        cleaned_segments.extend(runtime.analyzer.run(video_path=path))

    outputs = []
    for segment in cleaned_segments:
        outputs.append(runtime.explorer.run(event_video_path=segment, summary="单事件摘要"))

    return {"task_queue": task_queue, "saved": outputs}
