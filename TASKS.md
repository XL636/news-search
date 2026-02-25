# InsightRadar 任务追踪

> 每次新开 Claude 会话时必读此文件，了解当前待办和优化方向。

## 当前任务状态

### 已完成 ✅

| # | 任务 | 完成日期 | 备注 |
|---|------|----------|------|
| 46 | ArXiv 论文采集器 | 2026-02-19 | ArXiv API + feedparser，cs.AI/cs.LG/cs.CL/cs.SE 类别，注册到 pipeline |
| 47 | 热度趋势追踪系统 | 2026-02-19 | heat_snapshots 表 + /api/trends + /api/snapshot + 侧边栏 TOP 5 趋势 |
| 48 | 自动调度器 | 2026-02-19 | APScheduler AsyncIOScheduler + 每日 08:00 采集 + 08:30 快照 + /api/scheduler |
| 1 | 项目脚手架搭建 | 2026-02-17 | 目录结构、配置、.gitignore、CLAUDE.md |
| 2 | 数据模型 + 存储层 | 2026-02-17 | Pydantic schemas + SQLite 三表 |
| 3 | GitHub 采集器 | 2026-02-17 | Search API，已修复 topics 解析 bug |
| 4 | Hacker News 采集器 | 2026-02-17 | Firebase API，top + show stories |
| 5 | RSS 采集器 | 2026-02-17 | feedparser，4 个 RSS 源 |
| 6 | Pipeline CLI | 2026-02-17 | collect / status / export 命令 |
| 7 | 5 个 Claude Skills | 2026-02-17 | data-collect, data-clean, data-classify, report-gen, insight-radar |
| 8 | Python 环境搭建 | 2026-02-17 | .venv + 4 个依赖安装成功 |
| 9 | 冒烟测试 | 2026-02-17 | 164 条数据采集成功（GitHub 30 + HN 54 + RSS 80） |
| 10 | 全功能测试 | 2026-02-17 | 33 项测试全部通过，详见 test.md |
| 11 | 端到端全流程验证 | 2026-02-17 | 186→119→119，日报已生成 output/digests/2026-02-17-digest.md |
| 12 | SKILL.md 添加 YAML frontmatter | 2026-02-17 | 5 个 Skill 全部补齐 name/description 字段 |
| 13 | GitHub Token 支持 | 2026-02-17 | 环境变量 GITHUB_PERSONAL_ACCESS_TOKEN，速率 60→5000/h |
| 14 | Web Dashboard | 2026-02-18 | FastAPI + 前端页面，领域过滤/搜索/排序 |
| 15 | 中英文双语 i18n | 2026-02-18 | 语言切换按钮，中文默认，localStorage 持久化 |
| 17 | 清理临时脚本 | 2026-02-18 | 删除 src/classify_run.py |
| 18 | 采集器错误重试 | 2026-02-18 | BaseCollector max_retries=3 + 指数退避 |
| 19 | RSS 源可配置化 | 2026-02-18 | data/feeds.json，fallback 到默认源 |
| 20 | 增量采集支持 | 2026-02-18 | collect_meta 表记录每个源最后采集时间 |
| 21 | Dashboard 刷新数据按钮 | 2026-02-18 | POST /api/collect + 前端刷新按钮 + toast 提示 |
| 22 | Dashboard UI 优化 | 2026-02-18 | 2列布局、分页、卡片重设计、域名横向滚动 |
| 23 | Dashboard 翻译功能 | 2026-02-18 | translations 表 + Google Translate API + 前端翻译开关 |
| 24 | MCP Server | 2026-02-18 | FastMCP 暴露 5 个工具，项目级注册自动加载 |
| 25 | Skill: mcp-digest | 2026-02-18 | 基于 MCP 工具的日报生成 Skill |
| 26 | report-gen 改造: Word 文档 + 领域模板 | 2026-02-18 | .docx 输出、11 领域模板、自定义关键词、generate_docx.py 脚本 |
| 27 | 首次 AI Coding .docx 报告生成 | 2026-02-18 | 通过 MCP 等效接口获取数据，自定义关键词模板，55 条匹配，40KB docx |
| 28 | Dashboard v3 — 全面视觉重设计 | 2026-02-18 | 侧边栏布局、KPI 卡片、Glass-morphism、3列响应式、ambient 背景 |
| 29 | Dashboard AI 搜索功能 | 2026-02-18 | GLM-4-Plus 流式 SSE + 双视图 Tab + Perplexity 风格引用 |
| 30 | API Key 管理 UI | 2026-02-18 | 前端配置面板 + GET/POST /api/ai-config + settings.json 持久化 |
| 31 | Dashboard 暖色主题 | 2026-02-18 | indigo/slate → amber/stone，全面暖色调重设计 |
| 32 | 文章 AI 解读功能 | 2026-02-18 | 卡片 AI 按钮 + 侧滑面板 + /api/ai-analyze SSE 端点 |
| 33 | 一键最新热点功能 | 2026-02-18 | 闪电按钮 + /api/ai-latest SSE 端点 + TOP 20 AI 总结 |
| 34 | 后端 GLM 流式重构 | 2026-02-18 | 提取 _stream_glm() 共享函数，三端点复用 |
| 35 | 前端 SSE 处理重构 | 2026-02-18 | 提取 _processSSE() 共享函数，三处复用 |
| 36 | AI 搜索联网增强 (GLM web_search) | 2026-02-18 | _stream_glm() 启用 web_search 工具，三端点联网搜索 |
| 37 | 本地搜索优化 (智能分词+领域映射) | 2026-02-18 | 中英文分词、2字滑窗、QUERY_DOMAIN_MAP、热门兜底 |
| 38 | RSS 数据源扩充 | 2026-02-18 | feeds.json 从 4 个源扩充到 16 个（Dev.to/Reddit/YouTube/B站等） |
| 39 | 修复 AI 搜索虚假引用 + 网络结果回存 | 2026-02-19 | GLM web_search 结果捕获→分类→存库→前端来源卡片显示 + Web 来源 AI 解读 + 刷新按钮双视图 |
| 40 | 网络来源展示优化 | 2026-02-19 | "联网补充"分隔线 + 引用 tooltip + 无URL卡片不可点击 + 保留无链接web结果 |
| 41 | AI 搜索视图翻译功能 | 2026-02-19 | 翻译按钮双视图可见 + AI来源卡片 card-title/data-original + 自动翻译 |
| 42 | AI 搜索引用不匹配修复 | 2026-02-19 | 搜索回退逻辑 + 0项GLM调用 + filterCitedSources + 引用重映射 + 25项测试计划 |
| 43 | AI 搜索引用内容匹配修复 | 2026-02-19 | tokenize + computeMatchScore + filterCitedSources 完全重写：索引匹配→内容匹配 |
| 44 | Dashboard Premium UI 全面升级 | 2026-02-19 | CSS 设计令牌 + JetBrains Mono + 噪点纹理 + 光球漂移 + 结构化骨架屏 + stagger 动画 + hero 浮动 + 搜索框光晕 + 引用升级 + 侧边栏指示条等 Vercel/Linear 级视觉 |
| 45 | Dashboard 背景微调提亮 | 2026-02-19 | bg-base #0f0e0c→#1a1816 + 五层背景变量提亮 + orb 透明度 .10→.15 + Tailwind surface 色值同步 |
| 49 | Dashboard UI/UX Pro Max 优化 | 2026-02-20 | Round 1: prefers-reduced-motion + focus-visible + aria-labels + 键盘导航 + z-index修正 + emoji→SVG + 动画减弱 + 卡片上浮 + 搜索框微交互 + 排版微调; Round 2 (Skill Audit): aria-live + skip-nav + form labels + aria-hidden + role landmarks + 触屏按钮可见 |
| 50 | Dashboard 视觉美化 (Visual Beautification) | 2026-02-20 | Fira Sans/Code 字体升级 + 4级 Elevation 阴影系统 + KPI Bento Grid + 玻璃光反射 + hero 光晕 + 搜索框旋转发光 + AI 回答面板色条 + 3-stop 渐变升级 + 侧边栏分隔线/玻璃标题 + 彩色趋势指标 + count-up 动画 + 第三光球 + 药丸徽章/标签 |
| 51 | `datetime.utcnow()` 全局替换 | 2026-02-20 | 5 文件 14 处替换为 `datetime.now(timezone.utc)` |
| 52 | 搜索输入长度校验 | 2026-02-20 | AISearchRequest 500 / search 200 / TranslateRequest 2000 |
| 53 | HTTP 缓存头 | 2026-02-20 | domains/stats/trends max-age=60, scheduler max-age=10 |
| 54 | CORS 中间件 | 2026-02-20 | CORSMiddleware allow_origins=* |
| 55 | OpenAPI 文档元数据 | 2026-02-20 | title=InsightRadar, version=0.18.0, /docs 可用 |
| 56 | Content-Security-Policy 头 | 2026-02-20 | CSPMiddleware + cdn.jsdelivr.net 白名单 |
| 57 | `get_classified_items()` 加 LIMIT | 2026-02-20 | limit=1000, offset=0 分页参数 |
| 58 | 数据库连接上下文管理器 | 2026-02-20 | store.py `get_db()` context manager 自动关闭 |
| 59 | 路由拆分 (APIRouter) | 2026-02-20 | server.py 809→114 行，拆分为 routers/ai.py + data.py + translate.py + errors.py |
| 60 | 统一错误响应格式 | 2026-02-20 | ErrorResponse model + validation/general exception handlers |
| 61 | Pydantic Settings 配置管理 | 2026-02-20 | src/settings.py — pydantic-settings BaseSettings |
| 62 | 结构化日志 (JSON) | 2026-02-20 | src/logging_config.py — JSONFormatter + setup_logging() |
| 63 | 单元测试框架 | 2026-02-20 | pytest + 14 个测试（store/schemas/config）全部通过 |
| 64 | pre-commit hooks | 2026-02-20 | ruff lint + format + .pre-commit-config.yaml |
| 65 | 数据过期清理 (TTL) | 2026-02-20 | cleanup_old_data(conn, days=30) — 5 表清理 |
| 66 | 健康检查端点 | 2026-02-20 | GET /api/health — DB/scheduler/collectors 状态 |
| 67 | WebSocket 实时推送 | 2026-02-20 | GET /api/ws — ConnectionManager + JSON broadcast |
| 68 | 用户偏好后端持久化 | 2026-02-20 | GET/POST /api/preferences — settings.json 持久化 |
| 69 | 数据导出功能 | 2026-02-20 | GET /api/export?format=json\|csv — 一键下载 |
| 70 | RSS 源健康监控 | 2026-02-20 | GET /api/feed-health — 各 RSS 源成功率/延迟 |
| 71 | 全文搜索 (FTS5) | 2026-02-20 | classified_items_fts 虚拟表 + 3 sync triggers + search_fts() |
| 72 | 异步数据库 (aiosqlite) | 2026-02-20 | aget_db/aget_stats/aget_domains/aget_classified_items 等 14 个 async 函数 + 路由端点全面 async 化 |
| 73 | 内存 TTL 缓存 (cachetools) | 2026-02-20 | src/cache.py — stats/items/trends 三级 TTL 缓存 + 采集后自动失效 |
| 74 | Docker 容器化 | 2026-02-20 | Dockerfile (multi-stage python:3.12-slim) + docker-compose.yml + .dockerignore |
| 75 | CI/CD Pipeline | 2026-02-20 | .github/workflows/ci.yml — ruff lint/format + pytest，push/PR 自动触发 |
| 76 | 性能监控 (OpenTelemetry) | 2026-02-20 | src/telemetry.py + TracerProvider + ConsoleSpanExporter + FastAPIInstrumentor |
| 77 | API 速率限制 (slowapi) | 2026-02-20 | AI 10/min + 读 120/min + 写 5/min + 429 JSON 响应 |
| 78 | WebSocket 前端自动刷新 | 2026-02-20 | Header 绿色脉冲指示灯 + 采集完成自动刷新 + 断线重连 |
| 79 | 一键导出按钮 | 2026-02-20 | Header 导出按钮 + CSV/JSON 下拉菜单 + 浏览器下载 |
| 80 | 用户偏好同步 | 2026-02-20 | 页面加载应用偏好 + 切换时自动保存到服务器 |
| 81 | RSS 源健康监控前端 | 2026-02-20 | 侧边栏源状态区块 + 绿/黄/红状态点 + 实时监控 |
| 82 | 系统状态指示 | 2026-02-20 | Header logo 旁状态点 + /api/health 轮询 + tooltip |
| 83 | 全文搜索升级 | 2026-02-20 | 新增 /api/search FTS5 端点 + 前端搜索优先使用 FTS |

