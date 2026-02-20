"""Shared test fixtures for InsightRadar."""
import sqlite3

import pytest

from src.storage.store import init_db


@pytest.fixture
def db_conn(tmp_path):
    """Create a temporary SQLite database for testing."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    init_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def sample_raw_item():
    """Return a sample RawItem dict for testing."""
    return {
        "source": "github",
        "source_id": "test-123",
        "title": "Test Repository",
        "url": "https://github.com/test/repo",
        "description": "A test repository for unit testing",
        "author": "testuser",
        "stars": 100,
        "comments_count": 10,
        "language": "Python",
        "tags": ["test", "python"],
    }
