"""索引存储：分块 + 向量 + BM25，支持落盘（JSON + 向量二进制）。

大语料（数万块）下向量检索必须走 numpy 矩阵乘，纯 Python 逐条算余弦会慢到不可用。
向量单独存成 .npz，JSON 只留文本，索引体积从数百 MB 降到几十 MB。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .bm25 import BM25
from .chunking import chunk_text, split_sentences
from .embedding import Embedder, cosine, tokenize
from .tokens import count_tokens

try:  # 大语料必需；缺失时退回纯 Python
    import numpy as np
except Exception:  # pragma: no cover
    np = None


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
        self._vecs = None         # 原始向量矩阵 (N, d)，惰性归一化
        self._mat_key = 0         # 块数变化时失效

    # ---- 建索引 ----
    def add_document(self, name: str, text: str) -> int:
        if self.mode == "sentence":
            parts = [s for s in split_sentences(text) if len(s) >= 4]
        else:
            parts = chunk_text(text, self.size, self.overlap)
        vecs = self.embedder.embed(parts)
        for i, (part, vec) in enumerate(zip(parts, vecs)):
            self.chunks.append(Chunk(doc=name, idx=i, text=part, vec=vec))
        self._invalidate()
        return len(parts)

    def add_documents(self, docs: dict[str, str]) -> int:
        """批量建索引：所有块一次性 embed，减少 API 调用与 400 风险。"""
        pending: list[tuple[str, str]] = []
        for name, text in docs.items():
            if self.mode == "sentence":
                parts = [p for p in split_sentences(text) if p.strip() and len(p) >= 4]
            else:
                parts = chunk_text(text, self.size, self.overlap)
            for p in parts:
                if p.strip():
                    pending.append((name, p.strip()))
        if not pending:
            return 0
        vecs = self.embedder.embed([p for _, p in pending])
        counters: dict[str, int] = {}
        for (name, text), vec in zip(pending, vecs):
            idx = counters.get(name, 0)
            counters[name] = idx + 1
            self.chunks.append(Chunk(doc=name, idx=idx, text=text, vec=vec))
        self._invalidate()
        return len(pending)

    def _invalidate(self) -> None:
        self._bm25 = None
        self._vecs = None

    @property
    def matrix(self):
        """归一化向量矩阵，按需构建；没有 numpy 时返回 None。"""
        if np is None:
            return None
        if self._mat_key != len(self.chunks):
            self._vecs = None
        if self._vecs is None:
            dim = next((len(c.vec) for c in self.chunks if c.vec), 0)
            mat = np.zeros((len(self.chunks), dim), dtype=np.float32)
            for i, c in enumerate(self.chunks):
                if c.vec:
                    mat[i, : len(c.vec)] = c.vec
            self._vecs = mat
        norms = np.linalg.norm(self._vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._mat_key = len(self.chunks)
        return self._vecs / norms

    @property
    def bm25(self) -> BM25:
        if self._bm25 is None:
            self._bm25 = BM25([c.text for c in self.chunks])
        return self._bm25

    # ---- 检索 ----
    def search_bm25(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        return [(self.chunks[i], s) for i, s in self.bm25.top_k(query, k)]

    def _vec_scores(self, qv: list[float]):
        """返回每个块的余弦分数（numpy 数组或 Python 列表）。"""
        mat = self.matrix
        if mat is None or not qv:
            return [cosine(qv, c.vec) for c in self.chunks]
        q = np.asarray(qv, dtype=np.float32)
        n = float(np.linalg.norm(q))
        if n == 0:
            return np.zeros(len(self.chunks), dtype=np.float32)
        return mat @ (q / n)

    def search_vector(self, query: str, k: int) -> list[tuple[Chunk, float]]:
        qv = self.embedder.embed([query])[0]
        return self.search_vector_precomputed(qv, k)

    def search_vector_precomputed(self, qv: list[float], k: int) -> list[tuple[Chunk, float]]:
        scores = self._vec_scores(qv)
        n = len(scores)
        k = max(1, min(k, n))
        if np is not None and hasattr(scores, "argpartition"):
            idx = np.argpartition(-scores, k - 1)[:k]
            idx = idx[np.argsort(-scores[idx])]
            return [(self.chunks[int(i)], float(scores[int(i)])) for i in idx]
        pairs = list(zip(self.chunks, scores))
        pairs.sort(key=lambda x: x[1], reverse=True)
        return pairs[:k]

    def search_hybrid_precomputed(self, query: str, qv: list[float], k: int, alpha: float = 0.2) -> list[tuple[Chunk, float]]:
        """混合检索，查询向量预先算好（省 API 调用）。"""
        bm = self.bm25.top_k(query, len(self.chunks))      # [(块下标, 分数)]
        scores = self._vec_scores(qv)
        bmax = max((s for _, s in bm), default=0.0) or 1.0
        vmax = float(max(scores)) if len(scores) else 1.0
        vmax = vmax or 1.0
        fused = [(self.chunks[i], alpha * s / bmax + (1 - alpha) * float(scores[i]) / vmax)
                 for i, s in bm]
        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:k]

    def search_hybrid(self, query: str, k: int, alpha: float = 0.2) -> list[tuple[Chunk, float]]:
        """BM25 与向量分数各自归一化后加权融合。"""
        qv = self.embedder.embed([query])[0]
        return self.search_hybrid_precomputed(query, qv, k, alpha)

    def search_bm25_prf(self, query: str, k: int, fb_docs: int = 5, fb_terms: int = 8) -> list[tuple[Chunk, float]]:
        """伪相关反馈：先用原始查询粗召回，再从结果里挑高权重词扩查询，二次检索。

        纯词法操作，不调用模型，零成本。
        """
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
            used += max(1, count_tokens(chunk.text))
            if used >= max_tokens:
                break
        return picked

    # ---- 持久化 ----
    def save(self, path: str | Path) -> None:
        """文本存 JSON，向量存同名 .npz；读取时两者自动配对。"""
        path = Path(path)
        payload = [{"doc": c.doc, "idx": c.idx, "text": c.text} for c in self.chunks]
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        if np is not None:
            mat = self._vecs
            if mat is None and any(c.vec for c in self.chunks):
                mat = np.asarray([c.vec for c in self.chunks], dtype=np.float32)
            if mat is not None and mat.size:
                np.savez_compressed(path.with_suffix(".npz"), vec=mat)

    def load(self, path: str | Path) -> None:
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        vec_file = path.with_suffix(".npz")
        self.chunks = [Chunk(doc=d["doc"], idx=d["idx"], text=d["text"], vec=d.get("vec", []))
                       for d in data]
        self._invalidate()
        if vec_file.exists() and np is not None:
            self._vecs = np.load(vec_file)["vec"].astype(np.float32)
            self._mat_key = len(self.chunks)
