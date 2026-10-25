"""间隔充分性的经验诊断：γ 越大，「多取几块」的边际收益是否越小？

若成立，则「按 γ 设阈值」是在用间隔预测边际收益，这正是空位 1 要证的东西的经验前提。
做法：按 γ 分桶，比较同一桶内 k=4 与 k=10 的命中率、以及 Δ = P(hit@10) − P(hit@4)。

python scripts/margin_sufficiency.py
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings  # noqa: E402
from budget_rag.pipeline import RAG  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def main() -> int:
    items = [json.loads(ln) for ln in (ROOT / "data" / "eval_real.jsonl").read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / "index_real.json")
    store = rag.store

    rows = []
    for it in items:
        r = store.search_hybrid(it["question"], 12)
        s1, s2 = (r[0][1], r[1][1]) if len(r) > 1 else (1.0, 0.0)
        gamma = (s1 - s2) / s1 if s1 else 0.0
        hits = {}
        for k in (4, 10):
            picked = [c for c, _ in r[:k]]
            hits[k] = int(any(norm(a) in norm(" ".join(c.text for c in picked)) for a in it["answers"]))
        rows.append({"gamma": gamma, "hit4": hits[4], "hit10": hits[10]})

    rows.sort(key=lambda x: x["gamma"])
    n = len(rows)
    q = n // 4
    bins = [(f"Q1 (γ≤{rows[q-1]['gamma']:.3f})", rows[:q]),
            (f"Q2", rows[q:2*q]),
            (f"Q3", rows[2*q:3*q]),
            (f"Q4 (γ>{rows[3*q-1]['gamma']:.3f})", rows[3*q:])]

    print(f"题 {n}")
    print(f"{'分箱':<22}{'n':>5}{'P(hit@4)':>10}{'P(hit@10)':>11}{'Δ(10−4)':>10}{'平均 token@10':>14}")
    table = []
    for name, chunk in bins:
        p4 = statistics.mean(r["hit4"] for r in chunk)
        p10 = statistics.mean(r["hit10"] for r in chunk)
        table.append({"bin": name, "n": len(chunk), "p_hit4": p4, "p_hit10": p10, "delta": p10 - p4})
        print(f"{name:<22}{len(chunk):>5}{p4:>10.3f}{p10:>11.3f}{p10-p4:>10.3f}")

    # 单调性：Δ 是否随 γ 下降
    deltas = [t["delta"] for t in table]
    mono = all(deltas[i] >= deltas[i + 1] - 1e-9 for i in range(len(deltas) - 1))
    print(f"\nΔ 随 γ 单调不增: {mono}  ({'支持间隔假设' if mono else '不严格单调，需要更细的分箱或条件说明'})")

    out = ROOT / "results" / "margin_sufficiency.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"n": n, "bins": table, "monotone": mono}, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print("写入", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
