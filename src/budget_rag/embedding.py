"""Embedding：离线哈希向量（零依赖），真实模型按同接口替换。"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

_WORD = re.compile(r"[a-zA-Z0-9_]+")
_CJK = re.compile(r"[\u4e00-\u9fff]")


def tokenize(text: str) -> list[str]:
    """英文按词、中文按字 + 相邻二字，够用且无依赖。"""
    text = text.lower()
    tokens = _WORD.findall(text)
    cjk = _CJK.findall(text)
    tokens.extend(cjk)
    tokens.extend(a + b for a, b in zip(cjk, cjk[1:]))
    return tokens


class Embedder(Protocol):
    dim: int
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbedder:
    """特征哈希到固定维度，再 L2 归一化。确定性、离线、免费。"""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in tokenize(text):
            h = int.from_bytes(hashlib.blake2b(tok.encode(), digest_size=8).digest(), "big")
            vec[h % self.dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))

class OpenAIEmbedder:
    """任何 OpenAI 兼容的 /embeddings 接口（SiliconFlow、通义、本地 vLLM 等）。"""

    def __init__(self, base: str, model: str, key: str, dim: int = 1024, timeout: int = 60) -> None:
        self.base = base.rstrip("/")
        self.model = model
        self.key = key
        self.dim = dim
        self.timeout = timeout

    def embed(self, texts: list[str]) -> list[list[float]]:
        import json
        import urllib.request

        body = json.dumps({"model": self.model, "input": texts}).encode()
        req = urllib.request.Request(
            f"{self.base}/embeddings",
            data=body,
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
        )
        import time as _time

        self.last_usage = {"prompt_tokens": 0}
        data = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                break
            except Exception:
                if attempt == 2:
                    raise
                _time.sleep(1.5 * (attempt + 1))
        self.last_usage = {"prompt_tokens": int((data.get("usage") or {}).get("prompt_tokens", 0))}
        vecs = [item["embedding"] for item in data["data"]]
        if vecs:
            self.dim = len(vecs[0])          # 用真实维度覆盖默认值
        out = []
        for v in vecs:
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / norm for x in v])
        return out


class CachedEmbedder:
    """给 embedding 加一层 SQLite 缓存：同一段文本只算一次。

    真实模型的调用成本在「重复建索引」上最明显——200 条语料跑一次要重算几千条向量。
    """

    def __init__(self, inner, cache=None) -> None:
        from .cache import EmbedCache

        self.inner = inner
        self.dim = getattr(inner, "dim", 0)
        self.model = getattr(inner, "model", getattr(inner, "dim", "hash"))
        self.cache = cache or EmbedCache()
        self.embed_tokens = 0          # 真实消耗（仅统计 miss 的那部分）

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = str(self.model)
        cached = self.cache.get_many(model, texts)
        miss_idx = [i for i, v in enumerate(cached) if v is None]
        if miss_idx:
            fresh = self.inner.embed([texts[i] for i in miss_idx])
            self.embed_tokens += int((getattr(self.inner, "last_usage", {}) or {}).get("prompt_tokens", 0))
            self.cache.put_many(model, [texts[i] for i in miss_idx], fresh)
            for j, i in enumerate(miss_idx):
                cached[i] = fresh[j]
        if cached and cached[0]:
            self.dim = len(cached[0])
        return [v if v is not None else [] for v in cached]


def build_embedder(settings) -> "Embedder":
    """有 key 用真实模型，没有就退回离线哈希，保证永远能跑。"""
    base = getattr(settings, "embed_base", "")
    key = getattr(settings, "embed_key", "")
    if base and key:
        inner = OpenAIEmbedder(base, getattr(settings, "embed_model", "BAAI/bge-m3"), key,
                               getattr(settings, "embed_dim", 1024))
        return CachedEmbedder(inner)          # 真实模型一律走缓存
    return HashEmbedder(getattr(settings, "embed_dim", 256))
