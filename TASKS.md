# InsightRadar 任务追踪

> 每次新开 Claude 会话时必读此文件，了解当前待办和优化方向。

## 当前任务状态

### 已完成 ✅

| # | 任务 | 完成日期 | 备注 |
|---|------|----------|------|
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

### 进行中 🔄

| # | 任务 | 开始日期 | 状态 |
|---|------|----------|------|
| — | 暂无 | — | — |

### 待办 📋

| # | 任务 | 优先级 | 说明 |
|---|------|--------|------|
| 16 | 修复 Skill 注册问题 | P2 | YAML frontmatter 格式正确但 Claude Code 未加载 |

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

5. **更多数据源**
   - Product Hunt API
   - Reddit r/programming
   - ArXiv 论文（AI 领域）
   - Dev.to / Medium 技术博客

6. **热度趋势追踪**
   - 多日数据对比，识别上升/下降趋势
   - 需要 classified_items 增加 `date` 索引

7. **~~Web 界面~~** ✅ 已完成（含 v2 升级）
   - FastAPI 后端 `src/server.py` + 前端 `src/static/index.html`
   - 领域过滤、搜索、多排序、暗色主题
   - v2: 刷新数据按钮、分页加载更多、翻译功能、UI 优化（2列布局、卡片重设计）

8. **定时调度**
   - 系统级 cron / Windows Task Scheduler
   - 每日自动采集 + 生成报告

### 长期优化（规模化）

9. **用户个性化**
   - 根据用户关注领域定制日报内容
   - 关键词订阅 + 推送通知

10. **多语言支持**（部分完成）
    - ~~Dashboard UI 中英文切换~~ ✅ 已完成
    - 日报支持中英文双版本
    - 数据源支持日文/韩文技术社区
