"""InsightRadar configuration."""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_PATH = DATA_DIR / "insight_radar.db"
OUTPUT_DIR = PROJECT_ROOT / "output" / "digests"

# Ensure directories exist
for d in [RAW_DIR, PROCESSED_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# GitHub Search API
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")  # 环境变量读取，有则用，无则匿名
GITHUB_SEARCH_QUERY = "stars:>100 pushed:>{date}"  # filled at runtime
GITHUB_MAX_ITEMS = 30

# Hacker News Firebase API
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_TOP_STORIES_URL = f"{HN_API_BASE}/topstories.json"
HN_SHOW_STORIES_URL = f"{HN_API_BASE}/showstories.json"
HN_ITEM_URL = f"{HN_API_BASE}/item/{{item_id}}.json"
HN_MAX_ITEMS = 30

# RSS Feeds — load from data/feeds.json if available, otherwise use defaults
_FEEDS_FILE = DATA_DIR / "feeds.json"
_DEFAULT_RSS_FEEDS = [
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    {"name": "Hacker News Best", "url": "https://hnrss.org/best"},
]

if _FEEDS_FILE.exists():
    try:
        RSS_FEEDS = json.loads(_FEEDS_FILE.read_text(encoding="utf-8"))
        logger.info("Loaded %d RSS feeds from %s", len(RSS_FEEDS), _FEEDS_FILE)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to load %s (%s), using defaults", _FEEDS_FILE, e)
        RSS_FEEDS = _DEFAULT_RSS_FEEDS
else:
    RSS_FEEDS = _DEFAULT_RSS_FEEDS

# ArXiv Paper API
ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.SE"]
ARXIV_MAX_ITEMS = 30

# Heat index weights
HEAT_WEIGHTS = {
    "stars": 0.3,  # GitHub stars / HN points
    "comments": 0.2,  # Discussion activity
    "recency": 0.2,  # How recent
    "cross_platform": 0.3,  # Appears on multiple sources
}

# Domain categories
DOMAINS = [
    "AI/ML",
    "DevTools",
    "Hardware",
    "Cloud",
    "Security",
    "Web",
    "Mobile",
    "Data",
    "Blockchain",
    "Biotech",
    "Other",
]

# Source authority ranking (higher = more authoritative)
SOURCE_AUTHORITY = {
    "github": 3,
    "hackernews": 2,
    "arxiv": 2,
    "rss": 1,
}

# HTTP settings
HTTP_TIMEOUT = 30  # seconds
HTTP_USER_AGENT = "InsightRadar/0.1 (https://github.com/insight-radar)"

# Qwen (通义千问) — DashScope OpenAI-compatible API
QWEN_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
QWEN_MODEL = "qwen-plus"
QWEN_VL_MODEL = "qwen-vl-plus"
AI_SEARCH_MAX_ITEMS = 20
IMAGE_MAX_SIZE_MB = 4
IMAGE_MAX_SIZE_BYTES = IMAGE_MAX_SIZE_MB * 1024 * 1024
