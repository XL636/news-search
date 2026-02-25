# InsightRadar 项目进度

> 每次新开 Claude 会话时必读此文件，快速了解项目当前状态。

## 项目概要

| 项 | 值 |
|----|-----|
| 项目 | InsightRadar — 全球创新与开源情报聚合系统 |
| 阶段 | MVP 完成 ✅ |
| 启动日期 | 2026-02-17 |
| 技术栈 | Python 3.14 / httpx / feedparser / pydantic / SQLite / FastAPI |

---

## 当前进度

### 整体进度：██████████████ 100%

| 模块 | 状态 | 进度 |
|------|------|------|
| 项目结构 | ✅ 完成 | 100% |
| 数据模型 (schemas.py) | ✅ 完成 | 100% |
| 存储层 (store.py) | ✅ 完成 | 100% |
| GitHub 采集器 | ✅ 完成 | 100% |
| HN 采集器 | ✅ 完成 | 100% |
| RSS 采集器 | ✅ 完成 | 100% |
| Pipeline CLI | ✅ 完成 | 100% |
| Skill: data-collect | ✅ 完成 | 100% |
| Skill: data-clean | ✅ 完成 | 100% |
| Skill: data-classify | ✅ 完成 | 100% |
| Skill: report-gen | ✅ 完成 | 100% |
| Skill: insight-radar | ✅ 完成 | 100% |
| 全功能测试 (test.md) | ✅ 完成 | 100% |
| 端到端全流程验证 | ✅ 完成 | 100% |
| Web Dashboard | ✅ 完成 | 100% |
| 中英文 i18n | ✅ 完成 | 100% |
| Dashboard 刷新数据 | ✅ 完成 | 100% |
| Dashboard UI 优化 | ✅ 完成 | 100% |
| Dashboard 翻译功能 | ✅ 完成 | 100% |
| MCP Server | ✅ 完成 | 100% |
| Skill: mcp-digest | ✅ 完成 | 100% |
| report-gen v2 (Word + 领域模板) | ✅ 完成 | 100% |
| Dashboard v3 视觉重设计 | ✅ 完成 | 100% |
| Dashboard AI 搜索功能 | ✅ 完成 | 100% |
| API Key 管理 UI | ✅ 完成 | 100% |
| Dashboard 暖色主题 | ✅ 完成 | 100% |
| 文章 AI 解读功能 | ✅ 完成 | 100% |
| 一键最新热点功能 | ✅ 完成 | 100% |
| 后端/前端 GLM+SSE 重构 | ✅ 完成 | 100% |
| AI 搜索联网增强 (web_search) | ✅ 完成 | 100% |
| 本地搜索优化 (智能分词) | ✅ 完成 | 100% |
| RSS 数据源扩充 (16 源) | ✅ 完成 | 100% |
| AI 搜索虚假引用修复 + 网络结果回存 | ✅ 完成 | 100% |
| 网络来源展示优化 (分隔线+tooltip) | ✅ 完成 | 100% |
| AI 搜索视图翻译功能 | ✅ 完成 | 100% |
| AI 搜索引用准确性修复 | ✅ 完成 | 100% |
| AI 搜索引用内容匹配 (v2) | ✅ 完成 | 100% |
| Dashboard Premium UI 升级 | ✅ 完成 | 100% |
| Dashboard 背景微调提亮 | ✅ 完成 | 100% |
| Dashboard UI/UX Accessibility 优化 | ✅ 完成 | 100% |
| Dashboard 视觉美化 (Visual Beautification) | ✅ 完成 | 100% |
| 结构化日志 (JSON Logging) | ✅ 完成 | 100% |
| 单元测试框架 (pytest) | ✅ 完成 | 100% |
| Pre-commit Hooks (ruff) | ✅ 完成 | 100% |
| DB 上下文管理器 (get_db) | ✅ 完成 | 100% |
| 路由拆分 (APIRouter) | ✅ 完成 | 100% |
| 统一错误响应 (ErrorResponse) | ✅ 完成 | 100% |
| Pydantic Settings 配置 | ✅ 完成 | 100% |
| 数据过期清理 (TTL) | ✅ 完成 | 100% |
| 健康检查端点 (/api/health) | ✅ 完成 | 100% |
| WebSocket 实时推送 (/api/ws) | ✅ 完成 | 100% |
| 用户偏好持久化 (/api/preferences) | ✅ 完成 | 100% |
| 数据导出 (/api/export) | ✅ 完成 | 100% |
| RSS 源健康监控 (/api/feed-health) | ✅ 完成 | 100% |
| 全文搜索 FTS5 | ✅ 完成 | 100% |
| ArXiv 论文采集器 | ✅ 完成 | 100% |
| 热度趋势追踪系统 | ✅ 完成 | 100% |
| 自动调度器 (APScheduler) | ✅ 完成 | 100% |
| 异步数据库 (aiosqlite) | ✅ 完成 | 100% |
| 内存 TTL 缓存 (cachetools) | ✅ 完成 | 100% |
| Docker 容器化 | ✅ 完成 | 100% |
| CI/CD Pipeline (GitHub Actions) | ✅ 完成 | 100% |
| 性能监控 (OpenTelemetry) | ✅ 完成 | 100% |
| API 速率限制 (slowapi) | ✅ 完成 | 100% |
| WebSocket 前端自动刷新 | ✅ 完成 | 100% |
| 一键导出按钮 | ✅ 完成 | 100% |
| 用户偏好同步 | ✅ 完成 | 100% |
| RSS 源健康监控前端 | ✅ 完成 | 100% |
| 系统状态指示 | ✅ 完成 | 100% |
| 全文搜索 API (FTS5) | ✅ 完成 | 100% |
| 单篇文章导出按钮 | ✅ 完成 | 100% |
| AI 对话讨论功能 | ✅ 完成 | 100% |
| Docker 本地部署验证 | ✅ 完成 | 100% |
| 导出全文抓取 + AI 引用修复 | ✅ 完成 | 100% |
| WebSocket + favicon 404 修复 | ✅ 完成 | 100% |
| 图片搜文章功能 (GLM-4.6V-Flash) | ✅ 完成 | 100% |
| Bug 修复 (WS泄漏/竞态/DB连接) | ✅ 完成 | 100% |
| 安全加固 (CORS/错误隐藏/Docker) | ✅ 完成 | 100% |
| 前端性能 (itemDataCache LRU) | ✅ 完成 | 100% |

