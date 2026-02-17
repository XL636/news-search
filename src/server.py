"""FastAPI web dashboard for InsightRadar."""

import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.config import DB_PATH
from src.storage.store import get_connection, init_db


STATIC_DIR = Path(__file__).parent / "static"


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
    limit: int = Query(200),
):
    """Get classified items with optional filters."""
    conn = get_connection()
    query = "SELECT * FROM classified_items WHERE 1=1"
    params: list = []

    if domain and domain != "All":
        query += " AND domain = ?"
        params.append(domain)

    if search:
        query += " AND (title LIKE ? OR description LIKE ? OR tags LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    if sort == "heat":
        query += " ORDER BY heat_index DESC"
    elif sort == "stars":
        query += " ORDER BY stars DESC"
    elif sort == "recent":
        query += " ORDER BY published_at DESC"
    elif sort == "comments":
        query += " ORDER BY comments_count DESC"

    query += " LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
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
    return items


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


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the dashboard page."""
    html_path = STATIC_DIR / "index.html"
    return html_path.read_text(encoding="utf-8")
