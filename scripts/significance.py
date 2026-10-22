"""显著性检验：配对 bootstrap + McNemar，比较两个策略的逐题结果。

python scripts/significance.py --file results/baselines.json --ours ours
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def mcnemar(b: int, c: int) -> float:
    """精确二项检验（双侧），b/c 是两系统不一致的题数。"""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def paired_bootstrap(a: list[int], b: list[int], n_boot: int = 2000, seed: int = 7) -> tuple[float, float, float]:
    n = len(a)
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(sum(a[i] - b[i] for i in idx) / n)
    diffs.sort()
    mean = sum(a[i] - b[i] for i in range(n)) / n
    return mean, diffs[int(0.025 * n_boot)], diffs[int(0.975 * n_boot) - 1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="results/baselines.json")
    ap.add_argument("--ours", default="ours")
    args = ap.parse_args()

    rows = json.loads((ROOT / args.file).read_text(encoding="utf-8"))
    names = list(rows[0].keys())
    ours = [r[args.ours]["hit"] for r in rows]

    print(f"n={len(rows)}  基准={args.ours}  均值={sum(ours)/len(ours):.4f}\n")
    print(f"{'对手':<12}{'对手均值':>10}{'差值':>8}{'95% CI':>20}{'McNemar p':>12}{'显著':>6}")

    for name in names:
        if name == args.ours:
            continue
        other = [r[name]["hit"] for r in rows]
        mean, lo, hi = paired_bootstrap(ours, other)
        b = sum(1 for r in rows if r[args.ours]["hit"] == 1 and r[name]["hit"] == 0)
        c = sum(1 for r in rows if r[args.ours]["hit"] == 0 and r[name]["hit"] == 1)
        p = mcnemar(b, c)
        sig = "是" if (lo > 0 and p < 0.05) else ("边缘" if lo > 0 else "否")
        print(f"{name:<12}{sum(other)/len(other):>10.4f}{mean:>+8.4f}"
              f"{f'[{lo:+.3f},{hi:+.3f}]':>20}{p:>12.4f}{sig:>6}")

    print("\nMcNemar 只数不一致的题（b=我们对该错，c=我们对错该对）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
