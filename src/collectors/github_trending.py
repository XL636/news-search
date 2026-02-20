"""GitHub trending repositories collector using Search API."""

import json
import logging
from datetime import datetime, timedelta, timezone

import httpx

from src.config import (
    GITHUB_API_BASE,
    GITHUB_MAX_ITEMS,
    GITHUB_TOKEN,
    HTTP_TIMEOUT,
    HTTP_USER_AGENT,
)
from src.collectors.base import BaseCollector
from src.models.schemas import RawItem

logger = logging.getLogger(__name__)


class GitHubCollector(BaseCollector):
    """Collect trending repositories from GitHub Search API."""

    name = "github"

    async def collect(self) -> list[RawItem]:
        items: list[RawItem] = []
        since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        query = f"stars:>50 pushed:>{since}"

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": HTTP_USER_AGENT,
        }
        if GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            try:
                resp = await client.get(
                    f"{GITHUB_API_BASE}/search/repositories",
                    params={
                        "q": query,
                        "sort": "stars",
                        "order": "desc",
                        "per_page": GITHUB_MAX_ITEMS,
                    },
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as e:
                logger.error("GitHub API error: %s", e)
                return items

        for repo in data.get("items", [])[:GITHUB_MAX_ITEMS]:
            published = None
            if repo.get("created_at"):
                try:
                    published = datetime.fromisoformat(
                        repo["created_at"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            items.append(RawItem(
                source="github",
                source_id=str(repo["id"]),
                title=repo.get("full_name", ""),
                url=repo.get("html_url", ""),
                description=repo.get("description", "") or "",
                author=repo.get("owner", {}).get("login", ""),
                stars=repo.get("stargazers_count", 0),
                comments_count=repo.get("open_issues_count", 0),
                language=repo.get("language", "") or "",
                tags=repo.get("topics") or [],
                published_at=published,
                raw_json=json.dumps(repo, default=str),
            ))

        logger.info("GitHub: collected %d repos", len(items))
        return items
