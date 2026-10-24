"""在真实文档语料上评测：Recall@budget（答案片段是否进入预算内上下文）。

python scripts/eval_real.py --set data/eval_real.jsonl --budget 300
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

from budget_rag.config import Settings  # noqa: E402
from budget_rag.pipeline import RAG  # noqa: E402
from budget_rag.store import Store  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def hit(chunks, answers) -> int:
    text = norm(" ".join(c.text for c in chunks))
    return int(any(norm(a) in text for a in answers))


def take_k(ranked, k: int):
    return [c for c, _ in ranked[:k]]


def take_budget(ranked, budget: int):
    picked, used = [], 0
    for chunk, _score in ranked:
        picked.append(chunk)
        used += max(1, count_tokens(chunk.text))
        if used >= budget:
            break
    return picked


def ci(xs: list[float], n: int = 2000, seed: int = 7) -> tuple[float, float]:
    rng = random.Random(seed)
    m = len(xs)
    means = sorted(sum(rng.choice(xs) for _ in range(m)) / m for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    if args.limit:
        items = items[: args.limit]
    print(f"题目 {len(items)} 条 | 预算 {args.budget} token | 索引 {args.index}")

    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / args.index)
    store: Store = rag.store
    print(f"语料 {len({c.doc for c in store.chunks})} 篇 / {len(store.chunks)} 块\n")

    methods = {"BM25": [], "Dense": [], "Hybrid": [], "Ours": [], "Adaptive": [],
               "Hybrid-k3": [], "Hybrid-k5": [], "Hybrid-k8": [], "Dense-k5": []}
    tokens_used = {k: [] for k in methods}

    for i, it in enumerate(items, 1):
        q, gold = it["question"], it["answers"]
        b = args.budget

        picked = take_budget(store.search_bm25(q, 200), b)
        methods["BM25"].append(hit(picked, gold))
        tokens_used["BM25"].append(sum(count_tokens(c.text) for c in picked))

        picked = take_budget(store.search_vector(q, 200), b)
        methods["Dense"].append(hit(picked, gold))
        tokens_used["Dense"].append(sum(count_tokens(c.text) for c in picked))

        picked = take_budget(store.search_hybrid(q, 200), b)
        methods["Hybrid"].append(hit(picked, gold))
        tokens_used["Hybrid"].append(sum(count_tokens(c.text) for c in picked))

        # 自适应预算：top1/top2 间隔大 → 认为简单，用紧预算；否则用宽预算
        ranked = store.search_hybrid(q, 20)
        if len(ranked) >= 2:
            s1, s2 = ranked[0][1], ranked[1][1]
            margin = (s1 - s2) / s1 if s1 else 0.0
        else:
            margin = 1.0
        tight, wide, tau = min(b, 120), max(b, 800), 0.25
        budget_i = tight if margin > tau else wide
        picked = take_budget(store.search_hybrid(q, 200), budget_i)
        methods["Adaptive"].append(hit(picked, gold))
        tokens_used["Adaptive"].append(sum(count_tokens(c.text) for c in picked))

        # 固定 k 基线：系统常用的做法，按条数取满
        for kk in (3, 5, 8):
            pk = take_k(store.search_hybrid(q, 200), kk)
            methods[f"Hybrid-k{kk}"].append(hit(pk, gold))
            tokens_used[f"Hybrid-k{kk}"].append(sum(count_tokens(c.text) for c in pk))
        pk = take_k(store.search_vector(q, 200), 5)
        methods["Dense-k5"].append(hit(pk, gold))
        tokens_used["Dense-k5"].append(sum(count_tokens(c.text) for c in pk))

        out = rag.query(q, ctx_tokens=b)
        tr = out["trace"]
        keyed = set(tr["docs"]) if isinstance(tr.get("docs"), (list, tuple)) else set()
        chosen = [c for c in store.chunks if f"{c.doc}#{c.idx}" in keyed]
        methods["Ours"].append(hit(chosen, gold))
        tokens_used["Ours"].append(sum(count_tokens(c.text) for c in chosen))

        if i % 10 == 0:
            print(f"  {i}/{len(items)} " + " ".join(
                f"{k}={statistics.mean(v):.3f}" for k, v in methods.items() if v))

    print(f"\n{'方法':<10}{'Recall':>8}{'95% CI':>18}{'平均 token':>12}")
    result = {}
    for name, xs in methods.items():
        recall = statistics.mean(xs)
        lo, hi = ci(xs)
        tok = statistics.mean(tokens_used[name]) if tokens_used[name] else 0
        print(f"{name:<10}{recall:>8.3f}{f'[{lo:.3f},{hi:.3f}]':>18}{tok:>12.0f}")
        result[name] = {"recall": recall, "ci": [lo, hi], "tokens": tok, "n": len(xs)}

    out = ROOT / "results" / f"eval_real_b{args.budget}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
