"""主结果的种子稳定性：对 per-item 结果做 3 次 2/3 子采样，报告均值±标准差。

读取 results/baselines.json（由 scripts/baselines.py 生成）。
python scripts/seed_stability.py
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="results/baselines.json")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--ratio", type=float, default=2 / 3)
    args = ap.parse_args()

    rows = json.loads((ROOT / args.file).read_text(encoding="utf-8"))
    names = list(rows[0].keys())
    n = len(rows)

    print(f"n={n}  子采样比例={args.ratio:.2f}  seeds={args.seeds}\n")
    print(f"{'方法':<12}{'全量':>8}{'子采样均值':>12}{'标准差':>8}{'95% 区间':>16}")

    for name in names:
        hits = [r[name]["hit"] for r in rows]
        full = sum(hits) / n
        means = []
        for seed in range(args.seeds):
            rng = random.Random(seed)
            idx = rng.sample(range(n), int(n * args.ratio))
            means.append(sum(hits[i] for i in idx) / len(idx))
        sd = statistics.stdev(means) if len(means) > 1 else 0.0
        lo, hi = min(means), max(means)
        print(f"{name:<12}{full:>8.4f}{statistics.mean(means):>12.4f}{sd:>8.4f}"
              f"{f'[{lo:.3f},{hi:.3f}]':>16}")

    print("\n说明：子采样用不同随机种子抽 2/3 样本，衡量结论对样本选择的敏感度。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
