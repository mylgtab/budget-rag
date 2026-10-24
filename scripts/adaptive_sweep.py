"""按难度自适应检索深度：用 top1/top2 间隔决定取几块。

固定 k 的毛病是「简单题浪费、难题不够」。这里用检索分数间隔做难度代理：
间隔大 → 模型有把握 → 少取；间隔小 → 多取。

python scripts/adaptive_sweep.py --budget-index index_real.json
"""

from __future__ import annotations

import argparse
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--pool", type=int, default=30, help="取多少条候选用于分析")
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / args.index)
    store = rag.store
    print(f"题 {len(items)} | 块 {len(store.chunks)}")

    cached = []
    for it in items:
        r = store.search_hybrid(it["question"], args.pool)
        cached.append((it, r))

    def evaluate(k_easy: int, k_hard: int, tau: float) -> tuple[float, float]:
        hits, toks = [], []
        for it, r in cached:
            s1, s2 = (r[0][1], r[1][1]) if len(r) > 1 else (1.0, 0.0)
            margin = (s1 - s2) / s1 if s1 else 0.0
            k = k_easy if margin > tau else k_hard
            picked = [c for c, _ in r[:k]]
            text = norm(" ".join(c.text for c in picked))
            hits.append(int(any(norm(a) in text for a in it["answers"])))
            toks.append(sum(count_tokens(c.text) for c in picked))
        return statistics.mean(hits), statistics.mean(toks)

    base_recall, base_tokens = evaluate(8, 8, 1.1)      # 固定 k=8
    print(f"固定 k=8：recall {base_recall:.3f}, token {base_tokens:.0f}")

    best = None
    rows = []
    for tau in (0.02, 0.05, 0.08, 0.12, 0.2):
        for ke, kh in ((3, 8), (2, 8), (3, 10), (4, 10), (2, 10)):
            rec, tok = evaluate(ke, kh, tau)
            rows.append({"tau": tau, "k_easy": ke, "k_hard": kh, "recall": rec, "tokens": tok})
            if rec >= base_recall - 0.005 and (best is None or tok < best["tokens"]):
                best = rows[-1]

    if best:
        saved = (1 - best["tokens"] / base_tokens) * 100
        print(f"最佳：tau={best['tau']} k_easy={best['k_easy']} k_hard={best['k_hard']} "
              f"→ recall {best['recall']:.3f}, token {best['tokens']:.0f}（省 {saved:.0f}%）")
    else:
        print("没有配置在等价召回下节省 token")

    out = ROOT / "results" / "adaptive_sweep.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"fixed_k8": {"recall": base_recall, "tokens": base_tokens},
                               "sweep": rows, "best": best}, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
