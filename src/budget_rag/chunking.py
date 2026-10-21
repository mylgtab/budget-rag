"""分块：按段落聚合到目标长度，句尾断开，带重叠。"""

from __future__ import annotations

import re

_SENT = re.compile(r"[^。！？!?\.\n]+[。！？!?\.]?")


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.findall(text) if s.strip()]


def chunk_text(text: str, size: int = 320, overlap: int = 60) -> list[str]:
    """把长文切成 size 左右的块，相邻块保留 overlap 字符上下文。"""
    if size <= 0:
        raise ValueError("size must be > 0")
    sentences = split_sentences(text)
    chunks: list[str] = []
    buf = ""
    for sent in sentences:
        if len(buf) + len(sent) <= size:
            buf += sent
            continue
        if buf:
            chunks.append(buf)
            buf = buf[-overlap:] if overlap > 0 else ""
        while len(sent) > size:          # 单句超长，硬切
            chunks.append(sent[:size])
            sent = sent[size - overlap if overlap else size:]
        buf += sent
    if buf.strip():
        chunks.append(buf)
    return [c.strip() for c in chunks if c.strip()]
