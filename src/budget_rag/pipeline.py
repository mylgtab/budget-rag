"""RAG 主链路：路由 → 检索 → 生成 → 记账。"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .config import Settings
from .embedding import HashEmbedder
from .llm import OfflineAnswerer
from .router import decide
from .store import Store


def _tokens(text: str) -> int:
    """粗估：中文约 1.5 字 = 1 token。"""
    return max(1, int(len(text) / 1.5))


@dataclass
class Trace:
    path: str
    reason: str
    k: int
    docs: list[str] = field(default_factory=list)
    context_tokens: int = 0
    cost_rmb: float = 0.0
    latency_ms: float = 0.0

    def as_dict(self) -> dict:
        return {
            "path": self.path, "reason": self.reason, "k": self.k,
            "docs": self.docs, "context_tokens": self.context_tokens,
            "cost_rmb": round(self.cost_rmb, 6), "latency_ms": round(self.latency_ms, 1),
        }


class RAG:
    def __init__(self, settings: Settings | None = None, answerer=None) -> None:
        self.s = settings or Settings.from_env()
        self.store = Store(HashEmbedder(self.s.embed_dim), self.s.chunk_size, self.s.chunk_overlap)
        self.answerer = answerer or OfflineAnswerer()

    def ingest(self, docs: dict[str, str]) -> int:
        return sum(self.store.add_document(name, text) for name, text in docs.items())

    def query(self, question: str, budget: float | None = None) -> dict:
        t0 = time.perf_counter()
        route = decide(
            question,
            budget if budget is not None else self.s.budget_rmb,
            self.s.top_k, self.s.cheap_max_chars, self.s.strong_min_chars,
        )

        if route.path == "strong":
            hits = self.store.search_hybrid(question, route.k)
            price = self.s.price_strong
        else:
            hits = self.store.search_bm25(question, route.k)
            price = self.s.price_cheap

        contexts = [c.text for c, _ in hits]
        ctx_tokens = sum(_tokens(c) for c in contexts)
        answer = self.answerer.answer(question, contexts) if contexts else "（没有检索到内容）"
        cost = (ctx_tokens + _tokens(answer)) / 1000 * price

        return {
            "answer": answer,
            "trace": Trace(
                path=route.path, reason=route.reason, k=route.k,
                docs=[f"{c.doc}#{c.idx}" for c, _ in hits],
                context_tokens=ctx_tokens, cost_rmb=cost,
                latency_ms=(time.perf_counter() - t0) * 1000,
            ).as_dict(),
        }
