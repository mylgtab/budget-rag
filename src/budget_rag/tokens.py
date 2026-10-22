"""token 计数：优先真 tokenizer（tiktoken），没有就退回字面估算。

CI 里不装 tiktoken 也能跑，只是数字是估算值——这点在报告里要写清楚。
"""

from __future__ import annotations

_ENC = "unset"
_CACHE: dict[str, int] = {}


def _encoder():
    global _ENC
    if _ENC != "unset":
        return _ENC
    try:
        import tiktoken

        _ENC = tiktoken.get_encoding("cl100k_base")
    except Exception:          # 没装 / 拉不到词表
        _ENC = None
    return _ENC


def count_tokens(text: str) -> int:
    if not text:
        return 0
    hit = _CACHE.get(text)
    if hit is not None:
        return hit
    enc = _encoder()
    if enc is not None:
        try:
            n = max(1, len(enc.encode(text)))
        except Exception:
            n = max(1, int(len(text) / 1.5))
    else:
        n = max(1, int(len(text) / 1.5))
    if len(_CACHE) < 50000:
        _CACHE[text] = n
    return n


def backend() -> str:
    return "tiktoken/cl100k" if _encoder() is not None else "heuristic(chars/1.5)"
