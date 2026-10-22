"""TriviaQA 专用评测：LongBench 版的 input 含 few-shot，需要抽出真正的问句。

答案是一长串别名，因此用「命中任一别名」作为 contain 判定。
python scripts/longbench_triviaqa.py --limit 20 --model qwen3-4b --base http://127.0.0.1:11434/v1 --no-think
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

from budget_rag.config import Settings                # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.metrics import contain, em, f1        # noqa: E402
from budget_rag.store import Store                    # noqa: E402
from budget_rag.tokens import count_tokens            # noqa: E402

RAG_PROMPT = """只根据资料回答问题。答不出就说「不知道」。
答案要短，只输出答案本身。

资料：
{ctx}

问题：{q}
答案："""

NONE_PROMPT = """回答问题。答不出就说「不知道」。只输出答案本身。

问题：{q}
答案："""


def extract_question(text: str) -> str:
    """LongBench triviaqa 的 input 结构：... 示例 ... Question:\\n<问句>\\nAnswer:"""
    if "Question:" in text:
        tail = text.rsplit("Question:", 1)[1]
        tail = tail.split("Answer:")[0]
        return " ".join(tail.split()).strip()
    return " ".join(text.split()).strip()


def split_passages(ctx: str) -> dict[str, str]:
    """把 "Passage:\n<title>\n<body>" 拆成 {title: body}，标题参与检索。"""
    parts = [p.strip() for p in re.split(r"Passage:\s*", ctx) if p.strip()]
    out: dict[str, str] = {}
    for i, block in enumerate(parts):
        lines = block.splitlines()
        if len(lines) >= 2:
            title, body = lines[0].strip(), "\n".join(lines[1:]).strip()
            out[f"{i}:{title}"] = f"{title}\n{body}"
        else:
            out[f"{i}"] = block
    return out


def take_budget(hits, budget: int, max_chunks: int | None = None) -> str:
    if max_chunks is None:
        max_chunks = max(8, budget // 15)     # 每块约 15 token，别让上限先卡死预算
    out, used = [], 0
    for c, _ in hits:
        out.append(c.text)
        used += count_tokens(c.text)
        if used >= budget or len(out) >= max_chunks:
            break
    return "\n".join(out)


def ask(settings: Settings, prompt: str, model=None, base=None, key=None, max_tokens=64) -> tuple[str, int]:
    body = json.dumps({
        "model": model or settings.llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0, "max_tokens": max_tokens,
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
    ap.add_argument("--file", default="data/longbench/triviaqa.jsonl")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--tokens", type=int, default=800)
    ap.add_argument("--embed", default="real", choices=["hash", "real"])
    ap.add_argument("--model", default="")
    ap.add_argument("--base", default="")
    ap.add_argument("--key", default="")
    ap.add_argument("--no-think", action="store_true")
    ap.add_argument("--out", default="results/qa_triviaqa.json")
    args = ap.parse_args()

    s = Settings.from_env()
    if not s.api_key and not args.key:
        print("需要 DEEPSEEK_API_KEY 或 --key")
        return 1
    emb = build_embedder(s) if args.embed == "real" else HashEmbedder(s.embed_dim)

    items = [json.loads(l) for l in (ROOT / args.file).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    stats = {m: {"c": 0.0, "e": 0.0, "f": 0.0, "hit": 0, "tok": 0} for m in ("rag", "none")}
    rows = []
    t0 = time.perf_counter()

    for i, item in enumerate(items, 1):
        q = extract_question(item["input"])
        aliases = [str(a) for a in item["answers"]]
        passages = split_passages(item["context"])

        store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
        store.add_documents(passages)
        qv = emb.embed([q])[0]
        hits = store.search_hybrid_precomputed(q, qv, len(store.chunks), alpha=0.2)
        ctx = take_budget(hits, args.tokens)

        for mode in ("rag", "none"):
            prompt = (RAG_PROMPT.format(ctx=ctx[:9000], q=q) if mode == "rag"
                      else NONE_PROMPT.format(q=q))
            if args.no_think:
                prompt += " /no_think"
            ans, tokens = ask(s, prompt, args.model or None, args.base or None, args.key or None)
            stats[mode]["c"] += max(contain(ans, a) for a in aliases)
            stats[mode]["e"] += max(em(ans, a) for a in aliases)
            stats[mode]["f"] += max(f1(ans, a) for a in aliases)
            stats[mode]["tok"] += tokens
            if mode == "rag":
                stats[mode]["hit"] += int(any(a.lower() in ctx.lower() for a in aliases))
                rows.append({"q": q, "rag_answer": ans, "gold": aliases[0]})
            else:
                rows[-1]["none_answer"] = ans
        if i % 5 == 0:
            print(f"  {i}/{len(items)}")

    n = len(items) or 1
    print(f"\nTriviaQA（n={n}, {time.perf_counter()-t0:.0f}s）")
    print(f"{'模式':<6}{'contain':>10}{'EM':>8}{'F1':>8}{'平均token':>12}")
    for m in ("rag", "none"):
        st = stats[m]
        print(f"{m:<6}{st['c']/n:>10.4f}{st['e']/n:>8.4f}{st['f']/n:>8.4f}{st['tok']/n:>12.0f}")
    print(f"  答案别名命中上下文的比例: {stats['rag']['hit']/n:.4f}")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"明细: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
