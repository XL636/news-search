# data-clean — 数据清洗与语义去重

## 触发条件
- 用户说 "清洗数据"、"clean data"、"去重"、"deduplicate"
- `/data-clean` 命令
- 由 `insight-radar` 全流程编排自动调用

## 执行步骤

### 1. 读取原始数据
从 SQLite 数据库读取最近 48 小时的 raw_items：
```bash
cd D:/claude/news-search && python -c "
import json, sys
sys.path.insert(0, '.')
from src.storage.store import get_connection, init_db, get_raw_items
conn = get_connection()
init_db(conn)
items = get_raw_items(conn, since_hours=48)
print(json.dumps([i.model_dump(mode='json') for i in items], indent=2, default=str, ensure_ascii=False))
conn.close()
"
```

### 2. 智能清洗（Claude 驱动）
对读取到的 raw_items 执行以下处理：

**时间过滤**：丢弃 `published_at` 超过 48 小时的旧内容（如果 published_at 为空，保留）

**语义去重**：识别同一事件/项目的跨平台报道并合并：
- 同一 GitHub 仓库在 GitHub trending 和 HN 上同时出现
- 同一新闻在多个 RSS 源中出现
- 标题或 URL 高度相似的条目
合并规则：保留信息最丰富的版本，sources 字段记录所有来源

**冲突消解**：当同一事件有多个来源时：
- 优先使用权威来源的描述（官方仓库 > 主流媒体 > 社区讨论）
- stars/comments 取最大值
- tags 合并去重

### 3. 写入清洗结果
将清洗后的数据写入数据库和 JSON 文件：
```bash
cd D:/claude/news-search && python -c "
import json, sys
from datetime import datetime
sys.path.insert(0, '.')
from src.storage.store import get_connection, init_db, clear_processed, insert_cleaned_item
from src.models.schemas import CleanedItem
conn = get_connection()
init_db(conn)
clear_processed(conn)
# Insert each cleaned item (items provided as JSON from the cleaning step)
cleaned_data = ... # the cleaned items as list of dicts
for item_dict in cleaned_data:
    item = CleanedItem(**item_dict)
    insert_cleaned_item(conn, item)
conn.close()
"
```

同时保存到文件：`data/processed/{YYYY-MM-DD}/cleaned.json`

### 4. 输出统计
向用户汇报：
- 原始条目数 → 清洗后条目数
- 去重合并了多少条
- 过滤了多少条过旧内容

## 输出格式
每条 CleanedItem 包含：
```json
{
  "title": "项目/文章标题",
  "url": "主链接",
  "description": "合并后的最佳描述",
  "author": "作者",
  "sources": ["github", "hackernews"],
  "source_ids": ["github:123", "hn:456"],
  "stars": 1500,
  "comments_count": 200,
  "language": "Python",
  "tags": ["ai", "machine-learning"],
  "published_at": "2025-01-15T10:00:00",
  "merge_note": "Merged GitHub repo with HN discussion"
}
```

## 关键原则
- 宁可保留存疑的条目，也不要误删有价值的内容
- 合并时保留所有来源信息，便于后续追溯
- 描述字段选取最详细、最准确的版本
