"""用模型改写查询，测召回提升；小样本试水，成本几分钱。

python scripts/llm_rewrite_test.py --set data/eval_500.jsonl --limit 150
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings            # noqa: E402
from budget_rag.embedding import build_embedder   # noqa: E402
from budget_rag.store import Store                # noqa: E402

PROMPT = (
    "把下面的问题改写成适合关键词检索的查询词。\n"
    "要求：输出 5-10 个词或短语，用空格分隔；保留原问题的关键概念，"
    "补充同义词或上位词；不要解释，不要标点，不要回答问题。\n\n"
    "问题：{q}\n改写："
)


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


def rewrite(settings: Settings, q: str) -> str:
    body = json.dumps({
        "model": settings.llm_model,
        "messages": [{"role": "user", "content": PROMPT.format(q=q)}],
        "temperature": 0.0,
        "max_tokens": 80,
    }).encode()
    req = urllib.request.Request(
        f"{settings.llm_base}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {settings.api_key}", "Content-Type": "application/json"},
    )
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"改写失败: {last}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--limit", type=int, default=150)
    ap.add_argument("--tokens", type=int, default=300)
    ap.add_argument("--mode", default="sentence")
    args = ap.parse_args()

    settings = Settings.from_env()
    if not settings.api_key:
        print("缺少 DEEPSEEK_API_KEY")
        return 1

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    store = Store(build_embedder(settings), settings.chunk_size, settings.chunk_overlap, args.mode)
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))

    base = replace = expand = 0
    for i, item in enumerate(items, 1):
        q = item["question"]
        golds = item["answers"]

        ctx = take_budget(store.search_bm25(q, 50), args.tokens)
        base += any(norm(g) in norm(ctx) for g in golds)

        rq = rewrite(settings, q)
        ctx_r = take_budget(store.search_bm25(rq, 50), args.tokens)
        replace += any(norm(g) in norm(ctx_r) for g in golds)

        ctx_e = take_budget(store.search_bm25(f"{q} {rq}", 50), args.tokens)
        expand += any(norm(g) in norm(ctx_e) for g in golds)

        if i % 50 == 0:
            print(f"  {i}/{len(items)}")

    n = len(items)
    print(f"\n[{args.mode}] budget={args.tokens}  n={n}")
    print(f"  原始查询      : {base/n:.4f}")
    print(f"  模型改写(替换): {replace/n:.4f}  (Δ={replace/n - base/n:+.4f})")
    print(f"  原始+改写(扩) : {expand/n:.4f}  (Δ={expand/n - base/n:+.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
