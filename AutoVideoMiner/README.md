# AutoVideoMiner

A LangGraph-oriented multi-agent architecture skeleton for:

- PlannerAgent → keyword generation with history avoidance
- CrawlerAgent → dynamic DOM crawling with HITL fallback
- EvaluatorAgent → quality gate + search history persistence
- AnalyzerAgent → split/merge event video segments
- ExplorerAgent → event summary and category upsert

## Bedrock initialization

All model initialization is centralized in `app/llm.py`:

- `ChatBedrock`: `amazon.nova-lite-v1:0`
- `BedrockEmbeddings`: `amazon.titan-embed-text-v1`

Both share one `bedrock-runtime` boto3 client created by `init_bedrock()`.

## 本地运行准备（改为依赖形式 FFmpeg）

### 1) FFmpeg（通过 Python 依赖提供）

`AnalyzerAgent` 使用 `VisionFFmpegTool`，依赖以下包：

- `imageio-ffmpeg`（提供 FFmpeg 可执行文件）
- `ffmpeg-python`（Python 调用接口）

安装示例：

```bash
pip install imageio-ffmpeg ffmpeg-python
```

> 已取消 GUI 里的本地 FFmpeg 地址选择。

### 2) SQLite

- Python 标准库自带 `sqlite3` 模块。
- 项目会使用数据库文件：`data/db/autovidminer.db`。

### 3) GUI 检查

运行 Streamlit 后点击 **“检查运行环境”**：

- 检查 FFmpeg 依赖是否可用
- 自动创建 `data/workspace` 与 `data/db`

## 快速检查

```bash
python scripts/preflight_check.py
```

该脚本会检查：

- `imageio-ffmpeg` 是否可用
- `ffmpeg-python` 是否可用
- `sqlite3` 模块是否可用
- `data/workspace` 与 `data/db` 是否可写
