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

### AI 搜索虚假引用修复 + 网络结果回存（2026-02-19）

```
问题：GLM web_search 联网后回答引用 [N] 可能指向网络结果，但前端只显示本地来源卡片
修复：
  _stream_glm()：捕获 GLM 返回的 web_search 字段，累积到 web_results 列表
  _process_web_sources()：分类（URL域名+关键词双层）→ insert_web_search_item() 存库
  classify_web_result_domain()：URL 匹配（github→DevTools, arxiv→AI/ML 等）+ 关键词匹配
  insert_web_search_item()：三表写入（raw→cleaned→classified），URL 去重，heat_index=30
  init_db()：新增 idx_raw_url + idx_classified_url 索引
  前端 _processSSE()：新增 onWebSources 回调处理 web_sources SSE 事件
  前端 renderAISources()：网络来源卡片蓝色左边框 + Web badge，无 AI 解读按钮
  SOURCE_STYLES 新增 web_search 样式（蓝色）
  Prompt 规则 9：联网搜索引用编号接在本地数据之后
  网络来源卡片支持 AI 解读按钮（与本地来源体验一致）
  刷新按钮从信息流专属改为双视图共享，AI 搜索界面可直接刷新数据
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

### M3: 功能扩展（进行中）
- 更多数据源
- ~~Web 界面~~ ✅ 已完成（FastAPI Dashboard + 中英文 i18n）
- ~~Dashboard v2~~ ✅ 已完成（刷新按钮 + UI 优化 + 分页 + 翻译功能）
- ~~Dashboard v3~~ ✅ 已完成（全面视觉重设计：侧边栏 + KPI + Glass-morphism + 3列响应式）
- 定时调度

---

## 已知问题

| # | 问题 | 严重度 | 状态 |
|---|------|--------|------|
| 1 | ~~GitHub API 无认证，速率限制 60 次/h~~ | 低 | ✅ 已修复，使用 GITHUB_PERSONAL_ACCESS_TOKEN |
| 2 | `datetime.utcnow()` 弃用警告（schemas.py 中） | 低 | models 层仍用 utcnow，pipeline 已修复 |

---

## 下一步行动

1. 修复 Skill 注册问题（SKILL.md frontmatter 正确但 Claude Code 未加载）
2. 进入 M3 功能扩展：更多数据源、定时调度等
