# Biotech 领域报告模板

> 本文件定义 Biotech/医疗科技 领域报告的章节结构。Claude 生成 JSON 时严格按此结构输出。

## 报告结构

### 1. 执行摘要 (Executive Summary)
- heading1: "{date} 生物科技与医疗领域情报日报"
- subtitle: "数据源: GitHub, Hacker News, RSS | 共 {total_items} 条"
- separator
- heading2: "执行摘要"
- paragraph: 3-5 句话概括今日生物科技领域最重要的进展

### 2. AI + 生物医药 (AI in Biomedicine)
- heading2: "AI + 生物医药"
- table: 项目列表
  - headers: ["项目/工具", "应用领域", "说明", "热度", "来源"]
- bullet_list: 药物发现、蛋白质结构预测、医学影像 AI

### 3. 基因编辑与合成生物学 (Gene Editing & Synthetic Biology)
- heading2: "基因编辑与合成生物学"
- bullet_list: CRISPR 工具、基因疗法、合成生物学平台
- paragraph: 技术进展分析

### 4. 医疗器械与数字健康 (MedTech & Digital Health)
- heading2: "医疗器械与数字健康"
- bullet_list: 可穿戴设备、远程医疗、电子健康记录
- paragraph: 技术趋势

### 5. 生物信息学工具 (Bioinformatics Tools)
- heading2: "生物信息学工具"
- table: 工具列表
  - headers: ["工具", "类型", "说明", "Stars/评论", "来源"]
- bullet_list: 开源生物信息学软件、数据库、分析管道

### 6. 行业与监管 (Industry & Regulatory)
- heading2: "行业与监管"
- bullet_list: FDA/EMA 审批、临床试验、投融资动态
- paragraph: 如无相关内容简述

### 7. 数据概览 (Data Overview)
- separator
- heading2: "数据概览"
- key_value: 统计数据
  - pairs: [Biotech 条目总数, 热度分布, 子领域分布, 主要来源]

## 写作指引
- 科学术语准确，必要时附通俗解释
- 区分临床前研究和临床试验阶段
- 关注开源工具和可复现性
