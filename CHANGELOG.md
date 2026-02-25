# Changelog

本文件记录 InsightRadar 项目的所有变更。格式参考 [Keep a Changelog](https://keepachangelog.com/)。

---

## [0.24.2] - 2026-02-25

### Changed
- **AI 模型升级**: 文本模型 `glm-4-plus` → `glm-5`（200K 上下文，128K 输出），视觉模型 `glm-4.6v-flash` → `glm-4.6v`（128K 上下文，支持工具调用）

---

## [0.24.1] - 2026-02-25

### Added
- **图片粘贴上传**: 在搜索框中 Ctrl+V 粘贴剪贴板图片，自动触发图片搜索
- **图片拖拽上传**: 拖拽图片到搜索框区域，松手后自动触发图片搜索
- **拖拽视觉反馈**: 拖拽悬停时搜索框显示 amber 高亮边框和背景

### Changed
- **`processImageFile()` 提取**: 从 `handleImageUpload` 中抽取共用处理函数，文件选择/粘贴/拖拽三入口统一调用
- 粘贴的图片文件名显示为 `pasted-image.png`（原始文件名不可用时）

---

## [0.24.0] - 2026-02-25

### Added
- **图片搜文章功能**: 上传图片 → GLM-4.6V-Flash 提取关键词 → 搜索本地库 → GLM-4-Plus 流式分析推荐
  - 后端 `POST /api/ai-image-search` SSE 端点：两阶段调用（VL 关键词提取 + 文本分析），速率限制 5/min
  - 后端 `_call_glm_sync()` 非流式 GLM 调用辅助函数
  - 后端 `build_image_extract_prompt()` / `build_image_search_prompt()` prompt 构建函数
  - 后端 `AIImageSearchRequest` Pydantic 模型
  - 前端图片按钮 + 隐藏文件选择器 + 图片预览条（缩略图 + 文件名 + 大小 + 删除按钮）
  - 前端 `doImageSearch()` / `triggerImageUpload()` / `handleImageUpload()` / `clearImageUpload()` 函数
  - 前端 `compressImage()` 画布压缩：>2MB 自动缩放至 1200px + JPEG 0.8 质量
  - 前端 `_processSSE()` 扩展 `onImageAnalysis` 回调处理 `image_analysis` 事件
  - 前端关键词标签（`.ai-keyword-tag` 琥珀药丸）展示 VL 提取结果
  - i18n 新增 6 个中英文键（aiImageBtn / aiImageSearching / aiImageTooLarge / aiImageInvalid / aiImageQuery / aiImageKeywords）
- **Docker HEALTHCHECK**: 每 30s 检查 `/api/health`，10s 启动宽限期
- **Docker 非 root 用户**: `appuser` 用户运行容器，提升安全性

### Fixed
- **WebSocket 连接泄漏（Bug #2.1）**: `broadcast()` 发送失败的连接现已在循环结束后批量断开
- **收集端点竞态条件（Bug #2.4）**: `_collect_lock` 改用 `asyncio.wait_for` 非阻塞获取，返回 HTTP 409
- **数据库连接泄漏（Bug #2.3）**: `search_items_for_ai()` / `_process_web_sources()` / `get_top_items()` 改用 `with get_db() as conn:` 上下文管理器

### Changed
- **CORS 配置收紧（Security #3.1）**: `allow_origins` 从 `["*"]` 改为从环境变量 `ALLOWED_ORIGINS` 读取，默认 `http://localhost:8000`
- **错误响应信息隐藏（Security #3.2）**: 生产环境（非 DEBUG）不再返回异常详细信息，仅记录到日志
- **CSP img-src 增加 blob:**: 支持前端图片预览 Canvas 压缩
- **itemDataCache LRU 上限**: 最多 200 条缓存，超出清除最早的 50 条
- **docker-compose.yml**: 新增 `ALLOWED_ORIGINS` 环境变量

---

## [0.23.1] - 2026-02-25

### Fixed
- **WebSocket 404**: `requirements.txt` 中 `uvicorn` 改为 `uvicorn[standard]`，包含 `websockets`/`httptools`/`uvloop` 等标准依赖
- **favicon.ico 404**: `server.py` 新增 `GET /favicon.ico` 路由返回 204 No Content

---

## [0.23.0] - 2026-02-20

### Fixed
- **导出内容不完整**: `exportSingleArticle()` 改为 async，导出前调用 `/api/fetch-content` 按需抓取文章原始网页全文，内容远超原来的 500 字符截断；失败时 fallback 到原有 description
- **AI 搜索引用 [N] 与文章不匹配**: 重写 `filterCitedSources()`，删除 `tokenize` + `computeMatchScore` 模糊关键词匹配，改为 `localSources[N-1]` 直接索引映射（后端 `build_ai_prompt` 保证 `[N]` = `items[N-1]`）
- **AI 搜索重复渲染**: 删除 `doAISearch` 和 `doLatestSearch` 的 `onDone` 回调中多余的 `renderFinalMarkdown(fullText)` 调用，只保留 SSE 循环结束后的调用

### Added
- 后端 `POST /api/fetch-content` 端点: 按需抓取文章原始网页内容，HTML→纯文本（去 script/style/标签），限 8000 字符，速率限制 10/min

### Removed
- `tokenize()` / `computeMatchScore()` 前端函数（被直接索引映射替代）

---

## [0.22.1] - 2026-02-20

### Added
- Docker 本地部署验证: `docker-compose up -d --build` 构建并启动成功，容器正常运行于 `localhost:8000`

---

## [0.22.0] - 2026-02-20

### Added
- 单篇文章导出按钮: 每张卡片 footer 新增「导出」按钮，纯前端生成 Markdown 文件并触发浏览器下载
- AI 对话讨论功能: AI 解读分析完成后，面板底部出现输入框，可继续追问讨论多轮
- 后端 `POST /api/ai-chat` SSE 端点: 复用 `_stream_glm()` + `_ai_search_semaphore`，支持文章上下文 + 初始分析 + 对话历史
- `build_chat_prompt()` 函数: 构建文章上下文 + 初始分析 + 对话历史的多轮消息
- `AIChatRequest` / `AIChatMessage` Pydantic 模型
- `exportSingleArticle()` 前端函数: 纯前端 Markdown 文件生成 + Blob 下载
- `sendChatMessage()` 前端函数: 流式 SSE 对话 + 气泡渲染
- Chat CSS: `.chat-bubble.user` / `.chat-bubble.assistant` / `.chat-send-btn` / `.chat-divider` / `#analyze-chat-area`
- 6 个新增 i18n 键: `exportArticle` / `exportArticleDone` / `chatPlaceholder` / `chatSend` / `chatThinking`

### Removed
- Header 全局导出按钮 (`export-dropdown-wrap` + `toggleExportDropdown()` + `doExport()`)
- `.export-dropdown-wrap` / `.export-dropdown` CSS 规则
- `exportBtn` / `exportStarted` i18n 键

### Changed
- AI 解读面板从纯展示变为可交互对话面板（分析结果 + 对话气泡 + 固定底部输入框）
- `openAnalyzePanel()` 新增 chat 状态重置
- `closeAnalyzePanel()` 新增 chat abort + 状态清理
- `streamAnalysis()` onDone 回调新增: 保存分析全文，显示对话输入框
- `renderCard()` / `renderAISources()` footer 新增导出按钮

---

## [0.21.0] - 2026-02-20

### Added
- WebSocket 前端自动刷新: Header 绿色脉冲指示灯，采集完成自动刷新页面，断线指数退避重连
- 一键导出按钮: Header 导出按钮 + CSV/JSON glass 下拉菜单，触发浏览器下载
- 用户偏好同步: 页面加载应用服务器偏好，切换语言/排序/视图自动保存
- RSS 源健康监控前端: 侧边栏数据源状态区块，绿/黄/红状态点实时显示
- 系统状态指示: Logo 旁 8px 状态点，/api/health 60 秒轮询，tooltip 详情
- 全文搜索 API: GET /api/search FTS5 端点，前端搜索优先使用 FTS
- 15 个新增 i18n 键（中英文）

### Changed
- Feed 搜索从 LIKE 升级为 FTS5（更快更准）
- PAGE_SIZE 从 const 改为 let，支持用户偏好动态设置

---

## [0.20.0] - 2026-02-20

### Added
- **Async Database Layer (aiosqlite)** — 14 个异步 DB 函数，Web 端点不再阻塞事件循环
  - `aget_connection()` / `aget_db()` async context manager / `ainit_db()` async init
  - `aget_classified_items()` — async 查询 + 过滤 + 分页 + 排序
  - `aget_stats()` / `aget_domains()` — async 统计和领域列表
  - `asearch_fts()` — async FTS5 全文搜索
  - `aget_trending_items()` / `aget_item_trend()` — async 趋势数据
  - `aget_feed_health()` / `aget_export_items()` — async 源健康和数据导出
  - `aget_translation()` / `asave_translation()` — async 翻译缓存
  - 所有 sync 函数保持不变，CLI/scheduler 继续使用同步版本
- **OpenTelemetry 性能监控** — `src/telemetry.py`
  - `TracerProvider` + `ConsoleSpanExporter` (开发模式，可替换为 OTLP 导出器)
  - `FastAPIInstrumentor` 自动追踪所有 HTTP 请求 (延迟/状态码/路径)
  - `setup_telemetry(app)` 在 FastAPI lifespan 中初始化
- AI 路由 async 搜索：`asearch_items_for_ai()` / `aget_top_items()` 异步版本
- `requirements.txt` 新增：`aiosqlite>=0.20`、`opentelemetry-api>=1.20`、`opentelemetry-sdk>=1.20`、`opentelemetry-instrumentation-fastapi>=0.41b0`

### Changed
- **路由端点全面 async 化**：7 个 data.py 端点 + 1 个 translate.py 端点从 sync→async
  - `api_domains` / `api_items` / `api_stats` / `api_trends` / `api_health` / `api_export` / `api_feed_health`
  - `api_translate` — 翻译缓存读写使用 async DB
  - `api_ai_search` / `api_ai_latest` — 生成器内部搜索改用 async 版本
- **Docker 容器化** — `Dockerfile` (multi-stage python:3.12-slim) + `docker-compose.yml` (port 8000, data volume) + `.dockerignore`
- **CI/CD Pipeline** — `.github/workflows/ci.yml`：push/PR 触发 ruff lint/format + pytest，Python 3.12 + pip 缓存
- **API 速率限制 (slowapi)** — `SlowAPIMiddleware` + 分级限流：AI 端点 10/min、读端点 120/min、写端点 5/min、429 JSON 响应
- **内存 TTL 缓存 (cachetools)** — `src/cache.py`：stats 60s / items 30s / trends 120s 三级 TTL 缓存，采集/快照后自动失效
- `requirements.txt` 新增：`slowapi>=0.1.9`、`cachetools>=5.0`

### Changed
- **路由端点全面 async 化**：7 个 data.py 端点 + 1 个 translate.py 端点从 sync→async
  - `api_domains` / `api_items` / `api_stats` / `api_trends` / `api_health` / `api_export` / `api_feed_health`
  - `api_translate` — 翻译缓存读写使用 async DB
  - `api_ai_search` / `api_ai_latest` — 生成器内部搜索改用 async 版本
- 版本号 0.19.0 → 0.20.0

---

## [0.19.0] - 2026-02-20

### Added
- **Route Splitting (APIRouter)** — `server.py` 从 809 行瘦身至 114 行，拆分为 4 个路由模块
  - `src/routers/ai.py` (514 行)：AI 搜索/分析/最新热点/API Key 配置
  - `src/routers/data.py` (343 行)：数据查询/统计/采集/趋势/健康检查/WS/偏好/导出/RSS
  - `src/routers/translate.py` (54 行)：Google Translate 代理
  - `src/routers/errors.py` (25 行)：ErrorResponse model + 全局 exception handlers
- **Unified Error Response** — `ErrorResponse` Pydantic model + `validation_exception_handler` + `general_exception_handler`
- **Pydantic Settings** — `src/settings.py` 使用 `pydantic-settings` BaseSettings 管理配置，env_prefix="INSIGHTRADAR_"
- **DB Context Manager** — `store.py` 新增 `get_db()` contextmanager，自动关闭连接
- **Data TTL Cleanup** — `cleanup_old_data(conn, days=30)` 清理 5 张表过期数据
- **Health Check Endpoint** — `GET /api/health` 返回 DB 连接/调度器状态/采集器信息
- **WebSocket Real-time Push** — `GET /api/ws` + `ConnectionManager` 类，JSON broadcast 实时推送
- **User Preferences API** — `GET/POST /api/preferences` 用户偏好持久化到 settings.json
- **Data Export** — `GET /api/export?format=json|csv` 一键下载 classified_items
- **RSS Feed Health** — `GET /api/feed-health` 各 RSS 源成功率和延迟监控
- **Full-Text Search (FTS5)** — `classified_items_fts` 虚拟表 + 3 个同步触发器 (INSERT/DELETE/UPDATE)
  - `search_fts(conn, query, limit, offset)` 全文搜索函数
  - `rebuild_fts_index(conn)` 索引重建
  - `init_db()` 自动创建 FTS 表/触发器
- **Structured JSON Logging** `src/logging_config.py` — `JSONFormatter` 格式化为 JSON lines + `setup_logging()` 配置函数（支持 JSON/human-readable 双模式）
  - 支持 `request_id` 追踪、异常堆栈、日志级别配置
  - 自动降噪：httpx/httpcore WARNING、apscheduler INFO
- **Unit Test Framework** — pytest + pytest-asyncio 测试套件，14 个测试全部通过
  - `tests/conftest.py`：`db_conn` 临时数据库 fixture + `sample_raw_item` 样本数据
  - `tests/test_store.py`：存储层测试（插入/去重/查询/统计/采集元数据）
  - `tests/test_schemas.py`：数据模型测试（默认值/unique_key/UTC 时区）
  - `tests/test_config.py`：配置测试（DOMAINS/API/DB_PATH）
  - `pytest.ini`：测试配置（testpaths/asyncio_mode=auto）
- **Pre-commit Hooks** — ruff lint + format 自动检查
  - `ruff.toml`：target-version py312, line-length 120, select E/F/W/I/UP/B/SIM
  - `.pre-commit-config.yaml`：ruff-pre-commit v0.4.4（lint --fix + format）
- `requirements.txt` 新增：`pytest>=8.0`、`pytest-asyncio>=0.23`、`ruff>=0.4`、`pydantic-settings>=2.0`

---

## [0.18.0] - 2026-02-20

### Fixed
- **`datetime.utcnow()` 全局替换** — 5 个文件全部从 `datetime.utcnow()` 迁移到 `datetime.now(timezone.utc)`，消除 Python 3.12+ DeprecationWarning
  - `src/models/schemas.py`：4 个 Field default_factory
  - `src/storage/store.py`：5 处 utcnow() 调用
  - `src/scheduler.py`：2 处时间戳记录
  - `src/collectors/github_trending.py`：日期计算
  - `src/collectors/hackernews.py`：`utcfromtimestamp()` → `fromtimestamp(tz=timezone.utc)`

### Added
- **CORS 中间件** — `CORSMiddleware` 允许跨域访问（allow_origins=*, allow_methods=*, allow_headers=*）
- **Content-Security-Policy 头** — `CSPMiddleware` 设置 CSP 安全头（script-src/style-src/font-src/img-src/connect-src 白名单）
- **HTTP 缓存头** — `/api/domains`, `/api/stats`, `/api/trends`: `Cache-Control: public, max-age=60`; `/api/scheduler`: `max-age=10`
- **OpenAPI 文档元数据** — `FastAPI(title="InsightRadar", description=..., version="0.18.0")`，访问 `/docs` 查看完整 API 文档
- **搜索输入长度校验** — `AISearchRequest.query` max_length=500, `api_items search` max_length=200, `TranslateRequest.text` max_length=2000
- **`get_classified_items()` 分页** — 新增 `limit=1000, offset=0` 参数防止全表扫描
- **优化路线图** — TASKS.md 新增 27 项 Tier 1-4 优化任务（#51-#77），progress.md 新增 6 Phase 路线图

### Removed
- **14 个未引用截图** — 清理项目根目录未被任何文档引用的 PNG 文件，保留 6 个被引用的

---

## [0.17.0] - 2026-02-20

### Added
- **Typography Upgrade** — 字体从 Inter + JetBrains Mono 升级为 Fira Sans + Fira Code（更技术感的 dashboard 字体，支持连字）
- **4-Level Elevation System** — 新增 `--elevation-1` 到 `--elevation-4` 维度层级阴影系统，替代扁平阴影
- **KPI Bento Grid** — KPI 卡片从 1 列改为 2 列 bento 布局，首行跨列；新增图标、渐变强调条、stagger 入场动画
- **KPI Count-up Animation** — KPI 数字加载时 ease-out 计数动画（`animateCount()` 函数）
- **Glass Light Reflections** — `.glass` 和 `.glass-light` 新增顶部边缘高光渐变
- **Ambient Orb-3** — 新增第三个暖琥珀色光球（底部右侧，更丰富的环境深度）
- **AI Hero Radial Halo** — AI 搜索 hero 图标新增双层放射状光晕 + 呼吸动画
- **Search Box Glow Border** — 搜索框 focus 时新增 conic-gradient 旋转发光边框
- **AI Answer Panel Accent Stripe** — AI 回答面板左侧新增 amber 渐变色条
- **Header Logo-Tab Separator** — header 中 logo 与 tab 导航间新增渐变分隔线
- **Sidebar Visual Separators** — 侧边栏 KPI/趋势/域名 区块间新增渐变分隔线
- **Sidebar Glass Section Headers** — 侧边栏标题新增玻璃磨砂背景
- **Colored Trend Indicators** — 趋势方向从文字箭头升级为彩色 SVG 箭头 + 背景色调

### Changed
- **3-Stop CTA Gradient** — 所有 amber 按钮/激活态梯度升级为 `#fbbf24 → #d97706 → #b45309`（Tab/Lang/Chip/搜索按钮/Logo）
- **Card Elevation** — 卡片默认 elevation-1，hover 升至 elevation-3 + glow + scale(1.005)
- **Card Top Accent Line** — 卡片顶部高光线从白色换为 amber 渐变
- **Card Hover Inner Glow** — 卡片 hover 新增暖色 amber wash 覆盖渐变
- **KPI Card Elevation** — KPI 卡片默认 elevation-2，hover 升至 elevation-3 + glow
- **Source Badges Pill Style** — 来源徽章改为圆角药丸样式 + 更多内边距 + 模糊背景
- **Tag Pills Softer** — 标签改为圆角药丸 + 更柔和背景 + 更多内边距
- **Suggestion Chips Glass** — 建议芯片改为玻璃磨砂效果 + 更大圆角 + hover elevation
- **Toast Glass Enhancement** — Toast 通知改为更强的模糊效果 + spring 弹性动画 + elevation-3
- **Analyze Panel Elevation-4** — AI 解读侧滑面板使用最高层级 elevation-4 阴影
- **Sidebar Hover Glow** — 域名项 hover 新增左侧内发光效果
- **Scrollbar Warm Tint** — 滚动条 thumb hover 颜色改为暖 amber 色调
- **Empty State Warm Gradient** — 空态图标背景改为 amber 暖色渐变
- **Header Blur Increased** — 头部模糊从 20px 增强到 24px
- **Border Subtle Brightness** — 全局 `--border-subtle` 透明度从 .06 提升到 .08

## [0.16.0] - 2026-02-20

### Added
- **Accessibility: `prefers-reduced-motion`** — 新增 `@media (prefers-reduced-motion: reduce)` CSS 块，禁用/减速所有装饰动画（orb漂移、hero浮动、热度脉冲、卡片入场、骨架屏闪烁、loading波浪、toast动画）
- **Accessibility: focus-visible 样式** — 所有可交互元素（按钮、Tab、chips、域名项、输入框、链接）添加 `2px amber outline` focus-visible 样式
- **Accessibility: aria-labels** — icon-only 按钮（刷新、翻译、关闭面板、搜索）添加 i18n-aware `aria-label`
- **Accessibility: 键盘导航** — 侧边栏域名项添加 `tabindex="0"`、`role="button"` 及 Enter/Space 键盘处理

### Added (Round 2 — UI/UX Pro Max Skill Audit)
- **aria-live 动态区域** — AI 回答面板 `aria-live="polite"` + Toast 容器 `role="status" aria-live="polite"` + 错误区 `role="alert"`
- **Skip Navigation 链接** — 键盘用户可跳过导航直达内容（sr-only + focus 可见）
- **表单 aria-label** — 所有输入框添加 i18n aria-label（AI 搜索/信息流搜索/排序/API Key x2）
- **aria-hidden 装饰元素** — 光球、hero 图标、搜索图标、header 按钮 SVG 添加 `aria-hidden="true"`
- **role="search"** — AI 搜索框添加 landmark role
- **role="status"** — 调度状态区添加语义角色

### Changed
- **AI 解读按钮触屏可见** — hover-only `opacity:0` → 默认 `opacity:.45`（触屏设备可见 + hover 全显）
- **select focus 样式** — 排序下拉添加 `focus:ring-1 focus:ring-amber-500/30` 替代 outline-none
- **z-index 修正** — `body::before` 噪点纹理从 `z-index: 9999` 降为 `z-index: 1`（已有 `pointer-events: none`）
- **Emoji → SVG** — 网络来源分隔线中的 🌐 emoji 替换为内联 SVG globe 图标
- **装饰动画减弱** — orb 透明度 `.15` → `.12`；hero 浮动动画 `6s` → `8s`（更柔和）
- **卡片交互升级** — hover 新增 `translateY(-2px)` 上浮效果 + transition 包含 transform；热门卡片光晕改为柔和渐变
- **搜索框微交互** — `focus-within` 新增 `scale(1.01)` 微放大效果
- **排版微调** — 卡片标题统一 `letter-spacing: -0.01em`；KPI 数字新增 `letter-spacing: -0.02em`

## [0.15.0] - 2026-02-19

### Added
- **ArXiv 论文采集器** `src/collectors/arxiv.py`：使用 ArXiv API 采集 cs.AI/cs.LG/cs.CL/cs.SE 类别最新论文
  - feedparser 解析 Atom XML，映射到 RawItem（title/abstract/author/categories）
  - `source="arxiv"`, `source_id="arxiv:{id}"`
  - `config.py` 新增 `ARXIV_API_URL`、`ARXIV_CATEGORIES`、`ARXIV_MAX_ITEMS=30`
  - `pipeline.py` COLLECTORS 注册 ArXivCollector
  - `SOURCE_AUTHORITY` 新增 `"arxiv": 2`
- **热度趋势追踪系统**（完整垂直切片）
  - `store.py`：`heat_snapshots` 表 + `take_daily_snapshot()` + `get_trending_items()` + `get_item_trend()`
  - `server.py`：`GET /api/trends?days=3&limit=20` + `POST /api/snapshot`
  - 前端侧边栏趋势区块：TOP 5 趋势项，↑/↓/→ 方向标记 + 迷你热度条
  - i18n：`trendTitle`/`trendUp`/`trendDown`/`trendStable`/`trendEmpty`（中英文）
- **自动调度器** `src/scheduler.py`
  - APScheduler `AsyncIOScheduler` 集成 FastAPI lifespan
  - Job 1: 每日 08:00 UTC 执行 `cmd_collect()` 全源采集
  - Job 2: 每日 08:30 UTC 执行 `take_daily_snapshot()` 热度快照
  - 调度时间可通过 `data/settings.json` 配置
  - `GET /api/scheduler` 返回调度状态（running/jobs/next_run/last_run）
  - 前端侧边栏底部调度状态显示（绿色运行指示灯 + 下次采集时间）
  - i18n：`schedulerStatus`/`schedulerNext`/`schedulerOff`/`schedulerRunning`（中英文）
  - `requirements.txt` 新增 `apscheduler>=3.10,<4.0`
- **Medium Tech RSS**：`data/feeds.json` 新增 `https://medium.com/feed/tag/technology`（总计 17 个源）
- 前端 `SOURCE_STYLES` 新增 `arxiv` 条目：紫色风格（`#c084fc`），label 显示 "论文"
- 前端 i18n `sourceNames` 新增 `arxiv: '论文'`(zh) / `arxiv: 'Paper'`(en)

---

## [0.14.1] - 2026-02-19

### Changed
- **Dashboard 背景微调提亮**：基础背景色 `#0f0e0c` → `#1a1816`，整体提亮一档保持暖色暗主题
- CSS 设计令牌五层背景变量全部提亮：`--bg-raised`、`--bg-surface`、`--bg-overlay`、`--bg-hover`
- 光球（orbs）透明度 `.10` → `.15`，环境光更明显
- Tailwind surface 色板同步更新：`950: #1a1816`、`900: #1f1d1a`、`800: #272522`

---

## [0.14.0] - 2026-02-19

### Added
- **CSS 设计令牌系统**：`:root` 变量 — 颜色(bg/border/text)、阴影(sm~xl+glow)、圆角(sm~2xl)、动效(ease-out/spring/duration)
- **JetBrains Mono 字体**：KPI 数字、热度分数、引用徽章使用等宽数字字体
- **字体层级类**：`.text-display/.text-heading/.text-subheading/.text-body/.text-caption/.text-mono`
- **噪点纹理**：`body::before` 内联 SVG feTurbulence，opacity .015
- **光球漂移动画**：`orbDrift` 20s 缓慢漂移 + radial-gradient 光球
- **卡片顶部高光线**：`.card::before` 1px 白色渐隐线模拟光照
- **热门卡片红色光晕**：`.card-hot::after` 右上角 radial glow
- **热度脉冲动画**：`heatPulse` 热门项(≥70)脉冲发光
- **卡片 stagger 入场**：每张 40ms 延迟(max 600ms)，`requestAnimationFrame` 设置
- **结构化骨架屏**：域名条+标题行+描述行+热度条+badge 结构
- **Hero 浮动+呼吸**：`heroFloat`(6s 上下) + `heroPulse`(光晕呼吸)
- **搜索框三层光晕**：focus 时 3px+1px+shadow-lg 三层效果
- **搜索按钮高光**：`::before` hover 白色 overlay
- **建议 chips 上浮**：hover translateY(-2px) + shadow
- **回答面板顶部渐隐线**：amber gradient 渐隐线
- **流式光标 gradient+glow**：渐变色 + box-shadow 发光
- **Loading wave 弹跳**：translateY -8px 交错动画替代 pulse
- **引用徽章升级**：border + hover 上浮 + shadow + JetBrains Mono
- **来源卡片高亮动画**：`sourceHighlight` keyframe + amber overlay
- **侧边栏 active 指示条**：左侧 2px amber 高度动画
- **侧边栏标题样式**：10px 大写 + 0.08em letter-spacing
- **AI 解读按钮渐显**：默认隐藏，card:hover 时 fade-in
- **分析面板背景模糊**：overlay backdrop-filter: blur(4px) + panel shadow
- **闪电按钮 border 化**：透明底色 + border + hover glow
- **Toast 模糊入场**：blur(2px) + scale(.95) 入场动画
- **Tab active 高光**：gradient + inset 高光 + shadow
- **Lang 切换 gradient**：active 态 amber gradient + shadow
- **Ghost 按钮 glow**：hover 时 `::before` radial amber glow
- **Divider 工具类**：`.divider-gradient` / `.divider-accent`

### Changed
- 底色加深 `#12110f` → `#0f0e0c`(更深更沉稳)
- 滚动条更细 6px → 5px + 更透明
- `::selection` 加 color: #fff
- 全局 heading 加 `letter-spacing: -0.025em`
- Heat bar 更细 3px → 2px + 过渡 0.8s
- Tag pill 加 hover 态
- KPI 卡片使用 JetBrains Mono + hover amber overlay
- Domain count badge 使用 JetBrains Mono
- 卡片 hover 改为 shadow 上升 + border 变色（移除 translateY 跳跃）
- `.glass-light` 更透明(.4 → .35)

---

## [0.13.0] - 2026-02-19

### Fixed
- **AI 搜索引用彻底修复**：用内容匹配替代索引匹配，解决 GLM `[N]` 与来源卡片不对应的根本问题
  - 旧方案：`[5]` → `aiSources[4]`（索引匹配），GLM 编号错位时完全失效
  - 新方案：提取引用上下文关键词 → tokenize → 与所有来源标题/描述打分 → 匹配真正对应的来源

### Added
- `tokenize(text)` 函数：中英文混合分词（英文单词 + 中文单字/bigram），去重
- `computeMatchScore(contextTokens, source)` 函数：标题权重 3x + 描述权重 1x 打分
- `filterCitedSources()` 内容匹配逻辑：上下文 80 字提取 → 逐引用最佳匹配 → usedSourceIndices 防重复 → 最低阈值 ≥2

### Changed
- `filterCitedSources()` 完全重写：索引匹配 → 内容匹配，匹配后按引用编号排序重建 aiSources
- 未匹配引用的 citation badge 直接移除（`el.remove()`）
- 未引用的 web 来源追加到匹配来源之后

---

## [0.12.0] - 2026-02-19

### Fixed
- **AI 搜索引用不匹配**：搜索无关键词时不再返回无关热门项填充，GLM 直接使用联网搜索
- **来源卡片过多**：前端 `filterCitedSources()` 过滤未引用来源，只显示 AI 实际引用的卡片
- **引用编号重映射**：过滤后引用编号连续（无跳号），tooltip 和点击滚动同步更新

### Added
- `filterCitedSources()` 前端函数：扫描 AI 文本提取引用编号 → 过滤 aiSources → 重映射引用
- AI 搜索视图来源卡片支持翻译功能：标题添加 `.card-title` class + `data-original` 属性
- `renderAISources()` 末尾自动检测翻译模式，渲染后自动翻译新卡片
- `build_ai_prompt()` 支持 0 项本地数据，提示 GLM 使用联网搜索
- 25 项引用准确性测试计划 (test.md §12)

### Changed
- `search_items_for_ai()` 回退逻辑：0 匹配时返回空列表（不再填充无关热门项）；≥1 匹配时才补充
- `api_ai_search()` 不再在 0 结果时提前返回，改为调用 GLM + web_search
- Prompt 规则 9：明确禁止 GLM 对联网搜索结果使用 [N] 编号引用
- 翻译按钮从信息流专属（`feed-only-btn`）改为双视图共享
- `renderAISources()` 支持 0 来源时隐藏来源区域

---

## [0.11.0] - 2026-02-19

### Fixed
- **AI 搜索虚假引用修复**：GLM `web_search` 联网返回的网络来源现在正确捕获、分类、存库、并显示在前端来源卡片中

### Added
- `_stream_glm()` 捕获 GLM 流式响应中 `web_search` 字段，累积网络搜索结果并在流结束前 yield `event: web_sources` SSE 事件
- `classify_web_result_domain()` 两层领域分类：URL 域名匹配（github.com→DevTools, arxiv.org→AI/ML 等 12 条规则）+ 关键词匹配（10 个领域，中英文关键词）
- `_process_web_sources()` 辅助函数：拦截 `web_sources` 事件 → 分类 → 存库 → 构造前端格式化数据（含 `refer` 字段传递，支持无 URL 条目）
- `insert_web_search_item()` 三表写入（raw_items→cleaned_items→classified_items），source=`web_search`，URL 去重，heat_index 默认 30
- `init_db()` 新增 `idx_raw_url` 和 `idx_classified_url` 索引加速 URL 去重查询
- 前端 `_processSSE()` 新增 `onWebSources` 回调参数
- 前端 `_mergeWebSources()` 将网络来源追加到 `aiSources` 末尾
- 前端 `renderAISources()` 支持网络来源：蓝色左边框（`.web-source`），Web badge 蓝色样式，AI 解读按钮
- 前端 `renderAISources()` 新增 "🌐 联网补充" 蓝色分隔线，清晰区分本地数据与网络搜索补充
- 前端引用 `[N]` 徽章新增 `title` 属性，hover 显示对应来源标题（辅助用户验证引用准确性）
- 无 URL 的网络来源卡片设为不可点击（`cursor:default`）
- `SOURCE_STYLES` 新增 `web_search` 条目：蓝色背景 + 蓝色文字 + "Web" 标签
- `.ai-source-card.web-source` CSS：`border-left: 2px solid rgba(59,130,246,.3)`
- Prompt 规则 9：联网搜索引用编号接在本地数据之后
- 网络来源卡片支持 AI 解读按钮（与本地来源一致）
- 刷新数据按钮在 AI 搜索视图和信息流视图均可见

### Changed
- `_process_web_sources()` 保留无 URL 条目（GLM 部分 web_search 结果缺少 link 字段），仅对有 URL 的条目写入数据库
- 刷新按钮移除 `feed-only-btn` 限制，两个视图均显示

### Known Issues
- GLM `web_search` 的 `refer` 字段是顺序 ID（ref_1, ref_2...），不与 AI 文本中的 `[N]` 引用编号对应。部分引用（如 `[1]`）可能指向联网搜索结果而非本地数据卡片 — 这是 GLM API 的固有限制，已通过 hover tooltip 缓解

## [0.10.0] - 2026-02-18

### Added
- **AI 搜索联网增强**：`_stream_glm()` 新增 `enable_search` 参数，启用 GLM `web_search` 工具实现实时联网搜索
- 三个 AI 端点（`/api/ai-search`、`/api/ai-analyze`、`/api/ai-latest`）全部开启联网搜索能力
- Prompt 新增联网搜索指引规则（规则 6-8）：优先本地数据，联网补充最新动态
- `QUERY_DOMAIN_MAP` 关键词→领域映射表：11 个领域，支持中英文关键词（如 'cloud'→'Cloud'、'安全'→'Security'）
- `_row_to_item()` 辅助函数：消除 SQLite row → dict 转换的重复代码
- `data/feeds.json` 新增 12 个 RSS 源（总计 16 个）：Dev.to、Product Hunt、Lobsters、InfoQ、ByteByteGo、Reddit r/programming + r/technology、少数派、TechNode、Fireship (YouTube)、ThePrimeagen (YouTube)、Bilibili 科技热搜 (RSSHub)

### Changed
- **本地搜索优化**：`search_items_for_ai()` 完全重写，四层搜索策略：
  - Layer 1: 中英文智能分词（`re.findall` 替代 `split()`）+ 中文 2 字滑窗
  - Layer 2: 每个 token 独立 LIKE OR 匹配（title/description/tags/domain）
  - Layer 3: 关键词自动推断领域，追加 `domain =` 精确匹配
  - Layer 4: 结果不足 5 条时热门文章兜底，确保用户总能看到内容
- `build_analysis_prompt()` 新增联网搜索指引（规则 6-7）
- `get_top_items()` 重构：使用 `_row_to_item()` 消除重复代码

## [0.9.0] - 2026-02-18

### Added
- **文章 AI 解读**：Feed 卡片和 AI 来源卡片底部新增「AI 解读」按钮，点击打开右侧滑出面板，流式展示 AI 深度分析
- **一键最新热点**：AI 搜索栏旁新增闪电「最新热点」按钮，一键获取热度 TOP 20 文章的 AI 总结
- 后端 `POST /api/ai-analyze` SSE 端点：单文章深度分析（核心概述→技术亮点→行业影响→潜在风险→趋势延伸）
- 后端 `POST /api/ai-latest` SSE 端点：查询 heat_index TOP 20 + AI 总结，发送 sources + streaming text
- 后端 `_stream_glm()` 共享异步生成器：封装 GLM API 调用 + SSE 输出，三个端点共用
- 后端 `build_analysis_prompt()` 文章分析专用 Prompt 构建函数
- 后端 `get_top_items()` 按热度查询 TOP N 文章
- 前端 `#ai-analyze-overlay` 侧滑面板：480px 宽（移动端全宽），含文章信息、流式 AI 分析、API Key 配置
- 前端 `_processSSE()` 共享 SSE 解析函数：`doAISearch`、`doLatestSearch`、`streamAnalysis` 三处复用
- 前端 `itemDataCache` 对象：缓存卡片 item 数据供 AI 解读面板使用
- 前端 `.btn-ai-analyze` 琥珀色小按钮样式
- 前端 `.ai-latest-btn` 闪电按钮样式
- i18n 新增键：aiAnalyzeBtn、aiAnalyzeTitle、aiAnalyzing、aiLatestBtn、aiLatestQuery（中英文）

### Changed
- `renderCard()` 重构：footer 区新增 AI 解读按钮，缓存 item 到 `itemDataCache`
- `renderAISources()` 重构：来源卡片从 `<a>` 改为 `<div>`（避免 `<a>` 内嵌按钮），新增 AI 解读按钮
- `doAISearch()` 重构：SSE 解析逻辑提取到 `_processSSE()` 共享函数
- `api_ai_search` 端点重构：GLM 流式代码提取到 `_stream_glm()` 共享函数
- `resetAISearch()` 更新：重置闪电按钮 disabled 状态

## [0.8.2] - 2026-02-18

### Changed
- **暖色主题重设计**：整体色调从冷色（indigo/slate）切换到暖色（amber/stone）
- 背景色改为暖灰 `#12110f`，文字色改为暖白 `#d4d0c8`
- 主强调色从 indigo-500 改为 amber-600 (`#d97706`)，Tab/按钮/搜索栏/引用徽章全部统一
- Glass-morphism 底色从冷蓝灰改为暖棕灰 `rgba(22,21,18,.7)`
- Ambient 背景光球从 indigo/violet 改为 amber/brown 渐变
- 领域配色全面调整：AI/ML 琥珀金、Security 暖黄、Web 暖灰、Mobile 橙色等
- 热度条配色：正常 `#b08d57`（暖铜）、高热 amber 渐变、低热 `#78716c`（暖灰）
- Tailwind 配置 surface 色板替换为暖色系

## [0.8.1] - 2026-02-18

### Added
- **API Key 管理 UI**：AI 搜索无 API Key 时自动显示配置面板，用户可直接在界面输入并保存 ZhipuAI API Key
- 后端 `GET/POST /api/ai-config` 端点：查询/保存 API Key，持久化到 `data/settings.json`
- `_runtime_api_key` 运行时 API Key 管理：环境变量 → settings 文件 → UI 设置三级来源
- 前端 `#ai-key-setup` 面板：Glass 风格卡片、密码输入框、保存按钮、状态提示
- `saveApiKey()` 函数：保存后自动重试之前的搜索
- `showAIError()` 增强：检测 `needsApiKey` 信号时显示配置面板而非通用错误
- i18n 新增键：aiKeyTitle、aiKeyDesc、aiKeySaveBtn、aiKeyPlaceholder、aiKeySaved、aiKeySaveError（中英文）

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
