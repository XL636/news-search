# Changelog

本文件记录 InsightRadar 项目的所有变更。格式参考 [Keep a Changelog](https://keepachangelog.com/)。

---

## [0.8.0] - 2026-02-18

### Added
- **AI 搜索功能**：Dashboard 新增交互式 AI 搜索视图，支持自然语言查询科技新闻和开源项目
- 后端 `POST /api/ai-search` SSE 流式端点：搜索 classified_items → 构建 prompt → 调用 ZhipuAI GLM-4-Plus 流式 API
- `src/config.py` 新增 ZhipuAI 配置：`ZHIPUAI_API_KEY`、`ZHIPUAI_BASE_URL`、`ZHIPUAI_MODEL`、`AI_SEARCH_MAX_ITEMS`
- SQL LIKE 分词搜索：按空格分词 + 完整 query 宽匹配，支持中英文关键词
- SSE 事件流协议：`event:sources` → `data:{"text":"..."}` chunks → `event:done`
- `asyncio.Semaphore(3)` 并发控制，最多 3 个并发 AI 搜索
- 前端双视图 Tab 架构：Header 中央 Tab 导航（AI 搜索 / 信息流），默认显示 AI 搜索
- Hero 欢迎区：渐变 AI 图标 + "今天想了解什么？" 问候语 + 建议 chips
- Perplexity 风格 AI 回答面板：流式 Markdown 渲染 + `[N]` 引用徽章（可点击滚动到来源）
- 来源卡片网格：2 列布局展示匹配的新闻/项目，含领域标签、热度分数、Stars/评论数
- 轻量 Markdown 渲染器：regex 解析 `###` / `**bold**` / `- list` / `[N]` 引用
- 流式打字效果：`streaming-cursor` 闪烁光标动画
- 完善的错误处理：API key 未配置、无匹配数据、GLM API 超时/错误均有友好提示
- i18n 新增键：tabAISearch、tabFeed、aiGreeting、aiSubtitle、aiSearchPlaceholder、aiSearchBtn、aiSearching、aiSourcesLabel、aiQueryLabel、aiNewSearch、aiSuggestions

### Changed
- Header 布局调整：刷新/翻译按钮仅在 Feed 视图显示，语言切换两个视图共用
- Feed 视图数据懒加载：首次切换到 Feed Tab 时才加载数据，提升初始加载速度
- Feed 视图内容包裹进 `#view-feed` div，AI 搜索视图为 `#view-ai-search` div

## [0.7.0] - 2026-02-18

### Changed
- Dashboard 全面视觉重设计（v3）：从平铺布局改为侧边栏 + 主内容区架构
- 新增左侧固定侧边栏：KPI 统计卡片（原始/清洗/分类数据量）+ 领域导航列表
- Glass-morphism 设计语言：`backdrop-filter: blur(16px)`、半透明边框、模糊玻璃效果
- Ambient 背景：两个固定渐变光球（indigo + violet），营造深空氛围
- 卡片网格从 2 列改为 3 列响应式（xl:3 / md:2 / sm:1）
- 页面最大宽度从 `max-w-5xl` 扩展到 `max-w-[1400px]`
- 卡片圆角从 12px 增大到 16px，热度条改为渐变色填充
- 热度指示器重设计：数字 + 发光圆点（热度 >= 70 带 box-shadow 光晕）
- 搜索栏和排序组件封装进 glass-light 面板
- 来源徽章、标签样式精细化：更小字号、更精致的圆角和间距
- Inter 字体（Google Fonts CDN）替代系统默认 sans-serif
- 移动端响应式：< 1024px 隐藏侧边栏，显示横向滚动域名 chips
- 桌面端侧边栏 sticky 定位，跟随滚动
- 按钮统一使用 `btn-ghost` 样式类（半透明背景 + 微边框）
- 语言切换按钮改为 `lang-toggle` 胶囊样式
- 领域导航和移动端 chips 选中状态同步
- 自定义 Tailwind 配置：扩展 surface 色板和 Inter 字体族
- 自定义滚动条样式（6px 宽，透明轨道）

## [0.6.1] - 2026-02-18

### Added
- 首次使用 report-gen v2 生成 AI Coding 领域 .docx 报告
- 通过 MCP 等效接口（get_items keyword search）从 SQLite 获取 55 条匹配数据
- 按 `template-custom.md` 元指令自适应生成跨领域（AI/ML + DevTools）报告结构
- 输出 `output/digests/2026-02-18-ai-coding-report.docx`（6 章节，40KB）

## [0.6.0] - 2026-02-18

### Added
- `report-gen` Skill 改造为 Word 文档输出：生成格式化 .docx 报告替代 Markdown
- `generate_docx.py` 脚本：接收结构化 JSON，输出带 Calibri 字体、深蓝主题色、Light Grid Accent 1 表格样式的 .docx 文件
- 13 个领域报告模板 `references/template-*.md`：AI/ML、Security、DevTools、Cloud、Hardware、Web、Mobile、Data、Blockchain、Biotech、Other、自定义关键词元模板、全领域概览
- 支持 3 种报告模式：预定义领域（11 类）、自定义关键词过滤、全领域概览
- `python-docx>=1.1` 依赖添加到 `requirements.txt`

### Changed
- `report-gen/SKILL.md` 重写：新增参数解析、SQLite 数据过滤（domain 精确匹配 / keyword LIKE 搜索）、模板分发、JSON 生成、docx 脚本调用流程
- `insight-radar/SKILL.md` Phase 4 更新：输出改为 .docx，支持可选 domain 参数
- 报告输出路径从 `{date}-digest.md` 改为 `{date}-{topic-slug}-report.docx`

## [0.5.2] - 2026-02-18

### Added
- Skill: `mcp-digest` — 基于 MCP 工具的日报生成 Skill，通过 get_stats/get_domains/get_items 拉取数据后生成结构化 Markdown 日报

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
