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

### 进行中 🔄

| # | 任务 | 开始日期 | 状态 |
|---|------|----------|------|
| — | 暂无 | — | — |

### 待办 📋

| # | 任务 | 优先级 | 说明 |
|---|------|--------|------|
| 10 | 端到端全流程验证 | P0 | 运行 `/insight-radar` 产出完整日报 |

---

## 优化方案

### 短期优化（MVP 阶段可做）

1. **GitHub Token 支持**
   - 当前未使用认证，API 速率限制 60 次/小时
   - 方案：在 `config.py` 增加环境变量 `GITHUB_TOKEN`，通过 Header 传递
   - 收益：速率限制提升到 5000 次/小时

2. **采集器错误重试**
   - 当前单次失败即跳过
   - 方案：在 `BaseCollector` 中增加 `max_retries` + 指数退避
   - 收益：网络波动时更稳定

3. **RSS 源可配置化**
   - 当前硬编码 4 个 RSS 源
   - 方案：将 RSS 源列表移到 `data/feeds.json` 或 `.env` 文件
   - 收益：用户可自定义关注的信息源

4. **增量采集优化**
   - 当前每次全量采集，靠 UNIQUE 约束去重
   - 方案：记录各数据源最后采集时间，仅获取增量
   - 收益：减少 API 调用，加快采集速度

### 中期优化（MVP 后）

5. **更多数据源**
   - Product Hunt API
   - Reddit r/programming
   - ArXiv 论文（AI 领域）
   - Dev.to / Medium 技术博客

6. **热度趋势追踪**
   - 多日数据对比，识别上升/下降趋势
   - 需要 classified_items 增加 `date` 索引

7. **Web 界面**
   - 简单的 Flask/FastAPI 服务 + HTML 页面
   - 展示日报 + 历史趋势图表

8. **定时调度**
   - 系统级 cron / Windows Task Scheduler
   - 每日自动采集 + 生成报告

### 长期优化（规模化）

9. **用户个性化**
   - 根据用户关注领域定制日报内容
   - 关键词订阅 + 推送通知

10. **多语言支持**
    - 日报支持中英文双版本
    - 数据源支持日文/韩文技术社区
