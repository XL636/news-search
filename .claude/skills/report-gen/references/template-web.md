# Web 领域报告模板

> 本文件定义 Web 领域报告的章节结构。Claude 生成 JSON 时严格按此结构输出。

## 报告结构

### 1. 执行摘要 (Executive Summary)
- heading1: "{date} Web 技术领域情报日报"
- subtitle: "数据源: GitHub, Hacker News, RSS | 共 {total_items} 条"
- separator
- heading2: "执行摘要"
- paragraph: 3-5 句话概括今日 Web 领域最重要的进展

### 2. 前端框架与库 (Frontend Frameworks & Libraries)
- heading2: "前端框架与库"
- table: 框架动态
  - headers: ["框架/库", "版本", "更新内容", "热度", "来源"]
- bullet_list: React, Vue, Svelte, Angular, Solid 等生态动态

### 3. 后端与 API (Backend & API)
- heading2: "后端与 API"
- bullet_list: 后端框架、API 设计、GraphQL/REST/gRPC 动态
- paragraph: 技术分析

### 4. 浏览器技术 (Browser Technologies)
- heading2: "浏览器技术"
- bullet_list: Web API、CSS 新特性、WebAssembly、Web Components
- paragraph: 标准化进展

### 5. 全栈与元框架 (Full-Stack & Meta-Frameworks)
- heading2: "全栈与元框架"
- bullet_list: Next.js, Nuxt, SvelteKit, Remix, Astro 等动态
- paragraph: SSR/SSG/ISR 趋势

### 6. 性能与 Web Vitals
- heading2: "性能与 Web Vitals"
- bullet_list: 性能优化工具、Core Web Vitals 相关动态
- paragraph: 如无相关内容简述

### 7. 数据概览 (Data Overview)
- separator
- heading2: "数据概览"
- key_value: 统计数据
  - pairs: [Web 条目总数, 热度分布, 前后端比例, 主要来源]

## 写作指引
- 包含框架版本号和迁移指南链接
- 关注 breaking changes 和迁移成本
- 对比同类方案时注明适用场景
