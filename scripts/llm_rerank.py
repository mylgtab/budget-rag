"""用聊天模型做语义重排（替代 embedding 的一种便宜方案）。

先 BM25 粗召回 N 条，再让模型给每条打 0-10 分，按分数取块。
python scripts/llm_rerank.py --limit 100
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings               # noqa: E402
from budget_rag.embedding import build_embedder       # noqa: E402
from budget_rag.metrics import norm                  # noqa: E402
from budget_rag.store import Store                   # noqa: E402
from budget_rag.tokens import count_tokens           # noqa: E402

PROMPT = """给下面每个候选片段的相关性打分，0 到 10 的整数。
10 = 直接包含问题答案；5 = 主题相关但没有答案；0 = 完全无关。
只输出 JSON 数组，形如 [8, 2, 0]，按候选顺序，不要解释。

问题：{q}

{cands}
"""


def take_budget(chunks, budget: int) -> str:
    ctx, used = [], 0
    for c in chunks:
        ctx.append(c)
        used += count_tokens(c)
        if used >= budget:
            break
    return "".join(ctx)


def score(settings: Settings, q: str, cands: list[str]) -> list[int]:
    body_text = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(cands))
    body = json.dumps({
        "model": settings.llm_model,
        "messages": [{"role": "user", "content": PROMPT.format(q=q, cands=body_text)}],
        "temperature": 0.0,
        "max_tokens": 120,
    }).encode()
    req = urllib.request.Request(
        f"{settings.llm_base}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {settings.api_key}", "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            raw = data["choices"][0]["message"]["content"]
            nums = [int(x) for x in re.findall(r"\d+", raw)]
            return nums[: len(cands)] + [0] * (len(cands) - len(nums[: len(cands)]))
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return [0] * len(cands)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--candidates", type=int, default=8)
    ap.add_argument("--tokens", type=int, default=300)
    args = ap.parse_args()

    s = Settings.from_env()
    if not s.api_key:
        print("缺少 DEEPSEEK_API_KEY")
        return 1

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    store = Store(build_embedder(s), s.chunk_size, s.chunk_overlap, "sentence")
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))

    base_hit = rerank_hit = 0
    t0 = time.perf_counter()
    for i, item in enumerate(items, 1):
        q, golds = item["question"], item["answers"]
        pool = [c for c, _ in store.search_bm25(q, args.candidates)]

        ctx_base = take_budget([c.text for c in pool], args.tokens)
        base_hit += any(norm(g) in norm(ctx_base) for g in golds)

        marks = score(s, q, [c.text for c in pool])
        order = sorted(range(len(pool)), key=lambda j: marks[j], reverse=True)
        ctx_re = take_budget([pool[j].text for j in order], args.tokens)
        rerank_hit += any(norm(g) in norm(ctx_re) for g in golds)

        if i % 25 == 0:
            print(f"  {i}/{len(items)}")

    n = len(items)
    print(f"\nn={n}  候选={args.candidates}  预算={args.tokens} token  耗时={(time.perf_counter()-t0)/60:.1f} 分钟")
    print(f"  BM25 原始顺序 : {base_hit/n:.4f}")
    print(f"  LLM 重排      : {rerank_hit/n:.4f}   (Δ={rerank_hit/n - base_hit/n:+.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
