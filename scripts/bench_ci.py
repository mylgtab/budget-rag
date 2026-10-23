"""从逐题结果计算外部基准的置信区间、子采样稳定性与配对显著性。

读取 results/bench100_*.json（由 longbench_qa.py / longbench_triviaqa.py 生成）。
python scripts/bench_ci.py
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.metrics import contain  # noqa: E402

FILES = {
    "HotpotQA": "results/bench100_hotpotqa.json",
    "2WikiMultiHopQA": "results/bench100_2wikimqa.json",
    "MuSiQue": "results/bench100_musique.json",
    "TriviaQA": "results/bench100_triviaqa.json",
}


def mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(b, c) + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def ci(xs: list[int], n_boot: int = 2000, seed: int = 7) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(xs)
    means = sorted(sum(rng.choice(xs) for _ in range(n)) / n for _ in range(n_boot))
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1]


def main() -> int:
    print(f"{'数据集':<16}{'有检索':>8}{'95% CI':>18}{'子采样 mean±sd':>18}{'无检索':>8}{'McNemar p':>11}")
    rows = []
    for name, rel in FILES.items():
        p = ROOT / rel
        if not p.exists():
            print(f"{name:<16} 缺少 {rel}")
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        rag, none = [], []
        for r in data:
            g = r.get("gold", "")
            rag.append(int(contain(r.get("rag_answer", ""), g) >= 0.999))
            none.append(int(contain(r.get("none_answer", ""), g) >= 0.999))

        n = len(rag)
        m_rag, m_none = sum(rag) / n, sum(none) / n
        lo, hi = ci(rag)
        subs = []
        for seed in range(5):
            rng = random.Random(seed)
            idx = rng.sample(range(n), int(n * 2 / 3))
            subs.append(sum(rag[i] for i in idx) / len(idx))
        sd = statistics.stdev(subs)
        b = sum(1 for x, y in zip(rag, none) if x == 1 and y == 0)
        c = sum(1 for x, y in zip(rag, none) if x == 0 and y == 1)
        p_val = mcnemar(b, c)

        print(f"{name:<16}{m_rag:>8.3f}{f'[{lo:.3f},{hi:.3f}]':>18}"
              f"{f'{statistics.mean(subs):.3f}±{sd:.3f}':>18}{m_none:>8.3f}{p_val:>11.4f}")
        rows.append({"dataset": name, "n": n, "rag": m_rag, "rag_ci": [lo, hi],
                     "subsample_mean": statistics.mean(subs), "subsample_sd": sd,
                     "none": m_none, "mcnemar_p": p_val, "wins": b, "losses": c})

    out = ROOT / "results" / "bench100_summary.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n汇总: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
