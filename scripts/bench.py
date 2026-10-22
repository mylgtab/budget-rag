"""策略对比台：跑多个检索策略，输出对比表 + 柱状图 + 自助法置信区间。

python scripts/bench.py --set data/eval_set.jsonl --bootstrap 1000
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings          # noqa: E402
from budget_rag.llm import OfflineAnswerer      # noqa: E402
from budget_rag.store import Store              # noqa: E402
from budget_rag.embedding import build_embedder  # noqa: E402
from budget_rag.router import decide            # noqa: E402

_WORD = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]")

# 级联策略置信阈值：top1 与 top2 的相对差距小于它，就认为检索拿不准，升级
MARGIN = 0.25


def norm(s: str) -> str:
    return "".join(s.split()).lower()


def f1(pred: str, gold: str) -> float:
    p, g = _WORD.findall(str(pred).lower()), _WORD.findall(str(gold).lower())
    if not p or not g:
        return float(norm(pred) == norm(gold))
    gs, common = list(g), 0
    for t in p:
        if t in gs:
            gs.remove(t)
            common += 1
    if common == 0:
        return 0.0
    prec, rec = common / len(p), common / len(g)
    return 2 * prec * rec / (prec + rec)


@dataclass
class Strategy:
    name: str
    kind: str          # "bm25" | "hybrid" | "adaptive"
    k: int
    price: float       # 元 / 1k tokens
    note: str = ""


STRATEGIES = [
    Strategy("naive-bm25-k3", "bm25", 3, 0.0005, "固定 top-3，纯关键词"),
    Strategy("fixed-bm25-k1", "bm25", 1, 0.0005, "最省，只取一条"),
    Strategy("fixed-hybrid-k5", "hybrid", 5, 0.002, "固定深检索，混合"),
    Strategy("adaptive-budget", "adaptive", 0, 0.0012, "按预算与难度路由"),
    Strategy("cascade-conf", "cascade", 2, 0.0012, "先便宜查，置信低才升级"),
]


def run_one(strategy: Strategy, store: Store, answerer, items: list[dict],
            budget: float) -> list[dict]:
    rows = []
    for item in items:
        t0 = time.perf_counter()
        if strategy.kind == "adaptive":
            route = decide(item["question"], budget, 3)
            hits = (store.search_hybrid(item["question"], route.k) if route.hybrid
                    else store.search_bm25(item["question"], route.k))
            price = 0.0005 if not route.hybrid else 0.002
        elif strategy.kind == "cascade":
            cheap = store.search_bm25(item["question"], strategy.k)
            s1 = cheap[0][1] if cheap else 0.0
            s2 = cheap[1][1] if len(cheap) > 1 else 0.0
            confident = s1 > 0 and (s1 - s2) / (s1 + 1e-9) >= MARGIN
            if confident:
                hits, price = cheap, 0.0005
            else:                                   # 拿不准就升级
                hits, price = store.search_hybrid(item["question"], 5), 0.002
        else:
            hits = (store.search_hybrid(item["question"], strategy.k) if strategy.kind == "hybrid"
                    else store.search_bm25(item["question"], strategy.k))
            price = strategy.price

        ctx = [c.text for c, _ in hits]
        answer = answerer.answer(item["question"], ctx) if ctx else ""
        joined = "".join(ctx)
        golds = item["answers"]
        tokens = sum(max(1, int(len(c) / 1.5)) for c in ctx) + max(1, int(len(answer) / 1.5))
        rows.append({
            "recall": float(any(norm(g) in norm(joined) for g in golds)),
            "em": float(any(norm(answer) == norm(g) for g in golds)),
            "f1": max(f1(answer, g) for g in golds),
            "cost": tokens / 1000 * price,
            "ms": (time.perf_counter() - t0) * 1000,
        })
    return rows


def bootstrap_ci(values: list[float], n: int = 1000, alpha: float = 0.05, seed: int = 7) -> tuple[float, float]:
    rng = random.Random(seed)
    k = len(values)
    means = []
    for _ in range(n):
        means.append(sum(values[rng.randrange(k)] for _ in range(k)) / k)
    means.sort()
    lo = means[int(alpha / 2 * n)]
    hi = means[int((1 - alpha / 2) * n) - 1]
    return lo, hi


def bar_svg(rows: list[dict], path: Path) -> None:
    w, h, ml, mr, mt, mb = 720, 420, 80, 30, 30, 90
    names = [r["name"] for r in rows]
    bw = (w - ml - mr) / len(rows) * 0.55
    gap = (w - ml - mr) / len(rows)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="system-ui,sans-serif">',
             f'<rect width="{w}" height="{h}" fill="white"/>']
    for i in range(5):
        v = i / 4
        y = h - mb - v * (h - mt - mb)
        parts.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{w-mr}" y2="{y:.1f}" stroke="#eee"/>')
        parts.append(f'<text x="{ml-8}" y="{y+4:.1f}" font-size="11" fill="#666" text-anchor="end">{v:.2f}</text>')
    colors = ["#a0aec0", "#90cdf4", "#4299e1", "#2b6cb0"]
    for i, r in enumerate(rows):
        x = ml + gap * i + (gap - bw) / 2
        bh = r["recall"] * (h - mt - mb)
        y = h - mb - bh
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{colors[i % len(colors)]}" rx="3"/>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" font-size="11" fill="#1a202c" text-anchor="middle">{r["recall"]:.3f}</text>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{h-mb+16:.1f}" font-size="10" fill="#444" text-anchor="middle">{r["name"]}</text>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{h-mb+32:.1f}" font-size="9" fill="#888" text-anchor="middle">{r["cost"]:.5f} 元</text>')
    parts.append(f'<line x1="{ml}" y1="{h-mb}" x2="{w-mr}" y2="{h-mb}" stroke="#333"/>')
    parts.append(f'<text x="18" y="{(mt+h-mb)/2}" font-size="12" fill="#333" transform="rotate(-90 18 {(mt+h-mb)/2})" text-anchor="middle">Recall@k</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="data/sample_docs")
    ap.add_argument("--set", default="data/eval_set.jsonl")
    ap.add_argument("--budget", type=float, default=0.01)
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    settings = Settings.from_env()
    store = Store(build_embedder(settings), settings.chunk_size, settings.chunk_overlap)
    for p in sorted(Path(args.docs).glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))
    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()]
    answerer = OfflineAnswerer()

    rows = []
    for s in STRATEGIES:
        per = run_one(s, store, answerer, items, args.budget)
        n = len(per)
        rec = sum(r["recall"] for r in per) / n
        lo, hi = bootstrap_ci([r["recall"] for r in per], args.bootstrap)
        rows.append({
            "name": s.name,
            "note": s.note,
            "recall": rec,
            "ci_low": lo,
            "ci_high": hi,
            "em": sum(r["em"] for r in per) / n,
            "f1": sum(r["f1"] for r in per) / n,
            "cost": sum(r["cost"] for r in per) / n,
            "p95_ms": sorted(r["ms"] for r in per)[max(0, int(n * 0.95) - 1)],
        })
        print(f"{s.name:<18} recall={rec:.4f} [{lo:.4f},{hi:.4f}]  "
              f"f1={rows[-1]['f1']:.4f}  cost/q={rows[-1]['cost']:.6f}")

    outdir = ROOT / args.out
    outdir.mkdir(exist_ok=True)
    with (outdir / "bench.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    lines = ["| 策略 | 说明 | Recall@k (95% CI) | F1 | cost/q | p95 |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| `{r['name']}` | {r['note']} | {r['recall']:.3f} "
                     f"[{r['ci_low']:.3f}, {r['ci_high']:.3f}] | {r['f1']:.3f} | "
                     f"{r['cost']:.6f} | {r['p95_ms']:.1f} ms |")
    fig = ROOT / "docs" / "figures"
    fig.mkdir(parents=True, exist_ok=True)
    bar_svg(rows, fig / "bench.svg")
    (outdir / "bench.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"\n表: {outdir / 'bench.md'}\n图: {fig / 'bench.svg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
