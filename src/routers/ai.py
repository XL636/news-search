"""AI search and analysis routes for InsightRadar."""

import asyncio
import base64 as _b64
import json
import logging
import re

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import (
    AI_SEARCH_MAX_ITEMS,
    IMAGE_MAX_SIZE_BYTES,
    QWEN_BASE_URL,
    QWEN_MODEL,
    QWEN_VL_MODEL,
)
from src.storage.store import aget_db, get_db, insert_web_search_item

router = APIRouter(prefix="/api", tags=["ai"])

limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

# Runtime state — set by server.py lifespan
_runtime_api_key: str = ""
_ai_search_semaphore = asyncio.Semaphore(3)


def set_api_key(key: str):
    global _runtime_api_key
    _runtime_api_key = key


def get_api_key() -> str:
    return _runtime_api_key


# ========== Domain Classification Maps ==========

QUERY_DOMAIN_MAP = {
    "cloud": "Cloud",
    "云": "Cloud",
    "云计算": "Cloud",
    "ai": "AI/ML",
    "人工智能": "AI/ML",
    "ml": "AI/ML",
    "llm": "AI/ML",
    "security": "Security",
    "安全": "Security",
    "漏洞": "Security",
    "web": "Web",
    "前端": "Web",
    "frontend": "Web",
    "devtools": "DevTools",
    "开发工具": "DevTools",
    "mobile": "Mobile",
    "移动": "Mobile",
    "data": "Data",
    "数据": "Data",
    "blockchain": "Blockchain",
    "区块链": "Blockchain",
    "hardware": "Hardware",
    "硬件": "Hardware",
    "biotech": "Biotech",
    "生物": "Biotech",
}

_DOMAIN_URL_MAP = {
    "github.com": "DevTools",
    "gitlab.com": "DevTools",
    "npmjs.com": "DevTools",
    "arxiv.org": "AI/ML",
    "huggingface.co": "AI/ML",
    "openai.com": "AI/ML",
    "cloud.google.com": "Cloud",
    "aws.amazon.com": "Cloud",
    "azure.microsoft.com": "Cloud",
    "developer.apple.com": "Mobile",
    "developer.android.com": "Mobile",
    "cve.org": "Security",
    "nvd.nist.gov": "Security",
}

_DOMAIN_KEYWORD_MAP = {
    "AI/ML": ["ai", "ml", "llm", "gpt", "model", "neural", "deep learning", "大模型", "人工智能", "机器学习"],
    "Security": ["security", "vulnerability", "cve", "exploit", "安全", "漏洞", "攻击"],
    "Cloud": ["cloud", "kubernetes", "k8s", "docker", "aws", "azure", "云", "容器"],
    "DevTools": ["developer", "ide", "compiler", "framework", "sdk", "工具", "开发"],
    "Web": ["frontend", "react", "vue", "css", "browser", "前端", "网页"],
    "Mobile": ["ios", "android", "mobile", "app", "移动", "手机"],
    "Data": ["database", "sql", "analytics", "data", "数据", "数据库"],
    "Blockchain": ["blockchain", "crypto", "web3", "defi", "区块链", "加密"],
    "Biotech": ["biotech", "genomics", "crispr", "生物", "基因"],
    "Hardware": ["chip", "semiconductor", "cpu", "gpu", "芯片", "硬件"],
}


# ========== Helper Functions ==========


def classify_web_result_domain(title: str, url: str, content: str) -> str:
    """Classify a web search result into a domain category."""
    url_lower = url.lower()
    for domain_host, domain_name in _DOMAIN_URL_MAP.items():
        if domain_host in url_lower:
            return domain_name

    text = (title + " " + content).lower()
    for domain_name, keywords in _DOMAIN_KEYWORD_MAP.items():
        for kw in keywords:
            if kw in text:
                return domain_name

    return "Other"


def _row_to_item(r) -> dict:
    return {
        "id": r["id"],
        "title": r["title"],
        "url": r["url"],
        "description": r["description"] or "",
        "domain": r["domain"],
        "tags": json.loads(r["tags"]) if r["tags"] else [],
        "heat_index": r["heat_index"],
        "heat_reason": r["heat_reason"] or "",
        "stars": r["stars"],
        "comments_count": r["comments_count"],
        "sources": json.loads(r["sources"]) if r["sources"] else [],
        "published_at": r["published_at"],
    }


