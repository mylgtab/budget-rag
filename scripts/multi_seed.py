"""多 seed 方差：同一配置换不同划分，报告 mean ± std。

只跑检索（不调生成），配合向量缓存几乎零成本。
python scripts/multi_seed.py --seeds 3 --limit 300
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings               # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.metrics import norm                  # noqa: E402
from budget_rag.store import Store                   # noqa: E402
from budget_rag.tokens import count_tokens            # noqa: E402


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
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--tokens", type=int, default=300)
    ap.add_argument("--alpha", type=float, default=0.2)
    args = ap.parse_args()

    s = Settings.from_env()
    real = bool(s.embed_base and s.embed_key)
    emb = build_embedder(s) if real else HashEmbedder(s.embed_dim)
    store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()]
    items = items[: args.limit]
    print(f"embedder={'real' if real else 'hash'}  n={len(items)}  alpha={args.alpha}  budget={args.tokens}")

    # 一次算完所有查询向量（缓存命中后接近免费）
    qvecs = emb.embed([it["question"] for it in items])

    results = []
    for seed in range(args.seeds):
        # 自助重采样：每次抽同样大小的样本（可重复），才有方差可言
        rng = random.Random(seed)
        order = [rng.randrange(len(items)) for _ in range(len(items))]
        hit = 0
        for pos in order:
            item = items[pos]
            hits = store.search_hybrid_precomputed(item["question"], qvecs[pos],
                                                   len(store.chunks), alpha=args.alpha)
            ctx = take_budget(hits, args.tokens)
            hit += any(norm(g) in norm(ctx) for g in item["answers"])
        r = hit / len(items)
        results.append(r)
        print(f"  seed={seed}  recall={r:.4f}")

    mean = statistics.mean(results)
    std = statistics.stdev(results) if len(results) > 1 else 0.0
    print(f"\nRecall = {mean:.4f} ± {std:.4f}（{args.seeds} 次划分）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
