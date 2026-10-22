"""P3 敏感性：改写的「成本系数」变化时，最优门控阈值是否按理论移动。

对每条题算两套上下文：不改写 vs 改写后；再按阈值决定用哪套。
扫描阈值 × 成本系数，给出最优阈值。

python scripts/threshold_sensitivity.py --limit 200
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings                # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.llm import LLMAnswerer                # noqa: E402
from budget_rag.metrics import norm                   # noqa: E402
from budget_rag.store import Store                    # noqa: E402
from budget_rag.tokens import count_tokens             # noqa: E402

THRESHOLDS = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.7, 1.0]
LAMBDAS = [0.25, 0.5, 1.0, 2.0, 4.0]


def tokens_of(chunks) -> int:
    return sum(count_tokens(c.text) for c in chunks)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--embed", default="real", choices=["hash", "real"])
    ap.add_argument("--out", default="results/threshold_sensitivity.json")
    args = ap.parse_args()

    s = Settings.from_env()
    if not s.api_key:
        print("需要 DEEPSEEK_API_KEY")
        return 1
    emb = build_embedder(s) if args.embed == "real" else HashEmbedder(s.embed_dim)
    store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))
    answerer = LLMAnswerer(s)

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    records = []

    for i, item in enumerate(items, 1):
        q, golds = item["question"], item["answers"]
        qv = emb.embed([q])[0]
        base_pairs = store.search_hybrid_precomputed(q, qv, 3, alpha=0.2)
        base = [c for c, _ in base_pairs]
        s1 = base_pairs[0][1] if base_pairs else 0.0
        s2 = base_pairs[1][1] if len(base_pairs) > 1 else 0.0
        conf = (s1 - s2) / s1 if s1 > 0 else 0.0

        sub = answerer.rewrite_query(q) or ""
        q2 = f"{q} {sub}" if sub else q
        rw = [c for c, _ in store.search_hybrid_precomputed(q2, emb.embed([q2])[0], 3, alpha=0.2)]

        base_text = "".join(c.text for c in base)
        rw_text = "".join(c.text for c in rw)
        records.append({
            "conf": conf,
            "base_hit": int(any(norm(g) in norm(base_text) for g in golds)),
            "rw_hit": int(any(norm(g) in norm(rw_text) for g in golds)),
            "base_tok": tokens_of(base),
            "rw_tok": tokens_of(rw),
            "rw_extra": 80,
        })
        if i % 50 == 0:
            print(f"  {i}/{len(items)}")

    n = len(records)
    print(f"\nn={n}  平均置信度={sum(r['conf'] for r in records)/n:.3f}")

    print(f"\n{'阈值':>6}{'改写率':>8}{'质量':>8}{'平均token':>12}")
    curve = []
    for t in THRESHOLDS:
        rew = [r for r in records if r["conf"] < t]
        q_hit = sum(r["rw_hit"] if r["conf"] < t else r["base_hit"] for r in records) / n
        cost = sum((r["rw_tok"] + r["rw_extra"]) if r["conf"] < t else r["base_tok"] for r in records) / n
        curve.append({"t": t, "rate": len(rew) / n, "quality": q_hit, "cost": cost})
        print(f"{t:>6.2f}{len(rew)/n:>8.1%}{q_hit:>8.4f}{cost:>12.0f}")

    print(f"\n{'成本系数':>10}{'最优阈值':>10}{'质量':>8}{'成本':>8}")
    best = {}
    for lam in LAMBDAS:
        scored = [(c["quality"] - lam * c["cost"] / 1000.0, c) for c in curve]
        scored.sort(key=lambda x: -x[0])
        _, c = scored[0]
        best[lam] = c["t"]
        print(f"{lam:>10.2f}{c['t']:>10.2f}{c['quality']:>8.4f}{c['cost']:>8.0f}")

    ts = [best[lam] for lam in LAMBDAS]
    print(f"\n最优阈值随成本系数变化: {ts}")
    print(f"P3（成本越高阈值越低）: {'成立' if all(ts[i] >= ts[i+1] for i in range(len(ts)-1)) else '不成立'}")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"records": records, "curve": curve, "best": best}, ensure_ascii=False), encoding="utf-8")
    print(f"明细: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