### 图片搜文章 + 全面优化 (v0.24.0) — 2026-02-25

```
新功能：图片搜文章
  架构：图片 → GLM-4.6V-Flash 提取关键词(非流式) → 搜本地库 → GLM-4-Plus 分析推荐(流式 SSE)
  后端：POST /api/ai-image-search + _call_glm_sync() + build_image_extract_prompt() + build_image_search_prompt()
  前端：图片上传按钮 + 预览条 + Canvas 压缩(>2MB 缩放 1200px JPEG 0.8) + 关键词标签
  SSE 新事件：image_analysis（关键词+摘要）

Bug 修复：
  WebSocket broadcast() 连接泄漏 → 失败连接批量断开
  收集端点竞态条件 → asyncio.wait_for 非阻塞获取 + HTTP 409
  DB 连接泄漏 → search_items_for_ai/get_top_items/process_web_sources 改用 with get_db()

安全加固：
  CORS: allow_origins ["*"] → ALLOWED_ORIGINS 环境变量，默认 localhost:8000
  错误响应: 生产环境隐藏详细 traceback，仅记录日志
  Docker: HEALTHCHECK 30s + 非 root appuser 用户
  CSP: img-src 增加 blob: 支持

性能优化：
  itemDataCache LRU 上限 200 条，超出清除最早 50 条
```

### 最近一次全流程运行（2026-02-17）

```
采集：186 条 raw_items（GitHub 30 + HN 63 + RSS 93）
清洗：186 → 119 条（去除 58 条过旧 + 9 组跨平台合并）
分类：119 条全部标注（10 个领域，平均热度 33.6）
日报：output/digests/2026-02-17-digest.md 已生成
```

