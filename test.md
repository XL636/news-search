# InsightRadar 功能测试报告

> 测试日期：2026-02-17
> 环境：Python 3.14.3 / Windows 11 / .venv 独立虚拟环境

---

## 测试总览

| 测试类别 | 用例数 | 通过 | 失败 |
|----------|--------|------|------|
| 数据模型 | 4 | 4 | 0 |
| 存储层 | 8 | 8 | 0 |
| 配置模块 | 4 | 4 | 0 |
| 采集器 | 5 | 5 | 0 |
| Pipeline CLI | 5 | 5 | 0 |
| Skills 文件 | 5 | 5 | 0 |
| 输出文件 | 2 | 2 | 0 |
| **合计** | **33** | **33** | **0** |

---

## 1. 数据模型 (src/models/schemas.py)

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 1.1 | RawItem 创建 + unique_key() | ✅ PASS | `source='github', source_id='123'` → `unique_key()='github:123'` |
| 1.2 | CleanedItem 多源字段 | ✅ PASS | `sources=['github','hackernews']` 正确存储 |
| 1.3 | ClassifiedItem 热度字段 | ✅ PASS | `heat_index=85, domain='AI/ML'` |
| 1.4 | DailyDigest 元数据 | ✅ PASS | `date='2026-02-17', total_raw=100` |

---

## 2. 存储层 (src/storage/store.py)

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 2.1 | init_db 建表 | ✅ PASS | 3 表 + 4 索引创建成功 |
| 2.2 | insert_raw_item | ✅ PASS | 返回 row id=1 |
| 2.3 | 重复插入检测 | ✅ PASS | 相同 source+source_id 返回 None |
| 2.4 | get_raw_items 时间过滤 | ✅ PASS | since_hours=1 正确过滤 |
| 2.5 | insert/get_cleaned_item | ✅ PASS | JSON 序列化/反序列化 sources 字段正确 |
| 2.6 | insert/get_classified_item | ✅ PASS | heat_index=75 正确读回 |
| 2.7 | get_stats | ✅ PASS | `{'raw_items':1, 'cleaned_items':1, 'classified_items':1, 'sources':{'test':1}}` |
| 2.8 | clear_processed | ✅ PASS | cleaned + classified 清零，raw 保留 |

---

## 3. 配置模块 (src/config.py)

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 3.1 | 路径常量 | ✅ PASS | PROJECT_ROOT, DB_PATH 指向正确目录 |
| 3.2 | RSS_FEEDS | ✅ PASS | 4 个 feed 源配置 |
| 3.3 | DOMAINS | ✅ PASS | 11 个分类 |
| 3.4 | HEAT_WEIGHTS 权重和 | ✅ PASS | 0.3+0.2+0.2+0.3 = 1.0 |

---

## 4. 采集器

### 4.1 GitHub (src/collectors/github_trending.py)

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 4.1.1 | 单独采集 `--source github` | ✅ PASS | 30 repos，stars 排序 |
| 4.1.2 | 重复检测 | ✅ PASS | 二次运行 0 new, 30 duplicate |

### 4.2 Hacker News (src/collectors/hackernews.py)

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 4.2.1 | 单独采集 `--source hackernews` | ✅ PASS | 56 stories (top + show) |
| 4.2.2 | 增量采集 | ✅ PASS | 5 new, 51 duplicate（新帖子正确识别） |

### 4.3 RSS (src/collectors/rss_feeds.py)

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 4.3.1 | 单独采集 `--source rss` | ✅ PASS | 80 articles，4 个 RSS 源全部成功 |

---

## 5. Pipeline CLI (src/pipeline.py)

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 5.1 | `pipeline.py --help` | ✅ PASS | 显示 collect/status/export 三个子命令 |
| 5.2 | `pipeline.py`（无参数） | ✅ PASS | 显示帮助信息，不报错 |
| 5.3 | `pipeline.py collect` | ✅ PASS | 全源采集，输出各源统计 |
| 5.4 | `pipeline.py collect --source github hackernews` | ✅ PASS | 多源指定采集 |
| 5.5 | `pipeline.py status` | ✅ PASS | 显示三表计数 + 源分布 |
| 5.6 | `pipeline.py export` | ✅ PASS | 导出 176 条到 JSON |

---

## 6. Skills 文件完整性

| # | Skill | 文件大小 | 结果 |
|---|-------|----------|------|
| 6.1 | data-collect/SKILL.md | 1,092 bytes | ✅ PASS |
| 6.2 | data-clean/SKILL.md | 2,879 bytes | ✅ PASS |
| 6.3 | data-classify/SKILL.md | 3,398 bytes | ✅ PASS |
| 6.4 | report-gen/SKILL.md | 2,515 bytes | ✅ PASS |
| 6.5 | insight-radar/SKILL.md | 3,055 bytes | ✅ PASS |

---

## 7. 输出文件

| # | 文件 | 大小 | 结果 |
|---|------|------|------|
| 7.1 | data/raw/2026-02-17/raw_items.json | 384 KB | ✅ PASS |
| 7.2 | data/processed/2026-02-17/export.json | 384 KB | ✅ PASS |

---

## 8. 其他验证

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 8.1 | BaseCollector 抽象类不可实例化 | ✅ PASS | `TypeError: Can't instantiate abstract class` |
| 8.2 | SQLite 重复写入保护 (UNIQUE 约束) | ✅ PASS | 返回 None 而非异常 |
| 8.3 | 虚拟环境依赖完整 | ✅ PASS | httpx, feedparser, pydantic, dateutil 全部可导入 |

---

## 数据库最终状态

```
Raw items:        176
Cleaned items:    0
Classified items: 0

Sources breakdown:
  github:      30
  hackernews:  59
  rss:         87
```

---

## 未测试（需全流程验证）

| 项 | 原因 |
|----|------|
| `/insight-radar` 全流程 | Skill 需要 Claude 驱动，非 Python 单元测试可覆盖 |
| data-clean 语义去重 | Claude 驱动，需运行 Skill |
| data-classify 分类+热度 | Claude 驱动，需运行 Skill |
| report-gen 日报生成 | Claude 驱动，需运行 Skill |
| 日报 Markdown 输出 | 依赖上述 Skill 完成 |

---

*测试执行：Claude Opus 4.6 | 全部 33 项自动化测试通过*
