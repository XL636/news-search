---
name: data-classify
description: "对清洗后的数据进行领域分类（11类）、细粒度标签提取和热度指数评估（0-100）。触发词：/data-classify、分类、classify、打标签、tag items、热度评分。"
---

# data-classify — 分类标签与热度评估

## 触发条件
- 用户说 "分类"、"classify"、"打标签"、"tag items"、"热度评分"
- `/data-classify` 命令
- 由 `insight-radar` 全流程编排自动调用

## 执行步骤

### 1. 读取清洗后数据
从 SQLite 数据库读取 cleaned_items：
```bash
cd D:/claude/news-search && python -c "
import json, sys
sys.path.insert(0, '.')
from src.storage.store import get_connection, init_db, get_cleaned_items
conn = get_connection()
init_db(conn)
items = get_cleaned_items(conn)
print(json.dumps([i.model_dump(mode='json') for i in items], indent=2, default=str, ensure_ascii=False))
conn.close()
"
```

### 2. 智能分类（Claude 驱动）
对每条 CleanedItem 执行以下处理：

**领域分类**（必须选一个）：
- AI/ML — 人工智能、机器学习、深度学习、LLM、NLP、CV
- DevTools — 开发工具、IDE、编译器、构建系统、CLI
- Hardware — 芯片、嵌入式、IoT、机器人
- Cloud — 云计算、容器、K8s、Serverless、IaC
- Security — 网络安全、加密、漏洞、隐私
- Web — 前端、后端框架、浏览器、HTTP
- Mobile — iOS、Android、跨平台、Flutter、React Native
- Data — 数据库、数据工程、ETL、可视化
- Blockchain — 加密货币、Web3、DeFi、智能合约
- Biotech — 生物技术、医疗科技、基因编辑
- Other — 不属于以上类别

**细粒度标签**（尽可能提取）：
- 开源协议（MIT, Apache-2.0, GPL 等）
- 编程语言（Python, Rust, TypeScript 等）
- 框架/工具名称
- 相关公司名
- 算法/技术名称

**热度指数 (0-100)**：
综合以下因素评分：
- Stars/Points 绝对值和增长率（权重 30%）
- 评论/讨论活跃度（权重 20%）
- 发布时间新鲜度（权重 20%）
- 跨平台出现次数（sources 数组长度，权重 30%）

评分参考：
- 90-100：现象级项目，全网关注
- 70-89：高热度，值得重点关注
- 50-69：中等热度，领域内有影响
- 30-49：一般关注度
- 0-29：低热度或小众

**heat_reason**：简短说明为什么给这个分数（一句话）

### 3. 写入分类结果
将分类后的数据写入数据库和 JSON 文件：
```bash
cd D:/claude/news-search && python -c "
import json, sys
from datetime import datetime
sys.path.insert(0, '.')
from src.storage.store import get_connection, init_db, insert_classified_item
from src.models.schemas import ClassifiedItem
conn = get_connection()
init_db(conn)
# Delete old classified items
conn.execute('DELETE FROM classified_items')
conn.commit()
# Insert each classified item
classified_data = ... # the classified items as list of dicts
for item_dict in classified_data:
    item = ClassifiedItem(**item_dict)
    insert_classified_item(conn, item)
conn.close()
"
```

同时保存到文件：`data/processed/{YYYY-MM-DD}/classified.json`

### 4. 输出统计
向用户汇报：
- 各领域条目分布
- 热度 Top 5 条目
- 平均热度指数

## 输出格式
每条 ClassifiedItem 包含：
```json
{
  "cleaned_item_id": 1,
  "title": "项目标题",
  "url": "链接",
  "description": "描述",
  "domain": "AI/ML",
  "tags": ["python", "transformer", "MIT", "OpenAI"],
  "heat_index": 85,
  "heat_reason": "GitHub 3k stars in 24h, trending on HN front page",
  "sources": ["github", "hackernews"],
  "stars": 3000,
  "comments_count": 150
}
```
