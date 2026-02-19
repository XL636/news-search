# Changelog

本文件记录 InsightRadar 项目的所有变更。格式参考 [Keep a Changelog](https://keepachangelog.com/)。

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