| 84 | 单篇文章导出按钮 | 2026-02-20 | 删除 Header 全局导出 → 每张卡片 footer 导出按钮，纯前端 Markdown 生成下载 |
| 85 | AI 对话讨论功能 | 2026-02-20 | AI 解读面板增加多轮对话，POST /api/ai-chat SSE 端点 + 前端气泡 UI |
| 86 | Docker 本地部署验证 | 2026-02-20 | docker-compose up -d --build 构建成功，容器运行于 localhost:8000，调度器/OTel 正常 |
| 87 | 导出内容不完整修复 | 2026-02-20 | exportSingleArticle async + /api/fetch-content 按需抓取全文，fallback 到 description |
| 88 | AI 搜索引用编号不匹配修复 | 2026-02-20 | filterCitedSources 重写：模糊匹配→直接索引 localSources[N-1]，删除 tokenize/computeMatchScore |
| 89 | AI 搜索重复渲染修复 | 2026-02-20 | 删除 doAISearch/doLatestSearch onDone 中多余 renderFinalMarkdown 调用 |
| 90 | WebSocket 404 + favicon 404 修复 | 2026-02-25 | uvicorn→uvicorn[standard] 补 websockets 依赖 + /favicon.ico 返回 204 |
| 91 | 图片搜文章功能 | 2026-02-25 | GLM-4.6V-Flash 关键词提取 + 本地搜索 + GLM-4-Plus 流式分析，前端图片上传/压缩/预览 |
| 92 | WebSocket 连接泄漏修复 | 2026-02-25 | broadcast() 失败连接批量断开 |
| 93 | 收集端点竞态条件修复 | 2026-02-25 | asyncio.wait_for 非阻塞获取锁 + HTTP 409 |
| 94 | DB 连接上下文管理器修复 | 2026-02-25 | search_items_for_ai / _process_web_sources / get_top_items 改用 with get_db() |
| 95 | CORS 配置收紧 | 2026-02-25 | ALLOWED_ORIGINS 环境变量，默认 localhost:8000 |
| 96 | 错误响应信息隐藏 | 2026-02-25 | 生产环境隐藏详细 traceback |
| 97 | Docker 安全加固 | 2026-02-25 | HEALTHCHECK + 非 root appuser 用户 |
| 98 | itemDataCache LRU 上限 | 2026-02-25 | 最多 200 条缓存，超出清除最早 50 条 |
| 99 | CSP img-src blob: | 2026-02-25 | 支持前端图片预览 Canvas 压缩 |
| 100 | 图片粘贴 & 拖拽上传 | 2026-02-25 | 搜索框支持 Ctrl+V 粘贴图片 + 拖拽放置图片，自动触发搜索 |