### report-gen v2 改造（2026-02-18）

```
输出格式：Markdown → Word 文档 (.docx)
报告模式：3 种（全领域概览 / 预定义领域 / 自定义关键词）
领域模板：13 个 references/template-*.md
docx 脚本：generate_docx.py（Calibri 字体、深蓝主题、表格样式）
新增依赖：python-docx>=1.1
```

### 首次 AI Coding 报告生成（2026-02-18）

```
报告类型：自定义关键词 (AI coding)
数据来源：MCP 等效接口 → SQLite classified_items
匹配条目：55 条（关键词: ai, coding）
章节结构：执行摘要 → AI 编程工具 → 代码生成模型 → Vibe Coding → 开源争议 → 投融资
输出文件：output/digests/2026-02-18-ai-coding-report.docx (40KB)
```

### Dashboard v3 视觉重设计（2026-02-18）

```
布局：侧边栏（KPI + 领域导航）+ 主内容区（搜索 + 3列卡片网格）
设计：Glass-morphism 效果、ambient 渐变背景球、Inter 字体
KPI：原始采集/清洗/分类 三个统计卡片
卡片：渐变热度条、热度发光点、星标/评论图标、line-clamp 截断
响应式：xl 3列 / md 2列 / sm 1列，移动端域名 chips 替代侧边栏
```

### Dashboard AI 搜索功能（2026-02-18）

```
后端：POST /api/ai-search SSE 流式端点 + ZhipuAI GLM-4-Plus
搜索：SQL LIKE 分词匹配 classified_items，按 heat_index DESC
流式：httpx.AsyncClient.stream() → SSE (sources → text chunks → done)
并发：asyncio.Semaphore(3) 限制最多 3 个并发搜索
前端：双视图 Tab（AI 搜索 / 信息流），默认 AI 搜索
UI：Perplexity 风格 — hero 欢迎语 + 建议 chips + 流式 Markdown + [N] 引用徽章 + 来源卡片
渲染：轻量 regex Markdown 解析 + streaming cursor 动画
```

### API Key 管理 UI（2026-02-18）

```
后端：GET/POST /api/ai-config 查询/保存 API Key
存储：data/settings.json 持久化，环境变量优先
前端：#ai-key-setup 配置面板 — Glass 风格卡片、密码输入框、保存/状态提示
流程：无 key 搜索 → needsApiKey → 显示面板 → 保存 → 自动重试搜索
i18n：中英双语（aiKeyTitle/aiKeyDesc/aiKeySaveBtn/aiKeyPlaceholder/aiKeySaved/aiKeySaveError）
```

### Dashboard 暖色主题（2026-02-18）

```
色调：冷色（indigo/slate）→ 暖色（amber/stone）
背景：#12110f 暖深灰，Glass rgba(22,21,18,.7)
强调色：amber-600 (#d97706) 统一 Tab/按钮/引用
文字：#d4d0c8 暖白 + #a8a29e 暖灰副文字
光球：amber #d97706 + brown #92400e ambient 渐变
领域色：AI/ML 琥珀金、Security 暖黄、DevTools 暖绿、Web 暖灰
热度：正常 #b08d57 暖铜、高热 amber 渐变、低热 #78716c
```

### 文章 AI 解读 + 一键最新热点（2026-02-18）

```
文章解读：卡片底部 AI 解读按钮 → 右侧滑出 480px 面板 → 流式 AI 分析
  后端：POST /api/ai-analyze SSE（核心概述→技术亮点→行业影响→潜在风险→趋势延伸）
  前端：#ai-analyze-overlay 侧滑面板 + streamAnalysis() + closeAnalyzePanel()

最新热点：搜索栏旁闪电按钮 → heat_index TOP 20 → AI 总结
  后端：POST /api/ai-latest SSE（get_top_items → build_ai_prompt → _stream_glm）
  前端：doLatestSearch() 复用 _processSSE() 共享 SSE 解析

重构：
  后端：_stream_glm() 共享 GLM 流式生成器，三端点复用
  前端：_processSSE() 共享 SSE 解析，三处复用
  前端：itemDataCache 缓存卡片数据，renderAISources 改为 <div>
```

