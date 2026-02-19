"""FastAPI web dashboard for InsightRadar."""

import asyncio
import json
import logging
import re
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config import (
    AI_SEARCH_MAX_ITEMS,
    DB_PATH,
    ZHIPUAI_API_KEY,
    ZHIPUAI_BASE_URL,
    ZHIPUAI_MODEL,
)
from src.pipeline import cmd_collect
from src.storage.store import get_connection, get_translation, init_db, insert_web_search_item, save_translation

logger = logging.getLogger(__name__)


STATIC_DIR = Path(__file__).parent / "static"
SETTINGS_FILE = Path(__file__).parent.parent / "data" / "settings.json"

_collect_lock = asyncio.Lock()
_ai_search_semaphore = asyncio.Semaphore(3)

# Runtime API key: env var first, then settings file
_runtime_api_key: str = ZHIPUAI_API_KEY


def _load_api_key() -> str:
    """Load API key from env var or settings file."""
    if ZHIPUAI_API_KEY:
        return ZHIPUAI_API_KEY
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return data.get("zhipuai_api_key", "")
        except (json.JSONDecodeError, OSError):
            pass
    return ""


def _save_api_key(key: str):
    """Save API key to settings file."""
    global _runtime_api_key
    _runtime_api_key = key
    data = {}
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    data["zhipuai_api_key"] = key
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    global _runtime_api_key
    conn = get_connection()
    init_db(conn)
    conn.close()
    _runtime_api_key = _load_api_key()
    yield


app = FastAPI(title="InsightRadar Dashboard", lifespan=lifespan)


