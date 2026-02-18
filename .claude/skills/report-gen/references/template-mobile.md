# Mobile 领域报告模板

> 本文件定义 Mobile 领域报告的章节结构。Claude 生成 JSON 时严格按此结构输出。

## 报告结构

### 1. 执行摘要 (Executive Summary)
- heading1: "{date} 移动开发领域情报日报"
- subtitle: "数据源: GitHub, Hacker News, RSS | 共 {total_items} 条"
- separator
- heading2: "执行摘要"
- paragraph: 3-5 句话概括今日移动开发领域最重要的进展

### 2. iOS 生态 (iOS Ecosystem)
- heading2: "iOS 生态"
- table: iOS 动态
  - headers: ["项目/更新", "类型", "说明", "热度", "来源"]
- bullet_list: Swift/SwiftUI 更新、Xcode 工具链、App Store 政策

### 3. Android 生态 (Android Ecosystem)
- heading2: "Android 生态"
- table: Android 动态
  - headers: ["项目/更新", "类型", "说明", "热度", "来源"]
- bullet_list: Kotlin/Jetpack Compose 更新、Android Studio、Play Store 变化

### 4. 跨平台方案 (Cross-Platform)
- heading2: "跨平台方案"
- bullet_list: Flutter, React Native, KMP, MAUI 等动态
- paragraph: 跨平台方案对比分析

### 5. 移动端 AI (Mobile AI)
- heading2: "移动端 AI"
- bullet_list: 端侧模型、Core ML、TensorFlow Lite、ONNX Runtime 动态
- paragraph: 端侧推理趋势

### 6. 应用与分发 (Apps & Distribution)
- heading2: "应用与分发"
- bullet_list: 应用商店政策、PWA、超级应用趋势
- paragraph: 如无相关内容简述

### 7. 数据概览 (Data Overview)
- separator
- heading2: "数据概览"
- key_value: 统计数据
  - pairs: [Mobile 条目总数, iOS/Android/跨平台比例, 热度分布, 主要来源]

## 写作指引
- 标注平台版本要求（如 iOS 17+, API level 34+）
- 跨平台方案注明性能和原生差异
- 关注隐私政策和审核规则变化