def search_items_for_ai(query: str, limit: int = AI_SEARCH_MAX_ITEMS) -> list[dict]:
    """Search classified_items with smart tokenization + domain mapping + fallback."""
    with get_db() as conn:
        tokens = re.findall(r"[a-zA-Z0-9/._-]+|[\u4e00-\u9fff]+", query)

        expanded = []
        for tok in tokens:
            expanded.append(tok)
            if re.match(r"[\u4e00-\u9fff]", tok) and len(tok) > 2:
                for i in range(len(tok) - 1):
                    expanded.append(tok[i : i + 2])

        conditions = []
        params: list = []
        for tok in set(expanded):
            conditions.append("(title LIKE ? OR description LIKE ? OR tags LIKE ? OR domain LIKE ?)")
            t = f"%{tok}%"
            params.extend([t, t, t, t])

        matched_domains = set()
        for tok in tokens:
            domain = QUERY_DOMAIN_MAP.get(tok.lower())
            if domain:
                matched_domains.add(domain)
        for d in matched_domains:
            conditions.append("domain = ?")
            params.append(d)

        where = " OR ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM classified_items WHERE {where} ORDER BY heat_index DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()

        items = [_row_to_item(r) for r in rows]

        if 1 <= len(items) < 5:
            existing_ids = {item["id"] for item in items}
            need = limit - len(items)
            placeholders = ",".join("?" * len(existing_ids))
            extra = conn.execute(
                f"SELECT * FROM classified_items WHERE id NOT IN ({placeholders}) ORDER BY heat_index DESC LIMIT ?",
                [*existing_ids, need],
            ).fetchall()
            items.extend(_row_to_item(r) for r in extra)

    return items


async def asearch_items_for_ai(query: str, limit: int = AI_SEARCH_MAX_ITEMS) -> list[dict]:
    """Async search classified_items with smart tokenization + domain mapping + fallback."""
    async with aget_db() as conn:
        tokens = re.findall(r"[a-zA-Z0-9/._-]+|[\u4e00-\u9fff]+", query)

        expanded = []
        for tok in tokens:
            expanded.append(tok)
            if re.match(r"[\u4e00-\u9fff]", tok) and len(tok) > 2:
                for i in range(len(tok) - 1):
                    expanded.append(tok[i : i + 2])

        conditions = []
        params: list = []
        for tok in set(expanded):
            conditions.append("(title LIKE ? OR description LIKE ? OR tags LIKE ? OR domain LIKE ?)")
            t = f"%{tok}%"
            params.extend([t, t, t, t])

        matched_domains = set()
        for tok in tokens:
            domain = QUERY_DOMAIN_MAP.get(tok.lower())
            if domain:
                matched_domains.add(domain)
        for d in matched_domains:
            conditions.append("domain = ?")
            params.append(d)

        where = " OR ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM classified_items WHERE {where} ORDER BY heat_index DESC LIMIT ?"
        params.append(limit)
        async with conn.execute(sql, params) as cursor:
            rows = await cursor.fetchall()

        items = [_row_to_item(r) for r in rows]

        if 1 <= len(items) < 5:
            existing_ids = {item["id"] for item in items}
            need = limit - len(items)
            placeholders = ",".join("?" * len(existing_ids))
            async with conn.execute(
                f"SELECT * FROM classified_items WHERE id NOT IN ({placeholders}) ORDER BY heat_index DESC LIMIT ?",
                [*existing_ids, need],
            ) as cursor:
                extra = await cursor.fetchall()
            items.extend(_row_to_item(r) for r in extra)

    return items


async def aget_top_items(limit: int = 20) -> list[dict]:
    """Async get top items by heat_index for trending summary."""
    async with (
        aget_db() as conn,
        conn.execute("SELECT * FROM classified_items ORDER BY heat_index DESC LIMIT ?", [limit]) as cursor,
    ):
        rows = await cursor.fetchall()
    return [_row_to_item(r) for r in rows]


