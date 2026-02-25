"""Unified error handling for InsightRadar."""

import logging
import os

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

_DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")


class ErrorResponse(BaseModel):
    error: str
    detail: str = ""
    status_code: int = 500


async def validation_exception_handler(request: Request, exc):
    detail = str(exc) if _DEBUG else "Invalid request parameters"
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "detail": detail, "status_code": 422},
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    detail = str(exc)[:200] if _DEBUG else "An unexpected error occurred"
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": detail, "status_code": 500},
    )
