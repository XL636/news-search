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

---

## 9. Dashboard AI 搜索功能测试（v0.8.0）

> 测试日期：2026-02-18
> 测试方式：Python API 验证 + Playwright 前端交互 + 截图确认

### 9.0 测试总览

| 测试类别 | 用例数 | 通过 | 失败 |
|----------|--------|------|------|
| HTML 结构 | 9 | 9 | 0 |
| 现有 API 兼容性 | 3 | 3 | 0 |
| AI 搜索端点 | 1 | 1 | 0 |
| 搜索函数 | 4 | 4 | 0 |
| Prompt 构建 | 1 | 1 | 0 |
| 前端交互 (Playwright) | 7 | 7 | 0 |
| **合计** | **25** | **25** | **0** |

---

### 9.1 HTML 结构验证

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 9.1.1 | Homepage 加载 | ✅ PASS | 57,005 bytes HTML |
| 9.1.2 | `#view-ai-search` 存在 | ✅ PASS | AI 搜索视图容器 |
| 9.1.3 | `#view-feed` 存在 | ✅ PASS | Feed 视图容器 |
| 9.1.4 | `.tab-btn` 存在 | ✅ PASS | Tab 切换按钮 |
| 9.1.5 | `#ai-search-input` 存在 | ✅ PASS | AI 搜索输入框 |
| 9.1.6 | `.suggestion-chip` 存在 | ✅ PASS | 建议标签 |
| 9.1.7 | i18n `aiGreeting` 存在 | ✅ PASS | 国际化字段 |
| 9.1.8 | `.streaming-cursor` CSS 存在 | ✅ PASS | 流式光标动画 |
| 9.1.9 | `.citation` CSS 存在 | ✅ PASS | 引用徽章样式 |

---

### 9.2 现有 API 兼容性

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 9.2.1 | `/api/items` | ✅ PASS | total=119，分页正常 |
| 9.2.2 | `/api/stats` | ✅ PASS | raw=296, classified=119 |
| 9.2.3 | `/api/domains` | ✅ PASS | 10 个领域 |

---

### 9.3 AI 搜索端点

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 9.3.1 | 无 API key 时返回 SSE error | ✅ PASS | `event: error` + "请设置 ZHIPUAI_API_KEY 环境变量" |

---

### 9.4 搜索函数 `search_items_for_ai()`

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 9.4.1 | 英文关键词搜索 "AI coding" | ✅ PASS | 返回 20 条（限制 max=20） |
| 9.4.2 | 按 heat_index DESC 排序 | ✅ PASS | 第一条 heat=82，最后 heat=45 |
| 9.4.3 | 无匹配结果 | ✅ PASS | "xyznonexistent12345" 返回 0 条 |
| 9.4.4 | 返回字段完整性 | ✅ PASS | 12 个预期字段全部存在 |

---

### 9.5 Prompt 构建 `build_ai_prompt()`

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 9.5.1 | 构建 system + user 消息 | ✅ PASS | 2 条消息，system 含 [N] 规则，user 含 query + [1] 来源 |

---

### 9.6 前端交互测试 (Playwright)

| # | 用例 | 结果 | 截图 | 说明 |
|---|------|------|------|------|
| 9.6.1 | 默认显示 AI 搜索视图 | ✅ PASS | ai-search-default-view.png | Hero 区 + 搜索框 + 5 个建议 chips |
| 9.6.2 | 点击建议 chip 触发搜索 | ✅ PASS | ai-search-error-no-key.png | "AI coding" → 隐藏 hero → 显示错误提示 |
| 9.6.3 | 错误提示正确显示 | ✅ PASS | — | "AI 搜索未配置：请设置 ZHIPUAI_API_KEY 环境变量" |
| 9.6.4 | "新搜索"重置 | ✅ PASS | — | 点击后 Hero + 建议恢复，输入框清空 |
| 9.6.5 | 切换到 Feed 视图 | ✅ PASS | feed-view.png | KPI(296/119/119) + 10 领域 + 119 条 + 刷新/翻译按钮可见 |
| 9.6.6 | EN 语言切换 | ✅ PASS | ai-search-en.png | Tab→"AI Search/Feed"，域名/按钮/建议全英文 |
| 9.6.7 | 切回 AI 搜索视图保持英文 | ✅ PASS | — | "What do you want to know?" + EN suggestions |

---

### 9.7 未测试（需 GLM API key）

| 项 | 原因 |
|----|------|
| GLM-4-Plus 流式响应 | 需设置 `ZHIPUAI_API_KEY` 环境变量 |
| 流式 Markdown 渲染 + 光标动画 | 依赖 GLM API 返回文本流 |
| [N] 引用点击滚动到来源卡片 | 依赖 AI 回答中生成引用 |
| 并发限制 (Semaphore=3) | 需多并发请求压测 |

---

*测试执行：Claude Opus 4.6 | 25 项 AI 搜索功能测试全部通过*

---

## 10. API Key 管理 UI 测试（v0.8.1）

> 测试日期：2026-02-18
> 测试方式：Python API 验证 + Playwright 前端交互

### 10.0 测试总览

| 测试类别 | 用例数 | 通过 | 失败 |
|----------|--------|------|------|
| API 端点 | 3 | 3 | 0 |
| HTML 结构 | 8 | 8 | 0 |
| 前端交互 (Playwright) | 4 | 4 | 0 |
| **合计** | **15** | **15** | **0** |

---

### 10.1 API 端点验证

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 10.1.1 | `GET /api/ai-config` 无 key | ✅ PASS | `{"configured": false, "masked_key": ""}` |
| 10.1.2 | `POST /api/ai-config` 保存 key | ✅ PASS | `{"status": "ok", "message": "API key 已保存"}` |
| 10.1.3 | `GET /api/ai-config` 有 key | ✅ PASS | `{"configured": true, "masked_key": "test-key...5678"}` |

---

### 10.2 HTML 结构验证

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 10.2.1 | `#ai-key-setup` 存在 | ✅ PASS | API Key 配置面板容器 |
| 10.2.2 | `#ai-key-input` 存在 | ✅ PASS | 密码输入框 |
| 10.2.3 | `saveApiKey()` 函数存在 | ✅ PASS | 保存 API Key 函数 |
| 10.2.4 | `needsApiKey` 处理逻辑 | ✅ PASS | showAIError 检测 needsApiKey 信号 |
| 10.2.5 | i18n `aiKeyTitle` 中文 | ✅ PASS | "配置 AI 搜索" |
| 10.2.6 | i18n `aiKeyTitle` 英文 | ✅ PASS | "Configure AI Search" |
| 10.2.7 | i18n `aiKeySaveBtn` 存在 | ✅ PASS | 保存按钮文字 |
| 10.2.8 | `applyLang` 设置 key 面板 | ✅ PASS | ai-key-title/desc/save-btn/input 全部更新 |

---

### 10.3 前端交互测试 (Playwright)

| # | 用例 | 结果 | 说明 |
|---|------|------|------|
| 10.3.1 | 无 API Key 时点击建议触发搜索 | ✅ PASS | 显示 "Configure AI Search" 配置面板 |
| 10.3.2 | 配置面板显示正确 (EN) | ✅ PASS | 标题 + 描述 + 输入框 + Save 按钮 |
| 10.3.3 | 切换中文语言后面板更新 | ✅ PASS | "配置 AI 搜索" + "输入 API Key..." + "保存" |
| 10.3.4 | 点击"新搜索"重置隐藏面板 | ✅ PASS | 返回 Hero 视图，配置面板隐藏 |

---

*测试执行：Claude Opus 4.6 | 15 项 API Key 管理 UI 测试全部通过*