def build_ai_prompt(query: str, items: list[dict]) -> list[dict]:
    """Build messages for Qwen API."""
    system = (
        "你是 InsightRadar AI 搜索助手，专门分析科技新闻和开源项目情报。\n"
        "根据用户问题和提供的新闻数据，生成简洁有洞察力的中文摘要。\n"
        "规则：\n"
        "1. 用 [N] 引用来源（N 从 1 开始），关键观点必须有引用\n"
        "2. 中文回答，技术术语可保留英文\n"
        "3. 用 Markdown 格式，### 做小标题分组\n"
        "4. 数据中没有的信息不要编造，诚实说明\n"
        "5. 控制在 500 字以内\n"
        "6. 你具备联网搜索能力，可以搜索最新信息补充回答\n"
        "7. 优先使用提供的本地数据，联网搜索补充最新动态\n"
        "8. 如果本地数据不足以回答，请主动联网搜索获取最新信息\n"
        "9. 联网搜索获取的信息，不要使用 [N] 编号引用（N 仅用于引用本地数据）。联网搜索结果请直接描述，无需编号。"
    )

    if not items:
        user_msg = f"用户问题：{query}\n\n本地数据库中没有相关数据。请使用联网搜索获取最新信息并回答。"
    else:
        source_lines = []
        for i, item in enumerate(items, 1):
            desc = item["description"][:200] if item["description"] else ""
            sources = ", ".join(item["sources"]) if item["sources"] else ""
            tags = ", ".join(item["tags"][:5]) if item["tags"] else ""
            source_lines.append(
                f"[{i}] {item['title']}\n"
                f"  领域: {item['domain']} | 热度: {item['heat_index']} | Stars: {item['stars']} | 评论: {item['comments_count']}\n"
                f"  来源: {sources} | 标签: {tags}\n"
                f"  描述: {desc}\n"
                f"  URL: {item['url']}"
            )

        user_msg = (
            f"用户问题：{query}\n\n"
            f"相关数据（共 {len(items)} 条）：\n\n"
            + "\n\n".join(source_lines)
            + "\n\n请根据以上数据回答问题，使用 [N] 引用。"
        )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]


def build_analysis_prompt(item_data: dict) -> list[dict]:
    """Build messages for single-article deep analysis."""
    system = (
        "你是 InsightRadar AI 分析助手，专门深度解读科技新闻和开源项目。\n"
        "根据提供的文章信息，进行多维度深度分析。\n"
        "规则：\n"
        "1. 中文回答，技术术语可保留英文\n"
        "2. 用 Markdown 格式，### 做小标题分组\n"
        "3. 分析维度：核心内容概述 → 技术亮点 → 行业影响 → 潜在风险 → 趋势延伸\n"
        "4. 数据中没有的信息不要编造\n"
        "5. 控制在 600 字以内\n"
        "6. 你具备联网搜索能力，可联网补充文章背景信息和最新动态\n"
        "7. 如果文章信息有限，请主动联网搜索相关内容以丰富分析"
    )

    tags = ", ".join(item_data.get("tags", [])[:8])
    sources = ", ".join(item_data.get("sources", []))
    desc = (item_data.get("description") or "")[:500]

    user_msg = (
        f"请深度解读以下文章/项目：\n\n"
        f"标题：{item_data.get('title', '')}\n"
        f"领域：{item_data.get('domain', '')}\n"
        f"热度：{item_data.get('heat_index', 0)} — {item_data.get('heat_reason', '')}\n"
        f"Stars：{item_data.get('stars', 0)} | 评论：{item_data.get('comments_count', 0)}\n"
        f"来源：{sources}\n"
        f"标签：{tags}\n"
        f"描述：{desc}\n"
        f"URL：{item_data.get('url', '')}\n\n"
        f"请从以上信息出发，进行深度解读。"
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]


def build_chat_prompt(article_data: dict, initial_analysis: str, messages: list[dict]) -> list[dict]:
    """Build messages for follow-up chat about an article."""
    system = (
        "你正在与用户讨论一篇科技文章/开源项目。\n"
        "你之前已经对这篇文章进行了深度分析，现在用户想就此继续提问讨论。\n"
        "规则：\n"
        "1. 中文回答，技术术语可保留英文\n"
        "2. 用 Markdown 格式\n"
        "3. 回答要简洁、有深度\n"
        "4. 你具备联网搜索能力，可联网补充最新信息\n"
        "5. 不要编造数据中没有的信息\n"
        "6. 控制在 400 字以内"
    )

    tags = ", ".join(article_data.get("tags", [])[:8])
    sources = ", ".join(article_data.get("sources", []))
    desc = (article_data.get("description") or "")[:500]

    article_context = (
        f"文章信息：\n"
        f"标题：{article_data.get('title', '')}\n"
        f"领域：{article_data.get('domain', '')}\n"
        f"热度：{article_data.get('heat_index', 0)}\n"
        f"Stars：{article_data.get('stars', 0)} | 评论：{article_data.get('comments_count', 0)}\n"
        f"来源：{sources}\n"
        f"标签：{tags}\n"
        f"描述：{desc}\n"
        f"URL：{article_data.get('url', '')}"
    )

    result = [
        {"role": "system", "content": system},
        {"role": "user", "content": article_context},
    ]

    if initial_analysis:
        result.append({"role": "assistant", "content": initial_analysis})

    for msg in messages[-20:]:  # Cap at 20 turns
        result.append({"role": msg["role"], "content": msg["content"]})

    return result


