"""FastAPI web dashboard for InsightRadar."""

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config import DB_PATH
from src.pipeline import cmd_collect
from src.storage.store import get_connection, get_translation, init_db, save_translation


STATIC_DIR = Path(__file__).parent / "static"

_collect_lock = asyncio.Lock()


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


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the dashboard page."""
    html_path = STATIC_DIR / "index.html"
    return html_path.read_text(encoding="utf-8")
