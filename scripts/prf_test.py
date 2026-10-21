"""查询扩展（伪相关反馈）对比：纯词法、零成本。

python scripts/prf_test.py --set data/eval_500.jsonl --tokens 300
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings           # noqa: E402
from budget_rag.embedding import build_embedder  # noqa: E402
from budget_rag.store import Store               # noqa: E402


def norm(s: str) -> str:
    return "".join(s.split()).lower()


def toks(text: str) -> int:
    return max(1, int(len(text) / 1.5))


def take_budget(hits, budget: int) -> str:
    ctx, used = [], 0
    for chunk, _ in hits:
        ctx.append(chunk.text)
        used += toks(chunk.text)
        if used >= budget:
            break
    return "".join(ctx)


def run(store: Store, items: list[dict], budget: int, prf: bool) -> tuple[float, float]:
    hit = 0
    chars = 0
    for item in items:
        if prf:
            hits = store.search_bm25_prf(item["question"], 50)
        else:
            hits = store.search_bm25(item["question"], 50)
        ctx = take_budget(hits, budget)
        chars += len(ctx)
        if any(norm(g) in norm(ctx) for g in item["answers"]):
            hit += 1
    n = len(items) or 1
    return hit / n, chars / n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--tokens", type=int, default=300)
    args = ap.parse_args()

    settings = Settings.from_env()
    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()]

    for mode in ("sentence", "fixed"):
        store = Store(build_embedder(settings), settings.chunk_size, settings.chunk_overlap, mode)
        for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
            store.add_document(p.name, p.read_text(encoding="utf-8"))

        base_r, base_c = run(store, items, args.tokens, prf=False)
        prf_r, prf_c = run(store, items, args.tokens, prf=True)
        print(f"[{mode}] budget={args.tokens}")
        print(f"  基线      : recall={base_r:.4f}  平均上下文={base_c:.0f} 字")
        print(f"  PRF 扩展  : recall={prf_r:.4f}  平均上下文={prf_c:.0f} 字  (Δ={prf_r-base_r:+.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
