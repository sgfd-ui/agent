from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tool.vision_ffmpeg import VisionFFmpegTool

st.set_page_config(page_title="AutoVideoMiner 控制面板", layout="wide")
st.title("AutoVideoMiner 控制面板")
st.write("展示任务状态、日志流和 HITL 中断提示。")

st.subheader("依赖环境检查")
st.caption("当前使用依赖形式 FFmpeg（imageio-ffmpeg + ffmpeg-python），不再需要本地地址选择。")

if st.button("检查运行环境"):
    workspace = Path("data/workspace")
    db_path = Path("data/db/autovidminer.db")
    workspace.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        ffmpeg_tool = VisionFFmpegTool()
        st.success(f"FFmpeg 依赖可用: {ffmpeg_tool.version()}")
    except Exception as exc:  # pragma: no cover - GUI runtime guard
        st.error(f"FFmpeg 依赖不可用: {exc}")

    st.info(f"Workspace 目录: {workspace.resolve()}")
    st.info(f"SQLite 文件将使用: {db_path.resolve()}")
