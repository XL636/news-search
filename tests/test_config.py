"""Tests for src/config.py."""
from src.config import DB_PATH, DOMAINS, GITHUB_API_BASE


class TestConfig:
    def test_domains_not_empty(self):
        assert len(DOMAINS) > 0

    def test_github_api_base(self):
        assert "github.com" in GITHUB_API_BASE or "api.github.com" in GITHUB_API_BASE

    def test_db_path_is_path(self):
        assert str(DB_PATH).endswith(".db")
