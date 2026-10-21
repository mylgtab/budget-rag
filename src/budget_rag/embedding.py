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
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        vecs = [item["embedding"] for item in data["data"]]
        out = []
        for v in vecs:
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / norm for x in v])
        return out


def build_embedder(settings) -> "Embedder":
    """有 key 用真实模型，没有就退回离线哈希，保证永远能跑。"""
    base = getattr(settings, "embed_base", "")
    key = getattr(settings, "embed_key", "")
    if base and key:
        return OpenAIEmbedder(base, getattr(settings, "embed_model", "BAAI/bge-m3"), key,
                              getattr(settings, "embed_dim", 1024))
    return HashEmbedder(getattr(settings, "embed_dim", 256))
