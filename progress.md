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

### 最近一次全流程运行（2026-02-17）

```
采集：186 条 raw_items（GitHub 30 + HN 63 + RSS 93）
清洗：186 → 119 条（去除 58 条过旧 + 9 组跨平台合并）
分类：119 条全部标注（10 个领域，平均热度 33.6）
日报：output/digests/2026-02-17-digest.md 已生成
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
