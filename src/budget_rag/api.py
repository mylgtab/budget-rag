"""最小 HTTP 服务：跑起来就能被 curl 调。"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from .config import Settings
from .llm import OfflineAnswerer
from .pipeline import RAG

app = FastAPI(title="budget-rag", version="0.1.0")
_settings = Settings.from_env()
_rag: RAG | None = None


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


@app.get("/health")
def health() -> dict:
    rag = _get_rag()
    return {"ok": True, "chunks": len(rag.store.chunks), "answerer": rag.answerer.name}


@app.post("/query")
def query(body: QueryIn) -> dict:
    return _get_rag().query(body.question, body.budget)