### AI 搜索虚假引用修复 + 网络来源展示优化（2026-02-19）

```
问题：GLM web_search 联网后回答引用 [N] 可能指向网络结果，但前端只显示本地来源卡片
修复（后端）：
  _stream_glm()：捕获 GLM 返回的 web_search 字段，累积到 web_results 列表
  _process_web_sources()：分类（URL域名+关键词双层）→ insert_web_search_item() 存库
    保留无 URL 的 web 结果（GLM 部分结果缺少 link），含 refer 字段传递
  classify_web_result_domain()：URL 匹配（github→DevTools, arxiv→AI/ML 等）+ 关键词匹配
  insert_web_search_item()：三表写入（raw→cleaned→classified），URL 去重，heat_index=30
  init_db()：新增 idx_raw_url + idx_classified_url 索引
修复（前端）：
  _processSSE()：新增 onWebSources 回调处理 web_sources SSE 事件
  _mergeWebSources()：网络来源追加到 aiSources 末尾
  renderAISources()："🌐 联网补充" 蓝色分隔线 + 蓝色左边框 + Web badge
  renderMarkdown()：引用 [N] 新增 title tooltip 显示对应来源标题
  无 URL 卡片设为不可点击（cursor:default）
  SOURCE_STYLES 新增 web_search 样式（蓝色）
  网络来源卡片支持 AI 解读按钮（与本地来源体验一致）
  刷新按钮从信息流专属改为双视图共享
已知限制：
  GLM refer 字段为顺序 ID（ref_1, ref_2），不直接对应 AI 文本 [N] 编号
  ~~部分引用可能指向联网结果而非对应本地卡片~~ ✅ 已通过内容匹配修复（v0.13.0）
  前端 tokenize + computeMatchScore 按上下文关键词与来源标题打分匹配
```

### 中期优化三连发（2026-02-19）

```
ArXiv 采集器：src/collectors/arxiv.py
  API: https://export.arxiv.org/api/query
  类别：cs.AI, cs.LG, cs.CL, cs.SE
  解析：feedparser Atom XML → RawItem 映射
  注册：pipeline.py COLLECTORS + config.py 配置常量
  前端：SOURCE_STYLES 紫色风格 + i18n '论文'/'Paper'

热度趋势追踪：完整垂直切片（DB → API → UI）
  DB: heat_snapshots 表 + take_daily_snapshot() + get_trending_items() + get_item_trend()
  API: GET /api/trends?days=3&limit=20 + POST /api/snapshot
  前端：侧边栏 TOP 5 趋势项（↑/↓/→ 标记 + 迷你热度条）+ i18n

自动调度：APScheduler AsyncIOScheduler
  模块：src/scheduler.py（start/stop/status）
  Job 1: 每日 08:00 UTC 全源采集
  Job 2: 每日 08:30 UTC 热度快照
  配置：data/settings.json (schedule_collect_hour/minute)
  集成：FastAPI lifespan startup/shutdown
  API: GET /api/scheduler 状态查询
  前端：侧边栏底部调度状态（绿色运行指示灯 + 下次采集时间）
  依赖：apscheduler>=3.10

数据源扩充：feeds.json 新增 Medium Tech RSS
```

### Dashboard 视觉美化 Visual Beautification（2026-02-20）

