# DevTools 领域报告模板

> 本文件定义 DevTools 领域报告的章节结构。Claude 生成 JSON 时严格按此结构输出。

## 报告结构

### 1. 执行摘要 (Executive Summary)
- heading1: "{date} 开发工具领域情报日报"
- subtitle: "数据源: GitHub, Hacker News, RSS | 共 {total_items} 条"
- separator
- heading2: "执行摘要"
- paragraph: 3-5 句话概括今日 DevTools 领域最重要的进展，突出新工具发布、语言版本更新、开发者体验改进

### 2. 开发者体验 (Developer Experience)
- heading2: "开发者体验"
- paragraph: IDE 插件、CLI 工具、代码补全、调试工具等改善开发者日常体验的动态
- table: 工具列表
  - headers: ["工具/插件", "类型", "亮点", "Stars/评论", "来源"]
- bullet_list: 对开发效率的实际影响分析

### 3. 编程语言与运行时 (Languages & Runtimes)
- heading2: "编程语言与运行时"
- bullet_list: 语言版本更新、新特性、运行时改进（Node.js, Deno, Bun, Python, Rust, Go 等）
- paragraph: 生态影响分析

### 4. 构建与包管理 (Build Tools & Package Management)
- heading2: "构建与包管理"
- table: 工具列表
  - headers: ["工具", "类型", "更新内容", "热度", "来源"]
- bullet_list: 构建速度、依赖管理、monorepo 工具动态

### 5. 测试与质量保证 (Testing & QA)
- heading2: "测试与质量保证"
- bullet_list: 测试框架、代码质量工具、CI/CD 管道工具
- paragraph: 趋势分析（如 AI 辅助测试、Property-based testing 等）

### 6. 性能与可观测性 (Performance & Observability)
- heading2: "性能与可观测性"
- bullet_list: APM 工具、日志分析、性能分析器、Profiler 动态
- paragraph: 技术要点分析

### 7. 开源亮点 (Open Source Highlights)
- heading2: "开源亮点"
- table: 值得关注的开源项目
  - headers: ["项目", "语言", "说明", "Stars", "来源"]
- bullet_list: 为什么这些项目值得关注

### 8. 数据概览 (Data Overview)
- separator
- heading2: "数据概览"
- key_value: 统计数据
  - pairs: [DevTools 条目总数, 热度分布, 主要语言分布, 主要来源]

## 写作指引
- 强调"对开发者工作流的实际影响"
- 包含版本号和关键更新内容
- 对比同类工具时保持客观
- 关注 DX (Developer Experience) 改进
