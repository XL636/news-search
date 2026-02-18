# InsightRadar

> 全球创新与开源情报聚合系统 — Global Innovation & Open Source Intelligence Aggregator

InsightRadar 从 GitHub、Hacker News、RSS 等多源采集科技新闻和开源项目动态，经清洗去重、领域分类、热度评估后，通过 AI 驱动的 Web Dashboard 提供智能搜索、文章解读和热点总结。

![Dashboard](dashboard-wide-v3.png)

## Features

- **多源数据采集** — GitHub Trending、Hacker News Top/Show、RSS (TechCrunch, Ars Technica, The Verge 等)
- **智能清洗去重** — 时间过滤、跨平台语义去重、冲突消解
- **11 领域分类** — AI/ML、DevTools、Security、Cloud、Web、Mobile、Hardware、Data、Blockchain、Biotech、Other
- **热度评估** — 0-100 综合热度指数（Stars、评论、时效性、跨平台出现）
- **AI 搜索** — 自然语言查询，GLM-4-Plus 流式回答 + 引用来源
- **文章 AI 解读** — 单篇文章深度分析（核心概述→技术亮点→行业影响→潜在风险→趋势延伸）
- **一键最新热点** — TOP 20 热门资讯 AI 总结
- **Web Dashboard** — Glass-morphism 暖色主题、中英文双语、响应式布局
- **Word 报告生成** — 按领域或关键词生成 .docx 格式情报报告

## Quick Start

### 1. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置（可选）

```bash
# GitHub Token (提升 API 速率限制 60 → 5000/h)
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_xxxx"

# ZhipuAI API Key (启用 AI 搜索/解读功能)
export ZHIPUAI_API_KEY="xxxx"
```

AI API Key 也可在 Dashboard 界面中直接配置。

### 3. 采集数据

```bash
python src/pipeline.py collect          # 全部源
python src/pipeline.py collect --source github  # 仅 GitHub
python src/pipeline.py status           # 查看数据库状态
```

### 4. 启动 Dashboard

```bash
python -m uvicorn src.server:app --host 127.0.0.1 --port 8000
```

访问 http://127.0.0.1:8000

## Architecture

```
GitHub API + HN API + RSS
        │
        ▼
  Python Collectors (src/collectors/)
        │
        ▼
  SQLite (raw_items → cleaned_items → classified_items)
        │
        ▼
  FastAPI Dashboard (src/server.py + src/static/index.html)
        │
        ├── AI 搜索 (POST /api/ai-search)
        ├── 文章解读 (POST /api/ai-analyze)
        ├── 最新热点 (POST /api/ai-latest)
        └── Word 报告 (.claude/skills/report-gen)
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Runtime | Python 3.14 |
| HTTP Client | httpx |
| RSS Parsing | feedparser |
| Data Models | Pydantic v2 |
| Database | SQLite |
| Web Framework | FastAPI + Uvicorn |
| Frontend | Tailwind CSS + Vanilla JS |
| AI Model | ZhipuAI GLM-4-Plus (streaming SSE) |
| Report | python-docx |

## Project Structure

```
src/
├── config.py              # 配置（数据源 URL、权重、AI 模型）
├── pipeline.py            # CLI 入口 (collect / status / export)
├── server.py              # FastAPI Web Dashboard 后端
├── mcp_server.py          # MCP Server (FastMCP)
├── models/
│   └── schemas.py         # Pydantic 数据模型
├── collectors/
│   ├── base.py            # BaseCollector 抽象基类
│   ├── github_trending.py # GitHub Search API 采集器
│   ├── hackernews.py      # HN Firebase API 采集器
│   └── rss_feeds.py       # RSS 聚合采集器
├── storage/
│   └── store.py           # SQLite 存储层
└── static/
    └── index.html         # Dashboard 前端（单文件 SPA）

.claude/skills/            # Claude Code Skills
├── data-collect/          # 采集编排
├── data-clean/            # 清洗去重
├── data-classify/         # 分类 + 热度评估
├── report-gen/            # Word 报告生成
├── insight-radar/         # 全流程一键编排
└── mcp-digest/            # MCP 日报生成
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/items` | 获取分类数据（支持领域过滤、搜索、排序、分页） |
| GET | `/api/domains` | 获取领域统计 |
| GET | `/api/stats` | 获取数据库统计 |
| POST | `/api/collect` | 触发数据采集 |
| POST | `/api/translate` | 文本翻译（带缓存） |
| GET/POST | `/api/ai-config` | AI API Key 查询/保存 |
| POST | `/api/ai-search` | AI 搜索（SSE 流式） |
| POST | `/api/ai-analyze` | 文章 AI 深度解读（SSE 流式） |
| POST | `/api/ai-latest` | 最新热点 AI 总结（SSE 流式） |

## License

MIT