def build_image_extract_prompt(image_base64: str) -> list[dict]:
    """Build multimodal prompt for image keyword extraction using VL model."""
    return [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_base64}},
                {
                    "type": "text",
                    "text": (
                        "分析这张图片，提取与科技/开源/编程相关的关键词。\n"
                        '返回 JSON 格式：{"keywords": ["关键词1", "关键词2", ...], "summary": "一句话描述图片内容"}\n'
                        "规则：\n"
                        "1. keywords 提取 3-8 个关键词，优先英文技术术语\n"
                        "2. summary 用中文简述图片主要内容，20字以内\n"
                        "3. 只返回 JSON，不要其他文字"
                    ),
                },
            ],
        },
    ]


def build_image_search_prompt(summary: str, keywords: list[str], items: list[dict], user_query: str = "") -> list[dict]:
    """Build prompt for image-based article search analysis."""
    system_parts = [
        "你是 InsightRadar AI 搜索助手，用户上传了一张图片",
    ]
    if user_query:
        system_parts.append("并附带了文字描述")
    system_parts.append("，你需要根据图片内容和用户意图找到相关的科技新闻和开源项目。\n")
    system = (
        "".join(system_parts) + "规则：\n"
        "1. 用 [N] 引用来源（N 从 1 开始），关键观点必须有引用\n"
        "2. 中文回答，技术术语可保留英文\n"
        "3. 用 Markdown 格式，### 做小标题分组\n"
        "4. 数据中没有的信息不要编造\n"
        "5. 控制在 500 字以内\n"
        "6. 你具备联网搜索能力，可以搜索最新信息补充回答\n"
        "7. 联网搜索获取的信息不要使用 [N] 编号引用"
    )

    kw_str = ", ".join(keywords)
    # Build context header: user query first (search intent), then VL analysis
    context_parts = []
    if user_query:
        context_parts.append(f"用户描述：{user_query}")
    context_parts.append(f"图片描述：{summary}")
    context_parts.append(f"识别关键词：{kw_str}")
    context_header = "\n".join(context_parts)

    if not items:
        user_msg = f"{context_header}\n\n本地数据库中没有相关数据。请使用联网搜索获取最新信息并回答。"
    else:
        source_lines = []
        for i, item in enumerate(items, 1):
            desc = item["description"][:200] if item["description"] else ""
            sources = ", ".join(item["sources"]) if item["sources"] else ""
            tags = ", ".join(item["tags"][:5]) if item["tags"] else ""
            source_lines.append(
                f"[{i}] {item['title']}\n"
                f"  领域: {item['domain']} | 热度: {item['heat_index']} | Stars: {item['stars']}\n"
                f"  来源: {sources} | 标签: {tags}\n"
                f"  描述: {desc}\n"
                f"  URL: {item['url']}"
            )
        tail = (
            "请根据用户描述、图片内容和以上数据，分析推荐相关文章，使用 [N] 引用。"
            if user_query
            else "请根据图片内容和以上数据，分析推荐相关文章，使用 [N] 引用。"
        )
        user_msg = (
            f"{context_header}\n\n相关数据（共 {len(items)} 条）：\n\n" + "\n\n".join(source_lines) + f"\n\n{tail}"
        )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]


