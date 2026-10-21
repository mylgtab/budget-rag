"""预算扫描：画出 Recall–成本权衡曲线（零依赖，直接产 SVG）。

python scripts/sweep.py --set data/eval_set.jsonl --out results
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings          # noqa: E402
from budget_rag.llm import OfflineAnswerer      # noqa: E402
from budget_rag.pipeline import RAG             # noqa: E402

BUDGETS = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]


def norm(s: str) -> str:
    return "".join(s.split()).lower()


def evaluate(rag: RAG, items: list[dict], budget: float) -> tuple[float, float]:
    hit = 0
    cost = 0.0
    for item in items:
        out = rag.query(item["question"], budget=budget)
        tr = out["trace"]
        ctx = "".join(c.text for c in rag.store.chunks if f"{c.doc}#{c.idx}" in tr["docs"])
        if any(norm(g) in norm(ctx) for g in item["answers"]):
            hit += 1
        cost += tr["cost_rmb"]
    n = len(items) or 1
    return hit / n, cost / n


def svg(points: list[tuple[float, float, float]], path: Path) -> None:
    """points: [(cost, recall, budget)]，手搓一个折线图，省掉 matplotlib。"""
    w, h, ml, mr, mt, mb = 680, 420, 70, 30, 30, 60
    costs = [p[0] for p in points] or [0, 1]
    recall = [p[1] for p in points] or [0, 1]
    cx0, cx1 = min(costs), max(costs)
    ry0 = max(0.0, min(recall) - 0.05)
    ry1 = min(1.0, max(recall) + 0.05)
    sx = lambda c: ml + (c - cx0) / ((cx1 - cx0) or 1) * (w - ml - mr)          # noqa: E731
    sy = lambda r: h - mb - (r - ry0) / ((ry1 - ry0) or 1) * (h - mt - mb)      # noqa: E731

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="system-ui,sans-serif">',
        f'<rect width="{w}" height="{h}" fill="white"/>',
    ]
    for i in range(5):                                   # y 轴网格
        r = ry0 + (ry1 - ry0) * i / 4
        y = sy(r)
        parts.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{w-mr}" y2="{y:.1f}" stroke="#eee"/>')
        parts.append(f'<text x="{ml-8}" y="{y+4:.1f}" font-size="11" fill="#666" text-anchor="end">{r:.2f}</text>')
    for i in range(5):                                   # x 轴刻度
        c = cx0 + (cx1 - cx0) * i / 4
        x = sx(c)
        parts.append(f'<text x="{x:.1f}" y="{h-mb+18}" font-size="11" fill="#666" text-anchor="middle">{c:.5f}</text>')
    parts.append(f'<line x1="{ml}" y1="{h-mb}" x2="{w-mr}" y2="{h-mb}" stroke="#333"/>')
    parts.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{h-mb}" stroke="#333"/>')

    pts = " ".join(f"{sx(c):.1f},{sy(r):.1f}" for c, r, _ in points)
    parts.append(f'<polyline points="{pts}" fill="none" stroke="#2b6cb0" stroke-width="2.5"/>')
    for c, r, b in points:
        parts.append(f'<circle cx="{sx(c):.1f}" cy="{sy(r):.1f}" r="4" fill="#2b6cb0"/>')
        parts.append(f'<text x="{sx(c):.1f}" y="{sy(r)-10:.1f}" font-size="10" fill="#2b6cb0" text-anchor="middle">{b}</text>')

    parts.append(f'<text x="{(ml+w-mr)/2}" y="{h-14}" font-size="12" fill="#333" text-anchor="middle">cost / query (RMB)</text>')
    parts.append(f'<text x="18" y="{(mt+h-mb)/2}" font-size="12" fill="#333" transform="rotate(-90 18 {(mt+h-mb)/2})" text-anchor="middle">Recall@3</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_set.jsonl")
    ap.add_argument("--docs", default="data/sample_docs")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="限制评测条数，调试用")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    settings = Settings.from_env()
    settings.top_k = args.k
    rag = RAG(settings, OfflineAnswerer())
    rag.ingest({p.name: p.read_text(encoding="utf-8") for p in sorted(Path(args.docs).glob("*.md"))})

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        items = items[: args.limit]

    rows = []
    for b in BUDGETS:
        recall, cost = evaluate(rag, items, b)
        rows.append((cost, recall, b))
        print(f"budget={b:<8} recall@3={recall:.4f}  cost/q={cost:.6f}")

    outdir = ROOT / args.out
    outdir.mkdir(exist_ok=True)
    (outdir / "sweep.csv").write_text(
        "budget,cost_per_query,recall@3\n" + "\n".join(f"{b},{c:.6f},{r:.4f}" for c, r, b in rows) + "\n",
        encoding="utf-8",
    )
    fig = ROOT / "docs" / "figures"
    fig.mkdir(parents=True, exist_ok=True)
    svg(rows, fig / "tradeoff.svg")
    print(f"\nCSV: {outdir / 'sweep.csv'}  图: {fig / 'tradeoff.svg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
