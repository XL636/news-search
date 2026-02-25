"""InsightRadar MCP Server — expose dashboard data as Claude Code tools."""

import asyncio
import json
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

from src.pipeline import cmd_collect
from src.storage.store import (
    get_connection,
    get_translation,
    init_db,
    save_translation,
)

mcp = FastMCP("InsightRadar", instructions="全球创新与开源情报聚合系统 — 查询情报、触发采集、翻译文本")

# Ensure DB is initialized
_conn = get_connection()
init_db(_conn)
_conn.close()

_collect_lock = asyncio.Lock()


@mcp.tool()
def get_items(
    domain: str = "All",
    search: str = "",
    sort: str = "heat",
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """查询分类后的情报条目，支持领域过滤、搜索、排序和分页。

    Args:
        domain: 领域过滤，如 AI/ML, DevTools, Security 等，"All" 为全部
        search: 搜索关键词（匹配标题/描述/标签）
        sort: 排序方式 - heat(热度) / stars / comments / recent
        limit: 每页数量
        offset: 偏移量
    """
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

    total = conn.execute(f"SELECT COUNT(*) FROM classified_items {base_where}", params).fetchone()[0]

    order_map = {
        "heat": "heat_index DESC",
        "stars": "stars DESC",
        "recent": "published_at DESC",
        "comments": "comments_count DESC",
    }
    order = order_map.get(sort, "heat_index DESC")

    rows = conn.execute(
        f"SELECT * FROM classified_items {base_where} ORDER BY {order} LIMIT ? OFFSET ?",
        [*params, limit, offset],
    ).fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append(
            {
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
            }
        )
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@mcp.tool()
def get_domains() -> list[dict]:
    """获取所有领域及其条目数量。"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT domain, COUNT(*) as count FROM classified_items GROUP BY domain ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [{"domain": r["domain"], "count": r["count"]} for r in rows]


@mcp.tool()
def get_stats() -> dict:
    """获取数据库统计信息（原始/清洗/分类条目数 + 数据源分布）。"""
    conn = get_connection()
    stats = {}
    for table in ["raw_items", "cleaned_items", "classified_items"]:
        stats[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    rows = conn.execute("SELECT source, COUNT(*) as cnt FROM raw_items GROUP BY source").fetchall()
    stats["sources"] = {r["source"]: r["cnt"] for r in rows}
    conn.close()
    return stats


@mcp.tool()
async def collect_data() -> dict:
    """触发数据采集（GitHub + HN + RSS），返回采集统计。"""
    if _collect_lock.locked():
        return {"status": "busy", "message": "采集任务正在进行中"}

    async with _collect_lock:
        try:
            result = await cmd_collect()
            return {"status": "ok", "stats": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}


@mcp.tool()
async def translate_text(text: str, target: str = "zh") -> dict:
    """翻译文本（带 SQLite 缓存），默认翻译为中文。

    Args:
        text: 要翻译的文本
        target: 目标语言代码，默认 zh（中文）
    """
    import httpx

    text = text.strip()
    if not text:
        return {"translated": ""}

    conn = get_connection()
    cached = get_translation(conn, text, target)
    if cached:
        conn.close()
        return {"translated": cached, "cached": True}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "auto", "tl": target, "dt": "t", "q": text[:500]},
            )
            resp.raise_for_status()
            data = resp.json()
            translated = "".join(part[0] for part in data[0] if part[0])
    except Exception as e:
        conn.close()
        return {"translated": "", "error": str(e)}

    save_translation(conn, text, translated, target)
    conn.close()
    return {"translated": translated, "cached": False}


if __name__ == "__main__":
    mcp.run()
