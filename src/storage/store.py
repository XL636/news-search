"""SQLite storage layer for InsightRadar."""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from src.config import DB_PATH
from src.models.schemas import ClassifiedItem, CleanedItem, RawItem


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Get a SQLite connection with WAL mode."""
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS raw_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT DEFAULT '',
            author TEXT DEFAULT '',
            stars INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            language TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            published_at TEXT,
            collected_at TEXT NOT NULL,
            raw_json TEXT DEFAULT '',
            UNIQUE(source, source_id)
        );

        CREATE TABLE IF NOT EXISTS cleaned_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT DEFAULT '',
            author TEXT DEFAULT '',
            sources TEXT DEFAULT '[]',
            source_ids TEXT DEFAULT '[]',
            stars INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            language TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            published_at TEXT,
            cleaned_at TEXT NOT NULL,
            merge_note TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS classified_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cleaned_item_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT DEFAULT '',
            author TEXT DEFAULT '',
            sources TEXT DEFAULT '[]',
            domain TEXT DEFAULT 'Other',
            tags TEXT DEFAULT '[]',
            heat_index INTEGER DEFAULT 0,
            heat_reason TEXT DEFAULT '',
            stars INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            language TEXT DEFAULT '',
            published_at TEXT,
            classified_at TEXT NOT NULL,
            FOREIGN KEY (cleaned_item_id) REFERENCES cleaned_items(id)
        );

        CREATE TABLE IF NOT EXISTS collect_meta (
            source TEXT PRIMARY KEY,
            last_collected_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_raw_source ON raw_items(source);
        CREATE INDEX IF NOT EXISTS idx_raw_collected ON raw_items(collected_at);
        CREATE INDEX IF NOT EXISTS idx_classified_domain ON classified_items(domain);
        CREATE INDEX IF NOT EXISTS idx_classified_heat ON classified_items(heat_index DESC);
    """)
    conn.commit()


def _serialize_dt(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s)


# --- Raw Items ---

