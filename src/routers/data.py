"""Data API routes for InsightRadar."""

import asyncio
import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from src.pipeline import cmd_collect
from src.storage.store import (
    get_connection,
    get_item_trend,
    get_trending_items,
    take_daily_snapshot,
)

router = APIRouter(prefix="/api", tags=["data"])

_collect_lock = asyncio.Lock()

SETTINGS_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "settings.json"


# ========== WebSocket Manager ==========

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


ws_manager = ConnectionManager()


# ========== Endpoints ==========

@router.get("/domains")
def api_domains():
    """Get all domains with item counts."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT domain, COUNT(*) as count FROM classified_items GROUP BY domain ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return JSONResponse(
        content=[{"domain": r["domain"], "count": r["count"]} for r in rows],
        headers={"Cache-Control": "public, max-age=60"},
    )


@router.get("/items")
def api_items(
    domain: str | None = Query(None),
    search: str | None = Query(None, max_length=200),
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


@router.get("/stats")
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
    return JSONResponse(content=stats, headers={"Cache-Control": "public, max-age=60"})


@router.post("/collect")
async def api_collect():
    """Trigger data collection. Returns 409 if already running."""
    if _collect_lock.locked():
        return {"status": "busy", "message": "Collection already in progress"}

    async with _collect_lock:
        try:
            result = await cmd_collect()
            await ws_manager.broadcast({"type": "collection_complete", "stats": result})
            return {
                "status": "ok",
                "stats": result,
                "message": "Collection complete. Run /insight-radar to process data.",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


@router.get("/trends")
def api_trends(days: int = Query(3), limit: int = Query(20)):
    """Get trending items based on heat_index changes between snapshots."""
    conn = get_connection()
    items = get_trending_items(conn, days=days, limit=limit)
    for item in items:
        item["history"] = get_item_trend(conn, item["url"], days=7)
    conn.close()
    return JSONResponse(content={"items": items}, headers={"Cache-Control": "public, max-age=60"})


@router.post("/snapshot")
def api_snapshot():
    """Manually trigger a daily heat snapshot."""
    conn = get_connection()
    count = take_daily_snapshot(conn)
    conn.close()
    return {"status": "ok", "snapshotted": count}


@router.get("/scheduler")
def api_scheduler_status():
    """Get scheduler status and next run times."""
    from src.scheduler import get_scheduler_status
    return JSONResponse(content=get_scheduler_status(), headers={"Cache-Control": "public, max-age=10"})


# ========== Health Check ==========

@router.get("/health")
def api_health():
    """Health check endpoint returning system status."""
    status = {"status": "ok", "checks": {}}

    # Database check
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        status["checks"]["database"] = {"status": "ok"}
    except Exception as e:
        status["checks"]["database"] = {"status": "error", "detail": str(e)[:100]}
        status["status"] = "degraded"

    # Scheduler check
    try:
        from src.scheduler import get_scheduler_status
        sched = get_scheduler_status()
        status["checks"]["scheduler"] = {"status": "ok" if sched.get("running") else "stopped"}
    except Exception:
        status["checks"]["scheduler"] = {"status": "unknown"}

    return status


# ========== WebSocket ==========

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# ========== User Preferences ==========

class UserPreferences(BaseModel):
    language: str = "zh"
    theme: str = "warm"
    default_view: str = "ai-search"
    default_sort: str = "heat"
    items_per_page: int = 20


@router.get("/preferences")
def get_preferences():
    """Get user preferences."""
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            prefs = data.get("preferences", {})
            return UserPreferences(**prefs).model_dump()
        except Exception:
            pass
    return UserPreferences().model_dump()


@router.post("/preferences")
def save_preferences(prefs: UserPreferences):
    """Save user preferences."""
    data = {}
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    data["preferences"] = prefs.model_dump()
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok"}


# ========== Data Export ==========

@router.get("/export")
def api_export(format: str = Query("json", pattern="^(json|csv)$")):
    """Export classified items as JSON or CSV."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM classified_items ORDER BY heat_index DESC LIMIT 5000"
    ).fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "id": r["id"], "title": r["title"], "url": r["url"],
            "description": r["description"] or "", "domain": r["domain"],
            "tags": r["tags"] or "[]", "heat_index": r["heat_index"],
            "stars": r["stars"], "comments_count": r["comments_count"],
            "language": r["language"] or "", "published_at": r["published_at"] or "",
            "sources": r["sources"] or "[]",
        })

    if format == "csv":
        output = io.StringIO()
        if items:
            writer = csv.DictWriter(output, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=insightradar-export.csv"},
        )

    return Response(
        content=json.dumps(items, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=insightradar-export.json"},
    )


# ========== Feed Health ==========

@router.get("/feed-health")
def api_feed_health():
    """Get RSS feed health status from collect_meta."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT source, last_collected_at FROM collect_meta ORDER BY source"
    ).fetchall()
    conn.close()

    now = datetime.now(timezone.utc)
    health = []
    for r in rows:
        last = r["last_collected_at"]
        try:
            last_dt = datetime.fromisoformat(last)
            hours_ago = (now - last_dt).total_seconds() / 3600
            status = "healthy" if hours_ago < 25 else ("stale" if hours_ago < 72 else "dead")
        except Exception:
            hours_ago = -1
            status = "unknown"
        health.append({
            "source": r["source"],
            "last_collected": last,
            "hours_ago": round(hours_ago, 1),
            "status": status,
        })
    return {"feeds": health}
