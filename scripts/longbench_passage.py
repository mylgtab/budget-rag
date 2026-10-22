"""LongBench passage_retrieval_zh：给定长查询，找出包含答案的段落。

答案是「段落N」，因此可以直接用「gold 段落是否被召回」衡量检索，不需要生成。
python scripts/longbench_passage.py --limit 100
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings                  # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.store import Store                      # noqa: E402
from budget_rag.tokens import count_tokens               # noqa: E402

_SPLIT = re.compile(r"段落\s*(\d+)\s*[:：]")


def parse_passages(context: str) -> dict[str, str]:
    """把 context 拆成 {段落N: 正文}。"""
    marks = list(_SPLIT.finditer(context))
    out: dict[str, str] = {}
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(context)
        out[f"段落{int(m.group(1))}"] = context[start:end].strip()
    return out


def take_budget(hits, budget: int) -> list:
    picked, used = [], 0
    for chunk, _ in hits:
        picked.append(chunk)
        used += count_tokens(chunk.text)
        if used >= budget:
            break
    return picked


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="data/longbench/passage_retrieval_zh.jsonl")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--tokens", type=int, default=300)
    ap.add_argument("--embed", default="hash", choices=["hash", "real"])
    args = ap.parse_args()

    s = Settings.from_env()
    if args.embed == "real":
        if not (s.embed_base and s.embed_key):
            print("需要 RAG_EMBED_BASE / RAG_EMBED_KEY")
            return 1
        emb = build_embedder(s)
    else:
        emb = HashEmbedder(s.embed_dim)

    items = [json.loads(l) for l in (ROOT / args.file).read_text(encoding="utf-8").splitlines() if l.strip()]
    items = items[: args.limit]
    print(f"n={len(items)}  embedder={args.embed}  budget={args.tokens} token")

    hit_bm25 = hit_vec = 0
    t0 = time.perf_counter()
    for i, item in enumerate(items, 1):
        passages = parse_passages(item["context"])
        gold = item["answers"][0].strip()
        q = item["input"]

        store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
        store.add_documents(passages)

        picked = take_budget(store.search_to_budget(q, args.tokens, hybrid=False), args.tokens)
        hit_bm25 += int(any(c.doc == gold for c in picked))

        if args.embed == "real":
            qv = emb.embed([q])[0]
            ranked = store.search_vector_precomputed(qv, len(store.chunks))
        else:
            ranked = store.search_hybrid_precomputed(q, emb.embed([q])[0], len(store.chunks), alpha=0.2)
        picked_v = take_budget(ranked, args.tokens)
        hit_vec += int(any(c.doc == gold for c in picked_v))

        if i % 20 == 0:
            print(f"  {i}/{len(items)}")

    n = len(items) or 1
    label = "向量" if args.embed == "real" else "哈希混合"
    print(f"\n结果（{time.perf_counter() - t0:.0f}s）")
    print(f"  BM25 段落召回 : {hit_bm25 / n:.4f}")
    print(f"  {label} 段落召回: {hit_vec / n:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