```
字体升级：Inter + JetBrains Mono → Fira Sans + Fira Code
  Fira Sans：分析型 dashboard 专业字体，300-700 粗细
  Fira Code：连字支持，KPI/热度等数字场景

维度层级系统：4级 Elevation 阴影
  --elevation-1: 卡片静态
  --elevation-2: KPI卡片/悬停中间态
  --elevation-3: 卡片悬停/重要面板
  --elevation-4: 模态框/AI解读侧滑面板

KPI Bento Grid：
  1列→2列 bento 布局，首行跨列
  每个 KPI 新增图标（下载/过滤/标签）+ 渐变强调条
  stagger 入场动画（0ms/80ms/160ms）
  count-up 数字计数动画

玻璃态增强：
  .glass/.glass-light 顶部边缘高光渐变
  header 模糊 20px→24px
  --border-subtle 透明度 .06→.08
  第三光球 orb-3（暖琥珀，右下）

AI 搜索视觉升级：
  Hero 双层放射状光晕 + 呼吸动画
  搜索框 conic-gradient 旋转发光边框
  建议芯片玻璃磨砂效果
  AI 回答面板左侧 amber 渐变色条

卡片视觉打磨：
  默认 elevation-1，hover 升 elevation-3 + scale(1.005)
  顶部高光线白色→amber 渐变
  hover 暖色 amber wash 内发光
  来源徽章→圆角药丸 + 模糊背景
  标签→圆角药丸 + 更柔和背景

渐变升级：3-stop CTA 渐变
  所有 amber 按钮/激活态：#fbbf24 → #d97706 → #b45309

侧边栏升级：
  区块间渐变分隔线
  标题玻璃磨砂背景
  域名项 hover 左侧内发光
  趋势方向彩色 SVG 箭头 + 背景色调

微交互：
  Toast spring 弹性动画 + elevation-3
  滚动条 amber hover 色调
  空态暖色渐变图标
```

### Dashboard UI/UX Accessibility 优化（2026-02-20）

```
Accessibility:
  prefers-reduced-motion: @media block 禁用所有装饰动画（orb/hero/heat/card/skeleton/cursor/toast）
  focus-visible: 所有交互元素 2px amber outline（按钮/Tab/chips/域名/输入框/链接）
  aria-labels: icon-only 按钮添加 i18n-aware aria-label（刷新/翻译/关闭/搜索）
  键盘导航: 侧边栏 domain-item 添加 tabindex="0" + role="button" + Enter/Space handler

UI Polish:
  z-index: body::before 噪点纹理 9999 → 1
  emoji→SVG: 联网来源分隔线 🌐 → inline SVG globe
  动画减弱: orb 透明度 .15→.12，hero 浮动 6s→8s
  卡片交互: hover translateY(-2px) 上浮 + 热门卡片柔和光晕
  搜索框: focus-within scale(1.01) 微放大
  排版: card-title letter-spacing -0.01em，kpi-value letter-spacing -0.02em

Round 2（UI/UX Pro Max Skill 审计修复）:
  aria-live: AI 回答面板 polite + Toast 容器 status + 错误区 alert
  skip-nav: 键盘用户 "Skip to content" 链接（sr-only + focus 可见）
  form labels: 所有 input/select 添加 i18n aria-label（5 个表单控件）
  aria-hidden: 装饰元素（光球/hero 图标/搜索图标/header SVG）标记隐藏
  role landmarks: role="search" 搜索框 + role="status" 调度状态
  触屏优化: AI 解读按钮 opacity 0→.45（触屏可见）
  outline 修复: select focus 添加 ring 替代 outline-none
```

### Dashboard Premium UI 全面升级（2026-02-19）

```
目标：Vercel/Linear 级设计质感
设计令牌：:root CSS 变量系统（颜色/边框/阴影/圆角/动效/时长）
字体：JetBrains Mono（KPI/热度/引用等数字场景）
纹理：body::before SVG feTurbulence 噪点
光球：radial-gradient + orbDrift 20s 缓慢漂移
卡片：顶部高光线 + hover shadow 上升 + AI 解读按钮渐显 + 热门红色光晕
入场：card-stagger 40ms 延迟 + requestAnimationFrame
骨架：结构化（域名条+标题行+描述行+热度条+badge）
AI 搜索：hero 浮动+呼吸 + 搜索框三层光晕 + chips 上浮 + wave 弹跳
引用：JetBrains Mono + border + hover 上浮 + 来源卡片高亮动画
侧边栏：active 左侧 2px amber 指示条 + 标题 10px 大写
全局：Toast blur 入场 + Tab gradient + 分析面板 backdrop-blur
```

