"""极简 BM25：便宜路径的检索器，零依赖。"""

from __future__ import annotations

import math
from collections import Counter

from .embedding import tokenize


class BM25:
    def __init__(self, docs: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.docs = docs
        self.tokens = [tokenize(d) for d in docs]
        self.freqs = [Counter(t) for t in self.tokens]
        self.lens = [len(t) for t in self.tokens]
        self.avg = (sum(self.lens) / len(self.lens)) if self.lens else 0.0
        df: Counter = Counter()
        for t in self.tokens:
            df.update(set(t))
        n = len(docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def scores(self, query: str) -> list[float]:
        q = tokenize(query)
        out = []
        for i, freq in enumerate(self.freqs):
            s = 0.0
            dl = self.lens[i] or 1
            for w in q:
                if w not in freq:
                    continue
                idf = self.idf.get(w, 0.0)
                tf = freq[w]
                s += idf * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * dl / (self.avg or 1)))
            out.append(s)
        return out

    def top_k(self, query: str, k: int) -> list[tuple[int, float]]:
        scored = list(enumerate(self.scores(query)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]
