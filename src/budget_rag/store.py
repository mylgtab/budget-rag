"""索引存储：分块 + 向量 + BM25，支持落盘成 index.json。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .bm25 import BM25
from .chunking import chunk_text
from .embedding import Embedder, cosine


@dataclass
class Chunk:
    doc: str
    idx: int
    text: str
    vec: list[float] = field(default_factory=list)


class Store:
    def __init__(self, embedder: Embedder, size: int = 320, overlap: int = 60) -> None:
        self.embedder = embedder
        self.size, self.overlap = size, overlap
        self.chunks: list[Chunk] = []
        self._bm25: BM25 | None = None

    def add_document(self, name: str, text: str) -> int:
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
