"""Pydantic data models for InsightRadar."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class RawItem(BaseModel):
    """Raw item from any data source."""

    id: int | None = None
    source: str  # "github" | "hackernews" | "rss"
    source_id: str  # unique ID within the source
    title: str
    url: str
    description: str = ""
    author: str = ""
    stars: int = 0  # GitHub stars or HN points
    comments_count: int = 0
    language: str = ""  # programming language (GitHub)
    tags: list[str] = Field(default_factory=list)
    published_at: datetime | None = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    raw_json: str = ""  # original JSON for debugging

    def unique_key(self) -> str:
        return f"{self.source}:{self.source_id}"


class CleanedItem(BaseModel):
    """Item after deduplication and cleaning."""

    id: int | None = None
    title: str
    url: str
    description: str = ""
    author: str = ""
    sources: list[str] = Field(default_factory=list)  # e.g. ["github", "hackernews"]
    source_ids: list[str] = Field(default_factory=list)
    stars: int = 0
    comments_count: int = 0
    language: str = ""
    tags: list[str] = Field(default_factory=list)
    published_at: datetime | None = None
    cleaned_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    merge_note: str = ""  # why items were merged


class ClassifiedItem(BaseModel):
    """Item after classification and heat scoring."""

    id: int | None = None
    cleaned_item_id: int
    title: str
    url: str
    description: str = ""
    author: str = ""
    sources: list[str] = Field(default_factory=list)
    domain: str = "Other"  # one of DOMAINS from config
    tags: list[str] = Field(default_factory=list)
    heat_index: int = 0  # 0-100
    heat_reason: str = ""  # why this heat score
    stars: int = 0
    comments_count: int = 0
    language: str = ""
    published_at: datetime | None = None
    classified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DailyDigest(BaseModel):
    """Metadata for a generated daily digest."""

    date: str  # YYYY-MM-DD
    total_raw: int = 0
    total_cleaned: int = 0
    total_classified: int = 0
    sources_summary: dict[str, int] = Field(default_factory=dict)
    top_domains: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    output_path: str = ""
