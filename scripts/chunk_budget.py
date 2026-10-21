"""在相同 token 预算下比较分块粒度，修正 Recall@k 偏爱大块的偏差。

python scripts/chunk_budget.py --set data/eval_500.jsonl
产出 results/chunk_budget.csv + docs/figures/chunk_budget.svg
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings          # noqa: E402
from budget_rag.embedding import build_embedder  # noqa: E402
from budget_rag.store import Store              # noqa: E402

BUDGETS = [80, 120, 200, 300, 500, 800]


def norm(s: str) -> str:
    return "".join(s.split()).lower()


def toks(text: str) -> int:
    return max(1, int(len(text) / 1.5))


def build(mode: str, settings: Settings) -> Store:
    store = Store(build_embedder(settings), settings.chunk_size, settings.chunk_overlap, mode)
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))
    return store


def retrieve_to_budget(store: Store, question: str, budget: int) -> str:
    """按分数顺序取块，直到累计 token 达到预算。"""
    ranked = store.search_bm25(question, len(store.chunks))
    picked, used = [], 0
    for chunk, _score in ranked:
        picked.append(chunk.text)
        used += toks(chunk.text)
        if used >= budget:
            break
    return "".join(picked)


def evaluate(mode: str, settings: Settings, items: list[dict]) -> list[tuple[int, float, float]]:
    store = build(mode, settings)
    out = []
    for b in BUDGETS:
        hit = 0
        tokens = 0.0
        for item in items:
            ctx = retrieve_to_budget(store, item["question"], b)
            tokens += toks(ctx)
            if any(norm(g) in norm(ctx) for g in item["answers"]):
                hit += 1
        n = len(items) or 1
        out.append((b, hit / n, tokens / n))
    return out


def svg(series: dict[str, list[tuple[int, float, float]]], path: Path) -> None:
    w, h, ml, mr, mt, mb = 680, 420, 70, 30, 30, 60
    xs = [b for b, _, _ in next(iter(series.values()))]
    ys = [r for s in series.values() for _, r, _ in s]
    x0, x1 = min(xs), max(xs)
    y0, y1 = max(0.0, min(ys) - 0.05), min(1.0, max(ys) + 0.05)
    sx = lambda v: ml + (v - x0) / ((x1 - x0) or 1) * (w - ml - mr)      # noqa: E731
    sy = lambda v: h - mb - (v - y0) / ((y1 - y0) or 1) * (h - mt - mb)  # noqa: E731

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="system-ui,sans-serif">',
             f'<rect width="{w}" height="{h}" fill="white"/>']
    for i in range(5):
        v = y0 + (y1 - y0) * i / 4
        y = sy(v)
        parts.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{w-mr}" y2="{y:.1f}" stroke="#eee"/>')
        parts.append(f'<text x="{ml-8}" y="{y+4:.1f}" font-size="11" fill="#666" text-anchor="end">{v:.2f}</text>')
    for b in xs:
        parts.append(f'<text x="{sx(b):.1f}" y="{h-mb+18}" font-size="10" fill="#666" text-anchor="middle">{b}</text>')
    parts.append(f'<line x1="{ml}" y1="{h-mb}" x2="{w-mr}" y2="{h-mb}" stroke="#333"/>')
    parts.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{h-mb}" stroke="#333"/>')

    colors = {"fixed": "#2b6cb0", "sentence": "#dd6b20"}
    for name, s in series.items():
        pts = " ".join(f"{sx(b):.1f},{sy(r):.1f}" for b, r, _ in s)
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{colors.get(name, "#333")}" stroke-width="2.5"/>')
        for b, r, _ in s:
            parts.append(f'<circle cx="{sx(b):.1f}" cy="{sy(r):.1f}" r="3.5" fill="{colors.get(name, "#333")}"/>')
        lx = ml + 20
        ly = mt + 10 + 20 * list(series).index(name)
        parts.append(f'<rect x="{lx}" y="{ly-8}" width="14" height="3" fill="{colors.get(name, "#333")}"/>')
        parts.append(f'<text x="{lx+20}" y="{ly-2}" font-size="12" fill="#333">{name} 分块</text>')

    parts.append(f'<text x="{(ml+w-mr)/2}" y="{h-14}" font-size="12" fill="#333" text-anchor="middle">context token budget</text>')
    parts.append(f'<text x="18" y="{(mt+h-mb)/2}" font-size="12" fill="#333" transform="rotate(-90 18 {(mt+h-mb)/2})" text-anchor="middle">Recall (答案句在上下文内)</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    settings = Settings.from_env()
    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()]
    series = {mode: evaluate(mode, settings, items) for mode in ("fixed", "sentence")}

    for mode, rows in series.items():
        print(f"--- {mode} ---")
        for b, r, t in rows:
            print(f"  budget={b:<5} recall={r:.4f}  实际上下文={t:.0f} tokens")

    outdir = ROOT / args.out
    outdir.mkdir(exist_ok=True)
    lines = ["mode,budget,recall,actual_tokens"]
    for mode, rows in series.items():
        lines += [f"{mode},{b},{r:.4f},{t:.1f}" for b, r, t in rows]
    (outdir / "chunk_budget.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    fig = ROOT / "docs" / "figures"
    fig.mkdir(parents=True, exist_ok=True)
    svg(series, fig / "chunk_budget.svg")
    print(f"\nCSV: {outdir / 'chunk_budget.csv'}\n图: {fig / 'chunk_budget.svg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
