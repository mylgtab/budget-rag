"""多跳检索：先搜一轮，问模型「还缺什么信息」，再搜一轮，合并后作答。

对比模式：
- single：单轮检索（基线）
- bridge：两轮检索（第一轮结果 → 生成补充查询 → 第二轮）
- merge ：原始查询 + 补充查询各搜一轮，合并去重（不做生成式补充）

python scripts/multihop.py --file data/longbench/hotpotqa.jsonl --limit 30
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

ANSWER_PROMPT = """只根据资料回答问题。资料里没有就说「不知道」，不要编。
答案要短，只输出答案本身。

资料：
{ctx}

问题：{q}
答案："""

BRIDGE_PROMPT = """下面是一道需要两步推理的问题，以及第一轮检索到的资料。
资料可能只覆盖了一部分。请给出**还需要检索什么**——只输出一个简短的检索查询（3-10 个词），不要解释。

问题：{q}

已检索到的资料摘要：
{ctx}

还缺的信息（检索查询）："""


def parse_passages(context: str) -> dict[str, str]:
    marks = list(_SPLIT.finditer(context))
    out: dict[str, str] = {}
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(context)
        out[f"{m.group(1)}{int(m.group(2))}"] = context[start:end].strip()
    return out


def take_chunks(hits, budget: int, max_chunks: int = 24) -> list:
    picked, used = [], 0
    for chunk, _ in hits:
        picked.append(chunk)
        used += count_tokens(chunk.text)
        if used >= budget or len(picked) >= max_chunks:
            break
    return picked


def ask(settings: Settings, prompt: str, max_tokens: int = 80) -> tuple[str, int]:
    body = json.dumps({
        "model": settings.llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        f"{settings.llm_base}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {settings.api_key}", "Content-Type": "application/json"})
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
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--tokens", type=int, default=800)
    ap.add_argument("--modes", nargs="+", default=["single", "bridge"])
    ap.add_argument("--embed", default="real", choices=["hash", "real"])
    ap.add_argument("--out", default="results/multihop.json")
    args = ap.parse_args()

    s = Settings.from_env()
    if not s.api_key:
        print("需要 DEEPSEEK_API_KEY")
        return 1
    emb = build_embedder(s) if args.embed == "real" else HashEmbedder(s.embed_dim)

    items = [json.loads(l) for l in Path(args.file).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    print(f"n={len(items)}  budget={args.tokens}  modes={args.modes}")

    stats = {m: {"c": 0.0, "e": 0.0, "f": 0.0, "tok": 0, "hit": 0} for m in args.modes}
    rows = []
    t0 = time.perf_counter()

    for i, item in enumerate(items, 1):
        q, golds = item["input"], item["answers"]
        passages = parse_passages(item["context"]) or {"Passage1": item["context"]}
        store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
        store.add_documents(passages)

        qv = emb.embed([q])[0]
        hits1 = store.search_hybrid_precomputed(q, qv, len(store.chunks), alpha=0.2)
        chunks1 = take_chunks(hits1, args.tokens)
        ctx1 = "\n".join(c.text for c in chunks1)

        row = {"question": q, "gold": golds[0]}

        for mode in args.modes:
            tokens = 0
            if mode == "single":
                ctx = ctx1
            else:
                sub, t1 = ask(s, BRIDGE_PROMPT.format(q=q, ctx=ctx1[:1500]), max_tokens=40)
                tokens += t1
                q2 = f"{q} {sub}" if sub and "不知道" not in sub else f"{q} {golds[0] if False else ''}"
                qv2 = emb.embed([q2])[0]
                hits2 = store.search_hybrid_precomputed(q2, qv2, len(store.chunks), alpha=0.2)
                chunks2 = take_chunks(hits2, args.tokens)
                seen, merged = set(), []
                for c in chunks1 + chunks2:
                    key = (c.doc, c.idx)
                    if key in seen:
                        continue
                    seen.add(key)
                    merged.append(c)
                ctx = "\n".join(c.text for c in merged)
                row["subquery"] = sub

            answer, t2 = ask(s, ANSWER_PROMPT.format(ctx=ctx[:9000], q=q))
            tokens += t2
            stats[mode]["tok"] += tokens
            stats[mode]["c"] += max(contain(answer, g) for g in golds)
            stats[mode]["e"] += max(em(answer, g) for g in golds)
            stats[mode]["f"] += max(f1(answer, g) for g in golds)
            stats[mode]["hit"] += int(any(g.lower() in ctx.lower() for g in golds))
            row[f"{mode}_answer"] = answer
            row[f"{mode}_ctx_tokens"] = count_tokens(ctx)

        rows.append(row)
        if i % 5 == 0:
            print(f"  {i}/{len(items)}")

    n = len(items) or 1
    print(f"\n结果（{time.perf_counter()-t0:.0f}s）")
    print(f"{'模式':<8}{'contain':>10}{'EM':>8}{'F1':>8}{'命中':>8}{'token':>8}")
    for m in args.modes:
        st = stats[m]
        print(f"{m:<8}{st['c']/n:>10.4f}{st['e']/n:>8.4f}{st['f']/n:>8.4f}{st['hit']/n:>8.4f}{st['tok']/n:>8.0f}")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"明细: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
