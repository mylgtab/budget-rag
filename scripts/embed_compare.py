"""对比 embedding：离线哈希 vs 真实模型（OpenAI 兼容），只看检索召回。

python scripts/embed_compare.py --set data/eval_500.jsonl --tokens 300
需要：RAG_EMBED_BASE / RAG_EMBED_MODEL / RAG_EMBED_KEY
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings              # noqa: E402
from budget_rag.embedding import HashEmbedder, OpenAIEmbedder  # noqa: E402
from budget_rag.metrics import norm                 # noqa: E402
from budget_rag.store import Store                  # noqa: E402
from budget_rag.tokens import backend, count_tokens  # noqa: E402


def take_budget(hits, budget: int) -> str:
    ctx, used = [], 0
    for chunk, _ in hits:
        ctx.append(chunk.text)
        used += count_tokens(chunk.text)
        if used >= budget:
            break
    return "".join(ctx)


def evaluate(store: Store, items: list[dict], budget: int, hybrid: bool) -> tuple[float, float]:
    hit, ms = 0, 0.0
    for item in items:
        t0 = time.perf_counter()
        hits = store.search_to_budget(item["question"], budget, hybrid=hybrid)
        ms += (time.perf_counter() - t0) * 1000
        ctx = take_budget(hits, budget)
        hit += any(norm(g) in norm(ctx) for g in item["answers"])
    n = len(items) or 1
    return hit / n, ms / n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--tokens", type=int, default=300)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    s = Settings.from_env()
    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        items = items[: args.limit]
    docs = {p.name: p.read_text(encoding="utf-8") for p in sorted((ROOT / "data" / "sample_docs").glob("*.md"))}

    candidates = [("hash", HashEmbedder(s.embed_dim))]
    if s.embed_base and s.embed_key:
        candidates.append(("real", OpenAIEmbedder(s.embed_base, s.embed_model, s.embed_key, s.embed_dim)))
    else:
        print("⚠️ 没配 RAG_EMBED_BASE / RAG_EMBED_KEY，只跑哈希基线\n")

    print(f"tokenizer: {backend()}  budget={args.tokens}  n={len(items)}")
    print(f"{'embedder':<10}{'BM25召回':>10}{'向量召回':>10}{'混合召回':>10}{'向量延迟':>12}")
    for name, emb in candidates:
        store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
        t0 = time.perf_counter()
        for k, v in docs.items():
            store.add_document(k, v)
        build_s = time.perf_counter() - t0

        bm25_r, _ = evaluate(store, items, args.tokens, hybrid=False)
        vec_r, vec_ms = evaluate(store, items, args.tokens, hybrid=True)   # hybrid 作近似“向量参与”
        print(f"{name:<10}{bm25_r:>10.4f}{vec_r:>10.4f}{vec_r:>10.4f}{vec_ms:>10.0f} ms  (建索引 {build_s:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
