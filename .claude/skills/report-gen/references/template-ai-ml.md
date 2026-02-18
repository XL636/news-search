# AI/ML 领域报告模板

> 本文件定义 AI/ML 领域报告的章节结构。Claude 生成 JSON 时严格按此结构输出。

## 报告结构

### 1. 执行摘要 (Executive Summary)
- heading1: "{date} AI/ML 领域情报日报"
- subtitle: "数据源: GitHub, Hacker News, RSS | 共 {total_items} 条"
- separator
- heading2: "执行摘要"
- paragraph: 3-5 句话概括今日 AI/ML 领域最重要的进展，突出模型发布、重大融资、开源突破

### 2. 模型发布与基准评测 (Model Releases & Benchmarks)
- heading2: "模型发布与基准评测"
- paragraph: 概述本节内容
- table: 新发布/更新的模型列表
  - headers: ["模型名称", "发布方", "亮点", "热度", "来源"]
- bullet_list: 对每个模型的简要分析（性能提升、架构创新、适用场景）

### 3. 工具与基础设施 (Tools & Infrastructure)
- heading2: "AI 工具与基础设施"
- paragraph: 框架、推理引擎、训练平台、MLOps 工具的新动态
- table: 工具列表
  - headers: ["项目", "类型", "说明", "Stars/评论", "来源"]
- bullet_list: 开发者体验改进、性能优化要点

### 4. 研究亮点 (Research Highlights)
- heading2: "研究亮点"
- bullet_list: 值得关注的论文、方法论突破、新范式
- paragraph: 对研究趋势的分析（如果有多篇相关论文，指出共同方向）

### 5. 行业与融资 (Industry & Funding)
- heading2: "行业动态与融资"
- table: 融资/收购/合作事件
  - headers: ["公司/项目", "事件类型", "金额/详情", "来源"]
- paragraph: 行业趋势分析

### 6. 伦理与监管 (Ethics & Regulation)
- heading2: "伦理与监管"
- bullet_list: AI 安全、偏见、法规动态（GDPR/AI Act 等）
- paragraph: 如果本日无相关内容，简短说明"本日无重大伦理监管动态"

### 7. 新兴信号 (Emerging Signals)
- heading2: "新兴信号"
- bullet_list: 尚未大规模报道但值得关注的早期趋势、小型但有潜力的项目
- paragraph: 为什么这些信号值得关注

### 8. 数据概览 (Data Overview)
- separator
- heading2: "数据概览"
- key_value: 统计数据
  - pairs: [AI/ML 条目总数, 热度分布, 主要来源, 覆盖子领域]

## 写作指引
- 技术术语保留英文原名（如 Transformer、LoRA、RLHF）
- 模型对比时引用具体 benchmark 分数
- 关注可复现性和开源程度
- 避免炒作，客观评价实际影响
