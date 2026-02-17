# InsightRadar — 全球创新与开源情报聚合系统

## ⚠️ 每次新开会话必做

1. **先读 `progress.md`** — 了解项目当前状态和进度
2. **再读 `TASKS.md`** — 了解待办任务、进行中的工作、以及优化方向

## ⚠️ 每次完成任务或有任何改动必做

完成任何任务、修复 bug、新增功能、修改代码后，**必须同步更新以下三个文件**：

1. **`TASKS.md`** — 更新任务状态（待办→进行中→已完成），添加新发现的待办，维护优化方案列表
2. **`progress.md`** — 更新进度百分比、模块状态、测试结果、里程碑完成情况、已知问题
3. **`CHANGELOG.md`** — 记录所有变更（新增/修改/修复/删除），附日期，格式参考 Keep a Changelog

**不要创建新文件**，除非任务明确要求。优先编辑现有文件。

---

## 项目概述
InsightRadar 从 GitHub、Hacker News、RSS 等多源采集数据，经清洗/分类/热度评估后，生成"全球创新日报"。

## 架构
- **Python 代码** (`src/`): 确定性 I/O 操作（API 调用、RSS 解析、SQLite 读写）
- **Claude Skills** (`.claude/skills/`): 需要语义理解的智能处理（去重、分类、报告生成）

## 数据流
```
GitHub API + HN API + RSS → Python collectors → SQLite (raw_items)
  → Skill: data-clean (去重) → Skill: data-classify (分类+热度)
  → Skill: report-gen → output/digests/{date}-digest.md
```

## 关键命令
- `python src/pipeline.py collect` — 采集数据
- `python src/pipeline.py collect --source github` — 仅采集 GitHub
- `python src/pipeline.py status` — 查看数据库状态
- `python src/pipeline.py export` — 导出数据为 JSON
- `python -m uvicorn src.server:app --host 127.0.0.1 --port 8000` — 启动 Web Dashboard
- `/insight-radar` — 全流程：采集 → 清洗 → 分类 → 报告

## 目录结构
- `src/config.py` — 配置（数据源 URL、权重）
- `src/models/schemas.py` — Pydantic 数据模型
- `src/collectors/` — 采集器（github, hackernews, rss）
- `src/storage/store.py` — SQLite 存储层
- `src/pipeline.py` — CLI 入口
- `src/server.py` — FastAPI Web Dashboard 后端
- `src/static/index.html` — Dashboard 前端（中英文双语）
- `data/` — 运行时数据（gitignore）
- `output/digests/` — 生成的日报

## 技术栈
Python 3.14 | httpx | feedparser | pydantic | python-dateutil | SQLite | FastAPI | uvicorn

## 项目追踪文件
- `TASKS.md` — 任务状态 + 优化方案（每次改动必更新）
- `progress.md` — 项目进度 + 里程碑 + 已知问题（每次改动必更新）
- `CHANGELOG.md` — 所有变更记录（每次改动必更新）

## 注意事项
- 所有采集器继承 `BaseCollector`，实现 `collect()` 方法
- 数据模型使用 Pydantic v2
- SQLite 数据库位于 `data/insight_radar.db`
- Skills 处理的数据通过 JSON 文件在 `data/processed/` 中传递
- 不要随意创建新文件，优先编辑现有文件