@app.get("/api/domains")
def api_domains():
    """Get all domains with item counts."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT domain, COUNT(*) as count FROM classified_items GROUP BY domain ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [{"domain": r["domain"], "count": r["count"]} for r in rows]


@app.get("/api/items")
def api_items(
    domain: str | None = Query(None),
    search: str | None = Query(None),
    sort: str = Query("heat"),
    limit: int = Query(20),
    offset: int = Query(0),
):
    """Get classified items with optional filters and pagination."""
    conn = get_connection()
    base_where = "WHERE 1=1"
    params: list = []

    if domain and domain != "All":
        base_where += " AND domain = ?"
        params.append(domain)

    if search:
        base_where += " AND (title LIKE ? OR description LIKE ? OR tags LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    # Count total
    count_row = conn.execute(
        f"SELECT COUNT(*) FROM classified_items {base_where}", params
    ).fetchone()
    total = count_row[0]

    # Build order clause
    order = " ORDER BY heat_index DESC"
    if sort == "stars":
        order = " ORDER BY stars DESC"
    elif sort == "recent":
        order = " ORDER BY published_at DESC"
    elif sort == "comments":
        order = " ORDER BY comments_count DESC"

    query = f"SELECT * FROM classified_items {base_where}{order} LIMIT ? OFFSET ?"
    rows = conn.execute(query, [*params, limit, offset]).fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "id": r["id"],
            "title": r["title"],
            "url": r["url"],
            "description": r["description"],
            "author": r["author"],
            "sources": json.loads(r["sources"]) if r["sources"] else [],
            "domain": r["domain"],
            "tags": json.loads(r["tags"]) if r["tags"] else [],
            "heat_index": r["heat_index"],
            "heat_reason": r["heat_reason"],
            "stars": r["stars"],
            "comments_count": r["comments_count"],
            "language": r["language"],
            "published_at": r["published_at"],
        })
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@app.get("/api/stats")
def api_stats():
    """Get database statistics."""
    conn = get_connection()
    stats = {}
    for table in ["raw_items", "cleaned_items", "classified_items"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        stats[table] = count

    rows = conn.execute(
        "SELECT source, COUNT(*) as cnt FROM raw_items GROUP BY source"
    ).fetchall()
    stats["sources"] = {r["source"]: r["cnt"] for r in rows}

    conn.close()
    return stats


@app.post("/api/collect")
async def api_collect():
    """Trigger data collection. Returns 409 if already running."""
    if _collect_lock.locked():
        return {"status": "busy", "message": "Collection already in progress"}

    async with _collect_lock:
        try:
            result = await cmd_collect()
            return {
                "status": "ok",
                "stats": result,
                "message": "Collection complete. Run /insight-radar to process data.",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


class TranslateRequest(BaseModel):
    text: str
    target: str = "zh"


@app.post("/api/translate")
async def api_translate(req: TranslateRequest):
    """Translate text, with SQLite cache."""
    text = req.text.strip()
    if not text:
        return {"translated": ""}

    # Check cache
    conn = get_connection()
    cached = get_translation(conn, text, req.target)
    if cached:
        conn.close()
        return {"translated": cached, "cached": True}

    # Call Google Translate free endpoint
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://translate.googleapis.com/translate_a/single",
                params={
                    "client": "gtx",
                    "sl": "auto",
                    "tl": req.target,
                    "dt": "t",
                    "q": text[:500],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            translated = "".join(part[0] for part in data[0] if part[0])
    except Exception as e:
        conn.close()
        return {"translated": "", "error": str(e)}

    # Save to cache
    save_translation(conn, text, translated, req.target)
    conn.close()
    return {"translated": translated, "cached": False}


# ========== AI Config ==========

@app.get("/api/ai-config")
def api_ai_config_get():
    """Check if AI API key is configured."""
    has_key = bool(_runtime_api_key)
    # Return masked key for display
    masked = ""
    if _runtime_api_key:
        k = _runtime_api_key
        masked = k[:8] + "..." + k[-4:] if len(k) > 12 else "***"
    return {"configured": has_key, "masked_key": masked}


class AIConfigRequest(BaseModel):
    api_key: str


@app.post("/api/ai-config")
def api_ai_config_post(req: AIConfigRequest):
    """Save AI API key."""
    key = req.api_key.strip()
    if not key:
        return {"status": "error", "message": "API key 不能为空"}
    _save_api_key(key)
    return {"status": "ok", "message": "API key 已保存"}


# ========== AI Search ==========

QUERY_DOMAIN_MAP = {
    'cloud': 'Cloud', '云': 'Cloud', '云计算': 'Cloud',
    'ai': 'AI/ML', '人工智能': 'AI/ML', 'ml': 'AI/ML', 'llm': 'AI/ML',
    'security': 'Security', '安全': 'Security', '漏洞': 'Security',
    'web': 'Web', '前端': 'Web', 'frontend': 'Web',
    'devtools': 'DevTools', '开发工具': 'DevTools',
    'mobile': 'Mobile', '移动': 'Mobile',
    'data': 'Data', '数据': 'Data',
    'blockchain': 'Blockchain', '区块链': 'Blockchain',
    'hardware': 'Hardware', '硬件': 'Hardware',
    'biotech': 'Biotech', '生物': 'Biotech',
}


_DOMAIN_URL_MAP = {
    'github.com': 'DevTools', 'gitlab.com': 'DevTools', 'npmjs.com': 'DevTools',
    'arxiv.org': 'AI/ML', 'huggingface.co': 'AI/ML', 'openai.com': 'AI/ML',
    'cloud.google.com': 'Cloud', 'aws.amazon.com': 'Cloud', 'azure.microsoft.com': 'Cloud',
    'developer.apple.com': 'Mobile', 'developer.android.com': 'Mobile',
    'cve.org': 'Security', 'nvd.nist.gov': 'Security',
}

_DOMAIN_KEYWORD_MAP = {
    'AI/ML': ['ai', 'ml', 'llm', 'gpt', 'model', 'neural', 'deep learning', '大模型', '人工智能', '机器学习'],
    'Security': ['security', 'vulnerability', 'cve', 'exploit', '安全', '漏洞', '攻击'],
    'Cloud': ['cloud', 'kubernetes', 'k8s', 'docker', 'aws', 'azure', '云', '容器'],
    'DevTools': ['developer', 'ide', 'compiler', 'framework', 'sdk', '工具', '开发'],
    'Web': ['frontend', 'react', 'vue', 'css', 'browser', '前端', '网页'],
    'Mobile': ['ios', 'android', 'mobile', 'app', '移动', '手机'],
    'Data': ['database', 'sql', 'analytics', 'data', '数据', '数据库'],
    'Blockchain': ['blockchain', 'crypto', 'web3', 'defi', '区块链', '加密'],
    'Biotech': ['biotech', 'genomics', 'crispr', '生物', '基因'],
    'Hardware': ['chip', 'semiconductor', 'cpu', 'gpu', '芯片', '硬件'],
}


def classify_web_result_domain(title: str, url: str, content: str) -> str:
    """Classify a web search result into a domain category."""
    # Layer 1: URL domain matching (high priority)
    url_lower = url.lower()
    for domain_host, domain_name in _DOMAIN_URL_MAP.items():
        if domain_host in url_lower:
            return domain_name

    # Layer 2: keyword matching on title + content
    text = (title + " " + content).lower()
    for domain_name, keywords in _DOMAIN_KEYWORD_MAP.items():
        for kw in keywords:
            if kw in text:
                return domain_name

    return "Other"


def _row_to_item(r) -> dict:
    return {
        "id": r["id"],
        "title": r["title"],
        "url": r["url"],
        "description": r["description"] or "",
        "domain": r["domain"],
        "tags": json.loads(r["tags"]) if r["tags"] else [],
        "heat_index": r["heat_index"],
        "heat_reason": r["heat_reason"] or "",
        "stars": r["stars"],
        "comments_count": r["comments_count"],
        "sources": json.loads(r["sources"]) if r["sources"] else [],
        "published_at": r["published_at"],
    }


def search_items_for_ai(query: str, limit: int = AI_SEARCH_MAX_ITEMS) -> list[dict]:
    """Search classified_items with smart tokenization + domain mapping + fallback."""
    conn = get_connection()

    # Layer 1: smart tokenization — split Chinese and English
    tokens = re.findall(r'[a-zA-Z0-9/._-]+|[\u4e00-\u9fff]+', query)

    # Sliding window for long Chinese tokens (2-char bigrams)
    expanded = []
    for tok in tokens:
        expanded.append(tok)
        if re.match(r'[\u4e00-\u9fff]', tok) and len(tok) > 2:
            for i in range(len(tok) - 1):
                expanded.append(tok[i:i+2])

    # Layer 2: each token as LIKE OR match
    conditions = []
    params: list = []
    for tok in set(expanded):
        conditions.append("(title LIKE ? OR description LIKE ? OR tags LIKE ? OR domain LIKE ?)")
        t = f"%{tok}%"
        params.extend([t, t, t, t])

    # Layer 3: domain mapping — infer domain from tokens
    matched_domains = set()
    for tok in tokens:
        domain = QUERY_DOMAIN_MAP.get(tok.lower())
        if domain:
            matched_domains.add(domain)
    for d in matched_domains:
        conditions.append("domain = ?")
        params.append(d)

    where = " OR ".join(conditions) if conditions else "1=1"
    sql = f"SELECT * FROM classified_items WHERE {where} ORDER BY heat_index DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()

    items = [_row_to_item(r) for r in rows]

    # Layer 4: fallback — if fewer than 5 results, pad with top items
    if len(items) < 5:
        existing_ids = {item["id"] for item in items}
        need = limit - len(items)
        if existing_ids:
            placeholders = ",".join("?" * len(existing_ids))
            extra = conn.execute(
                f"SELECT * FROM classified_items WHERE id NOT IN ({placeholders}) ORDER BY heat_index DESC LIMIT ?",
                [*existing_ids, need],
            ).fetchall()
        else:
            extra = conn.execute(
                "SELECT * FROM classified_items ORDER BY heat_index DESC LIMIT ?",
                [need],
            ).fetchall()
        items.extend(_row_to_item(r) for r in extra)

    conn.close()
    return items


def build_ai_prompt(query: str, items: list[dict]) -> list[dict]:
    """Build messages for GLM-4-Plus API."""
    system = (
        "你是 InsightRadar AI 搜索助手，专门分析科技新闻和开源项目情报。\n"
        "根据用户问题和提供的新闻数据，生成简洁有洞察力的中文摘要。\n"
        "规则：\n"
        "1. 用 [N] 引用来源（N 从 1 开始），关键观点必须有引用\n"
        "2. 中文回答，技术术语可保留英文\n"
        "3. 用 Markdown 格式，### 做小标题分组\n"
        "4. 数据中没有的信息不要编造，诚实说明\n"
        "5. 控制在 500 字以内\n"
        "6. 你具备联网搜索能力，可以搜索最新信息补充回答\n"
        "7. 优先使用提供的本地数据，联网搜索补充最新动态\n"
        "8. 如果本地数据不足以回答，请主动联网搜索获取最新信息\n"
        "9. 联网搜索获取的补充信息，引用编号接在本地数据之后（如本地有 8 条，联网第一条用 [9]）"
    )

    source_lines = []
    for i, item in enumerate(items, 1):
        desc = item["description"][:200] if item["description"] else ""
        sources = ", ".join(item["sources"]) if item["sources"] else ""
        tags = ", ".join(item["tags"][:5]) if item["tags"] else ""
        source_lines.append(
            f"[{i}] {item['title']}\n"
            f"  领域: {item['domain']} | 热度: {item['heat_index']} | Stars: {item['stars']} | 评论: {item['comments_count']}\n"
            f"  来源: {sources} | 标签: {tags}\n"
            f"  描述: {desc}\n"
            f"  URL: {item['url']}"
        )

    user_msg = (
        f"用户问题：{query}\n\n"
        f"相关数据（共 {len(items)} 条）：\n\n"
        + "\n\n".join(source_lines)
        + "\n\n请根据以上数据回答问题，使用 [N] 引用。"
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]


async def _stream_glm(api_key: str, messages: list[dict], enable_search: bool = False):
    """Shared async generator: call GLM API and yield SSE chunks."""
    payload = {
        "model": ZHIPUAI_MODEL,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    if enable_search:
        payload["tools"] = [{
            "type": "web_search",
            "web_search": {
                "enable": True,
                "search_result": True,
            },
        }]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    web_results: list[dict] = []

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST", ZHIPUAI_BASE_URL, json=payload, headers=headers
            ) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    logger.error("GLM API error %s: %s", resp.status_code, body[:500])
                    yield f'event: error\ndata: {{"error": "AI 服务返回错误 ({resp.status_code})"}}\n\n'
                    return

                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        logger.debug("GLM raw chunk keys: %s", list(chunk.keys()))

                        # Capture web_search results (top-level field alongside choices)
                        ws = chunk.get("web_search")
                        if ws and isinstance(ws, list):
                            logger.debug("GLM web_search results (%d): %s", len(ws), json.dumps(ws, ensure_ascii=False)[:500])
                            web_results.extend(ws)

                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            chunk_data = json.dumps({"text": content}, ensure_ascii=False)
                            yield f"data: {chunk_data}\n\n"
                    except (json.JSONDecodeError, IndexError, KeyError):
                        continue

    except httpx.TimeoutException:
        yield 'event: error\ndata: {"error": "AI 服务请求超时，请稍后重试"}\n\n'
        return
    except Exception as e:
        logger.exception("GLM stream error")
        yield f'event: error\ndata: {{"error": "AI 服务异常: {str(e)[:100]}"}}\n\n'
        return

    # Emit web search results before done
    if web_results:
        yield f"event: web_sources\ndata: {json.dumps(web_results, ensure_ascii=False)}\n\n"

    yield "event: done\ndata: {}\n\n"


def _process_web_sources(raw_ws: list[dict]) -> list[dict]:
    """Classify web search results, store in DB, and return formatted items.

    Keeps items even without links (needed for refer-based citation mapping).
    Only stores to DB if a valid URL is present.
    """
    conn = get_connection()
    formatted = []
    for ws in raw_ws:
        title = ws.get("title", "").strip()
        link = ws.get("link", "").strip()
        content = ws.get("content", "").strip()
        media = ws.get("media", "").strip()
        refer = ws.get("refer", "")
        if not title:
            continue

        domain = classify_web_result_domain(title, link or "", content)
        # Only store to DB if we have a valid URL
        if link:
            insert_web_search_item(
                conn, title=title, url=link, content=content, media=media, domain=domain,
            )
        formatted.append({
            "title": title,
            "url": link or "",
            "description": content[:200] if content else "",
            "domain": domain,
            "tags": [],
            "heat_index": 30,
            "heat_reason": "网络搜索结果",
            "stars": 0,
            "comments_count": 0,
            "sources": ["web_search"],
            "published_at": None,
            "refer": refer,
        })
    conn.close()
    return formatted


class AISearchRequest(BaseModel):
    query: str


@app.post("/api/ai-search")
async def api_ai_search(req: AISearchRequest):
    """AI search with streaming SSE response."""
    if not _ai_search_semaphore._value:
        return StreamingResponse(
            iter(["event: error\ndata: {\"error\": \"服务繁忙，请稍后再试\"}\n\n"]),
            media_type="text/event-stream",
            status_code=429,
        )

    async def generate():
        async with _ai_search_semaphore:
            api_key = _runtime_api_key
            if not api_key:
                yield 'event: error\ndata: {"error": "needsApiKey"}\n\n'
                return

            items = search_items_for_ai(req.query)
            sources_data = json.dumps(items, ensure_ascii=False)
            yield f"event: sources\ndata: {sources_data}\n\n"

            if not items:
                yield 'data: {"text": "未找到与您查询相关的内容。请尝试其他关键词。"}\n\n'
                yield "event: done\ndata: {}\n\n"
                return

            messages = build_ai_prompt(req.query, items)
            async for chunk in _stream_glm(api_key, messages, enable_search=True):
                if chunk.startswith("event: web_sources\n"):
                    # Intercept: classify, store, and re-emit formatted web sources
                    try:
                        data_line = chunk.split("data: ", 1)[1].split("\n")[0]
                        raw_ws = json.loads(data_line)
                        formatted = _process_web_sources(raw_ws)
                        if formatted:
                            yield f"event: web_sources\ndata: {json.dumps(formatted, ensure_ascii=False)}\n\n"
                    except Exception:
                        logger.exception("Failed to process web_sources")
                    continue
                yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


# ========== AI Analyze (article deep analysis) ==========

def build_analysis_prompt(item_data: dict) -> list[dict]:
    """Build messages for single-article deep analysis."""
    system = (
        "你是 InsightRadar AI 分析助手，专门深度解读科技新闻和开源项目。\n"
        "根据提供的文章信息，进行多维度深度分析。\n"
        "规则：\n"
        "1. 中文回答，技术术语可保留英文\n"
        "2. 用 Markdown 格式，### 做小标题分组\n"
        "3. 分析维度：核心内容概述 → 技术亮点 → 行业影响 → 潜在风险 → 趋势延伸\n"
        "4. 数据中没有的信息不要编造\n"
        "5. 控制在 600 字以内\n"
        "6. 你具备联网搜索能力，可联网补充文章背景信息和最新动态\n"
        "7. 如果文章信息有限，请主动联网搜索相关内容以丰富分析"
    )

    tags = ", ".join(item_data.get("tags", [])[:8])
    sources = ", ".join(item_data.get("sources", []))
    desc = (item_data.get("description") or "")[:500]

    user_msg = (
        f"请深度解读以下文章/项目：\n\n"
        f"标题：{item_data.get('title', '')}\n"
        f"领域：{item_data.get('domain', '')}\n"
        f"热度：{item_data.get('heat_index', 0)} — {item_data.get('heat_reason', '')}\n"
        f"Stars：{item_data.get('stars', 0)} | 评论：{item_data.get('comments_count', 0)}\n"
        f"来源：{sources}\n"
        f"标签：{tags}\n"
        f"描述：{desc}\n"
        f"URL：{item_data.get('url', '')}\n\n"
        f"请从以上信息出发，进行深度解读。"
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]


class AIAnalyzeRequest(BaseModel):
    title: str = ""
    url: str = ""
    description: str = ""
    domain: str = ""
    tags: list[str] = []
    heat_index: int = 0
    heat_reason: str = ""
    stars: int = 0
    comments_count: int = 0
    sources: list[str] = []


@app.post("/api/ai-analyze")
async def api_ai_analyze(req: AIAnalyzeRequest):
    """Article deep analysis with streaming SSE response."""
    if not _ai_search_semaphore._value:
        return StreamingResponse(
            iter(["event: error\ndata: {\"error\": \"服务繁忙，请稍后再试\"}\n\n"]),
            media_type="text/event-stream",
            status_code=429,
        )

    async def generate():
        async with _ai_search_semaphore:
            api_key = _runtime_api_key
            if not api_key:
                yield 'event: error\ndata: {"error": "needsApiKey"}\n\n'
                return

            messages = build_analysis_prompt(req.model_dump())
            async for chunk in _stream_glm(api_key, messages, enable_search=True):
                yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


# ========== AI Latest (trending summary) ==========

def get_top_items(limit: int = 20) -> list[dict]:
    """Get top items by heat_index for trending summary."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM classified_items ORDER BY heat_index DESC LIMIT ?", [limit]
    ).fetchall()
    conn.close()
    return [_row_to_item(r) for r in rows]