def insert_raw_item(conn: sqlite3.Connection, item: RawItem) -> int | None:
    """Insert a raw item, skip if duplicate. Returns row id or None."""
    try:
        cursor = conn.execute(
            """INSERT INTO raw_items
               (source, source_id, title, url, description, author,
                stars, comments_count, language, tags, published_at,
                collected_at, raw_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                item.source,
                item.source_id,
                item.title,
                item.url,
                item.description,
                item.author,
                item.stars,
                item.comments_count,
                item.language,
                json.dumps(item.tags),
                _serialize_dt(item.published_at),
                _serialize_dt(item.collected_at),
                item.raw_json,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # duplicate


def get_raw_items(
    conn: sqlite3.Connection,
    source: str | None = None,
    since_hours: int = 48,
) -> list[RawItem]:
    """Get raw items, optionally filtered by source and recency."""
    query = "SELECT * FROM raw_items WHERE 1=1"
    params: list = []

    if source:
        query += " AND source = ?"
        params.append(source)

    if since_hours > 0:
        cutoff = datetime.utcnow() - timedelta(hours=since_hours)
        query += " AND collected_at >= ?"
        params.append(cutoff.isoformat())

    query += " ORDER BY collected_at DESC"

    rows = conn.execute(query, params).fetchall()
    items = []
    for row in rows:
        items.append(RawItem(
            id=row["id"],
            source=row["source"],
            source_id=row["source_id"],
            title=row["title"],
            url=row["url"],
            description=row["description"],
            author=row["author"],
            stars=row["stars"],
            comments_count=row["comments_count"],
            language=row["language"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            published_at=_parse_dt(row["published_at"]),
            collected_at=_parse_dt(row["collected_at"]),
            raw_json=row["raw_json"],
        ))
    return items


# --- Cleaned Items ---

def insert_cleaned_item(conn: sqlite3.Connection, item: CleanedItem) -> int:
    """Insert a cleaned item. Returns row id."""
    cursor = conn.execute(
        """INSERT INTO cleaned_items
           (title, url, description, author, sources, source_ids,
            stars, comments_count, language, tags, published_at,
            cleaned_at, merge_note)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            item.title,
            item.url,
            item.description,
            item.author,
            json.dumps(item.sources),
            json.dumps(item.source_ids),
            item.stars,
            item.comments_count,
            item.language,
            json.dumps(item.tags),
            _serialize_dt(item.published_at),
            _serialize_dt(item.cleaned_at),
            item.merge_note,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_cleaned_items(conn: sqlite3.Connection) -> list[CleanedItem]:
    """Get all cleaned items from the latest cleaning session."""
    rows = conn.execute(
        "SELECT * FROM cleaned_items ORDER BY cleaned_at DESC"
    ).fetchall()
    items = []
    for row in rows:
        items.append(CleanedItem(
            id=row["id"],
            title=row["title"],
            url=row["url"],
            description=row["description"],
            author=row["author"],
            sources=json.loads(row["sources"]) if row["sources"] else [],
            source_ids=json.loads(row["source_ids"]) if row["source_ids"] else [],
            stars=row["stars"],
            comments_count=row["comments_count"],
            language=row["language"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            published_at=_parse_dt(row["published_at"]),
            cleaned_at=_parse_dt(row["cleaned_at"]),
            merge_note=row["merge_note"],
        ))
    return items


# --- Classified Items ---

def insert_classified_item(conn: sqlite3.Connection, item: ClassifiedItem) -> int:
    """Insert a classified item. Returns row id."""
    cursor = conn.execute(
        """INSERT INTO classified_items
           (cleaned_item_id, title, url, description, author, sources,
            domain, tags, heat_index, heat_reason, stars, comments_count,
            language, published_at, classified_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            item.cleaned_item_id,
            item.title,
            item.url,
            item.description,
            item.author,
            json.dumps(item.sources),
            item.domain,
            json.dumps(item.tags),
            item.heat_index,
            item.heat_reason,
            item.stars,
            item.comments_count,
            item.language,
            _serialize_dt(item.published_at),
            _serialize_dt(item.classified_at),
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_classified_items(conn: sqlite3.Connection) -> list[ClassifiedItem]:
    """Get all classified items, ordered by heat index."""
    rows = conn.execute(
        "SELECT * FROM classified_items ORDER BY heat_index DESC"
    ).fetchall()
    items = []
    for row in rows:
        items.append(ClassifiedItem(
            id=row["id"],
            cleaned_item_id=row["cleaned_item_id"],
            title=row["title"],
            url=row["url"],
            description=row["description"],
            author=row["author"],
            sources=json.loads(row["sources"]) if row["sources"] else [],
            domain=row["domain"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            heat_index=row["heat_index"],
            heat_reason=row["heat_reason"],
            stars=row["stars"],
            comments_count=row["comments_count"],
            language=row["language"],
            published_at=_parse_dt(row["published_at"]),
            classified_at=_parse_dt(row["classified_at"]),
        ))
    return items


# --- Utility ---

def get_stats(conn: sqlite3.Connection) -> dict:
    """Get database statistics."""
    stats = {}
    for table in ["raw_items", "cleaned_items", "classified_items"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        stats[table] = count

    # Source breakdown for raw_items
    rows = conn.execute(
        "SELECT source, COUNT(*) as cnt FROM raw_items GROUP BY source"
    ).fetchall()
    stats["sources"] = {row["source"]: row["cnt"] for row in rows}

    return stats


def get_last_collect_time(conn: sqlite3.Connection, source: str) -> str | None:
    """Get the last collection timestamp for a source."""
    row = conn.execute(
        "SELECT last_collected_at FROM collect_meta WHERE source = ?", (source,)
    ).fetchone()
    return row["last_collected_at"] if row else None


def set_last_collect_time(conn: sqlite3.Connection, source: str) -> None:
    """Record the current time as last collection time for a source."""
    now = datetime.utcnow().isoformat()
    conn.execute(
        """INSERT INTO collect_meta (source, last_collected_at) VALUES (?, ?)
           ON CONFLICT(source) DO UPDATE SET last_collected_at = excluded.last_collected_at""",
        (source, now),
    )
    conn.commit()


def clear_processed(conn: sqlite3.Connection) -> None:
    """Clear cleaned and classified tables for a fresh processing run."""
    conn.execute("DELETE FROM classified_items")
    conn.execute("DELETE FROM cleaned_items")
    conn.commit()
