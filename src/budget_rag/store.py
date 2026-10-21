"""索引存储：分块 + 向量 + BM25，支持落盘成 index.json。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .bm25 import BM25
from .chunking import chunk_text, split_sentences
from .embedding import Embedder, cosine


@dataclass
class Chunk:
    doc: str
    idx: int
    text: str
    vec: list[float] = field(default_factory=list)


class Store:
    def __init__(self, embedder: Embedder, size: int = 320, overlap: int = 60, mode: str = "fixed") -> None:
        self.embedder = embedder
        self.size, self.overlap = size, overlap
        self.mode = mode
        self.chunks: list[Chunk] = []
        self._bm25: BM25 | None = None

    def add_document(self, name: str, text: str) -> int:
        if self.mode == "sentence":          # 每条事实单独一块，块更小更准
            parts = [s for s in split_sentences(text) if len(s) >= 4]
        else:
            parts = chunk_text(text, self.size, self.overlap)
        vecs = self.embedder.embed(parts)
        for i, (part, vec) in enumerate(zip(parts, vecs)):
            self.chunks.append(Chunk(doc=name, idx=i, text=part, vec=vec))
        self._bm25 = None
        return len(parts)

    @property
    def bm25(self) -> BM25:
        if self._bm25 is None:
            self._bm25 = BM25([c.text for c in self.chunks])
        return self._bm25

    def search_bm25(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        return [(self.chunks[i], s) for i, s in self.bm25.top_k(query, k)]

    def search_vector(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        qv = self.embedder.embed([query])[0]
        scored = [(c, cosine(qv, c.vec)) for c in self.chunks]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def search_hybrid(self, query: str, k: int, alpha: float = 0.5) -> list[tuple[Chunk, float]]:
        """BM25 与向量分数各自归一化后加权融合。"""
        bm = self.search_bm25(query, len(self.chunks))
        ve = {id(c): s for c, s in self.search_vector(query, len(self.chunks))}
        bmax = max((s for _, s in bm), default=0.0) or 1.0
        vmax = max(ve.values(), default=0.0) or 1.0
        fused = [(c, alpha * s / bmax + (1 - alpha) * ve.get(id(c), 0.0) / vmax) for c, s in bm]
        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:k]

    def search_bm25_prf(self, query: str, k: int, fb_docs: int = 5, fb_terms: int = 8) -> list[tuple[Chunk, float]]:
        """伪相关反馈：先用原始查询粗召回，再从结果里挑高权重词扩查询，二次检索。

        纯词法操作，不调用模型，零成本。
        """
        from .embedding import tokenize

        first = self.search_bm25(query, fb_docs)
        if not first:
            return []
        q_terms = set(tokenize(query))
        weights: dict[str, float] = {}
        for chunk, _score in first:
            for term in tokenize(chunk.text):
                if len(term) < 2 or term in q_terms:
                    continue
                weights[term] = weights.get(term, 0.0) + self.bm25.idf.get(term, 0.0)
        extra = sorted(weights, key=weights.get, reverse=True)[:fb_terms]
        if not extra:
            return first[:k]
        expanded = f"{query} {' '.join(extra)}"
        return self.search_bm25(expanded, k)

    def search_to_budget(self, query: str, max_tokens: int, hybrid: bool = False) -> list[tuple[Chunk, float]]:
        """按分数顺序取块，直到累计 token 达到预算；至少取一块。"""
        ranked = (self.search_hybrid(query, len(self.chunks)) if hybrid
                  else self.search_bm25(query, len(self.chunks)))
        picked: list[tuple[Chunk, float]] = []
        used = 0
        for chunk, score in ranked:
            picked.append((chunk, score))
            used += max(1, int(len(chunk.text) / 1.5))
            if used >= max_tokens:
                break
        return picked

    # ---- 持久化 ----
    def save(self, path: str | Path) -> None:
        payload = [
            {"doc": c.doc, "idx": c.idx, "text": c.text, "vec": [round(v, 6) for v in c.vec]}
            for c in self.chunks
        ]
        Path(path).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def load(self, path: str | Path) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.chunks = [Chunk(**d) for d in data]
        self._bm25 = None
