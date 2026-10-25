"""保形校准的覆盖率诊断：扫一整段 α，检查经验覆盖是否贴合名义覆盖。

单个目标只给一个点；审稿人更认「整条对角线」。
python scripts/conformal_sweep.py --method hybrid
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings  # noqa: E402
from budget_rag.pipeline import RAG  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def min_hit_budget(ranked, answers, cap: int = 1500) -> float:
    used = 0
    for chunk, _ in ranked:
        used += max(1, count_tokens(chunk.text))
        if any(norm(a) in norm(chunk.text) for a in answers):
            return used
        if used >= cap:
            break
    return math.inf


def conformal_quantile(scores: list[float], alpha: float) -> float:
    n = len(scores)
    k = math.ceil((n + 1) * (1 - alpha))
    if k > n:
        return math.inf
    return sorted(scores)[k - 1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--method", default="hybrid", choices=["hybrid", "dense", "bm25"])
    ap.add_argument("--n-fit", type=int, default=20)
    ap.add_argument("--repeats", type=int, default=100)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / args.index)
    store = rag.store
    fn = {"hybrid": store.search_hybrid, "dense": store.search_vector, "bm25": store.search_bm25}[args.method]

    print(f"{args.method}: {len(items)} 题，预计算所需预算…")
    need = [min_hit_budget(fn(it["question"], 200), it["answers"]) for it in items]

    alphas = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    rng = random.Random(args.seed)
    rows = []
    print(f"\n{'α':>5}{'名义覆盖':>10}{'经验覆盖':>10}{'均值|差距|':>11}{'最低覆盖':>10}{'预算(中位)':>12}{'拒绝率':>9}")
    for alpha in alphas:
        covs, budgets, refusals = [], [], 0
        for _ in range(args.repeats):
            idx = list(range(len(items)))
            rng.shuffle(idx)
            fit, test = idx[: args.n_fit], idx[args.n_fit:]
            B = conformal_quantile([need[i] for i in fit], alpha)
            if not math.isfinite(B):
                refusals += 1
                continue
            budgets.append(B)
            covs.append(float(np.mean([need[i] <= B for i in test])))
        if not covs:
            print(f"{alpha:>5.2f}{1-alpha:>10.2f}   全部拒绝（标定集不可达）")
            rows.append({"alpha": alpha, "nominal": 1 - alpha, "coverage": None,
                         "budget": None, "refusal_rate": 1.0})
            continue
        nominal = 1 - alpha
        cov = statistics.mean(covs)
        gap = abs(cov - nominal)
        lo = float(np.percentile(covs, 5))
        print(f"{alpha:>5.2f}{nominal:>10.3f}{cov:>10.3f}{gap:>11.3f}{lo:>10.3f}"
              f"{statistics.median(budgets):>12.0f}{refusals / args.repeats:>9.2f}")
        rows.append({"alpha": alpha, "nominal": nominal, "coverage": cov,
                     "coverage_p05": lo, "budget": statistics.median(budgets),
                     "refusal_rate": refusals / args.repeats})

    out = ROOT / "results" / f"conformal_sweep_{args.method}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
