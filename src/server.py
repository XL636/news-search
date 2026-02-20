"""FastAPI web dashboard for InsightRadar."""

import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

from src.config import ZHIPUAI_API_KEY
from src.routers import ai, data, translate
from src.routers.errors import general_exception_handler, validation_exception_handler
from src.storage.store import get_connection, init_db

STATIC_DIR = Path(__file__).parent / "static"
SETTINGS_FILE = Path(__file__).parent.parent / "data" / "settings.json"


def _load_api_key() -> str:
    """Load API key from env var or settings file."""
    if ZHIPUAI_API_KEY:
        return ZHIPUAI_API_KEY
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return data.get("zhipuai_api_key", "")
        except (json.JSONDecodeError, OSError):
            pass
    return ""


def _save_api_key(key: str):
    """Save API key to settings file."""
    ai.set_api_key(key)
    existing = {}
    if SETTINGS_FILE.exists():
        try:
            existing = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    existing["zhipuai_api_key"] = key
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and scheduler on startup."""
    conn = get_connection()
    init_db(conn)
    conn.close()
    # Load and distribute API key
    loaded_key = _load_api_key()
    ai.set_api_key(loaded_key)
    # Start scheduler
    from src.scheduler import start_scheduler
    start_scheduler()
    yield
    # Shutdown scheduler
    from src.scheduler import stop_scheduler
    stop_scheduler()


app = FastAPI(
    title="InsightRadar",
    description="全球创新与开源情报聚合系统 — AI-powered tech news aggregation and analysis",
    version="0.19.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: https://fastapi.tiangolo.com; "
            "connect-src 'self' https://translate.googleapis.com https://open.bigmodel.cn ws: wss:"
        )
        return response


app.add_middleware(CSPMiddleware)

# Register error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(data.router)
app.include_router(ai.router)
app.include_router(translate.router)


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the dashboard page."""
    html_path = STATIC_DIR / "index.html"
    return html_path.read_text(encoding="utf-8")
