# Hardware 领域报告模板

> 本文件定义 Hardware/Embedded/IoT 领域报告的章节结构。Claude 生成 JSON 时严格按此结构输出。

## 报告结构

### 1. 执行摘要 (Executive Summary)
- heading1: "{date} 硬件与嵌入式领域情报日报"
- subtitle: "数据源: GitHub, Hacker News, RSS | 共 {total_items} 条"
- separator
- heading2: "执行摘要"
- paragraph: 3-5 句话概括今日硬件领域最重要的进展

### 2. 芯片与处理器 (Chips & Processors)
- heading2: "芯片与处理器"
- table: 芯片动态
  - headers: ["芯片/平台", "厂商", "亮点", "热度", "来源"]
- bullet_list: 性能对比、架构创新、制程进展

### 3. 嵌入式系统 (Embedded Systems)
- heading2: "嵌入式系统"
- bullet_list: MCU、FPGA、RTOS、嵌入式开发工具动态
- paragraph: 技术分析

### 4. IoT 与边缘计算 (IoT & Edge Computing)
- heading2: "IoT 与边缘计算"
- table: IoT 项目列表
  - headers: ["项目", "类型", "说明", "Stars/评论", "来源"]
- bullet_list: 协议、平台、安全动态

### 5. 开源硬件 (Open Source Hardware)
- heading2: "开源硬件"
- bullet_list: RISC-V、开源 PCB、开发板项目
- paragraph: 社区动态和生态发展

### 6. 行业趋势 (Industry Trends)
- heading2: "行业趋势"
- bullet_list: 供应链、产能、市场动态
- paragraph: 趋势分析

### 7. 数据概览 (Data Overview)
- separator
- heading2: "数据概览"
- key_value: 统计数据
  - pairs: [Hardware 条目总数, 热度分布, 主要来源]

## 写作指引
- 包含具体技术规格（制程、核心数、功耗等）
- 区分消费级和工业级应用
- 关注开源硬件的社区活跃度