### 进行中 🔄

| # | 任务 | 开始日期 | 状态 |
|---|------|----------|------|
| — | 暂无 | — | — |

> **已完成**: #51-#57 Tier 1 快速修复 7 项 — 2026-02-20
> **已完成**: #58-#64 Tier 2 代码质量 7 项 — 2026-02-20
> **已完成**: #65-#71 Tier 3 功能增强 7 项 — 2026-02-20
> **已完成**: #72-#77 Tier 4 架构演进 6 项 — 2026-02-20

### 待办 📋

| # | 任务 | 优先级 | 说明 |
|---|------|--------|------|
| 16 | 修复 Skill 注册问题 | P2 | YAML frontmatter 格式正确但 Claude Code 未加载 |

| | **~~Tier 1 — 快速修复~~** ✅ 已完成 | | |
| | **~~Tier 2 — 代码质量~~** ✅ 已完成 | | |
| | **~~Tier 3 — 功能增强~~** ✅ 已完成 | | |

| | **~~Tier 4 — 架构演进~~** ✅ 已完成 | | |
| ~~72~~ | ~~异步数据库 (aiosqlite)~~ | ~~P3~~ | ✅ 14 个 async DB 函数 + 路由端点转 async |
| ~~73~~ | ~~内存 TTL 缓存 (cachetools)~~ | ~~P3~~ | ✅ stats/items/trends 三级缓存 + 自动失效 |
| ~~74~~ | ~~Docker 容器化~~ | ~~P3~~ | ✅ Dockerfile + docker-compose.yml + .dockerignore |
| ~~75~~ | ~~CI/CD Pipeline~~ | ~~P3~~ | ✅ GitHub Actions lint + test |
| ~~76~~ | ~~性能监控 (OpenTelemetry)~~ | ~~P3~~ | ✅ TracerProvider + FastAPIInstrumentor |
| ~~77~~ | ~~API 速率限制 (slowapi)~~ | ~~P3~~ | ✅ AI 10/min + 读 120/min + 写 5/min |

