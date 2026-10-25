"""逐题阈值：不调全局 τ，改成「看这道题自己的分数断崖」。

全局 τ 的问题：它是语料级常数，换语料要重调（论文里 scifact 0.12、nfcorpus 0.20）。
逐题版本把「取几块」交给单题内部的相邻分数落差：

    k* = 最小的 k（3 ≤ k ≤ 10），使得 (s_k - s_{k+1}) / s_1 ≥ delta
    若没有这样的 k，则取 k_max = 10

delta 是「愿意接受的相对断崖」，可在运行时给，也可用 (1-rho) 分位数从本批查询自标定。

python scripts/perquery_tau.py --set data/eval_real.jsonl --index index_real.json
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


def pick_k(scores: list[float], delta: float, k_min: int = 3, k_max: int = 10) -> int:
    if len(scores) < 2:
        return k_min
    s1 = max(scores[0], 1e-9)
    for k in range(k_min, min(k_max, len(scores) - 1) + 1):
        drop = (scores[k - 1] - scores[k]) / s1
        if drop >= delta:
            return k
    return k_max


def evaluate(items, store, delta: float, k_min: int = 3, k_max: int = 10):
    hits, toks, ks = 0, 0, []
    for it in items:
        ranked = store.search_hybrid(it["question"], k_max + 1)
        scores = [s for _, s in ranked]
        k = pick_k(scores, delta, k_min, k_max)
        ks.append(k)
        used, hit = 0, 0
        for chunk, _ in ranked[:k]:          # 统计整个上下文的 token，不因命中提前停
            used += max(1, count_tokens(chunk.text))
            if any(norm(a) in norm(chunk.text) for a in it["answers"]):
                hit = 1
        hits += hit
        toks += used
    return hits / len(items), toks / len(items), statistics.mean(ks)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--kmin", type=int, default=3)
    ap.add_argument("--kmax", type=int, default=10)
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / args.index)
    store = rag.store

    # 固定 k=8 参照
    rag_items = []
    for it in items:
        used, hit = 0, 0
        for chunk, _ in store.search_hybrid(it["question"], 8):
            used += max(1, count_tokens(chunk.text))
            if any(norm(a) in norm(chunk.text) for a in it["answers"]):
                hit = 1
        rag_items.append((hit, used))
    base_recall = sum(h for h, _ in rag_items) / len(items)
    base_tok = statistics.mean(u for _, u in rag_items)
    print(f"参照 固定 k=8: recall {base_recall:.3f} | token {base_tok:.0f}")

    rows = []
    print(f"\n{'delta':>7}{'recall':>9}{'token':>8}{'省':>7}{'平均 k':>8}")
    for delta in (0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20):
        r, t, mk = evaluate(items, store, delta, args.kmin, args.kmax)
        save = (base_tok - t) / base_tok * 100
        print(f"{delta:>7.2f}{r:>9.3f}{t:>8.0f}{save:>6.0f}%{mk:>8.1f}")
        rows.append({"delta": delta, "recall": r, "tokens": t, "saving_pct": save, "mean_k": mk})

    out = ROOT / "results" / "perquery_tau.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"fixed_k8": {"recall": base_recall, "tokens": base_tok},
                               "sweep": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n写入", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