async def _stream_qwen(
    api_key: str,
    messages: list[dict],
    enable_search: bool = False,
    model: str | None = None,
    max_tokens: int = 1024,
):
    """Shared async generator: call Qwen API (OpenAI-compatible) and yield SSE chunks."""
    payload = {
        "model": model or QWEN_MODEL,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }
    if enable_search:
        payload["enable_search"] = True
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with (
            httpx.AsyncClient(timeout=60) as client,
            client.stream("POST", QWEN_BASE_URL, json=payload, headers=headers) as resp,
        ):
            if resp.status_code != 200:
                body = await resp.aread()
                logger.error("Qwen API error %s: %s", resp.status_code, body[:500])
                yield f'event: error\ndata: {{"error": "AI 服务返回错误 ({resp.status_code})"}}\n\n'
                return

            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        chunk_data = json.dumps({"text": content}, ensure_ascii=False)
                        yield f"data: {chunk_data}\n\n"
                except (json.JSONDecodeError, IndexError, KeyError):
                    continue

    except httpx.TimeoutException:
        yield 'event: error\ndata: {"error": "AI 服务请求超时，请稍后重试"}\n\n'
        return
    except Exception as e:
        logger.exception("Qwen stream error")
        yield f'event: error\ndata: {{"error": "AI 服务异常: {str(e)[:100]}"}}\n\n'
        return

    yield "event: done\ndata: {}\n\n"


async def _call_qwen_sync(api_key: str, messages: list[dict], model: str, max_tokens: int = 256) -> dict:
    """Non-streaming Qwen API call for quick tasks like keyword extraction."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(QWEN_BASE_URL, json=payload, headers=headers)
            if resp.status_code != 200:
                logger.error("Qwen sync API error %s: %s", resp.status_code, resp.text[:500])
                return {"error": f"AI 服务返回错误 ({resp.status_code})"}
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"content": content}
    except httpx.TimeoutException:
        return {"error": "AI 服务请求超时"}
    except Exception as e:
        logger.exception("Qwen sync call error")
        return {"error": f"AI 服务异常: {str(e)[:100]}"}


def _process_web_sources(raw_ws: list[dict]) -> list[dict]:
    """Classify web search results, store in DB, and return formatted items."""
    with get_db() as conn:
        formatted = []
        for ws in raw_ws:
            title = ws.get("title", "").strip()
            link = ws.get("link", "").strip()
            content = ws.get("content", "").strip()
            media = ws.get("media", "").strip()
            refer = ws.get("refer", "")
            if not title:
                continue

            domain = classify_web_result_domain(title, link or "", content)
            if link:
                insert_web_search_item(
                    conn,
                    title=title,
                    url=link,
                    content=content,
                    media=media,
                    domain=domain,
                )
            formatted.append(
                {
                    "title": title,
                    "url": link or "",
                    "description": content[:200] if content else "",
                    "domain": domain,
                    "tags": [],
                    "heat_index": 30,
                    "heat_reason": "网络搜索结果",
                    "stars": 0,
                    "comments_count": 0,
                    "sources": ["web_search"],
                    "published_at": None,
                    "refer": refer,
                }
            )
    return formatted


def get_top_items(limit: int = 20) -> list[dict]:
    """Get top items by heat_index for trending summary."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM classified_items ORDER BY heat_index DESC LIMIT ?", [limit]).fetchall()
    return [_row_to_item(r) for r in rows]


# ========== Pydantic Models ==========


class AISearchRequest(BaseModel):
    query: str = Field(..., max_length=500)


class AIAnalyzeRequest(BaseModel):
    title: str = ""
    url: str = ""
    description: str = ""
    domain: str = ""
    tags: list[str] = []
    heat_index: int = 0
    heat_reason: str = ""
    stars: int = 0
    comments_count: int = 0
    sources: list[str] = []


class AIChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., max_length=5000)


class AIChatRequest(BaseModel):
    article: AIAnalyzeRequest
    initial_analysis: str = ""
    messages: list[AIChatMessage]


class AIConfigRequest(BaseModel):
    api_key: str


class AIImageSearchRequest(BaseModel):
    image: str = Field(..., description="Base64 data URI of the image")
    query: str = Field("", max_length=500, description="Optional user text query")


# ========== Endpoints ==========


@router.get("/ai-config")
def api_ai_config_get():
    """Check if AI API key is configured."""
    has_key = bool(_runtime_api_key)
    masked = ""
    if _runtime_api_key:
        k = _runtime_api_key
        masked = k[:8] + "..." + k[-4:] if len(k) > 12 else "***"
    return {"configured": has_key, "masked_key": masked}


