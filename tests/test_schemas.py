"""Tests for src/models/schemas.py."""
from src.models.schemas import ClassifiedItem, RawItem


class TestRawItem:
    def test_create_minimal(self):
        item = RawItem(source="github", source_id="123", title="Test", url="https://example.com")
        assert item.source == "github"
        assert item.stars == 0
        assert item.tags == []

    def test_unique_key(self):
        item = RawItem(source="github", source_id="abc", title="T", url="https://x.com")
        assert item.unique_key() == "github:abc"

    def test_collected_at_is_utc(self):
        item = RawItem(source="test", source_id="1", title="T", url="https://x.com")
        assert item.collected_at.tzinfo is not None


class TestClassifiedItem:
    def test_defaults(self):
        item = ClassifiedItem(cleaned_item_id=1, title="T", url="https://x.com")
        assert item.domain == "Other"
        assert item.heat_index == 0
        assert item.tags == []
