"""LongBench 子集评测：每条样本独立建索引，测「答案句是否被召回」。

python scripts/longbench_eval.py --file <jsonl> --tokens 300 --limit 50
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

from budget_rag.config import Settings                  # noqa: E402
from budget_rag.embedding import HashEmbedder, OpenAIEmbedder  # noqa: E402
from budget_rag.metrics import norm                     # noqa: E402
from budget_rag.store import Store                      # noqa: E402
from budget_rag.tokens import backend, count_tokens      # noqa: E402


def take_budget(hits, budget: int) -> str:
    ctx, used = [], 0
    for chunk, _ in hits:
        ctx.append(chunk.text)
        used += count_tokens(chunk.text)
        if used >= budget:
            break
    return "".join(ctx)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="LongBench jsonl")
    ap.add_argument("--tokens", type=int, default=300)
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--mode", default="sentence", choices=["sentence", "fixed"])
    ap.add_argument("--embed", default="hash", choices=["hash", "real"])
    args = ap.parse_args()

    s = Settings.from_env()
    if args.embed == "real":
        if not (s.embed_base and s.embed_key):
            print("需要 RAG_EMBED_BASE / RAG_EMBED_KEY")
            return 1
        emb = OpenAIEmbedder(s.embed_base, s.embed_model, s.embed_key)
    else:
        emb = HashEmbedder(s.embed_dim)

    items = []
    for line in Path(args.file).read_text(encoding="utf-8").splitlines():
        if line.strip():
            items.append(json.loads(line))
    items = items[: args.limit]

    print(f"文件={Path(args.file).name}  n={len(items)}  embedder={args.embed}  "
          f"chunk={args.mode}  budget={args.tokens}  tokenizer={backend()}")

    hits_bm25 = hits_vec = 0
    ctx_lens: list[int] = []
    t0 = time.perf_counter()

    for i, item in enumerate(items, 1):
        context = item.get("context") or item.get("contexts") or ""
        if isinstance(context, list):
            context = "\n".join(context)
        answers = item.get("answers") or []
        if isinstance(answers, str):
            answers = [answers]

        store = Store(emb, s.chunk_size, s.chunk_overlap, args.mode)
        store.add_document(f"item{i}", context)
        hit_fn = lambda ctx: any(norm(a) and norm(a) in norm(ctx) for a in answers)  # noqa: E731

        ctx_bm = take_budget(store.search_to_budget(item["input"], args.tokens, hybrid=False), args.tokens)
        hits_bm25 += hit_fn(ctx_bm)

        if args.embed == "real":
            qv = emb.embed([item["input"]])[0]
            ctx_v = take_budget(store.search_vector_precomputed(qv, len(store.chunks)), args.tokens)
        else:
            ctx_v = take_budget(store.search_to_budget(item["input"], args.tokens, hybrid=True), args.tokens)
        hits_vec += hit_fn(ctx_v)
        ctx_lens.append(count_tokens(ctx_bm))

        if i % 10 == 0:
            print(f"  {i}/{len(items)}  平均块数={len(store.chunks)}")

    n = len(items) or 1
    print(f"\n结果（{time.perf_counter() - t0:.1f}s）")
    print(f"  BM25 召回     : {hits_bm25 / n:.4f}")
    print(f"  向量/混合 召回: {hits_vec / n:.4f}")
    print(f"  平均上下文    : {statistics.mean(ctx_lens):.0f} tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
