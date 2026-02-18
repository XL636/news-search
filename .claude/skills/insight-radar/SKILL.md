---
name: insight-radar
description: "InsightRadar 全流程一键编排。从 GitHub/HN/RSS 采集数据，经清洗去重、分类标签、热度评估后，生成全球创新日报。触发词：/insight-radar、每日扫描、全流程、一键日报、run insight radar。"
argument-hint: "[可选: 指定数据源 github/hackernews/rss]"
---

# insight-radar — 全流程编排

## 触发条件
- 用户说 "每日扫描"、"全流程"、"run insight radar"、"一键日报"
- `/insight-radar` 命令

## 说明
InsightRadar 全球创新与开源情报聚合系统的一键编排 Skill。
按顺序执行：数据采集 → 清洗去重 → 分类标签 → 报告生成。

## 执行步骤

### Phase 1: 数据采集
运行 Python 采集管道，从 GitHub、Hacker News、RSS 获取最新数据：
```bash
cd D:/claude/news-search && python src/pipeline.py collect
```
检查采集结果：
```bash
cd D:/claude/news-search && python src/pipeline.py status
```
如果 raw_items 为 0，停止并提示用户检查网络。

### Phase 2: 数据清洗
执行 data-clean Skill 的完整流程：

1. 读取 raw_items（最近 48h）
```bash
cd D:/claude/news-search && python -c "
import json, sys
sys.path.insert(0, '.')
from src.storage.store import get_connection, init_db, get_raw_items
conn = get_connection()
init_db(conn)
items = get_raw_items(conn, since_hours=48)
print(json.dumps([i.model_dump(mode='json') for i in items], indent=2, default=str, ensure_ascii=False))
conn.close()
"
```

2. 对数据执行：
   - 时间过滤：丢弃 published_at 超过 48h 的旧内容
   - 语义去重：合并同一事件的跨平台报道（相同 URL、相似标题）
   - 冲突消解：权威来源优先（github > hackernews > rss）

3. 将清洗结果写入 SQLite cleaned_items 表，同时保存到 `data/processed/{date}/cleaned.json`

### Phase 3: 分类标签
执行 data-classify Skill 的完整流程：

1. 读取 cleaned_items
2. 对每条数据：
   - 分配领域分类（AI/ML, DevTools, Hardware, Cloud, Security, Web, Mobile, Data, Blockchain, Biotech, Other）
   - 提取细粒度标签（语言、框架、协议、公司名）
   - 计算热度指数 0-100（基于 stars、comments、recency、跨平台出现）
3. 将结果写入 SQLite classified_items 表，同时保存到 `data/processed/{date}/classified.json`

### Phase 4: 报告生成
执行 report-gen Skill 的完整流程，生成 Word 文档(.docx)格式报告：

1. 读取 classified_items
2. 确定报告模式：
   - 默认（无参数）：全领域概览报告
   - 指定领域参数（如 `AI/ML`、`Security`）：生成该领域专属报告
   - 自定义关键词（如 `AI coding`）：按关键词过滤并自适应生成
3. 按对应模板（`references/template-*.md`）生成结构化 JSON
4. 调用 `generate_docx.py` 将 JSON 转换为格式化 .docx 文件
5. 输出至 `output/digests/{YYYY-MM-DD}-{topic-slug}-report.docx`

### Phase 5: 完成确认
向用户展示：
- 四个阶段的执行摘要
- 日报文件路径
- 关键统计数据（采集 → 清洗 → 分类的漏斗数据）
- 邀请用户查看日报

## 错误处理
- 任何阶段失败时，输出已完成的阶段结果并明确指出失败点
- 采集阶段部分失败（某个数据源）仍继续后续流程
- 清洗/分类阶段如果数据为空，提前终止并提示原因

## 数据存储位置
- 数据库：`D:/claude/news-search/data/insight_radar.db`
- 原始数据：`D:/claude/news-search/data/raw/{date}/`
- 处理数据：`D:/claude/news-search/data/processed/{date}/`
- 日报输出：`D:/claude/news-search/output/digests/{date}-{topic-slug}-report.docx`
