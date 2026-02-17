# Changelog

本文件记录 InsightRadar 项目的所有变更。格式参考 [Keep a Changelog](https://keepachangelog.com/)。

---

## [0.1.0] - 2026-02-17

### Added
- 项目初始化：目录结构、CLAUDE.md、.gitignore、requirements.txt
- 数据模型 `src/models/schemas.py`：RawItem, CleanedItem, ClassifiedItem, DailyDigest
- SQLite 存储层 `src/storage/store.py`：三表 CRUD + 统计接口
- 配置文件 `src/config.py`：数据源 URL、权重参数、域分类
- GitHub 采集器 `src/collectors/github_trending.py`：Search API 获取高 star 仓库
- Hacker News 采集器 `src/collectors/hackernews.py`：Firebase API 获取 top + show stories
- RSS 采集器 `src/collectors/rss_feeds.py`：feedparser 聚合 4 个 RSS 源（TechCrunch、Ars Technica、The Verge、HN Best）
- 采集器基类 `src/collectors/base.py`：BaseCollector 抽象接口
- Pipeline CLI `src/pipeline.py`：collect / status / export 三个命令
- Skill: `data-collect` — 采集编排
- Skill: `data-clean` — 清洗去重（Claude 驱动）
- Skill: `data-classify` — 分类标签 + 热度评估（Claude 驱动）
- Skill: `report-gen` — 日报 Markdown 生成（Claude 驱动）
- Skill: `insight-radar` — 全流程一键编排
- Python 虚拟环境 `.venv/` + 依赖安装（httpx, feedparser, pydantic, python-dateutil）
- TASKS.md — 任务追踪与优化方案
- progress.md — 项目进度追踪
- CHANGELOG.md — 变更日志（本文件）

### Fixed
- GitHub 采集器 topics 字段解析：`repo["topics"]` 是字符串列表，移除错误的 `t["name"]` 访问
- Pipeline CLI 中 `datetime.utcnow()` 弃用警告，改用 `datetime.now()`
