"""Hacker News collector using Firebase API."""

import asyncio
import json
import logging
from datetime import datetime

import httpx

from src.config import (
    HN_ITEM_URL,
    HN_MAX_ITEMS,
    HN_SHOW_STORIES_URL,
    HN_TOP_STORIES_URL,
    HTTP_TIMEOUT,
    HTTP_USER_AGENT,
)
from src.collectors.base import BaseCollector
from src.models.schemas import RawItem

logger = logging.getLogger(__name__)


class HackerNewsCollector(BaseCollector):
    """Collect top and Show HN stories from Hacker News."""

    name = "hackernews"

    async def _fetch_item(
        self, client: httpx.AsyncClient, item_id: int
    ) -> dict | None:
        try:
            resp = await client.get(
                HN_ITEM_URL.format(item_id=item_id),
                headers={"User-Agent": HTTP_USER_AGENT},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            logger.warning("HN item %d fetch error: %s", item_id, e)
            return None

    async def collect(self) -> list[RawItem]:
        items: list[RawItem] = []
        seen_ids: set[int] = set()

        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            # Fetch both top stories and Show HN
            story_ids: list[int] = []
            for url in [HN_TOP_STORIES_URL, HN_SHOW_STORIES_URL]:
                try:
                    resp = await client.get(
                        url, headers={"User-Agent": HTTP_USER_AGENT}
                    )
                    resp.raise_for_status()
                    ids = resp.json() or []
                    for sid in ids[:HN_MAX_ITEMS]:
                        if sid not in seen_ids:
                            story_ids.append(sid)
                            seen_ids.add(sid)
                except httpx.HTTPError as e:
                    logger.error("HN story list error (%s): %s", url, e)

            # Fetch items in batches of 10
            for i in range(0, len(story_ids), 10):
                batch = story_ids[i : i + 10]
                results = await asyncio.gather(
                    *(self._fetch_item(client, sid) for sid in batch)
                )
                for story in results:
                    if not story or story.get("type") != "story":
                        continue
                    if story.get("dead") or story.get("deleted"):
                        continue

                    published = None
                    if story.get("time"):
                        published = datetime.utcfromtimestamp(story["time"])

                    hn_url = story.get("url", "")
                    if not hn_url:
                        hn_url = f"https://news.ycombinator.com/item?id={story['id']}"

                    items.append(RawItem(
                        source="hackernews",
                        source_id=str(story["id"]),
                        title=story.get("title", ""),
                        url=hn_url,
                        description=story.get("text", "") or "",
                        author=story.get("by", ""),
                        stars=story.get("score", 0),
                        comments_count=story.get("descendants", 0),
                        published_at=published,
                        raw_json=json.dumps(story, default=str),
                    ))

        logger.info("HackerNews: collected %d stories", len(items))
        return items