### AI 搜索联网增强 + 本地搜索优化 + 数据源扩充（2026-02-18）

```
联网搜索：_stream_glm() 新增 enable_search 参数，启用 GLM web_search 工具
  三端点（ai-search / ai-analyze / ai-latest）均开启联网搜索
  Prompt 增加联网搜索指引（优先本地数据，联网补充最新动态）

本地搜索优化：search_items_for_ai() 完全重写
  Layer 1: 中英文智能分词 re.findall + 2 字滑窗
  Layer 2: 每个 token LIKE OR 匹配
  Layer 3: QUERY_DOMAIN_MAP 领域映射（11 个领域，中英文关键词）
  Layer 4: 结果不足 5 条时热门兜底
  提取 _row_to_item() 消除 row→dict 重复代码

数据源扩充：feeds.json 从 4 个源扩充到 16 个
  新增：Dev.to / Product Hunt / Lobsters / InfoQ / ByteByteGo
  新增：Reddit r/programming + r/technology
  新增：少数派 / TechNode
  新增：Fireship + ThePrimeagen (YouTube RSS)
  新增：Bilibili 科技热搜 (RSSHub)
```

---

## 里程碑

### M1: MVP — 端到端日报生成
- **目标**：运行 `/insight-radar` 产出一份完整 Markdown 日报
- **完成标准**：
  - [x] 至少 2 个数据源的真实数据
  - [x] 无明显重复条目（9 组跨平台合并 + 58 条过旧过滤）
  - [x] 每条均有领域分类和热度评分（10 个领域，0-100 热度）
  - [x] 执行摘要可读且有信息价值
- **状态**：✅ MVP 完成！首份日报已生成

### M2: 优化迭代 ✅ 完成
- ~~GitHub Token 认证~~ ✅ 已完成
- ~~错误重试机制~~ ✅ 已完成（max_retries=3 + 指数退避）
- ~~RSS 源可配置化~~ ✅ 已完成（data/feeds.json）
- ~~增量采集~~ ✅ 已完成（collect_meta 表）

### M3: 功能扩展 ✅ 完成
- ~~更多数据源~~ ✅ 已完成（ArXiv 采集器 + Medium RSS + 共 17 个 RSS 源）
- ~~Web 界面~~ ✅ 已完成（FastAPI Dashboard + 中英文 i18n）
- ~~Dashboard v2~~ ✅ 已完成（刷新按钮 + UI 优化 + 分页 + 翻译功能）
- ~~Dashboard v3~~ ✅ 已完成（全面视觉重设计：侧边栏 + KPI + Glass-morphism + 3列响应式）
- ~~热度趋势追踪~~ ✅ 已完成（heat_snapshots + API + 侧边栏趋势区块）
- ~~定时调度~~ ✅ 已完成（APScheduler + FastAPI 集成 + 调度状态 UI）

---

## 已知问题

| # | 问题 | 严重度 | 状态 |
|---|------|--------|------|
| 1 | ~~GitHub API 无认证，速率限制 60 次/h~~ | 低 | ✅ 已修复，使用 GITHUB_PERSONAL_ACCESS_TOKEN |
| 2 | ~~`datetime.utcnow()` 弃用警告~~ | 低 | ✅ 已修复，全局替换为 `datetime.now(timezone.utc)` |

---

## 下一步行动

1. ~~修复 Skill 注册问题~~ (P2, 待排查)
2. ~~Phase 1: Tier 1 快速修复~~ ✅ 已完成
3. ~~Phase 2: Tier 2 代码质量~~ ✅ 已完成
4. ~~Phase 3-4: Tier 3 功能增强~~ ✅ 已完成
5. ~~Phase 5-6: Tier 4 架构演进~~ ✅ aiosqlite/cachetools/Docker/CI-CD/OpenTelemetry/slowapi
6. **全部 27 项优化已完成** — 项目进入维护阶段

---

## 下一阶段：优化路线图

> 全面审计后整理出 4 层 27 项优化，分 6 个 Phase 渐进执行。

