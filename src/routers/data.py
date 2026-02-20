"""Data API routes for InsightRadar."""

import asyncio
import csv
import io
import json
from pathlib import Path

from fastapi import APIRouter, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.cache import invalidate, items_cache, stats_cache, trends_cache
from src.pipeline import cmd_collect
from src.storage.store import (
    aget_classified_items,
    aget_db,
    aget_domains,
    aget_export_items,
    aget_feed_health,
    aget_item_trend,
    aget_stats,
    aget_trending_items,
    asearch_fts,
    get_connection,
    take_daily_snapshot,
)

router = APIRouter(prefix="/api", tags=["data"])

limiter = Limiter(key_func=get_remote_address)
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
@limiter.limit("120/minute")
async def api_domains(request: Request):
    """Get all domains with item counts."""
    cache_key = "domains"
    if cache_key in stats_cache:
        return JSONResponse(
            content=stats_cache[cache_key],
            headers={"Cache-Control": "public, max-age=60"},
        )
    async with aget_db() as conn:
        result = await aget_domains(conn)
    stats_cache[cache_key] = result
    return JSONResponse(
        content=result,
        headers={"Cache-Control": "public, max-age=60"},
    )


@router.get("/items")
@limiter.limit("120/minute")
async def api_items(
    request: Request,
    domain: str | None = Query(None),
    search: str | None = Query(None, max_length=200),
    sort: str = Query("heat"),
    limit: int = Query(20),
    offset: int = Query(0),
):
    """Get classified items with optional filters and pagination."""
    cache_key = f"items:{domain}:{search}:{sort}:{limit}:{offset}"
    if cache_key in items_cache:
        return items_cache[cache_key]
    async with aget_db() as conn:
        items, total = await aget_classified_items(
            conn, domain=domain, limit=limit, offset=offset, search=search, sort=sort,
        )
    result = {"items": items, "total": total, "limit": limit, "offset": offset}
    items_cache[cache_key] = result
    return result


@router.get("/search")
@limiter.limit("120/minute")
async def api_search(
    request: Request,
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Full-text search across classified items using FTS5."""
    async with aget_db() as conn:
        items = await asearch_fts(conn, q, limit, offset)
    return {"items": items, "query": q, "total": len(items)}


@router.get("/stats")
@limiter.limit("120/minute")
async def api_stats(request: Request):
    """Get database statistics."""
    cache_key = "stats"
    if cache_key in stats_cache:
        return JSONResponse(content=stats_cache[cache_key], headers={"Cache-Control": "public, max-age=60"})
    async with aget_db() as conn:
        stats = await aget_stats(conn)
    stats_cache[cache_key] = stats
    return JSONResponse(content=stats, headers={"Cache-Control": "public, max-age=60"})


@router.post("/collect")
@limiter.limit("5/minute")
async def api_collect(request: Request):
    """Trigger data collection. Returns 409 if already running."""
    if _collect_lock.locked():
        return {"status": "busy", "message": "Collection already in progress"}

    async with _collect_lock:
        try:
            result = await cmd_collect()
            invalidate(stats_cache, items_cache, trends_cache)
            await ws_manager.broadcast({"type": "collection_complete", "stats": result})
            return {
                "status": "ok",
                "stats": result,
                "message": "Collection complete. Run /insight-radar to process data.",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


@router.get("/trends")
@limiter.limit("120/minute")
async def api_trends(request: Request, days: int = Query(3), limit: int = Query(20)):
    """Get trending items based on heat_index changes between snapshots."""
    cache_key = f"trends:{days}:{limit}"
    if cache_key in trends_cache:
        return JSONResponse(content=trends_cache[cache_key], headers={"Cache-Control": "public, max-age=60"})
    async with aget_db() as conn:
        items = await aget_trending_items(conn, days=days, limit=limit)
        for item in items:
            item["history"] = await aget_item_trend(conn, item["url"], days=7)
    result = {"items": items}
    trends_cache[cache_key] = result
    return JSONResponse(content=result, headers={"Cache-Control": "public, max-age=60"})


@router.post("/snapshot")
@limiter.limit("5/minute")
def api_snapshot(request: Request):
    """Manually trigger a daily heat snapshot."""
    conn = get_connection()
    count = take_daily_snapshot(conn)
    conn.close()
    invalidate(trends_cache)
    return {"status": "ok", "snapshotted": count}


@router.get("/scheduler")
def api_scheduler_status():
    """Get scheduler status and next run times."""
    from src.scheduler import get_scheduler_status
    return JSONResponse(content=get_scheduler_status(), headers={"Cache-Control": "public, max-age=10"})


# ========== Health Check ==========

@router.get("/health")
async def api_health():
    """Health check endpoint returning system status."""
    status = {"status": "ok", "checks": {}}

    # Database check
    try:
        async with aget_db() as conn:
            await conn.execute("SELECT 1")
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
async def api_export(
    format: str = Query("json", pattern="^(json|csv)$"),
    domain: str | None = Query(None),
    search: str | None = Query(None, max_length=200),
    sort: str = Query("heat"),
):
    """Export classified items as JSON or CSV, respecting current filters."""
    async with aget_db() as conn:
        if domain or search:
            items, _ = await aget_classified_items(
                conn, domain=domain, search=search, sort=sort, limit=5000, offset=0,
            )
        else:
            items = await aget_export_items(conn)

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
async def api_feed_health():
    """Get RSS feed health status from collect_meta."""
    async with aget_db() as conn:
        health = await aget_feed_health(conn)
    return {"feeds": health}
