"""Translation routes for InsightRadar."""

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.storage.store import aget_db, aget_translation, asave_translation

router = APIRouter(prefix="/api", tags=["translate"])


class TranslateRequest(BaseModel):
    text: str = Field(..., max_length=2000)
    target: str = "zh"


@router.post("/translate")
async def api_translate(req: TranslateRequest):
    """Translate text, with SQLite cache."""
    text = req.text.strip()
    if not text:
        return {"translated": ""}

    # Check cache
    async with aget_db() as conn:
        cached = await aget_translation(conn, text, req.target)
        if cached:
            return {"translated": cached, "cached": True}

        # Call Google Translate free endpoint
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://translate.googleapis.com/translate_a/single",
                    params={
                        "client": "gtx",
                        "sl": "auto",
                        "tl": req.target,
                        "dt": "t",
                        "q": text[:500],
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                translated = "".join(part[0] for part in data[0] if part[0])
        except Exception as e:
            return {"translated": "", "error": str(e)}

        # Save to cache
        await asave_translation(conn, text, translated, req.target)
    return {"translated": translated, "cached": False}
