"""RSS feed aggregator using feedparser."""

import hashlib
import json
import logging
from datetime import datetime

import feedparser
import httpx
from dateutil import parser as date_parser

from src.collectors.base import BaseCollector
from src.config import HTTP_TIMEOUT, HTTP_USER_AGENT, RSS_FEEDS
from src.models.schemas import RawItem

logger = logging.getLogger(__name__)


class RSSCollector(BaseCollector):
    """Collect articles from configured RSS feeds."""

    name = "rss"

    def _parse_date(self, entry: dict) -> datetime | None:
        for field in ["published", "updated", "created"]:
            val = entry.get(field)
            if val:
                try:
                    return date_parser.parse(val)
                except (ValueError, TypeError):
                    continue
        return None

    def _make_source_id(self, feed_name: str, entry: dict) -> str:
        """Generate a stable source ID from feed name and entry link/title."""
        key = entry.get("link", "") or entry.get("title", "")
        return hashlib.sha256(f"{feed_name}:{key}".encode()).hexdigest()[:16]

    async def collect(self) -> list[RawItem]:
        items: list[RawItem] = []

        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            for feed_cfg in RSS_FEEDS:
                feed_name = feed_cfg["name"]
                feed_url = feed_cfg["url"]

                try:
                    resp = await client.get(feed_url, headers={"User-Agent": HTTP_USER_AGENT})
                    resp.raise_for_status()
                    feed_text = resp.text
                except httpx.HTTPError as e:
                    logger.error("RSS feed %s error: %s", feed_name, e)
                    continue

                feed = feedparser.parse(feed_text)

                for entry in feed.entries[:30]:
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "").strip()
                    if not title or not link:
                        continue

                    # Extract description/summary
                    desc = ""
                    if entry.get("summary"):
                        desc = entry["summary"]
                    elif entry.get("description"):
                        desc = entry["description"]
                    # Strip HTML tags (basic)
                    if "<" in desc:
                        import re

                        desc = re.sub(r"<[^>]+>", "", desc).strip()
                    # Truncate long descriptions
                    if len(desc) > 500:
                        desc = desc[:497] + "..."

                    author = entry.get("author", "")
                    published = self._parse_date(entry)

                    # Extract tags from categories
                    tags = []
                    for tag in entry.get("tags", []):
                        if isinstance(tag, dict) and tag.get("term"):
                            tags.append(tag["term"])
                        elif isinstance(tag, str):
                            tags.append(tag)

                    items.append(
                        RawItem(
                            source="rss",
                            source_id=self._make_source_id(feed_name, entry),
                            title=f"[{feed_name}] {title}",
                            url=link,
                            description=desc,
                            author=author,
                            tags=tags,
                            published_at=published,
                            raw_json=json.dumps(
                                {"feed": feed_name, "title": title, "link": link},
                                default=str,
                            ),
                        )
                    )

        logger.info("RSS: collected %d articles", len(items))
        return items