@router.post("/ai-config")
def api_ai_config_post(req: AIConfigRequest):
    """Save AI API key."""
    key = req.api_key.strip()
    if not key:
        return {"status": "error", "message": "API key 不能为空"}
    # Import save function from server module
    from src.server import _save_api_key

    _save_api_key(key)
    # Also update local runtime key
    set_api_key(key)
    return {"status": "ok", "message": "API key 已保存"}


@router.post("/ai-search")
@limiter.limit("10/minute")
async def api_ai_search(request: Request, req: AISearchRequest):
    """AI search with streaming SSE response."""
    if not _ai_search_semaphore._value:
        return StreamingResponse(
            iter(['event: error\ndata: {"error": "服务繁忙，请稍后再试"}\n\n']),
            media_type="text/event-stream",
            status_code=429,
        )

    async def generate():
        async with _ai_search_semaphore:
            api_key = _runtime_api_key
            if not api_key:
                yield 'event: error\ndata: {"error": "needsApiKey"}\n\n'
                return

            items = await asearch_items_for_ai(req.query)
            sources_data = json.dumps(items, ensure_ascii=False)
            yield f"event: sources\ndata: {sources_data}\n\n"

            messages = build_ai_prompt(req.query, items)
            async for chunk in _stream_qwen(api_key, messages, enable_search=True):
                if chunk.startswith("event: web_sources\n"):
                    try:
                        data_line = chunk.split("data: ", 1)[1].split("\n")[0]
                        raw_ws = json.loads(data_line)
                        formatted = _process_web_sources(raw_ws)
                        if formatted:
                            yield f"event: web_sources\ndata: {json.dumps(formatted, ensure_ascii=False)}\n\n"
                    except Exception:
                        logger.exception("Failed to process web_sources")
                    continue
                yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/ai-analyze")
@limiter.limit("10/minute")
async def api_ai_analyze(request: Request, req: AIAnalyzeRequest):
    """Article deep analysis with streaming SSE response."""
    if not _ai_search_semaphore._value:
        return StreamingResponse(
            iter(['event: error\ndata: {"error": "服务繁忙，请稍后再试"}\n\n']),
            media_type="text/event-stream",
            status_code=429,
        )

    async def generate():
        async with _ai_search_semaphore:
            api_key = _runtime_api_key
            if not api_key:
                yield 'event: error\ndata: {"error": "needsApiKey"}\n\n'
                return

            messages = build_analysis_prompt(req.model_dump())
            async for chunk in _stream_qwen(api_key, messages, enable_search=True):
                yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/ai-latest")
@limiter.limit("10/minute")
async def api_ai_latest(request: Request):
    """Trending news AI summary with streaming SSE response."""
    if not _ai_search_semaphore._value:
        return StreamingResponse(
            iter(['event: error\ndata: {"error": "服务繁忙，请稍后再试"}\n\n']),
            media_type="text/event-stream",
            status_code=429,
        )

    async def generate():
        async with _ai_search_semaphore:
            api_key = _runtime_api_key
            if not api_key:
                yield 'event: error\ndata: {"error": "needsApiKey"}\n\n'
                return

            items = await aget_top_items(20)
            sources_data = json.dumps(items, ensure_ascii=False)
            yield f"event: sources\ndata: {sources_data}\n\n"

            if not items:
                yield 'data: {"text": "数据库中暂无数据，请先采集数据。"}\n\n'
                yield "event: done\ndata: {}\n\n"
                return

            query = "今日最热科技新闻与开源动态"
            messages = build_ai_prompt(query, items)
            async for chunk in _stream_qwen(api_key, messages, enable_search=True):
                if chunk.startswith("event: web_sources\n"):
                    try:
                        data_line = chunk.split("data: ", 1)[1].split("\n")[0]
                        raw_ws = json.loads(data_line)
                        formatted = _process_web_sources(raw_ws)
                        if formatted:
                            yield f"event: web_sources\ndata: {json.dumps(formatted, ensure_ascii=False)}\n\n"
                    except Exception:
                        logger.exception("Failed to process web_sources")
                    continue
                yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/ai-chat")
