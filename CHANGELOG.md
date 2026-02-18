# Changelog

本文件记录 InsightRadar 项目的所有变更。格式参考 [Keep a Changelog](https://keepachangelog.com/)。

---

## [0.5.1] - 2026-02-18

### Added
- MCP Server `src/mcp_server.py`：基于 FastMCP，暴露 5 个工具（get_items、get_domains、get_stats、collect_data、translate_text）
- `.claude/settings.local.json` 注册 `insight-radar` MCP server，新会话自动加载

## [0.5.0] - 2026-02-18

### Added
- 刷新数据按钮：Header 右侧新增刷新按钮，点击触发 `POST /api/collect` 采集数据，带旋转动画和 toast 提示
- 翻译功能：Header 新增翻译开关按钮，开启后调用 Google Translate 免费 API 翻译标题和描述为中文
- 翻译缓存：`translations` 表（MD5 hash + target_lang 唯一索引）+ SQLite 缓存查询/写入函数
- 后端 `POST /api/translate` 端点：先查缓存，未命中调用翻译 API，结果写入缓存
- 后端 `POST /api/collect` 端点：asyncio.Lock 防止并发采集，调用 `cmd_collect()` 执行采集
- 分页支持：`/api/items` 新增 `offset` 参数，返回 `{ items, total, limit, offset }` 格式
- "加载更多"按钮：前端底部加载更多 + "已显示 X / Y 条"计数
- Toast 通知系统：右上角固定通知，5 秒后自动消失，支持 info/success/error 类型
- 卡片可展开详情区：tags 和 heat_reason 折叠到"展开/收起"按钮中
- 相对时间显示："2小时前"、"3天前"等
- 卡片作者显示
- i18n 新增键：refreshBtn、refreshing、refreshDone、refreshError、translateBtn、translateOn、expand、collapse、loadMore、shownCount

### Changed
- 页面最大宽度从 `max-w-7xl` 收窄至 `max-w-5xl`
- Grid 布局从 `lg:grid-cols-3` 改为 `md:grid-cols-2`（最多 2 列）
- 卡片间距从 `gap-4` 增加到 `gap-5`
- 卡片不再整体作为 `<a>` 标签，标题链接和卡片容器分离
- 热度 >= 70 的卡片左侧加红色边条（hot-border）
- 描述文字截断长度从 150 字符增加到 200 字符
- 域名筛选改为横向滚动（`overflow-x-auto`）替代换行
- Stats 信息从 Header 移到域名筛选下方
- `/api/items` 默认 limit 从 200 改为 20
- store.py 新增 `hashlib` 导入用于翻译缓存

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
