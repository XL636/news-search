"""In-memory TTL cache layer for InsightRadar API endpoints."""

import functools
import hashlib
import json

from cachetools import TTLCache

# Cache instances with different TTLs per use-case
stats_cache = TTLCache(maxsize=100, ttl=60)  # /api/stats, /api/domains — 60s
items_cache = TTLCache(maxsize=50, ttl=30)  # /api/items results — 30s
trends_cache = TTLCache(maxsize=10, ttl=120)  # /api/trends — 120s


def _make_key(prefix: str, **kwargs) -> str:
    """Build a deterministic cache key from prefix + sorted kwargs."""
    raw = json.dumps(kwargs, sort_keys=True, default=str)
    digest = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"{prefix}:{digest}"


def cached(cache: TTLCache, prefix: str):
    """Decorator that caches the return value of an endpoint function.

    The cache key is derived from the function's keyword arguments.
    Works with sync functions only (FastAPI sync endpoints).
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(**kwargs):
            key = _make_key(prefix, **kwargs)
            if key in cache:
                return cache[key]
            result = fn(**kwargs)
            cache[key] = result
            return result

        return wrapper

    return decorator


def invalidate(*caches: TTLCache):
    """Clear one or more cache instances."""
    for c in caches:
        c.clear()
