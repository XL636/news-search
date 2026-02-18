# 全领域概览报告模板

> 本文件定义全领域概览报告（无参数调用时的默认模式）的章节结构。
> 这是当前日报的增强版，覆盖所有领域。

## 报告结构

### 1. 报告头 (Report Header)
- heading1: "{date} InsightRadar 全球创新日报"
- subtitle: "数据源: GitHub, Hacker News, RSS | 共 {total_items} 条"
- separator

### 2. 执行摘要 (Executive Summary)
- heading2: "执行摘要"
- paragraph: 今日 3-5 条最重要的技术进展，每条 1-2 句话概括其意义。覆盖不同领域的亮点。

### 3. 热度排行 Top 10 (Top 10 by Heat Index)
- heading2: "热度排行 Top 10"
- table: 热度前 10 项目
  - headers: ["#", "热度", "标题", "领域", "来源"]
- separator
- heading3: "Top 10 详细分析"
- numbered_list: 对 Top 10 每项展开 2-3 句分析：为什么重要、技术亮点、潜在影响

### 4. 领域动态 (Domain Breakdown)
按条目数量从多到少排列各领域，空领域跳过。每个领域：
- heading2: "{domain_name}"
- table: 该领域所有条目
  - headers: ["标题", "热度", "说明", "来源"]
- bullet_list: 领域趋势简评

### 5. 跨平台强信号 (Cross-Platform Signals)
- heading2: "跨平台强信号"
- paragraph: 在 2 个以上数据源同时出现的项目列表及分析
- table: 跨平台项目
  - headers: ["项目", "出现源", "热度", "分析"]

### 6. 今日数据概览 (Data Overview)
- separator
- heading2: "今日数据概览"
- key_value: 统计数据
  - pairs:
    - 原始采集: X 条
    - 清洗去重后: Y 条
    - 分类标注: Z 条
    - 覆盖领域: N 个
    - 平均热度: XX
    - 热度 Top 3 领域: ...

## 写作指引
- 使用中文撰写，技术术语保留英文原名
- 客观陈述事实，避免过度炒作
- 突出"为什么这个重要"而不仅仅是"发生了什么"
- 对于开源项目，提及其技术亮点和应用场景
- 数据驱动：引用 stars 数、增长率等具体数字
- 全领域模式下每个领域分析不必太深，重在广度和对比
