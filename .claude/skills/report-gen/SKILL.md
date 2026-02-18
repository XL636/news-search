---
name: report-gen
description: "生成 Word 文档(.docx)格式的领域情报报告。支持 11 个预定义领域、自定义关键词、全领域概览三种模式。触发词：/report-gen、生成报告、generate report、日报、digest。"
argument-hint: "[可选: 领域名称或自定义关键词，如 AI/ML、security、AI coding]"
---

# report-gen — 领域情报报告生成（.docx）

## 触发条件
- 用户说 "生成报告"、"generate report"、"日报"、"digest"
- `/report-gen` 命令
- `/report-gen AI/ML` — 指定领域
- `/report-gen AI coding` — 自定义关键词
- 由 `insight-radar` 全流程编排自动调用

## 参数说明
- **无参数**: 生成全领域概览报告（使用 `template-all-domains.md`）
- **预定义领域**: `AI/ML`, `Security`, `DevTools`, `Cloud`, `Hardware`, `Web`, `Mobile`, `Data`, `Blockchain`, `Biotech`, `Other`
- **自定义关键词**: 任何非预定义领域的文字（如 `AI coding`, `Rust`, `会计`）

## 执行步骤

### Step 0: 检查 python-docx 依赖
```bash
cd D:/claude/news-search && python -c "import docx; print('python-docx OK')" 2>&1 || python -m pip install "python-docx>=1.1,<2.0"
```
如果安装失败，停止并提示用户手动安装。

### Step 1: 解析参数，确定报告模式

根据用户输入确定 `REPORT_MODE`:

**预定义领域映射表**（不区分大小写）:

| 用户输入 | REPORT_MODE | 模板文件 |
|----------|-------------|----------|
| (无参数) | `all` | `template-all-domains.md` |
| `AI/ML`, `ai`, `ml`, `ai-ml` | `ai-ml` | `template-ai-ml.md` |
| `Security`, `security`, `sec` | `security` | `template-security.md` |
| `DevTools`, `devtools`, `dev` | `devtools` | `template-devtools.md` |
| `Cloud`, `cloud`, `infra` | `cloud` | `template-cloud.md` |
| `Hardware`, `hardware`, `hw`, `iot` | `hardware` | `template-hardware.md` |
| `Web`, `web`, `frontend`, `backend` | `web` | `template-web.md` |
| `Mobile`, `mobile`, `ios`, `android` | `mobile` | `template-mobile.md` |
| `Data`, `data`, `database`, `db` | `data` | `template-data.md` |
| `Blockchain`, `blockchain`, `web3`, `defi` | `blockchain` | `template-blockchain.md` |
| `Biotech`, `biotech`, `bio`, `medtech` | `biotech` | `template-biotech.md` |
| `Other`, `other` | `other` | `template-other.md` |
| 其他任何文字 | `custom:{keyword}` | `template-custom.md` |

### Step 2: 从 SQLite 获取数据

根据 REPORT_MODE 过滤数据：

**模式 `all`（全领域）**:
```bash
cd D:/claude/news-search && python -c "
import json, sys
sys.path.insert(0, '.')
from src.storage.store import get_connection, init_db, get_classified_items, get_stats
conn = get_connection()
init_db(conn)
items = get_classified_items(conn)
stats = get_stats(conn)
print('=== STATS ===')
print(json.dumps(stats, indent=2))
print('=== ITEMS ===')
print(json.dumps([i.model_dump(mode='json') for i in items], indent=2, default=str, ensure_ascii=False))
conn.close()
"
```

**模式 `{domain}`（预定义领域）**:
```bash
cd D:/claude/news-search && python -c "
import json, sys, sqlite3
sys.path.insert(0, '.')
from src.storage.store import get_connection, init_db, get_classified_items, get_stats
conn = get_connection()
init_db(conn)
all_items = get_classified_items(conn)
domain = '{DOMAIN_VALUE}'  # e.g. 'AI/ML', 'Security', etc.
items = [i for i in all_items if i.domain == domain]
stats = get_stats(conn)
print('=== STATS ===')
print(json.dumps(stats, indent=2))
print(f'=== DOMAIN: {domain} ({len(items)} items) ===')
print(json.dumps([i.model_dump(mode='json') for i in items], indent=2, default=str, ensure_ascii=False))
conn.close()
"
```

**`{DOMAIN_VALUE}` 映射**: `ai-ml` → `AI/ML`, `security` → `Security`, `devtools` → `DevTools`, `cloud` → `Cloud`, `hardware` → `Hardware`, `web` → `Web`, `mobile` → `Mobile`, `data` → `Data`, `blockchain` → `Blockchain`, `biotech` → `Biotech`, `other` → `Other`

