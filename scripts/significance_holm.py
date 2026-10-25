"""配对显著性检验 + Holm 多重比较校正。

对同一批题上两个系统的逐题命中做 McNemar 精确检验，再对多个比较做 Holm 校正。

python scripts/significance_holm.py --budget 300
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings  # noqa: E402
from budget_rag.pipeline import RAG  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def hits_at(items, fn, budget: int) -> list[int]:
    out = []
    for it in items:
        used, hit = 0, 0
        for chunk, _ in fn(it["question"], 200):
            used += max(1, count_tokens(chunk.text))
            if any(norm(a) in norm(chunk.text) for a in it["answers"]):
                hit = 1
                break
            if used >= budget:
                break
        out.append(hit)
    return out


def mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(b, c) + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def holm(pvalues: list[float]) -> list[float]:
    """Holm–Bonferroni 校正：返回校正后的 p 值（保持原顺序）。"""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * pvalues[idx])
        running = max(running, val)
        adjusted[idx] = running
    return adjusted


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--index2", default="index_real_bgelarge.json")
    ap.add_argument("--budget", type=int, default=300)
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / args.index)
    store = rag.store

    bm25 = hits_at(items, store.search_bm25, args.budget)
    dense = hits_at(items, store.search_vector, args.budget)
    hybrid = hits_at(items, store.search_hybrid, args.budget)

    systems = {"BM25": bm25, "Dense": dense, "Hybrid": hybrid}
    if (ROOT / args.index2).exists():
        s2 = Settings.from_env()
        s2.embed_model = "BAAI/bge-large-en-v1.5"
        rag2 = RAG(s2)
        rag2.store.load(ROOT / args.index2)
        systems["Dense-large"] = hits_at(items, rag2.store.search_vector, args.budget)

    print(f"题 {len(items)} | 预算 {args.budget} | 命中率: " +
          ", ".join(f"{k}={sum(v)/len(v):.3f}" for k, v in systems.items()))

    comparisons = [("Hybrid", "BM25"), ("Hybrid", "Dense")]
    if "Dense-large" in systems:
        comparisons.append(("Hybrid", "Dense-large"))

    raw = []
    print(f"\n{'比较':<26}{'Hybrid 赢':>10}{'对手赢':>8}{'McNemar p':>12}")
    for a, b in comparisons:
        x, y = systems[a], systems[b]
        win = sum(1 for i, j in zip(x, y) if i == 1 and j == 0)
        loss = sum(1 for i, j in zip(x, y) if i == 0 and j == 1)
        p = mcnemar(win, loss)
        raw.append(p)
        print(f"{a} vs {b:<16}{win:>10}{loss:>8}{p:>12.4f}")

    adj = holm(raw)
    print(f"\n{'比较':<26}{'原始 p':>10}{'Holm p':>10}{'显著(0.05)':>12}")
    out = []
    for (a, b), p, pa in zip(comparisons, raw, adj):
        print(f"{a} vs {b:<16}{p:>10.4f}{pa:>10.4f}{'是' if pa < 0.05 else '否':>12}")
        out.append({"a": a, "b": b, "p_raw": p, "p_holm": pa, "significant": pa < 0.05})

    dest = ROOT / "results" / "significance_holm.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps({"budget": args.budget, "n": len(items),
                                "hit_rates": {k: sum(v) / len(v) for k, v in systems.items()},
                                "comparisons": out}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