---

## 优化方案

### 短期优化（MVP 阶段可做）

1. **~~GitHub Token 支持~~** ✅ 已完成
   - 环境变量 `GITHUB_PERSONAL_ACCESS_TOKEN`，config.py 读取，github_trending.py 自动加 Bearer header

2. **~~采集器错误重试~~** ✅ 已完成
   - BaseCollector 新增 `collect_with_retry()`，max_retries=3 + 指数退避（1s→2s→4s）

3. **~~RSS 源可配置化~~** ✅ 已完成
   - RSS 源从 `data/feeds.json` 加载，文件缺失或损坏时回退默认源

4. **~~增量采集优化~~** ✅ 已完成
   - `collect_meta` 表记录每个源最后采集时间，pipeline 日志显示增量状态

### 中期优化（MVP 后）

5. **~~更多数据源~~** ✅ 已完成
   - ~~Product Hunt API~~ ✅ RSS 已覆盖
   - ~~Reddit r/programming~~ ✅ RSS 已覆盖
   - ~~ArXiv 论文（AI 领域）~~ ✅ 专用 ArXiv API 采集器（cs.AI/cs.LG/cs.CL/cs.SE）
   - ~~Dev.to / Medium 技术博客~~ ✅ RSS 已覆盖 + Medium Tech 新增