**模式 `custom:{keyword}`（自定义关键词）**:
```bash
cd D:/claude/news-search && python -c "
import json, sys
sys.path.insert(0, '.')
from src.storage.store import get_connection, init_db, get_classified_items, get_stats
conn = get_connection()
init_db(conn)
all_items = get_classified_items(conn)
keywords = '{KEYWORD}'.lower().split()
items = []
for item in all_items:
    text = (item.title + ' ' + item.description + ' ' + ' '.join(item.tags)).lower()
    if any(kw in text for kw in keywords):
        items.append(item)
stats = get_stats(conn)
print('=== STATS ===')
print(json.dumps(stats, indent=2))
print(f'=== KEYWORD: {keywords} ({len(items)} items) ===')
print(json.dumps([i.model_dump(mode='json') for i in items], indent=2, default=str, ensure_ascii=False))
conn.close()
"
```

如果过滤后条目为 0，向用户说明无匹配数据，建议换关键词或使用全领域模式。

### Step 3: 读取对应模板

根据 REPORT_MODE 读取 `references/template-{mode}.md` 文件：
- 全领域: 读取 `D:\claude\news-search\.claude\skills\report-gen\references\template-all-domains.md`
- 预定义领域: 读取 `D:\claude\news-search\.claude\skills\report-gen\references\template-{mode}.md`
- 自定义关键词: 读取 `D:\claude\news-search\.claude\skills\report-gen\references\template-custom.md`

仔细阅读模板中定义的**章节结构**和**写作指引**。

### Step 4: 生成结构化 JSON

根据模板定义的章节结构，将数据组织为以下 JSON 格式：

```json
{
  "metadata": {
    "date": "YYYY-MM-DD",
    "report_type": "ai-ml",
    "topic_label": "AI/ML 领域情报日报",
    "total_items": 37
  },
  "sections": [
    { "type": "heading1", "text": "2026-02-18 AI/ML 领域情报日报" },
    { "type": "subtitle", "text": "数据源: GitHub, Hacker News, RSS | 共 37 条" },
    { "type": "separator" },
    { "type": "heading2", "text": "执行摘要" },
    { "type": "paragraph", "text": "今日 AI/ML 领域..." },
    { "type": "heading2", "text": "模型发布与基准评测" },
    { "type": "table", "headers": ["模型名称", "发布方", "亮点", "热度", "来源"], "rows": [["...", "...", "...", "85", "GitHub"]] },
    { "type": "bullet_list", "items": ["分析1...", "分析2..."] },
    { "type": "key_value", "pairs": [{"key": "条目总数", "value": "37"}, {"key": "平均热度", "value": "42"}] }
  ],
  "footer": "Generated by InsightRadar | 2026-02-18T12:00:00"
}
```

**支持的 section types**: `heading1`, `heading2`, `heading3`, `subtitle`, `paragraph`, `bullet_list`, `numbered_list`, `table`, `key_value`, `separator`

**重要**：
- 严格按照模板定义的章节顺序生成
- 每个章节使用模板中指定的 section type
- 如果某个章节无数据，添加一段 paragraph 说明"本日无相关内容"
- 表格行数据全部使用字符串类型
- 日期使用当天日期

将 JSON 写入文件：`D:\claude\news-search\data\processed\{YYYY-MM-DD}\report-content.json`

使用 Write 工具写入，确保目录存在：
```bash
mkdir -p D:/claude/news-search/data/processed/{YYYY-MM-DD}
```

### Step 5: 运行 generate_docx.py 生成 .docx

确定输出文件名：
- 全领域: `{date}-full-report.docx`
- 预定义领域: `{date}-{mode}-report.docx` (例如 `2026-02-18-ai-ml-report.docx`)
- 自定义关键词: `{date}-{keyword-slug}-report.docx` (例如 `2026-02-18-ai-coding-report.docx`)
  - keyword-slug: 小写，空格替换为连字符

```bash
cd D:/claude/news-search && python .claude/skills/report-gen/scripts/generate_docx.py \
  --input "data/processed/{YYYY-MM-DD}/report-content.json" \
  --output "output/digests/{date}-{topic-slug}-report.docx"
```

### Step 6: 输出确认

向用户汇报：
- 报告类型（全领域/领域名/自定义关键词）
- 包含条目数量
- 覆盖领域数（全领域模式）或匹配关键词
- 输出文件路径：`output/digests/{filename}.docx`
- 文件大小

## 写作原则
- 使用中文撰写，技术术语保留英文原名
- 客观陈述事实，避免过度炒作
- 突出"为什么这个重要"而不仅仅是"发生了什么"
- 对于开源项目，提及其技术亮点和应用场景
- 数据驱动：引用 stars 数、增长率等具体数字
- 严格按照模板章节结构组织内容，不要跳过或添加章节
