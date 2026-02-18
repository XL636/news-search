# Data 领域报告模板

> 本文件定义 Data（数据库/ETL/可视化）领域报告的章节结构。Claude 生成 JSON 时严格按此结构输出。

## 报告结构

### 1. 执行摘要 (Executive Summary)
- heading1: "{date} 数据技术领域情报日报"
- subtitle: "数据源: GitHub, Hacker News, RSS | 共 {total_items} 条"
- separator
- heading2: "执行摘要"
- paragraph: 3-5 句话概括今日数据技术领域最重要的进展

### 2. 数据库引擎 (Database Engines)
- heading2: "数据库引擎"
- table: 数据库动态
  - headers: ["数据库", "类型", "更新内容", "热度", "来源"]
- bullet_list: 关系型/NoSQL/NewSQL/时序/向量数据库动态

### 3. 数据处理与 ETL (Data Processing & ETL)
- heading2: "数据处理与 ETL"
- bullet_list: Spark, Flink, dbt, Airflow, Dagster 等工具动态
- paragraph: 实时 vs 批处理趋势分析

### 4. 数据分析与可视化 (Analytics & Visualization)
- heading2: "数据分析与可视化"
- table: 工具列表
  - headers: ["工具", "类型", "说明", "Stars/评论", "来源"]
- bullet_list: BI 工具、交互式笔记本、可视化库动态

### 5. 数据治理与质量 (Data Governance & Quality)
- heading2: "数据治理与质量"
- bullet_list: 数据目录、数据血缘、质量监控工具
- paragraph: 数据网格 (Data Mesh) 和数据产品趋势

### 6. 向量数据库与 AI 数据栈 (Vector DB & AI Data Stack)
- heading2: "向量数据库与 AI 数据栈"
- bullet_list: 向量数据库、Embedding 存储、RAG 数据管道
- paragraph: AI 原生数据基础设施趋势

### 7. 数据概览 (Data Overview)
- separator
- heading2: "数据概览"
- key_value: 统计数据
  - pairs: [Data 条目总数, 热度分布, 数据库类型分布, 主要来源]

## 写作指引
- 包含查询性能 benchmark（如 TPC-H, ClickBench）
- 区分 OLTP 和 OLAP 场景
- 关注数据格式标准（Parquet, Arrow, Iceberg）
