"""保形校准：给定目标质量 T，给出「有 1-α 把握达到 T」的预算。

与曲线拟合版（calibrate_budget.py）的区别：
- 曲线版：拟合饱和曲线 → 反解 → 加安全边际，报「达标率」
- 保形版：直接用经验的 (1-α) 分位数，无需假设曲线形状，给出有限样本覆盖保证

理论依据（split conformal）：若标定集与测试集可交换，则
    P(新样本的所需预算 ≤ B) ≥ 1-α，其中 B 取标定集分数的 ⌈(n+1)(1-α)⌉ 个次序统计量。

python scripts/conformal_calibration.py --targets 0.80 0.85 0.90
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
    """split conformal 的分位数：第 ⌈(n+1)(1-α)⌉ 个次序统计量。"""
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
    ap.add_argument("--targets", type=float, nargs="*", default=[0.80, 0.85, 0.90])
    ap.add_argument("--n-fit", type=int, default=20)
    ap.add_argument("--repeats", type=int, default=100)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / args.index)
    store = rag.store
    fn = {"hybrid": store.search_hybrid, "dense": store.search_vector, "bm25": store.search_bm25}[args.method]

    print(f"{args.method}: {len({c.doc for c in store.chunks})} 文档 / {len(store.chunks)} 块 / {len(items)} 题")
    print("预计算每题所需预算…")
    need = np.asarray([min_hit_budget(fn(it["question"], 200), it["answers"]) for it in items])
    finite = np.isfinite(need)
    print(f"  可命中 {finite.sum()}/{len(need)}，中位所需预算 {np.median(need[finite]):.0f} token")

    rng = random.Random(args.seed)
    summary = {}

    print(f"\n拟合集 {args.n_fit} 题 | 重复 {args.repeats} 次 | 目标 → α = 1-T")
    print(f"{'目标':>6}{'α':>7}{'预算(中位)':>11}{'经验覆盖':>10}{'名义覆盖':>10}{'差距':>8}")
    for t in args.targets:
        alpha = 1 - t
        budgets, covers = [], []
        for _ in range(args.repeats):
            idx = list(range(len(items)))
            rng.shuffle(idx)
            fit, test = idx[: args.n_fit], idx[args.n_fit:]
            B = conformal_quantile([need[i] for i in fit], alpha)
            if not math.isfinite(B):
                continue                     # 标定集里该目标不可达 → 拒绝
            budgets.append(B)
            covers.append(float(np.mean(need[test] <= B)))
        if not budgets:
            print(f"{t:>6.2f}{alpha:>7.2f}   不可达（标定集分位数不有限）")
            continue
        cov = statistics.mean(covers)
        print(f"{t:>6.2f}{alpha:>7.2f}{statistics.median(budgets):>11.0f}"
              f"{cov:>10.3f}{1 - alpha:>10.3f}{cov - (1 - alpha):>+8.3f}")
        summary[f"{t:.2f}"] = {
            "alpha": alpha,
            "budget_median": statistics.median(budgets),
            "empirical_coverage": cov,
            "nominal_coverage": 1 - alpha,
            "bytes": len(budgets),
        }

    out = ROOT / "results" / f"conformal_{args.method}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
