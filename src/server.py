"""FastAPI web dashboard for InsightRadar."""

import asyncio
import json
import logging
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
from src.storage.store import get_connection, get_translation, init_db, save_translation

logger = logging.getLogger(__name__)


STATIC_DIR = Path(__file__).parent / "static"

_collect_lock = asyncio.Lock()
_ai_search_semaphore = asyncio.Semaphore(3)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    conn = get_connection()
    init_db(conn)
    conn.close()
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


# ========== AI Search ==========

def search_items_for_ai(query: str, limit: int = AI_SEARCH_MAX_ITEMS) -> list[dict]:
    """Search classified_items with wide matching for AI context."""
    conn = get_connection()
    tokens = query.split()
    conditions = []
    params: list[str] = []

    # Full query as one LIKE (handles Chinese without spaces)
    conditions.append("(title LIKE ? OR description LIKE ? OR tags LIKE ? OR domain LIKE ?)")
    term = f"%{query}%"
    params.extend([term, term, term, term])

    # Each token as separate OR condition
    for tok in tokens:
        if tok == query:
            continue
        conditions.append("(title LIKE ? OR description LIKE ? OR tags LIKE ? OR domain LIKE ?)")
        t = f"%{tok}%"
        params.extend([t, t, t, t])

    where = " OR ".join(conditions)
    sql = f"SELECT * FROM classified_items WHERE {where} ORDER BY heat_index DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
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
        })
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
        "5. 控制在 500 字以内"
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
            # 1. Check API key
            if not ZHIPUAI_API_KEY:
                yield 'event: error\ndata: {"error": "AI 搜索未配置：请设置 ZHIPUAI_API_KEY 环境变量"}\n\n'
                return

            # 2. Search matching items
            items = search_items_for_ai(req.query)

            # 3. Send sources first
            sources_data = json.dumps(items, ensure_ascii=False)
            yield f"event: sources\ndata: {sources_data}\n\n"

            if not items:
                yield 'data: {"text": "未找到与您查询相关的内容。请尝试其他关键词。"}\n\n'
                yield "event: done\ndata: {}\n\n"
                return

            # 4. Build prompt and call GLM API
            messages = build_ai_prompt(req.query, items)
            payload = {
                "model": ZHIPUAI_MODEL,
                "messages": messages,
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 1024,
            }
            headers = {
                "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                "Content-Type": "application/json",
            }

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
                logger.exception("AI search error")
                yield f'event: error\ndata: {{"error": "AI 搜索异常: {str(e)[:100]}"}}\n\n'
                return

            yield "event: done\ndata: {}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the dashboard page."""
    html_path = STATIC_DIR / "index.html"
    return html_path.read_text(encoding="utf-8")
