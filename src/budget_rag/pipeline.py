"""RAG 主链路：预算选索引 → 检索到预算 → 生成 → 记账。"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .config import Settings
from .embedding import build_embedder
from .llm import OfflineAnswerer
from .router import decide
from .store import Store


def _confidence(hits) -> float:
    """检索置信度：top1 与 top2 的相对差距，越小越没把握。"""
    if not hits:
        return 0.0
    s1 = hits[0][1]
    s2 = hits[1][1] if len(hits) > 1 else 0.0
    return (s1 - s2) / s1 if s1 > 0 else 0.0


def _tokens(text: str) -> int:
    """粗估：中文约 1.5 字 = 1 token。"""
    return max(1, int(len(text) / 1.5))


@dataclass
class Trace:
    path: str
    reason: str
    k: int
    store: str = "fixed"          # 这次用了哪个索引
    docs: list[str] = field(default_factory=list)
    context_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    billed: bool = False          # True 表示 token 数来自 API 账单，不是估算
    cost_rmb: float = 0.0
    latency_ms: float = 0.0

    def as_dict(self) -> dict:
        return {
            "path": self.path, "reason": self.reason, "k": self.k, "store": self.store,
            "docs": self.docs, "context_tokens": self.context_tokens,
            "prompt_tokens": self.prompt_tokens, "completion_tokens": self.completion_tokens,
            "billed": self.billed,
            "cost_rmb": round(self.cost_rmb, 6), "latency_ms": round(self.latency_ms, 1),
        }


class RAG:
    def __init__(self, settings: Settings | None = None, answerer=None) -> None:
        self.s = settings or Settings.from_env()
        self.embedder = build_embedder(self.s)
        self.answerer = answerer or OfflineAnswerer()

        mode = self.s.chunk_mode
        if mode == "auto":                       # 双索引：句级 + 固定块
            self.stores = {
                "sentence": Store(self.embedder, self.s.chunk_size, self.s.chunk_overlap, "sentence"),
                "fixed": Store(self.embedder, self.s.chunk_size, self.s.chunk_overlap, "fixed"),
            }
        else:
            self.stores = {mode: Store(self.embedder, self.s.chunk_size, self.s.chunk_overlap, mode)}
        self.store = next(iter(self.stores.values()))     # 兼容旧接口

    # ---- 建索引 ----
    def ingest(self, docs: dict[str, str]) -> int:
        total = 0
        for store in self.stores.values():
            for name, text in docs.items():
                total = max(total, store.add_document(name, text))
        return total

    def _pick_store(self, ctx_tokens: int) -> tuple[str, Store]:
        if len(self.stores) == 1:
            name, store = next(iter(self.stores.items()))
            return name, store
        name = "sentence" if ctx_tokens <= self.s.auto_threshold else "fixed"
        return name, self.stores[name]

    def query(self, question: str, budget: float | None = None, ctx_tokens: int | None = None) -> dict:
        t0 = time.perf_counter()
        route = decide(
            question,
            budget if budget is not None else self.s.budget_rmb,
            self.s.top_k, self.s.cheap_max_chars, self.s.strong_min_chars,
        )
        want_tokens = ctx_tokens or self.s.ctx_tokens
        store_name, store = self._pick_store(want_tokens)

        search_query, rewritten = question, ""
        mode = self.s.rewrite_mode
        can_rewrite = hasattr(self.answerer, "rewrite_query")

        if mode == "always" and can_rewrite:
            rewritten = self.answerer.rewrite_query(question) or ""
        elif mode == "auto" and can_rewrite:
            first = store.search_to_budget(question, want_tokens, hybrid=route.hybrid)
            if _confidence(first) < self.s.rewrite_threshold:   # 没把握才花钱改写
                rewritten = self.answerer.rewrite_query(question) or ""
        if rewritten:
            search_query = f"{question} {rewritten}"            # 原始 + 改写，扩查询

        hits = store.search_to_budget(search_query, want_tokens, hybrid=route.hybrid)
        fallback_price = self.s.price_strong if route.hybrid else self.s.price_cheap

        contexts = [c.text for c, _ in hits]
        ctx_tokens_used = sum(_tokens(c) for c in contexts)

        usage = None
        if contexts and hasattr(self.answerer, "answer_with_usage"):
            answer, usage = self.answerer.answer_with_usage(question, contexts)
        else:
            answer = self.answerer.answer(question, contexts) if contexts else "（没有检索到内容）"

        rw = getattr(self.answerer, "last_rewrite_usage", None) or {}
        prompt_tokens = int((usage or {}).get("prompt_tokens", 0)) + int(rw.get("prompt_tokens", 0))
        completion_tokens = int((usage or {}).get("completion_tokens", 0)) + int(rw.get("completion_tokens", 0))
        billed = bool(prompt_tokens or completion_tokens)

        if billed:      # 有账单就用账单，单价按 100 万 token
            cost = prompt_tokens / 1_000_000 * self.s.price_in \
                + completion_tokens / 1_000_000 * self.s.price_out
        else:           # 离线抽取没有账单，退回估算
            prompt_tokens, completion_tokens = ctx_tokens_used, _tokens(answer)
            cost = (prompt_tokens + completion_tokens) / 1000 * fallback_price

        return {
            "answer": answer,
            "trace": Trace(
                path=route.path, reason=route.reason, k=len(hits), store=store_name,
                docs=[f"{c.doc}#{c.idx}" for c, _ in hits],
                context_tokens=ctx_tokens_used,
                prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                billed=billed, cost_rmb=cost,
                latency_ms=(time.perf_counter() - t0) * 1000,
            ).as_dict(),
        }
