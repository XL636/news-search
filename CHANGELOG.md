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

## [0.4.0] - 2026-02-18

### Added
- 采集器错误重试机制：BaseCollector 新增 `collect_with_retry()`，max_retries=3 + 指数退避（1s→2s→4s）
- RSS 源可配置化：从 `data/feeds.json` 加载 RSS 源列表，文件不存在或解析失败时回退到默认源
- 增量采集支持：新增 `collect_meta` 表记录每个源的最后采集时间，pipeline 日志显示上次采集时间
- 存储层新增 `get_last_collect_time()` / `set_last_collect_time()` 函数

### Removed
- 删除临时脚本 `src/classify_run.py`

### Changed
- Pipeline `cmd_collect()` 改用 `collect_with_retry()` 代替直接 `collect()`
- `config.py` RSS_FEEDS 从硬编码改为文件优先加载

## [0.3.0] - 2026-02-18

### Added
- Web Dashboard：FastAPI 后端 `src/server.py` + 前端 `src/static/index.html`
- API 接口：`/api/items`（支持领域过滤、搜索、多排序）、`/api/domains`（领域统计）、`/api/stats`（数据库统计）
- 前端功能：领域筛选 chips、关键词搜索（防抖 300ms）、4 种排序（热度/Stars/评论/时间）
- 暗色主题 UI，Tailwind CSS 样式，响应式三栏布局
- 每张卡片展示：领域标签、热度分数 + 进度条、来源徽章、Stars/评论数、标签
- 中英文双语支持：右上角语言切换按钮（中文/EN），偏好保存到 localStorage
- 中文翻译：领域名称（人工智能、开发工具、安全等）、排序选项、搜索占位符、统计信息、空状态提示
- 默认语言设为中文
- `requirements.txt` 新增 fastapi、uvicorn 依赖

## [0.2.1] - 2026-02-17

### Added
- GitHub Token 认证支持：从环境变量 `GITHUB_PERSONAL_ACCESS_TOKEN` 读取，速率限制从 60 次/h 提升到 5000 次/h
- `src/config.py` 新增 `GITHUB_TOKEN` 配置项
- `src/collectors/github_trending.py` 有 token 时自动加 `Authorization: Bearer` header，无 token 向下兼容

## [0.2.0] - 2026-02-17

### Added
- 首次完整运行 `/insight-radar` 全流程：采集 → 清洗 → 分类 → 日报生成
- 生成首份日报 `output/digests/2026-02-17-digest.md`
- 临时分类脚本 `src/classify_run.py`（待清理）

### Changed
- MVP 里程碑标记为完成：186 条原始数据 → 119 条清洗 → 119 条分类 → 完整日报

## [0.1.2] - 2026-02-17

### Fixed
- 5 个 SKILL.md 缺少 YAML frontmatter（name/description），导致 Claude Code 无法注册为可调用 skill
- 补齐 data-collect、data-clean、data-classify、report-gen、insight-radar 的 frontmatter 元数据

## [0.1.1] - 2026-02-17

### Added
- `test.md` — 全功能测试报告（33 项用例：模型、存储、配置、采集器、CLI、Skills、输出文件）