@app.post("/api/ai-latest")
async def api_ai_latest():
    """Trending news AI summary with streaming SSE response."""
    if not _ai_search_semaphore._value:
        return StreamingResponse(
            iter(["event: error\ndata: {\"error\": \"服务繁忙，请稍后再试\"}\n\n"]),
            media_type="text/event-stream",
            status_code=429,
        )

    async def generate():
        async with _ai_search_semaphore:
            api_key = _runtime_api_key
            if not api_key:
                yield 'event: error\ndata: {"error": "needsApiKey"}\n\n'
                return

            items = get_top_items(20)
            sources_data = json.dumps(items, ensure_ascii=False)
            yield f"event: sources\ndata: {sources_data}\n\n"

            if not items:
                yield 'data: {"text": "数据库中暂无数据，请先采集数据。"}\n\n'
                yield "event: done\ndata: {}\n\n"
                return

            query = "今日最热科技新闻与开源动态"
            messages = build_ai_prompt(query, items)
            async for chunk in _stream_glm(api_key, messages, enable_search=True):
                if chunk.startswith("event: web_sources\n"):
                    try:
                        data_line = chunk.split("data: ", 1)[1].split("\n")[0]
                        raw_ws = json.loads(data_line)
                        formatted = _process_web_sources(raw_ws)
                        if formatted:
                            yield f"event: web_sources\ndata: {json.dumps(formatted, ensure_ascii=False)}\n\n"
                    except Exception:
                        logger.exception("Failed to process web_sources")
                    continue
                yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the dashboard page."""
    html_path = STATIC_DIR / "index.html"
    return html_path.read_text(encoding="utf-8")
