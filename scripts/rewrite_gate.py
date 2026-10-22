"""对比查询改写的三种策略：off / always / auto（置信度门控）。

只测检索召回，不调用生成，成本仅为改写调用。
python scripts/rewrite_gate.py --set data/eval_500.jsonl --tokens 300
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings            # noqa: E402
from budget_rag.embedding import build_embedder   # noqa: E402
from budget_rag.llm import LLMAnswerer            # noqa: E402
from budget_rag.store import Store                # noqa: E402


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


def confidence(hits) -> float:
    if not hits:
        return 0.0
    s1 = hits[0][1]
    s2 = hits[1][1] if len(hits) > 1 else 0.0
    return (s1 - s2) / s1 if s1 > 0 else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--tokens", type=int, default=300)
    ap.add_argument("--threshold", type=float, default=0.25)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--mode", default="sentence")
    args = ap.parse_args()

    settings = Settings.from_env()
    if not settings.api_key:
        print("缺少 DEEPSEEK_API_KEY")
        return 1

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        items = items[: args.limit]

    store = Store(build_embedder(settings), settings.chunk_size, settings.chunk_overlap, args.mode)
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))
    answerer = LLMAnswerer(settings)

    stats = {m: {"hit": 0, "rw": 0, "ms": 0.0} for m in ("off", "always", "auto")}

    for i, item in enumerate(items, 1):
        q, golds = item["question"], item["answers"]

        t0 = time.perf_counter()
        hits_off = store.search_to_budget(q, args.tokens)
        stats["off"]["ms"] += (time.perf_counter() - t0) * 1000
        stats["off"]["hit"] += any(norm(g) in norm(take_budget(hits_off, args.tokens)) for g in golds)

        t0 = time.perf_counter()
        rq = answerer.rewrite_query(q) or ""
        stats["always"]["rw"] += 1
        hits_always = store.search_to_budget(f"{q} {rq}", args.tokens)
        stats["always"]["ms"] += (time.perf_counter() - t0) * 1000
        stats["always"]["hit"] += any(norm(g) in norm(take_budget(hits_always, args.tokens)) for g in golds)

        t0 = time.perf_counter()
        if confidence(hits_off) < args.threshold:
            rq2 = answerer.rewrite_query(q) or ""
            stats["auto"]["rw"] += 1
            hits_auto = store.search_to_budget(f"{q} {rq2}", args.tokens)
        else:
            hits_auto = hits_off
        stats["auto"]["ms"] += (time.perf_counter() - t0) * 1000
        stats["auto"]["hit"] += any(norm(g) in norm(take_budget(hits_auto, args.tokens)) for g in golds)

        if i % 50 == 0:
            print(f"  {i}/{len(items)}")

    n = len(items)
    print(f"\n[{args.mode}] budget={args.tokens}  n={n}  threshold={args.threshold}")
    print(f"{'策略':<8}{'recall':>8}{'改写次数':>10}{'改写比例':>10}{'平均延迟':>12}")
    for m in ("off", "always", "auto"):
        s = stats[m]
        print(f"{m:<8}{s['hit']/n:>8.4f}{s['rw']:>10}{s['rw']/n:>9.1%}{s['ms']/n:>10.0f} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
