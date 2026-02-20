"""SQLite storage layer for InsightRadar."""

import hashlib
import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
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


@contextmanager
def get_db(db_path: Path | None = None):
    """Context manager for database connections. Auto-closes on exit."""
    conn = get_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


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

        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_text_hash TEXT NOT NULL,
            target_lang TEXT NOT NULL,
            source_text TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(source_text_hash, target_lang)
        );

        CREATE INDEX IF NOT EXISTS idx_raw_source ON raw_items(source);
        CREATE INDEX IF NOT EXISTS idx_raw_collected ON raw_items(collected_at);
        CREATE INDEX IF NOT EXISTS idx_raw_url ON raw_items(url);
        CREATE INDEX IF NOT EXISTS idx_classified_domain ON classified_items(domain);
        CREATE INDEX IF NOT EXISTS idx_classified_heat ON classified_items(heat_index DESC);
        CREATE INDEX IF NOT EXISTS idx_classified_url ON classified_items(url);
        CREATE INDEX IF NOT EXISTS idx_translations_lookup ON translations(source_text_hash, target_lang);

        CREATE TABLE IF NOT EXISTS heat_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_url TEXT NOT NULL,
            title TEXT,
            domain TEXT,
            heat_index INTEGER,
            snapshot_date TEXT NOT NULL,
            UNIQUE(item_url, snapshot_date)
        );

        CREATE INDEX IF NOT EXISTS idx_snapshot_date ON heat_snapshots(snapshot_date);
        CREATE INDEX IF NOT EXISTS idx_snapshot_url_date ON heat_snapshots(item_url, snapshot_date);
    """)

    # FTS5 virtual table and sync triggers (must be outside executescript)
    try:
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS classified_items_fts USING fts5(
                title, description, tags,
                content='classified_items',
                content_rowid='id'
            )
        """)
    except Exception:
        pass

    try:
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS fts_ai AFTER INSERT ON classified_items BEGIN
                INSERT INTO classified_items_fts(rowid, title, description, tags)
                VALUES (new.id, new.title, new.description, new.tags);
            END
        """)
    except Exception:
        pass

    try:
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS fts_ad AFTER DELETE ON classified_items BEGIN
                INSERT INTO classified_items_fts(classified_items_fts, rowid, title, description, tags)
                VALUES ('delete', old.id, old.title, old.description, old.tags);
            END
        """)
    except Exception:
        pass

    try:
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS fts_au AFTER UPDATE ON classified_items BEGIN
                INSERT INTO classified_items_fts(classified_items_fts, rowid, title, description, tags)
                VALUES ('delete', old.id, old.title, old.description, old.tags);
                INSERT INTO classified_items_fts(rowid, title, description, tags)
                VALUES (new.id, new.title, new.description, new.tags);
            END
        """)
    except Exception:
        pass

    conn.commit()

    # Populate FTS index from existing data
    try:
        rebuild_fts_index(conn)
    except Exception:
        pass  # FTS table may not exist yet on first run


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
        cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
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


def get_classified_items(conn: sqlite3.Connection, limit: int = 1000, offset: int = 0) -> list[ClassifiedItem]:
    """Get classified items, ordered by heat index, with pagination."""
    rows = conn.execute(
        "SELECT * FROM classified_items ORDER BY heat_index DESC LIMIT ? OFFSET ?",
        (limit, offset),
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
    now = datetime.now(timezone.utc).isoformat()
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


# --- Web Search Items ---

def insert_web_search_item(
    conn: sqlite3.Connection,
    *,
    title: str,
    url: str,
    content: str,
    media: str,
    domain: str,
) -> int | None:
    """Insert a web search result into raw→cleaned→classified pipeline.

    Returns classified_items row id, or None if URL already exists.
    """
    # Dedup: skip if URL already in classified_items or raw_items
    existing = conn.execute(
        "SELECT id FROM classified_items WHERE url = ?", (url,)
    ).fetchone()
    if existing:
        return None
    existing = conn.execute(
        "SELECT id FROM raw_items WHERE url = ?", (url,)
    ).fetchone()
    if existing:
        return None

    now = datetime.now(timezone.utc).isoformat()
    source_id = hashlib.md5(url.encode("utf-8")).hexdigest()[:16]

    try:
        # 1. raw_items
        cur = conn.execute(
            """INSERT INTO raw_items
               (source, source_id, title, url, description, author,
                stars, comments_count, language, tags, published_at,
                collected_at, raw_json)
               VALUES (?, ?, ?, ?, ?, ?, 0, 0, '', '[]', ?, ?, '')""",
            ("web_search", source_id, title, url, content, media, now, now),
        )
        raw_id = cur.lastrowid

        # 2. cleaned_items
        cur = conn.execute(
            """INSERT INTO cleaned_items
               (title, url, description, author, sources, source_ids,
                stars, comments_count, language, tags, published_at,
                cleaned_at, merge_note)
               VALUES (?, ?, ?, ?, '["web_search"]', ?, 0, 0, '', '[]', ?, ?, '')""",
            (title, url, content, media, json.dumps([source_id]), now, now),
        )
        cleaned_id = cur.lastrowid

        # 3. classified_items
        cur = conn.execute(
            """INSERT INTO classified_items
               (cleaned_item_id, title, url, description, author, sources,
                domain, tags, heat_index, heat_reason, stars, comments_count,
                language, published_at, classified_at)
               VALUES (?, ?, ?, ?, ?, '["web_search"]', ?, '[]', 30, '网络搜索结果', 0, 0, '', ?, ?)""",
            (cleaned_id, title, url, content, media, domain, now, now),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


# --- Translations Cache ---

def _text_hash(text: str) -> str:
    """MD5 hash of text for cache lookup."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def get_translation(conn: sqlite3.Connection, text: str, target_lang: str) -> str | None:
    """Look up a cached translation. Returns translated text or None."""
    h = _text_hash(text[:500])
    row = conn.execute(
        "SELECT translated_text FROM translations WHERE source_text_hash = ? AND target_lang = ?",
        (h, target_lang),
    ).fetchone()
    return row["translated_text"] if row else None


