"""Unified error handling for InsightRadar."""

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: str = ""
    status_code: int = 500


async def validation_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "detail": str(exc), "status_code": 422},
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)[:200], "status_code": 500},
    )
