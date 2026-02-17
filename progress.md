# InsightRadar 项目进度

> 每次新开 Claude 会话时必读此文件，快速了解项目当前状态。

## 项目概要

| 项 | 值 |
|----|-----|
| 项目 | InsightRadar — 全球创新与开源情报聚合系统 |
| 阶段 | MVP 开发中 |
| 启动日期 | 2026-02-17 |
| 技术栈 | Python 3.14 / httpx / feedparser / pydantic / SQLite |

---

## 当前进度

### 整体进度：████████████░░ 85%

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
| 端到端全流程验证 | ⏳ 待验证 | 0% |

### 最近一次测试结果（2026-02-17）

```
采集数据：164 条
  - GitHub:      30 repos
  - HackerNews:  54 stories
  - RSS:         80 articles
清洗/分类/报告：尚未运行
```

---

## 里程碑

### M1: MVP — 端到端日报生成
- **目标**：运行 `/insight-radar` 产出一份完整 Markdown 日报
- **完成标准**：
  - [x] 至少 2 个数据源的真实数据
  - [ ] 无明显重复条目
  - [ ] 每条均有领域分类和热度评分
  - [ ] 执行摘要可读且有信息价值
- **状态**：采集管道已就绪，待运行全流程验证

### M2: 优化迭代（未开始）
- GitHub Token 认证
- 错误重试机制
- RSS 源可配置化
- 增量采集

### M3: 功能扩展（未开始）
- 更多数据源
- Web 界面
- 定时调度

---

## 已知问题

| # | 问题 | 严重度 | 状态 |
|---|------|--------|------|
| 1 | GitHub API 无认证，速率限制 60 次/h | 低 | 待优化 |
| 2 | `datetime.utcnow()` 弃用警告（schemas.py 中） | 低 | models 层仍用 utcnow，pipeline 已修复 |

---

## 下一步行动

1. **立即**：运行 `/insight-radar` 完成端到端验证
2. **之后**：根据验证结果修复问题，完善 MVP
