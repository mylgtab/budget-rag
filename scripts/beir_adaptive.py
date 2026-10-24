"""BEIR 上的预算自适应评测：同一批语料，报 nDCG@10 与平均上下文 token。

沿用 beir_retrieval.py 的数据加载与 nDCG 实现，只增加「按间隔决定取几条」的策略：
间隔大 → 少取；间隔小 → 多取。与固定 k 比较，同召回看谁更省。

python scripts/beir_adaptive.py --dataset scifact --embed real --limit 100
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from beir_retrieval import load_beir, ndcg_at_k  # noqa: E402

sys.path.insert(0, str(ROOT / "src"))
from budget_rag.bm25 import BM25  # noqa: E402
from budget_rag.config import Settings  # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="scifact")
    ap.add_argument("--data", default=str(ROOT / "data" / "beir"))
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--embed", default="real", choices=["hash", "real"])
    ap.add_argument("--alpha", type=float, default=0.2)
    args = ap.parse_args()

    path = Path(args.data) / args.dataset
    order, docs, queries, qrels = load_beir(path)
    qids = [q for q in qrels if q in queries]
    if args.limit:
        qids = qids[: args.limit]
    print(f"{args.dataset}: 文档 {len(order):,} / 查询 {len(qids)}")

    bm25 = BM25([docs[d] for d in order])
    s = Settings.from_env()
    emb = build_embedder(s) if args.embed == "real" else HashEmbedder(s.embed_dim)
    mat = np.asarray(emb.embed([docs[d] for d in order]), dtype=np.float32)
    mat /= np.maximum(np.linalg.norm(mat, axis=1, keepdims=True), 1e-9)

    fused_cache = []
    for qid in qids:
        q = queries[qid]
        bs = np.asarray(bm25.scores(q), dtype=np.float32)
        qv = np.asarray(emb.embed([q])[0], dtype=np.float32)
        qv /= max(float(np.linalg.norm(qv)), 1e-9)
        vs = mat @ qv
        fused = args.alpha * bs / (float(bs.max()) or 1.0) + (1 - args.alpha) * vs / (float(vs.max()) or 1.0)
        fused_cache.append((qid, fused))
        if len(fused_cache) % 25 == 0:
            print(f"  {len(fused_cache)}/{len(qids)}")

    def evaluate(k_easy: int, k_hard: int, tau: float):
        ndcgs, toks, r10 = [], [], []
        for qid, fused in fused_cache:
            ranked_idx = np.argsort(-fused)
            top = ranked_idx[: max(k_easy, k_hard)]
            s1 = float(fused[top[0]])
            s2 = float(fused[top[1]]) if len(top) > 1 else 0.0
            margin = (s1 - s2) / s1 if s1 else 0.0
            k = k_easy if margin > tau else k_hard
            chosen = [order[i] for i in top[:k]]
            rel = qrels[qid]
            ndcgs.append(ndcg_at_k(chosen, rel, 10))
            r10.append(1.0 if any(d in rel for d in chosen) else 0.0)
            toks.append(sum(count_tokens(docs[d]) for d in chosen))
        return float(np.mean(ndcgs)), float(np.mean(r10)), float(np.mean(toks))

    base = evaluate(10, 10, 2.0)
    print(f"\n固定 k=10：nDCG@10 {base[0]:.4f}  hit@k {base[1]:.4f}  token {base[2]:.0f}")
    base8 = evaluate(8, 8, 2.0)
    print(f"固定 k=8 ：nDCG@10 {base8[0]:.4f}  hit@k {base8[1]:.4f}  token {base8[2]:.0f}")

    rows = []
    for tau in (0.02, 0.05, 0.08, 0.12, 0.2):
        for ke, kh in ((3, 8), (4, 10), (2, 8), (3, 10)):
            ndcg, hit, tok = evaluate(ke, kh, tau)
            rows.append({"tau": tau, "k_easy": ke, "k_hard": kh,
                         "ndcg10": ndcg, "hit": hit, "tokens": tok})
    rows.sort(key=lambda r: (-round(r["ndcg10"], 4), r["tokens"]))
    print(f"\n{'tau':>6}{'k_easy':>7}{'k_hard':>7}{'nDCG@10':>9}{'hit':>7}{'token':>8}")
    for r in rows[:10]:
        print(f"{r['tau']:>6.2f}{r['k_easy']:>7}{r['k_hard']:>7}{r['ndcg10']:>9.4f}{r['hit']:>7.3f}{r['tokens']:>8.0f}")

    out = ROOT / "results" / f"beir_adaptive_{args.dataset}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"fixed_k10": base, "fixed_k8": base8, "sweep": rows},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
