# AutoVideoMiner

LangGraph-style multi-agent skeleton for automated event mining.

## Core topology

`START -> CheckTimeNode`

- 超时/停机：优雅流转到 `END`，并将最近日志写入 `data/logs/task_summary.md` 快照。
- 未超时：进入 `PlannerNode`。

Map-Reduce 扇出：

- `PlannerNode` 输出任务列表（platform + keyword）。
- 每个任务进入 `CrawlerSubGraph`：
  - `CrawlerNode`（网页抓取）
  - `EmbeddingFilterNode`（相似度阈值 0.6）
  - `EvaluatorNode`（图文复检）
  - 失败且 `retry_count < 3`：带建议回到 `CrawlerNode` 重试
  - 成功：`DownloadTool` 落盘，路径汇总到 `GlobalState`

扇入后串联：

- `AnalyzerNode` 切分
- `ExplorerNode` 入库
- 回到 `CheckTimeNode` 继续循环

## GUI 交互规范

### 左侧边栏

- 输入：场景目标（例如：`室外 监控`）
- 输入：定时窗口滑块（09:00 - 18:00）
- 操作：`一键启动` / `优雅停机 (Graceful Stop)`

### 右侧主区域

- Top 卡片：当日收集视频数、Token 消耗预估
- 数据大屏：`event_categories` 热门事件排行柱状图
- 终端日志流：展示 Agent 过程日志

### HITL 接管

- 后台线程轮询 `graph.get_state()`
- 若捕获 `next == "ask_human"`，显示接管面板
- 人类输入指令后调用 `graph.update_state()` 恢复流转

## Bedrock initialization

Centralized in `app/llm.py`:

- `ChatBedrock`: `amazon.nova-lite-v1:0`
- `BedrockEmbeddings`: `amazon.titan-embed-text-v1`

## Dependencies

```bash
pip install -r requirements.txt
```

## Quick check

```bash
python scripts/preflight_check.py
```
