"""端到端延迟与成本：各档位跑同一批题，报 p50/p95。

python scripts/latency_bench.py --limit 20
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings         # noqa: E402
from budget_rag.llm import LLMAnswerer         # noqa: E402
from budget_rag.pipeline import RAG            # noqa: E402

CONFIGS = [
    ("cheap（BM25 单路）", {"budget": 0.0005, "ctx_tokens": 300}),
    ("strong（混合检索）", {"budget": 0.05, "ctx_tokens": 300}),
    ("strong + 改写（全量）", {"budget": 0.05, "ctx_tokens": 300, "rewrite": "always"}),
    ("strong + 改写门控", {"budget": 0.05, "ctx_tokens": 300, "rewrite": "auto"}),
]


def pct(xs: list[float], p: float) -> float:
    xs = sorted(xs)
    if not xs:
        return 0.0
    k = max(0, min(len(xs) - 1, int(round((p / 100) * (len(xs) - 1)))))
    return xs[k]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--out", default="results/latency.json")
    args = ap.parse_args()

    s = Settings.from_env()
    if not s.api_key:
        print("需要 DEEPSEEK_API_KEY")
        return 1

    items = [json.loads(l) for l in (ROOT / args.set).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    docs = {p.name: p.read_text(encoding="utf-8") for p in sorted((ROOT / "data" / "sample_docs").glob("*.md"))}

    rows = []
    print(f"n={len(items)}\n{'配置':<24}{'p50':>9}{'p95':>9}{'均值':>9}{'成本/q':>12}{'召回':>8}")
    for name, cfg in CONFIGS:
        settings = Settings.from_env()
        settings.rewrite_mode = cfg.get("rewrite", "off")
        rag = RAG(settings, LLMAnswerer(settings))
        rag.ingest(docs)

        lat, costs, hit = [], [], 0
        for item in items:
            t0 = time.perf_counter()
            out = rag.query(item["question"], budget=cfg["budget"], ctx_tokens=cfg["ctx_tokens"])
            lat.append((time.perf_counter() - t0) * 1000)
            costs.append(out["trace"].get("cost_rmb", 0.0))
            ctx = "".join(
                c.text for c in rag.store.chunks if f"{c.doc}#{c.idx}" in out["trace"]["docs"]
            )
            norm = lambda x: "".join(str(x).split()).lower()  # noqa: E731
            hit += int(any(norm(g) in norm(ctx) for g in item["answers"]))

        r = {"config": name, "p50": pct(lat, 50), "p95": pct(lat, 95),
             "mean": statistics.mean(lat), "cost": statistics.mean(costs), "recall": hit / len(items)}
        rows.append(r)
        print(f"{name:<24}{r['p50']:>9.0f}{r['p95']:>9.0f}{r['mean']:>9.0f}"
              f"{r['cost']:>12.6f}{r['recall']:>8.4f}")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n结果: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
