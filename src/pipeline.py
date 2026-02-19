"""InsightRadar CLI pipeline — collect, status, export."""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import DATA_DIR, PROCESSED_DIR, RAW_DIR
from src.collectors.arxiv import ArXivCollector
from src.collectors.github_trending import GitHubCollector
from src.collectors.hackernews import HackerNewsCollector
from src.collectors.rss_feeds import RSSCollector
from src.storage.store import (
    get_connection,
    get_last_collect_time,
    get_raw_items,
    get_stats,
    init_db,
    insert_raw_item,
    set_last_collect_time,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("pipeline")

COLLECTORS = {
    "github": GitHubCollector,
    "hackernews": HackerNewsCollector,
    "rss": RSSCollector,
    "arxiv": ArXivCollector,
}


async def cmd_collect(sources: list[str] | None = None) -> dict:
    """Run data collection from specified sources."""
    conn = get_connection()
    init_db(conn)

    if sources:
        active = {k: v for k, v in COLLECTORS.items() if k in sources}
    else:
        active = COLLECTORS

    if not active:
        logger.error("No valid sources specified. Available: %s", list(COLLECTORS.keys()))
        return {"error": "No valid sources"}

    stats = {"total": 0, "new": 0, "duplicate": 0, "sources": {}}

    for name, collector_cls in active.items():
        last_time = get_last_collect_time(conn, name)
        if last_time:
            logger.info("Collecting from %s (last run: %s)...", name, last_time)
        else:
            logger.info("Collecting from %s (first run)...", name)

        collector = collector_cls()
        try:
            items = await collector.collect_with_retry()
        except Exception as e:
            logger.error("Collector %s failed after retries: %s", name, e)
            stats["sources"][name] = {"collected": 0, "error": str(e)}
            continue

        new_count = 0
        for item in items:
            row_id = insert_raw_item(conn, item)
            if row_id is not None:
                new_count += 1

        stats["total"] += len(items)
        stats["new"] += new_count
        stats["duplicate"] += len(items) - new_count
        stats["sources"][name] = {
            "collected": len(items),
            "new": new_count,
            "duplicate": len(items) - new_count,
        }
        set_last_collect_time(conn, name)
        logger.info("  %s: %d items (%d new, %d duplicate)",
                     name, len(items), new_count, len(items) - new_count)

    # Save raw data snapshot
    today = datetime.now().strftime("%Y-%m-%d")
    raw_dir = RAW_DIR / today
    raw_dir.mkdir(parents=True, exist_ok=True)

    all_items = get_raw_items(conn, since_hours=48)
    raw_path = raw_dir / "raw_items.json"
    raw_path.write_text(
        json.dumps([item.model_dump(mode="json") for item in all_items], indent=2, default=str),
        encoding="utf-8",
    )

    conn.close()

    logger.info("Collection complete: %d total, %d new, %d duplicate",
                stats["total"], stats["new"], stats["duplicate"])
    logger.info("Raw data saved to %s", raw_path)
    return stats


def cmd_status() -> dict:
    """Show database statistics."""
    conn = get_connection()
    init_db(conn)
    stats = get_stats(conn)
    conn.close()

    print("\n=== InsightRadar Database Status ===")
    print(f"  Raw items:        {stats.get('raw_items', 0)}")
    print(f"  Cleaned items:    {stats.get('cleaned_items', 0)}")
    print(f"  Classified items: {stats.get('classified_items', 0)}")
    if stats.get("sources"):
        print("\n  Sources breakdown:")
        for source, count in stats["sources"].items():
            print(f"    {source}: {count}")
    print()
    return stats


def cmd_export(output_path: str | None = None) -> str:
    """Export raw items to JSON."""
    conn = get_connection()
    init_db(conn)
    items = get_raw_items(conn, since_hours=0)  # all items
    conn.close()

    if not output_path:
        today = datetime.now().strftime("%Y-%m-%d")
        out_dir = PROCESSED_DIR / today
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / "export.json")

    data = [item.model_dump(mode="json") for item in items]
    Path(output_path).write_text(
        json.dumps(data, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Exported {len(data)} items to {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="InsightRadar — Global Innovation Intelligence Pipeline"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # collect
    collect_p = sub.add_parser("collect", help="Collect data from sources")
    collect_p.add_argument(
        "--source",
        choices=list(COLLECTORS.keys()),
        nargs="+",
        help="Specific sources to collect from (default: all)",
    )

    # status
    sub.add_parser("status", help="Show database statistics")

    # export
    export_p = sub.add_parser("export", help="Export raw items to JSON")
    export_p.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    if args.command == "collect":
        asyncio.run(cmd_collect(args.source))
    elif args.command == "status":
        cmd_status()
    elif args.command == "export":
        cmd_export(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