6. **~~热度趋势追踪~~** ✅ 已完成
   - heat_snapshots 表 + 每日快照 + 两次快照对比
   - GET /api/trends + POST /api/snapshot API
   - 侧边栏 TOP 5 趋势项（↑/↓/→ + 迷你热度条）

7. **~~Web 界面~~** ✅ 已完成（含 v3 重设计）
   - FastAPI 后端 `src/server.py` + 前端 `src/static/index.html`
   - 领域过滤、搜索、多排序、暗色主题
   - v2: 刷新数据按钮、分页加载更多、翻译功能、UI 优化（2列布局、卡片重设计）
   - v3: 侧边栏导航、KPI 统计卡片、Glass-morphism、3列响应式、ambient 渐变背景

8. **~~定时调度~~** ✅ 已完成
   - APScheduler AsyncIOScheduler 集成 FastAPI 生命周期
   - 每日 08:00 UTC 自动采集 + 08:30 UTC 热度快照
   - 时间可通过 data/settings.json 配置
   - GET /api/scheduler 状态查询 + 侧边栏调度状态显示

### 长期优化（规模化）

9. **用户个性化**
   - 根据用户关注领域定制日报内容
   - 关键词订阅 + 推送通知

10. **多语言支持**（部分完成）
    - ~~Dashboard UI 中英文切换~~ ✅ 已完成
    - 日报支持中英文双版本
    - 数据源支持日文/韩文技术社区
