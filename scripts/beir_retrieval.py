"""BEIR 子集检索评测：同一份语料上同时报两种口径。

    nDCG@10 / Recall@100   —— BEIR 官方口径，可与公开榜单对照
    Recall@budget          —— 本文口径：按分数取文档，累计 token 到预算即停，
                              命中任一相关文档即算召回（与 longbench_passage.py 一致）

文档级评测（一篇文档 = 一个检索单元），不切块，避免把「句级切块」的收益混进
公开基准的比较里；本文方法的切块收益仍在 200/500 条内部评测上报告。

用法：
    python scripts/beir_retrieval.py --dataset scifact
    python scripts/beir_retrieval.py --dataset scifact --sweep 100 200 300 500 800
    python scripts/beir_retrieval.py --dataset fiqa --limit 100 --embed real
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CORE = Path(os.getenv("BUDGET_RAG_CORE", str(ROOT)))
sys.path.insert(0, str(CORE / "src"))

from budget_rag.bm25 import BM25            # noqa: E402
from budget_rag.config import Settings     # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402

LOG2 = math.log2


def load_beir(path: Path):
    """读官方格式：corpus.jsonl / queries.jsonl / qrels/test.tsv。"""
    docs: dict[str, str] = {}
    order: list[str] = []
    with (path / "corpus.jsonl").open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            o = json.loads(line)
            title = (o.get("title") or "").strip()
            text = (o.get("text") or "").strip()
            docs[o["_id"]] = f"{title} {text}".strip() if title else text
            order.append(o["_id"])

    queries: dict[str, str] = {}
    with (path / "queries.jsonl").open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                o = json.loads(line)
                queries[o["_id"]] = o["text"].strip()

    qrels: dict[str, dict[str, int]] = {}
    test = path / "qrels" / "test.tsv"
    if not test.exists():
        cands = sorted((path / "qrels").glob("*.tsv"))
        if not cands:
            raise SystemExit(f"{path}/qrels 下没有 tsv")
        test = cands[0]
    with test.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                continue
            qid, did, score = parts[0], parts[1], parts[2]
            try:
                gain = int(float(score))
            except ValueError:
                continue  # 表头 query-id / corpus-id / score
            if gain <= 0:
                continue
            qrels.setdefault(qid, {})[did] = gain
    return order, docs, queries, qrels


def ndcg_at_k(ranked: list[str], rel: dict[str, int], k: int = 10) -> float:
    gains = [rel.get(d, 0) for d in ranked[:k]]
    dcg = sum(g / LOG2(i + 2) for i, g in enumerate(gains))
    ideal = sorted(rel.values(), reverse=True)[:k]
    idcg = sum(g / LOG2(i + 2) for i, g in enumerate(ideal))
    return dcg / idcg if idcg else 0.0


def budget_hit(ranked: list[str], rel: dict[str, int], docs: dict[str, str], budget: int) -> tuple[int, int]:
    """按分数取文档直到 token 预算用完；返回 (是否命中, 实际使用 token)。"""
    used = 0
    for did in ranked:
        used += max(1, count_tokens(docs[did]))
        if did in rel:
            return 1, used
        if used >= budget:
            break
    return 0, used


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="scifact")
    ap.add_argument("--data", default=str(ROOT / "data" / "beir"))
    ap.add_argument("--limit", type=int, default=0, help="只评测前 N 条查询（0=全部）")
    ap.add_argument("--tokens", type=int, default=300)
    ap.add_argument("--sweep", type=int, nargs="*", default=None,
                    help="预算扫描，如 --sweep 100 200 300 500 800")
    ap.add_argument("--embed", default="hash", choices=["hash", "real"])
    ap.add_argument("--alpha", type=float, default=0.2, help="混合检索里 BM25 的权重")
    args = ap.parse_args()

    path = Path(args.data) / args.dataset
    if not (path / "corpus.jsonl").exists():
        print(f"没找到 {path}/corpus.jsonl，先跑 fetch_beir.py")
        return 1

    order, docs, queries, qrels = load_beir(path)
    texts = [docs[d] for d in order]
    qids = [q for q in qrels if q in queries]
    if args.limit:
        qids = qids[: args.limit]
    print(f"{args.dataset}: 文档 {len(order):,} / 查询 {len(qids):,} / 相关判定 {sum(len(v) for v in qrels.values()):,}")

    t0 = time.perf_counter()
    bm25 = BM25(texts)
    print(f"  BM25 建索引 {time.perf_counter() - t0:.1f}s")

    s = Settings.from_env()
    if args.embed == "real":
        if not (s.embed_base and s.embed_key):
            print("需要 RAG_EMBED_BASE / RAG_EMBED_KEY（或改用 --embed hash）")
            return 1
        emb = build_embedder(s)
    else:
        emb = HashEmbedder(s.embed_dim)

    t0 = time.perf_counter()
    mat = np.asarray(emb.embed(texts), dtype=np.float32)
    mat /= np.maximum(np.linalg.norm(mat, axis=1, keepdims=True), 1e-9)
    print(f"  向量 {mat.shape} 耗时 {time.perf_counter() - t0:.1f}s")

    budgets = args.sweep if args.sweep else [args.tokens]
    stats = {m: {"ndcg": 0.0, "r100": 0.0, "hit": {b: 0 for b in budgets},
                 "tok": {b: 0 for b in budgets}} for m in ("bm25", "vector", "hybrid")}

    t0 = time.perf_counter()
    for n, qid in enumerate(qids, 1):
        q = queries[qid]
        rel = qrels[qid]
        bscores = np.asarray(bm25.scores(q), dtype=np.float32)
        qv = np.asarray(emb.embed([q])[0], dtype=np.float32)
        qv /= max(float(np.linalg.norm(qv)), 1e-9)
        vscores = mat @ qv

        bmax, vmax = float(bscores.max()) or 1.0, float(vscores.max()) or 1.0
        fused = args.alpha * bscores / bmax + (1 - args.alpha) * vscores / vmax

        rankings = {
            "bm25": [order[i] for i in np.argsort(-bscores)[:100]],
            "vector": [order[i] for i in np.argsort(-vscores)[:100]],
            "hybrid": [order[i] for i in np.argsort(-fused)[:100]],
        }
        for name, ranked in rankings.items():
            st = stats[name]
            st["ndcg"] += ndcg_at_k(ranked, rel, 10)
            st["r100"] += len(set(ranked) & set(rel)) / len(rel)
            for b in budgets:
                hit, used = budget_hit(ranked, rel, docs, b)
                st["hit"][b] += hit
                st["tok"][b] += used
        if n % 100 == 0:
            print(f"  {n}/{len(qids)}  ({time.perf_counter() - t0:.0f}s)")

    n = len(qids) or 1
    print(f"\n结果（{len(qids)} 条查询，{time.perf_counter() - t0:.0f}s）")
    header = f"{'方法':<8}{'nDCG@10':>10}{'Recall@100':>12}" + "".join(f"{'R@'+str(b):>10}" for b in budgets)
    print(header)
    for name, st in stats.items():
        line = f"{name:<8}{st['ndcg'] / n:>10.4f}{st['r100'] / n:>12.4f}"
        line += "".join(f"{st['hit'][b] / n:>10.4f}" for b in budgets)
        print(line)
    print("\n平均上下文 token（Recall@budget 同一批取数）")
    for name, st in stats.items():
        line = f"{name:<8}" + "".join(f"{st['tok'][b] / n:>10.0f}" for b in budgets)
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