| Phase | 内容 | 任务数 | 优先级 | 预期效果 |
|-------|------|--------|--------|----------|
| Phase 1 | Tier 1 快速修复 | 7 | P1 | 消除 deprecation 警告、安全加固、性能基线 |
| Phase 2 | Tier 2 代码质量 | 7 | P2 | 可维护性提升、测试覆盖、开发规范 |
| Phase 3 | Tier 3 功能增强 (前半) | 4 | P2 | 数据生命周期管理、健康监控、导出 |
| Phase 4 | Tier 3 功能增强 (后半) | 3 | P2 | 实时推送、全文搜索、用户偏好 |
| Phase 5 | Tier 4 架构演进 (前半) | 3 | P3 | 异步 DB、缓存层、容器化 |
| Phase 6 | Tier 4 架构演进 (后半) | 3 | P3 | CI/CD、性能监控、速率限制 |

### Tier 2 代码质量改造（2026-02-20）

```
路由拆分：server.py 809→114 行
  src/routers/__init__.py — 空初始化
  src/routers/ai.py (514 行) — AI 搜索/分析/最新/配置端点
  src/routers/data.py (343 行) — 数据/统计/采集/趋势/健康/WS/偏好/导出/RSS
  src/routers/translate.py (54 行) — 翻译端点
  src/routers/errors.py (25 行) — ErrorResponse + exception handlers

统一错误响应：ErrorResponse Pydantic model + 全局 exception handlers
Pydantic Settings：src/settings.py — BaseSettings + env_prefix
DB 上下文管理器：store.py get_db() @contextmanager 自动关闭
结构化日志：src/logging_config.py — JSONFormatter + setup_logging()
单元测试：pytest 14 tests (store/schemas/config) 全部通过
Pre-commit：ruff lint + format + .pre-commit-config.yaml
```

### Tier 3 功能增强（2026-02-20）

```
数据过期清理：cleanup_old_data(conn, days=30) — 5 表定期清理
健康检查：GET /api/health — DB连接/调度器/采集器状态
WebSocket：GET /api/ws — ConnectionManager + JSON broadcast 实时推送
用户偏好：GET/POST /api/preferences — settings.json 后端持久化
数据导出：GET /api/export?format=json|csv — 一键下载 classified_items
RSS 健康：GET /api/feed-health — 各 RSS 源成功率/延迟监控
全文搜索：classified_items_fts FTS5 虚拟表 + 3 sync triggers + search_fts()
  init_db() 自动创建 FTS 表/触发器 + rebuild_fts_index()
```

### Tier 4 架构演进 — 异步 DB + OpenTelemetry（2026-02-20）

```
异步数据库 (aiosqlite):
  store.py 新增 14 个 async 函数（aget_db/aget_connection/ainit_db/aget_classified_items/
    aget_stats/aget_domains/asearch_fts/aget_trending_items/aget_item_trend/
    aget_feed_health/aget_export_items/aget_translation/asave_translation）
  所有 sync 函数保持不变，CLI/scheduler 继续使用同步版本
  路由端点全面 async 化：
    data.py: api_domains/api_items/api_stats/api_trends/api_health/api_export/api_feed_health
    translate.py: api_translate
    ai.py: asearch_items_for_ai/aget_top_items（async 版本 + 端点生成器调用）
  依赖：aiosqlite>=0.20

OpenTelemetry 性能监控:
  src/telemetry.py: setup_telemetry(app)
    TracerProvider + Resource(service.name=insightradar)
    ConsoleSpanExporter (dev mode, 可替换为 OTLP)
    FastAPIInstrumentor 自动追踪所有 HTTP 请求
  server.py lifespan: 启动时调用 setup_telemetry(app)
  依赖：opentelemetry-api/sdk/instrumentation-fastapi

版本：0.19.0 → 0.20.0
测试：14 个 pytest 测试全部通过
```

### Tier 4 架构演进 — Docker + CI/CD + 缓存 + 限流（2026-02-20）

