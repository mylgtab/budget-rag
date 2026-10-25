"""给「自适应节省」加 bootstrap 置信区间。

对同一批题，比较固定 k=8 与自适应（tau=0.05, k=4/10）：
  - 召回差（自适应 − 固定）的 95% CI 与配对 p 值
  - token 节省百分比的 95% CI
重采样单位是「题」，B=10000，固定随机种子。

python scripts/bootstrap_saving.py
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
from budget_rag.tokens import count_tokens  # noqa: E402


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--tau", type=float, default=0.05)
    ap.add_argument("--k-easy", type=int, default=4)
    ap.add_argument("--k-hard", type=int, default=10)
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / args.index)
    store = rag.store
    print(f"题 {len(items)}")

    per_fixed, per_adapt = [], []
    for it in items:
        r = store.search_hybrid(it["question"], 30)
        s1, s2 = (r[0][1], r[1][1]) if len(r) > 1 else (1.0, 0.0)
        margin = (s1 - s2) / s1 if s1 else 0.0
        kf, ka = 8, (args.k_easy if margin > args.tau else args.k_hard)
        for k, bucket in ((kf, per_fixed), (ka, per_adapt)):
            picked = [c for c, _ in r[:k]]
            hit = int(any(norm(a) in norm(" ".join(c.text for c in picked)) for a in it["answers"]))
            toks = sum(count_tokens(c.text) for c in picked)
            bucket.append((hit, toks))

    n = len(items)
    base_r = statistics.mean(h for h, _ in per_fixed)
    adap_r = statistics.mean(h for h, _ in per_adapt)
    base_t = statistics.mean(t for _, t in per_fixed)
    adap_t = statistics.mean(t for _, t in per_adapt)
    saving = (1 - adap_t / base_t) * 100
    print(f"固定 k=8: recall {base_r:.4f} token {base_t:.0f}")
    print(f"自适应  : recall {adap_r:.4f} token {adap_t:.0f}（省 {saving:.1f}%）")

    rng = random.Random(args.seed)
    d_rec, s_pct = [], []
    for _ in range(args.boot):
        idx = [rng.randrange(n) for _ in range(n)]
        fr = statistics.mean(per_fixed[i][0] for i in idx)
        ar = statistics.mean(per_adapt[i][0] for i in idx)
        ft = statistics.mean(per_fixed[i][1] for i in idx)
        at = statistics.mean(per_adapt[i][1] for i in idx)
        d_rec.append(ar - fr)
        s_pct.append((1 - at / ft) * 100)

    def ci(xs, lo=2.5, hi=97.5):
        xs = sorted(xs)
        return xs[int(lo / 100 * len(xs))], xs[int(hi / 100 * len(xs))]

    dr_lo, dr_hi = ci(d_rec)
    sp_lo, sp_hi = ci(s_pct)
    # 配对 bootstrap 双侧 p：差值分布跨 0 的比例
    p = 2 * min(sum(1 for x in d_rec if x <= 0) / len(d_rec), sum(1 for x in d_rec if x >= 0) / len(d_rec))
    print(f"\n召回差（自适应−固定）: {adap_r - base_r:+.4f}  95% CI [{dr_lo:+.4f}, {dr_hi:+.4f}]  p≈{p:.4f}")
    print(f"token 节省           : {saving:.1f}%  95% CI [{sp_lo:.1f}%, {sp_hi:.1f}%]")

    out = ROOT / "results" / "bootstrap_saving.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        "n": n, "fixed_k8": {"recall": base_r, "tokens": base_t},
        "adaptive": {"recall": adap_r, "tokens": adap_t, "tau": args.tau,
                     "k_easy": args.k_easy, "k_hard": args.k_hard},
        "recall_diff": {"point": adap_r - base_r, "ci": [dr_lo, dr_hi], "p": p},
        "saving_pct": {"point": saving, "ci": [sp_lo, sp_hi]},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("写入", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
