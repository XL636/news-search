---
name: data-collect
description: "运行 InsightRadar 数据采集管道，从 GitHub、Hacker News、RSS 获取最新技术动态。触发词：/data-collect、采集数据、collect data、抓取、fetch sources。"
argument-hint: "[可选: github / hackernews / rss]"
---

# data-collect — 数据采集编排

## 触发条件
- 用户说 "采集数据"、"collect data"、"抓取"、"fetch sources"
- `/data-collect` 命令

## 执行步骤

1. **运行采集管道**
   ```bash
   cd D:/claude/news-search && python src/pipeline.py collect
   ```
   可选参数：`--source github`、`--source hackernews`、`--source rss`

2. **检查采集结果**
   ```bash
   cd D:/claude/news-search && python src/pipeline.py status
   ```

3. **输出统计报告**
   向用户汇报：
   - 各数据源采集条数
   - 新增 vs 重复条数
   - 总计条数
   - 是否有采集失败的数据源

## 错误处理
- 如果某个数据源失败（网络错误），仍继续采集其他数据源
- 如果全部失败，提示用户检查网络连接
- GitHub API 可能有速率限制，提示用户可配置 Token

## 输入
- 可选：`--source` 参数指定数据源（github / hackernews / rss）
- 不传参数则采集全部数据源

## 输出
- SQLite `raw_items` 表中的新数据
- `data/raw/{date}/raw_items.json` 快照文件
- 终端输出采集统计
