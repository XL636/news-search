# Cloud 领域报告模板

> 本文件定义 Cloud/Infrastructure 领域报告的章节结构。Claude 生成 JSON 时严格按此结构输出。

## 报告结构

### 1. 执行摘要 (Executive Summary)
- heading1: "{date} 云与基础设施领域情报日报"
- subtitle: "数据源: GitHub, Hacker News, RSS | 共 {total_items} 条"
- separator
- heading2: "执行摘要"
- paragraph: 3-5 句话概括今日 Cloud 领域最重要的进展

### 2. 容器与编排 (Containers & Orchestration)
- heading2: "容器与编排"
- paragraph: Kubernetes、Docker、容器运行时动态
- table: 项目列表
  - headers: ["项目", "类型", "更新内容", "热度", "来源"]
- bullet_list: 技术分析

### 3. Serverless 与 FaaS
- heading2: "Serverless 与 FaaS"
- bullet_list: 无服务器平台、函数计算、边缘计算动态
- paragraph: 趋势分析

### 4. 基础设施即代码 (IaC)
- heading2: "基础设施即代码"
- bullet_list: Terraform、Pulumi、CDK、Ansible 等工具动态
- paragraph: 最佳实践与生态变化

### 5. 服务网格与网络 (Service Mesh & Networking)
- heading2: "服务网格与网络"
- bullet_list: Istio、Envoy、网络策略、API Gateway 动态
- paragraph: 技术要点

### 6. 云平台动态 (Cloud Platform Updates)
- heading2: "云平台动态"
- table: 平台更新
  - headers: ["平台", "服务", "更新内容", "影响", "来源"]
- bullet_list: AWS/GCP/Azure 重要更新

### 7. 成本优化与 FinOps
- heading2: "成本优化与 FinOps"
- bullet_list: 云成本管理工具、FinOps 实践、优化策略
- paragraph: 如无相关内容简述

### 8. 数据概览 (Data Overview)
- separator
- heading2: "数据概览"
- key_value: 统计数据
  - pairs: [Cloud 条目总数, 热度分布, 主要平台分布, 主要来源]

## 写作指引
- 关注生产环境可用性和稳定性
- 区分 GA (Generally Available) 和 Preview/Beta 功能
- 强调架构决策的 trade-off
- 包含版本号和兼容性信息
