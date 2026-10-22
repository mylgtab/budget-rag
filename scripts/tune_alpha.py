"""扫混合权重 alpha：查询向量只算一次，缓存下来反复用。

python scripts/tune_alpha.py --tokens 300
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings               # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.metrics import norm                  # noqa: E402
from budget_rag.store import Store                   # noqa: E402
from budget_rag.tokens import count_tokens            # noqa: E402

ALPHAS = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]


def take_budget(hits, budget: int) -> str:
    ctx, used = [], 0
    for chunk, _ in hits:
        ctx.append(chunk.text)
        used += count_tokens(chunk.text)
        if used >= budget:
            break
    return "".join(ctx)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--tokens", type=int, default=300)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    s = Settings.from_env()
    if not (s.embed_base and s.embed_key):
        print("需要 RAG_EMBED_BASE / RAG_EMBED_KEY")
        return 1

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        items = items[: args.limit]

    emb = build_embedder(s)
    store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))
    print(f"索引：{len(store.chunks)} 块，维度 {emb.dim}")

    cache = ROOT / ".cache" / "qvec.json"
    cache.parent.mkdir(exist_ok=True)
    if cache.exists():
        qvecs = json.loads(cache.read_text(encoding="utf-8"))
        print(f"查询向量：读缓存 {len(qvecs)} 条")
    else:
        qs = [it["question"] for it in items]
        qvecs = []
        for i in range(0, len(qs), 32):
            qvecs.extend(emb.embed(qs[i:i + 32]))
        cache.write_text(json.dumps(qvecs), encoding="utf-8")
        print(f"查询向量：新算 {len(qvecs)} 条并缓存")

    print(f"\n{'alpha':>6}{'recall':>10}   说明")
    best = (0.0, -1.0)
    for a in ALPHAS:
        hit = 0
        for idx, item in enumerate(items):
            if a >= 1.0:
                hits = store.search_bm25(item["question"], len(store.chunks))
            elif a <= 0.0:
                hits = store.search_vector_precomputed(qvecs[idx], len(store.chunks))
            else:
                hits = store.search_hybrid_precomputed(item["question"], qvecs[idx], len(store.chunks), alpha=a)
            ctx = take_budget(hits, args.tokens)
            hit += any(norm(g) in norm(ctx) for g in item["answers"])
        r = hit / len(items)
        note = "纯向量" if a <= 0 else ("纯 BM25" if a >= 1 else "混合")
        print(f"{a:>6.1f}{r:>10.4f}   {note}")
        if r > best[1]:
            best = (a, r)
    print(f"\n最优 alpha={best[0]} recall={best[1]:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
