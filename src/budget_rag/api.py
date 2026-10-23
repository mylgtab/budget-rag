"""HTTP 服务：/v1 版本化 + 鉴权 + 限流。

- 版本：正式接口在 `/v1` 下，`/query`、`/health` 保留为兼容别名（不出现在 schema 中）。
- 鉴权：设置 `RAG_API_TOKEN` 后要求 `Authorization: Bearer <token>`；不设则开放（本地开发）。
- 限流：每客户端 IP 一个令牌桶，`RAG_RATE_LIMIT` 每分钟补充数、`RAG_RATE_BURST` 桶容量。
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from fastapi import APIRouter, FastAPI, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import Settings
from .llm import LLMAnswerer, OfflineAnswerer
from .pipeline import RAG

__version__ = "1.0.0"

app = FastAPI(
    title="budget-rag",
    version=__version__,
    description=(
        "成本感知的长文档问答检索。**正式接口在 `/v1` 下**；"
        "`/query`、`/health` 为兼容别名。"
    ),
)
router = APIRouter()
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
        answerer = LLMAnswerer(_settings) if _settings.api_key else OfflineAnswerer()
        _rag = RAG(_settings, answerer)
        idx = Path("index.json")
        if idx.exists():
            _rag.store.load(idx)
        else:
            docs_dir = Path("data/sample_docs")          # 没有索引就先建一份，避免空服务
            if docs_dir.exists():
                _rag.ingest({p.name: p.read_text(encoding="utf-8")
                             for p in sorted(docs_dir.glob("*.md"))})
                try:
                    _rag.store.save(idx)
                except Exception:
                    pass
    return _rag


class QueryIn(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="问题文本")
    budget: float | None = Field(None, ge=0, description="本次查询允许的成本（元）")
    ctx_tokens: int | None = Field(None, ge=1, le=20000, description="上下文 token 预算")


class TraceOut(BaseModel):
    path: str
    store: str | None = None
    cost_rmb: float = 0.0
    context_tokens: int = 0
    latency_ms: float = 0.0
    billed: bool = False


class QueryOut(BaseModel):
    answer: str = Field(..., description="答案文本")
    trace: dict = Field(..., description="检索路径、成本、token 与延迟")


class HealthOut(BaseModel):
    ok: bool
    chunks: int
    answerer: str
    auth: bool
    rate_per_min: int
    version: str


@router.get("/health", response_model=HealthOut, summary="健康检查")
def health() -> HealthOut:
    rag = _get_rag()
    return HealthOut(ok=True, chunks=len(rag.store.chunks), answerer=rag.answerer.name,
                     auth=bool(API_TOKEN), rate_per_min=RATE_PER_MIN, version=__version__)


@router.post("/query", response_model=QueryOut, summary="检索并回答",
             responses={401: {"description": "缺少或错误的 token"},
                        429: {"description": "超出限流"}})
def query(body: QueryIn, request: Request,
          authorization: str | None = Header(default=None)) -> QueryOut:
    _check_auth(authorization)
    _check_rate(request)
    out = _get_rag().query(body.question, body.budget, body.ctx_tokens)
    return QueryOut(answer=out["answer"], trace=out["trace"])


# 正式路径
app.include_router(router, prefix="/v1", tags=["v1"])
# 兼容别名（不出现在 OpenAPI 文档里）
app.include_router(router, prefix="", include_in_schema=False, tags=["legacy"])

_static = Path(__file__).parent / "static"
if _static.exists():
    app.mount("/ui", StaticFiles(directory=str(_static), html=True), name="ui")


@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/ui/")
