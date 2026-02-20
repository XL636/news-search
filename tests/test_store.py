"""Tests for src/storage/store.py."""
from datetime import datetime, timezone

from src.models.schemas import ClassifiedItem, CleanedItem, RawItem
from src.storage.store import (
    get_classified_items,
    get_last_collect_time,
    get_raw_items,
    get_stats,
    insert_classified_item,
    insert_cleaned_item,
    insert_raw_item,
    set_last_collect_time,
)


class TestRawItems:
    def test_insert_and_retrieve(self, db_conn, sample_raw_item):
        item = RawItem(**sample_raw_item)
        row_id = insert_raw_item(db_conn, item)
        assert row_id is not None
        assert row_id > 0

    def test_duplicate_insert_returns_none(self, db_conn, sample_raw_item):
        item = RawItem(**sample_raw_item)
        insert_raw_item(db_conn, item)
        result = insert_raw_item(db_conn, item)
        assert result is None

    def test_get_raw_items_by_source(self, db_conn, sample_raw_item):
        item = RawItem(**sample_raw_item)
        insert_raw_item(db_conn, item)
        items = get_raw_items(db_conn, source="github", since_hours=0)
        assert len(items) >= 1
        assert items[0].source == "github"


class TestClassifiedItems:
    def test_insert_and_get(self, db_conn):
        # First insert a cleaned item (FK requirement)
        cleaned = CleanedItem(
            title="Test",
            url="https://example.com",
            description="Test desc",
            sources=["github"],
            cleaned_at=datetime.now(timezone.utc),
        )
        cleaned_id = insert_cleaned_item(db_conn, cleaned)

        item = ClassifiedItem(
            cleaned_item_id=cleaned_id,
            title="Test",
            url="https://example.com",
            description="Test desc",
            domain="DevTools",
            heat_index=75,
            sources=["github"],
            classified_at=datetime.now(timezone.utc),
        )
        row_id = insert_classified_item(db_conn, item)
        assert row_id > 0

        items = get_classified_items(db_conn, limit=10)
        assert len(items) == 1
        assert items[0].domain == "DevTools"
        assert items[0].heat_index == 75


class TestStats:
    def test_empty_stats(self, db_conn):
        stats = get_stats(db_conn)
        assert stats["raw_items"] == 0
        assert stats["classified_items"] == 0


class TestCollectMeta:
    def test_set_and_get_collect_time(self, db_conn):
        set_last_collect_time(db_conn, "github")
        result = get_last_collect_time(db_conn, "github")
        assert result is not None

    def test_get_nonexistent_source(self, db_conn):
        result = get_last_collect_time(db_conn, "nonexistent")
        assert result is None
