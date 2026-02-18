# Security 领域报告模板

> 本文件定义 Security 领域报告的章节结构。Claude 生成 JSON 时严格按此结构输出。

## 报告结构

### 1. 执行摘要 (Executive Summary)
- heading1: "{date} 安全领域情报日报"
- subtitle: "数据源: GitHub, Hacker News, RSS | 共 {total_items} 条"
- separator
- heading2: "执行摘要"
- paragraph: 3-5 句话概括今日安全领域最重要的动态，突出高危漏洞、重大攻击事件、防御工具更新

### 2. 关键漏洞与威胁 (Critical Vulnerabilities & Threats)
- heading2: "关键漏洞与威胁"
- paragraph: 概述威胁态势
- table: 漏洞/威胁列表
  - headers: ["CVE/名称", "严重度", "影响范围", "状态", "来源"]
- bullet_list: 每个漏洞的技术细节、利用条件、缓解建议

### 3. 隐私与监控 (Privacy & Surveillance)
- heading2: "隐私与监控"
- bullet_list: 数据泄露事件、监控技术进展、隐私工具更新
- paragraph: 趋势分析

### 4. 攻防研究 (Offensive & Defensive Research)
- heading2: "攻防研究"
- table: 研究项目列表
  - headers: ["项目/论文", "方向", "关键发现", "热度", "来源"]
- bullet_list: 新攻击技术、防御方法论、红蓝队工具

### 5. 防御工具与平台 (Defense Tools & Platforms)
- heading2: "防御工具与平台"
- table: 安全工具列表
  - headers: ["工具名称", "类别", "说明", "Stars/评论", "来源"]
- bullet_list: 开源安全工具更新、企业安全平台动态

### 6. 行业安全事件 (Industry Incidents)
- heading2: "行业安全事件"
- bullet_list: 企业/组织安全事件、响应措施、教训总结
- paragraph: 如无重大事件，简述安全态势

### 7. 合规与法规动态 (Compliance & Regulatory)
- heading2: "合规与法规动态"
- bullet_list: 新法规、合规要求变化、执法行动
- paragraph: 对从业者的影响分析

### 8. 数据概览 (Data Overview)
- separator
- heading2: "数据概览"
- key_value: 统计数据
  - pairs: [Security 条目总数, 威胁等级分布, 主要来源, 覆盖子领域]

## 写作指引
- 漏洞描述包含 CVE 编号（如有）
- 区分"已修复"和"尚未修复"的漏洞
- 攻击技术描述保持教育性，不提供可直接利用的 PoC
- 强调防御措施和缓解建议
