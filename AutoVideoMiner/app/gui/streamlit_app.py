from __future__ import annotations

import threading
import time
from datetime import time as dtime, timedelta
from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.flow.graph import build_graph, run_cycle


def _ensure_runtime() -> None:
    if "graph_runtime" not in st.session_state:
        st.session_state.graph_runtime = build_graph()
    if "poller_started" not in st.session_state:
        st.session_state.poller_started = False
    if "latest_graph_state" not in st.session_state:
        st.session_state.latest_graph_state = st.session_state.graph_runtime.get_state().copy()


def _start_state_poller() -> None:
    if st.session_state.poller_started:
        return

    runtime = st.session_state.graph_runtime

    def _poll() -> None:
        while True:
            st.session_state.latest_graph_state = runtime.get_state().copy()
            time.sleep(1.0)

    thread = threading.Thread(target=_poll, daemon=True)
    thread.start()
    st.session_state.poller_started = True


st.set_page_config(page_title="AutoVideoMiner 控制面板", layout="wide")
_ensure_runtime()
_start_state_poller()
runtime = st.session_state.graph_runtime

# Left sidebar controls
st.sidebar.header("控制台")
scene_target = st.sidebar.text_input("场景目标", value=str(runtime.get_state().get("scene_target", "室外 监控")))
start_end = st.sidebar.slider(
    "定时窗口",
    min_value=dtime(0, 0),
    max_value=dtime(23, 59),
    value=(dtime(9, 0), dtime(18, 0)),
    step=timedelta(minutes=30),
)

if st.sidebar.button("一键启动"):
    runtime.update_state(
        {
            "scene_target": scene_target,
            "start_time": start_end[0].strftime("%H:%M"),
            "end_time": start_end[1].strftime("%H:%M"),
            "stop_requested": False,
            "next": "CheckTimeNode",
        }
    )
    run_cycle(runtime)

if st.sidebar.button("优雅停机 (Graceful Stop)"):
    runtime.update_state({"stop_requested": True})
    run_cycle(runtime)

# Main dashboard
st.title("AutoVideoMiner 监控大盘")
state = runtime.get_state()

c1, c2 = st.columns(2)
c1.metric("当日收集视频数", int(state.get("daily_video_count", 0)))
c2.metric("Token 消耗预估", int(state.get("token_estimate", 0)))

st.subheader("热门事件排行")
ranking = runtime.sqlite_tool.get_event_category_ranking(limit=10)
if ranking:
    chart_data = {row["summary"]: row["weight"] for row in ranking}
    st.bar_chart(chart_data)
else:
    st.info("暂无事件分类数据。")

st.subheader("终端日志流")
log_lines = state.get("logs", [])
st.code("\n".join(log_lines[-80:]) if log_lines else "(暂无日志)", language="text")

# HITL modal-like panel
if state.get("next") == "ask_human":
    payload = state.get("ask_human_payload") or {}
    st.error("HITL 接管中：检测到 ask_human 状态")
    st.write(f"原因: {payload.get('reason', 'unknown')}")
    if payload.get("images"):
        for img in payload["images"]:
            st.image(img)
    correction = st.text_area("请输入纠正指令")
    if st.button("提交并恢复流转"):
        runtime.update_state({"ask_human_payload": None, "next": "AnalyzerNode"})
        runtime.log(f"HITL instruction: {correction}")
        run_cycle(runtime)
