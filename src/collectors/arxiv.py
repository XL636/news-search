"""ArXiv paper collector using the ArXiv API."""

import json
import logging
import re
from datetime import datetime

import feedparser
import httpx
from dateutil import parser as date_parser

from src.collectors.base import BaseCollector
from src.config import (
    ARXIV_API_URL,
    ARXIV_CATEGORIES,
    ARXIV_MAX_ITEMS,
    HTTP_TIMEOUT,
    HTTP_USER_AGENT,
)
from src.models.schemas import RawItem

logger = logging.getLogger(__name__)


class ArXivCollector(BaseCollector):
    """Collect recent papers from ArXiv in CS categories."""

    name = "arxiv"

    def _extract_arxiv_id(self, entry_id: str) -> str:
        """Extract ArXiv paper ID from entry id URL.

        Example: 'http://arxiv.org/abs/2401.12345v1' -> '2401.12345'
        """
        match = re.search(r"(\d{4}\.\d{4,5})", entry_id)
        if match:
            return match.group(1)
        # Fallback: use the last path segment
        return entry_id.rstrip("/").split("/")[-1]

    def _parse_date(self, entry: dict) -> datetime | None:
        for field in ["published", "updated"]:
            val = entry.get(field)
            if val:
                try:
                    return date_parser.parse(val)
                except (ValueError, TypeError):
                    continue
        return None

    def _build_query_url(self) -> str:
        """Build the ArXiv API query URL."""
        cat_query = " OR ".join(f"cat:{cat}" for cat in ARXIV_CATEGORIES)
        params = (
            f"search_query={cat_query}&start=0&max_results={ARXIV_MAX_ITEMS}&sortBy=submittedDate&sortOrder=descending"
        )
        return f"{ARXIV_API_URL}?{params}"

    async def collect(self) -> list[RawItem]:
        items: list[RawItem] = []
        url = self._build_query_url()

        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.get(url, headers={"User-Agent": HTTP_USER_AGENT})
            resp.raise_for_status()
            feed_text = resp.text

        feed = feedparser.parse(feed_text)

        for entry in feed.entries:
            title = " ".join(entry.get("title", "").split())
            link = entry.get("link", "").strip()
            if not title or not link:
                continue

            arxiv_id = self._extract_arxiv_id(entry.get("id", link))
            abs_url = f"https://arxiv.org/abs/{arxiv_id}"

            # Abstract
            summary = entry.get("summary", "")
            summary = " ".join(summary.split())
            if len(summary) > 500:
                summary = summary[:497] + "..."

            # First author
            authors = entry.get("authors", [])
            first_author = ""
            if authors:
                if isinstance(authors[0], dict):
                    first_author = authors[0].get("name", "")
                elif hasattr(authors[0], "name"):
                    first_author = authors[0].name

            # Categories as tags
            tags = []
            for tag in entry.get("tags", []):
                if isinstance(tag, dict) and tag.get("term"):
                    tags.append(tag["term"])
                elif hasattr(tag, "term"):
                    tags.append(tag.term)

            published = self._parse_date(entry)

            items.append(
                RawItem(
                    source="arxiv",
                    source_id=f"arxiv:{arxiv_id}",
                    title=title,
                    url=abs_url,
                    description=summary,
                    author=first_author,
                    tags=tags,
                    published_at=published,
                    raw_json=json.dumps(
                        {"arxiv_id": arxiv_id, "title": title, "link": abs_url},
                        default=str,
                    ),
                )
            )

        logger.info("ArXiv: collected %d papers", len(items))
        return items
