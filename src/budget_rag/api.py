"""HTTP 服务：带鉴权与限流。

- 鉴权：设置 `RAG_API_TOKEN` 后要求 `Authorization: Bearer <token>`；不设则开放（本地开发）。
- 限流：每个客户端 IP 一个令牌桶，`RAG_RATE_LIMIT` 每分钟补充数、`RAG_RATE_BURST` 桶容量。
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import Settings
from .llm import OfflineAnswerer
from .pipeline import RAG

app = FastAPI(title="budget-rag", version="0.15.0")
_settings = Settings.from_env()
_rag: RAG | None = None

API_TOKEN = os.getenv("RAG_API_TOKEN", "").strip()
RATE_PER_MIN = int(os.getenv("RAG_RATE_LIMIT", "60"))
RATE_BURST = int(os.getenv("RAG_RATE_BURST", "10"))

_buckets: dict[str, tuple[float, float]] = {}   # ip -> (tokens, last_ts)


def _rate_ok(client: str) -> bool:
    """令牌桶：按时间补充，桶空则拒绝。"""
    now = time.monotonic()
    tokens, last = _buckets.get(client, (float(RATE_BURST), now))
    tokens = min(float(RATE_BURST), tokens + (now - last) * RATE_PER_MIN / 60.0)
    if tokens < 1.0:
        _buckets[client] = (tokens, now)
        return False
    _buckets[client] = (tokens - 1.0, now)
    return True


def _check_auth(authorization: str | None) -> None:
    if not API_TOKEN:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing token")
    if authorization[7:].strip() != API_TOKEN:
        raise HTTPException(status_code=401, detail="bad token")


def _check_rate(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    if not _rate_ok(client):
        raise HTTPException(status_code=429, detail="rate limit exceeded")


def _get_rag() -> RAG:
    global _rag
    if _rag is None:
        _rag = RAG(_settings, OfflineAnswerer())
        idx = Path("index.json")
        if idx.exists():
            _rag.store.load(idx)
    return _rag


class QueryIn(BaseModel):
    question: str
    budget: float | None = None
    ctx_tokens: int | None = None


_static = Path(__file__).parent / "static"
if _static.exists():
    app.mount("/ui", StaticFiles(directory=str(_static), html=True), name="ui")


@app.get("/")
def home():
    return RedirectResponse(url="/ui/")


@app.get("/health")
def health() -> dict:
    rag = _get_rag()
    return {"ok": True, "chunks": len(rag.store.chunks), "answerer": rag.answerer.name,
            "auth": bool(API_TOKEN), "rate_per_min": RATE_PER_MIN}


@app.post("/query")
def query(body: QueryIn, request: Request,
          authorization: str | None = Header(default=None)) -> dict:
    _check_auth(authorization)
    _check_rate(request)
    return _get_rag().query(body.question, body.budget, body.ctx_tokens)