```
Docker 容器化:
  Dockerfile: multi-stage build, python:3.12-slim, requirements layer cache
  docker-compose.yml: web service port 8000, ./data volume, env vars
  .dockerignore: 排除 .venv/__pycache__/.git/tests/*.png

CI/CD Pipeline:
  .github/workflows/ci.yml: push/PR 触发
  Job 1: ruff check + ruff format --check (lint)
  Job 2: pytest --tb=short (test, depends on lint)
  Python 3.12 + pip cache

API 速率限制 (slowapi):
  SlowAPIMiddleware + get_remote_address 客户端 IP 识别
  AI 端点: 10/minute (ai-search/ai-analyze/ai-latest)
  读端点: 120/minute (items/domains/stats/trends)
  写端点: 5/minute (collect/snapshot)
  429 RateLimitExceeded JSON 响应

内存 TTL 缓存 (cachetools):
  src/cache.py: 三级 TTLCache
  stats_cache: maxsize=100, ttl=60s
  items_cache: maxsize=50, ttl=30s
  trends_cache: maxsize=10, ttl=120s
  采集/快照后自动 invalidate()
```

### 前端 API 对接 (v0.21.0) — 2026-02-20

```
WebSocket 前端自动刷新:
  Header logo 旁绿色脉冲指示灯（连接中/已连接/已断开三态）
  采集完成 WebSocket 消息触发自动刷新页面数据
  断线指数退避重连（1s→2s→4s→...→30s 上限）

一键导出按钮:
  Header 导出按钮 + glass 风格 CSV/JSON 下拉菜单
  点击触发浏览器下载 /api/export?format=csv|json

用户偏好同步:
  页面加载时 GET /api/preferences 应用服务器偏好（语言/排序/视图/PAGE_SIZE）
  切换语言/排序/视图时自动 POST /api/preferences 保存到服务器

RSS 源健康监控前端:
  侧边栏新增数据源状态区块
  GET /api/feed-health 获取各源状态
  绿/黄/红状态点实时显示源健康度

系统状态指示:
  Logo 旁 8px 状态点（绿色=健康/黄色=降级/红色=异常）
  /api/health 60 秒轮询 + tooltip 显示详情

全文搜索 API:
  新增 GET /api/search FTS5 端点（routers/data.py）
  前端信息流搜索优先使用 FTS，fallback 到 LIKE
  PAGE_SIZE 从 const 改为 let，支持偏好动态设置
  15 个新增 i18n 键（中英文）
```

### 单篇导出 + AI 对话讨论 (v0.22.0) — 2026-02-20

```
单篇文章导出:
  删除 Header 全局导出按钮 (export-dropdown-wrap + toggleExportDropdown + doExport)
  每张卡片 footer 新增「导出」按钮（renderCard + renderAISources）
  纯前端 Markdown 生成: exportSingleArticle() → Blob → download
  格式: 标题/领域/热度/Stars/来源/标签/URL/描述

AI 对话讨论:
  后端: POST /api/ai-chat SSE 端点
    AIChatRequest (article + initial_analysis + messages)
    build_chat_prompt(): system → 文章上下文 → 初始分析 → 对话历史
    复用 _stream_glm() + _ai_search_semaphore + limiter 10/min
  前端: 面板底部固定输入框 + 对话气泡
    streamAnalysis() onDone → 保存分析全文 → 显示输入框
    sendChatMessage() → POST /api/ai-chat → SSE 流式渲染
    .chat-bubble.user (右对齐 amber) / .chat-bubble.assistant (左对齐 glass)
    关闭面板 / 重新打开 → 对话重置
```

### 当前状态
- **Phase 1**: ✅ 已完成（Tier 1 快速修复 7 项 — 2026-02-20）
- **Phase 2**: ✅ 已完成（Tier 2 代码质量 7 项 — 2026-02-20）
- **Phase 3-4**: ✅ 已完成（Tier 3 功能增强 7 项 — 2026-02-20）
- **Phase 5-6**: ✅ 已完成（Tier 4 架构演进 6 项 — 2026-02-20）