@limiter.limit("10/minute")
async def api_ai_chat(request: Request, req: AIChatRequest):
    """Article follow-up chat with streaming SSE response."""
    if not _ai_search_semaphore._value:
        return StreamingResponse(
            iter(['event: error\ndata: {"error": "服务繁忙，请稍后再试"}\n\n']),
            media_type="text/event-stream",
            status_code=429,
        )

    async def generate():
        async with _ai_search_semaphore:
            api_key = _runtime_api_key
            if not api_key:
                yield 'event: error\ndata: {"error": "needsApiKey"}\n\n'
                return

            messages = build_chat_prompt(
                req.article.model_dump(),
                req.initial_analysis,
                [m.model_dump() for m in req.messages],
            )
            async for chunk in _stream_qwen(api_key, messages, enable_search=True):
                yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/ai-image-search")
@limiter.limit("5/minute")
async def api_ai_image_search(request: Request, req: AIImageSearchRequest):
    """Image-based article search with streaming SSE response."""
    if not _ai_search_semaphore._value:
        return StreamingResponse(
            iter(['event: error\ndata: {"error": "服务繁忙，请稍后再试"}\n\n']),
            media_type="text/event-stream",
            status_code=429,
        )

    # Validate image size (base64 data URI)
    image_data = req.image
    # Remove data URI prefix for size check
    raw_b64 = image_data.split(",", 1)[-1] if "," in image_data else image_data
    try:
        decoded_size = len(_b64.b64decode(raw_b64))
    except Exception:
        return StreamingResponse(
            iter(['event: error\ndata: {"error": "无效的图片数据"}\n\n']),
            media_type="text/event-stream",
            status_code=400,
        )
    if decoded_size > IMAGE_MAX_SIZE_BYTES:
        return StreamingResponse(
            iter(
                [
                    f'event: error\ndata: {{"error": "图片过大（{decoded_size // 1024 // 1024}MB），请上传 4MB 以内的图片"}}\n\n'
                ]
            ),
            media_type="text/event-stream",
            status_code=400,
        )

    async def generate():
        async with _ai_search_semaphore:
            api_key = _runtime_api_key
            if not api_key:
                yield 'event: error\ndata: {"error": "needsApiKey"}\n\n'
                return

            # Hint to frontend
            yield f"data: {json.dumps({'text': ''}, ensure_ascii=False)}\n\n"

            # Stage 1: Extract keywords from image using VL model
            vl_messages = build_image_extract_prompt(image_data)
            result = await _call_qwen_sync(api_key, vl_messages, model=QWEN_VL_MODEL, max_tokens=256)

            if "error" in result:
                yield f"event: error\ndata: {json.dumps({'error': result['error']}, ensure_ascii=False)}\n\n"
                return

            # Parse keywords from VL response
            content = result.get("content", "")
            keywords = []
            summary = ""
            try:
                # Try to extract JSON from the response
                json_match = re.search(r"\{[^}]+\}", content)
                if json_match:
                    parsed = json.loads(json_match.group())
                    keywords = parsed.get("keywords", [])
                    summary = parsed.get("summary", "")
            except (json.JSONDecodeError, AttributeError):
                pass

            if not keywords:
                # Fallback: use the raw content as a single keyword
                keywords = [w.strip() for w in content.split(",") if w.strip()][:5]
                summary = content[:50]

            if not keywords:
                yield 'event: error\ndata: {"error": "无法从图片中提取关键词"}\n\n'
                return

            # Send image analysis result to frontend
            analysis_data = json.dumps({"keywords": keywords, "summary": summary}, ensure_ascii=False)
            yield f"event: image_analysis\ndata: {analysis_data}\n\n"

            # Stage 2: Combined search — user text takes priority + VL keywords supplement
            vl_query = " ".join(keywords[:5])
            search_query = f"{req.query} {vl_query}" if req.query else vl_query
            items = await asearch_items_for_ai(search_query)
            sources_data = json.dumps(items, ensure_ascii=False)
            yield f"event: sources\ndata: {sources_data}\n\n"

            # Stage 3: Stream AI analysis using Qwen (pass user_query for context)
            messages = build_image_search_prompt(summary, keywords, items, user_query=req.query)
            async for chunk in _stream_qwen(api_key, messages, enable_search=True):
                if chunk.startswith("event: web_sources\n"):
                    try:
                        data_line = chunk.split("data: ", 1)[1].split("\n")[0]
                        raw_ws = json.loads(data_line)
                        formatted = _process_web_sources(raw_ws)
                        if formatted:
                            yield f"event: web_sources\ndata: {json.dumps(formatted, ensure_ascii=False)}\n\n"
                    except Exception:
                        logger.exception("Failed to process web_sources")
                    continue
                yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")