def save_translation(conn: sqlite3.Connection, text: str, translated: str, target_lang: str) -> None:
    """Save a translation to the cache."""
    h = _text_hash(text[:500])
    try:
        conn.execute(
            """INSERT INTO translations (source_text_hash, target_lang, source_text, translated_text, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (h, target_lang, text[:500], translated, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # already cached


# --- Heat Snapshots (Trend Tracking) ---

def take_daily_snapshot(conn: sqlite3.Connection) -> int:
    """Snapshot current classified_items heat_index into heat_snapshots.
    Returns count of items snapshotted."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT url, title, domain, heat_index FROM classified_items"
    ).fetchall()
    count = 0
    for r in rows:
        try:
            conn.execute(
                """INSERT INTO heat_snapshots (item_url, title, domain, heat_index, snapshot_date)
                   VALUES (?, ?, ?, ?, ?)""",
                (r["url"], r["title"], r["domain"], r["heat_index"], today),
            )
            count += 1
        except sqlite3.IntegrityError:
            pass  # already snapshotted today
    conn.commit()
    return count


def get_trending_items(conn: sqlite3.Connection, days: int = 3, limit: int = 20) -> list[dict]:
    """Compare latest two snapshots, return items with biggest heat_index changes."""
    dates = conn.execute(
        "SELECT DISTINCT snapshot_date FROM heat_snapshots ORDER BY snapshot_date DESC LIMIT 2"
    ).fetchall()
    if len(dates) < 2:
        return []

    latest_date = dates[0]["snapshot_date"]
    prev_date = dates[1]["snapshot_date"]

    rows = conn.execute("""
        SELECT
            a.item_url, a.title, a.domain, a.heat_index as current_heat,
            b.heat_index as prev_heat,
            (a.heat_index - b.heat_index) as delta
        FROM heat_snapshots a
        JOIN heat_snapshots b ON a.item_url = b.item_url
        WHERE a.snapshot_date = ? AND b.snapshot_date = ?
        ORDER BY ABS(a.heat_index - b.heat_index) DESC
        LIMIT ?
    """, (latest_date, prev_date, limit)).fetchall()

    return [{
        "url": r["item_url"],
        "title": r["title"],
        "domain": r["domain"],
        "heat_index": r["current_heat"],
        "prev_heat": r["prev_heat"],
        "delta": r["delta"],
        "direction": "up" if r["delta"] > 0 else ("down" if r["delta"] < 0 else "stable"),
    } for r in rows]


def get_item_trend(conn: sqlite3.Connection, item_url: str, days: int = 7) -> list[dict]:
    """Return heat_index history for a single item over the last N days."""
    rows = conn.execute(
        """SELECT heat_index, snapshot_date FROM heat_snapshots
           WHERE item_url = ?
           ORDER BY snapshot_date DESC LIMIT ?""",
        (item_url, days),
    ).fetchall()
    return [{"heat_index": r["heat_index"], "date": r["snapshot_date"]} for r in rows]


# --- Data TTL Cleanup ---

def cleanup_old_data(conn: sqlite3.Connection, days: int = 30) -> dict:
    """Delete data older than N days. Returns counts of deleted rows."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    counts = {}
    for table, col in [
        ("raw_items", "collected_at"),
        ("cleaned_items", "cleaned_at"),
        ("classified_items", "classified_at"),
    ]:
        cursor = conn.execute(f"DELETE FROM {table} WHERE {col} < ?", (cutoff,))
        counts[table] = cursor.rowcount

    # Heat snapshots use date format
    cursor = conn.execute("DELETE FROM heat_snapshots WHERE snapshot_date < ?", (cutoff_date,))
    counts["heat_snapshots"] = cursor.rowcount

    # Translation cache
    cursor = conn.execute("DELETE FROM translations WHERE created_at < ?", (cutoff,))
    counts["translations"] = cursor.rowcount

    conn.commit()
    return counts


# --- FTS5 Full-Text Search ---

def rebuild_fts_index(conn: sqlite3.Connection) -> int:
    """Rebuild FTS5 index from classified_items. Call after bulk imports."""
    conn.execute("DELETE FROM classified_items_fts")
    cursor = conn.execute(
        "INSERT INTO classified_items_fts(rowid, title, description, tags) "
        "SELECT id, title, description, tags FROM classified_items"
    )
    conn.commit()
    return cursor.rowcount


def search_fts(conn: sqlite3.Connection, query: str, limit: int = 20, offset: int = 0) -> list[dict]:
    """Full-text search using FTS5. Returns classified items matching query."""
    tokens = re.findall(r'[a-zA-Z0-9]+|[\u4e00-\u9fff]+', query)
    if not tokens:
        return []

    fts_query = " OR ".join(f'"{t}"' for t in tokens)

    rows = conn.execute(
        """SELECT c.* FROM classified_items_fts f
           JOIN classified_items c ON f.rowid = c.id
           WHERE classified_items_fts MATCH ?
           ORDER BY rank
           LIMIT ? OFFSET ?""",
        (fts_query, limit, offset),
    ).fetchall()

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
            "author": r["author"] or "",
            "language": r["language"] or "",
        })
    return items
