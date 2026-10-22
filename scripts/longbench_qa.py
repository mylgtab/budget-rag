"""长文档问答完整链路：检索 → 生成 → 判定（LongBench hotpotqa 等）。

对比两种模式：
- rag ：先检索再答
- none：不检索直接答（下界）

python scripts/longbench_qa.py --file data/longbench/hotpotqa.jsonl --limit 50 --modes rag none
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

from budget_rag.config import Settings          # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.metrics import contain, em, f1  # noqa: E402
from budget_rag.store import Store              # noqa: E402
from budget_rag.tokens import count_tokens       # noqa: E402

_SPLIT = re.compile(r"(Passage|Paragraph|段落)\s*(\d+)\s*[:：]", re.IGNORECASE)

RAG_PROMPT = """只根据资料回答问题。资料里没有就说「不知道」，不要编。
答案要短，只输出答案本身。

资料：
{ctx}

问题：{q}
答案："""

NONE_PROMPT = """回答问题。答不出就说「不知道」，不要编。只输出答案本身。

问题：{q}
答案："""


def parse_passages(context: str) -> dict[str, str]:
    marks = list(_SPLIT.finditer(context))
    out: dict[str, str] = {}
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(context)
        out[f"{m.group(1)}{int(m.group(2))}"] = context[start:end].strip()
    return out


def take_budget(hits, budget: int, max_chunks: int = 24) -> str:
    ctx, used = [], 0
    for chunk, _ in hits:
        ctx.append(chunk.text)
        used += count_tokens(chunk.text)
        if used >= budget or len(ctx) >= max_chunks:
            break
    return "\n".join(ctx)


def ask(settings: Settings, prompt: str, max_tokens: int = 80,
        model: str | None = None, base: str | None = None, key: str | None = None) -> tuple[str, int]:
    body = json.dumps({
        "model": model or settings.llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        f"{base or settings.llm_base}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key or settings.api_key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode())
            u = data.get("usage") or {}
            return data["choices"][0]["message"]["content"].strip(), int(u.get("total_tokens", 0))
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return "", 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--tokens", type=int, default=800)
    ap.add_argument("--modes", nargs="+", default=["rag", "none"])
    ap.add_argument("--embed", default="real", choices=["hash", "real"])
    ap.add_argument("--out", default="results/longbench_qa.json")
    ap.add_argument("--model", default="")
    ap.add_argument("--base", default="")
    ap.add_argument("--key", default="")
    ap.add_argument("--no-think", action="store_true", help="给 Qwen3 加 /no_think")
    args = ap.parse_args()

    s = Settings.from_env()
    if not s.api_key:
        print("需要 DEEPSEEK_API_KEY")
        return 1
    emb = build_embedder(s) if args.embed == "real" else HashEmbedder(s.embed_dim)

    items = [json.loads(l) for l in Path(args.file).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    print(f"n={len(items)}  embedder={args.embed}  budget={args.tokens}  modes={args.modes}")

    stats = {m: {"c": 0.0, "e": 0.0, "f": 0.0, "tok": 0, "hit": 0} for m in args.modes}
    rows = []
    t0 = time.perf_counter()

    for i, item in enumerate(items, 1):
        q, golds = item["input"], item["answers"]
        passages = parse_passages(item["context"]) or {"Passage1": item["context"]}

        store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
        store.add_documents(passages)

        row = {"question": q, "gold": golds[0]}
        for mode in args.modes:
            if mode == "rag":
                hits = store.search_hybrid_precomputed(q, emb.embed([q])[0], len(store.chunks), alpha=0.2)
                ctx = take_budget(hits, args.tokens)
                span_hit = int(any(g.lower() in ctx.lower() for g in golds))
                _prompt = RAG_PROMPT.format(ctx=ctx[:2500], q=q)
                if args.no_think:
                    _prompt += " /no_think"
                answer, tokens = ask(s, _prompt,
                                 model=args.model or None, base=args.base or None, key=args.key or None)
                stats[mode]["hit"] += span_hit
                row["span_recall"] = span_hit
            else:
                _nprompt = NONE_PROMPT.format(q=q)
                if args.no_think:
                    _nprompt += " /no_think"
                answer, tokens = ask(s, _nprompt,
                                 model=args.model or None, base=args.base or None, key=args.key or None)

            stats[mode]["c"] += max(contain(answer, g) for g in golds)
            stats[mode]["e"] += max(em(answer, g) for g in golds)
            stats[mode]["f"] += max(f1(answer, g) for g in golds)
            stats[mode]["tok"] += tokens
            row[f"{mode}_answer"] = answer
        rows.append(row)

        if i % 10 == 0:
            print(f"  {i}/{len(items)}")

    n = len(items) or 1
    print(f"\n结果（{time.perf_counter()-t0:.0f}s）")
    print(f"{'模式':<6}{'contain':>10}{'EM':>8}{'F1':>8}{'平均token':>12}")
    for m in args.modes:
        st = stats[m]
        print(f"{m:<6}{st['c']/n:>10.4f}{st['e']/n:>8.4f}{st['f']/n:>8.4f}{st['tok']/n:>12.0f}")
    if "rag" in args.modes:
        print(f"  检索命中答案片段的比例: {stats['rag']['hit']/n:.4f}")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"明细: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
