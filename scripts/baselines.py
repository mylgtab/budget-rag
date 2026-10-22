"""基线对比：把我们的级联和 5 个基线放在同一批题上比。

基线：
  bm25_k3      经典稀疏检索，固定 3 块
  dense_k5     纯向量，固定 5 块
  hybrid_k5    混合固定（alpha=0.2）
  adaptive     近似 Adaptive-RAG：按查询复杂度选深度（启发式分类器，非训练模型）
  crag         近似 CRAG：检索后让模型判相关性，差就改写重检
  ours         我们的级联（预算路由 + 改写门控）

质量：答案片段是否被召回（该指标对所有策略一致，不含生成）
成本：平均上下文 token + 调用折算

python scripts/baselines.py --limit 200
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings                # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.llm import LLMAnswerer                # noqa: E402
from budget_rag.metrics import norm                   # noqa: E402
from budget_rag.store import Store                    # noqa: E402
from budget_rag.tokens import count_tokens             # noqa: E402

COMPLEX_HINTS = ("比较", "区别", "为什么", "如何", "怎么", "哪些", "关系", "对比", "优缺点")
JUDGE_PROMPT = """资料是否足以回答这个问题？只输出一个词：good / partial / bad。

问题：{q}
资料：
{ctx}
"""


def tokens_of(chunks) -> int:
    return sum(count_tokens(c.text) for c in chunks)


def judge(settings: Settings, q: str, ctx: str) -> str:
    body = json.dumps({
        "model": settings.llm_model,
        "messages": [{"role": "user", "content": JUDGE_PROMPT.format(q=q, ctx=ctx[:2000])}],
        "temperature": 0.0, "max_tokens": 10,
    }).encode()
    req = urllib.request.Request(
        f"{settings.llm_base}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {settings.api_key}", "Content-Type": "application/json"})
    for _ in range(2):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                t = json.loads(resp.read().decode())["choices"][0]["message"]["content"].lower()
            for v in ("good", "partial", "bad"):
                if v in t:
                    return v
            return "partial"
        except Exception:
            time.sleep(1.0)
    return "partial"


def is_complex(q: str, settings: Settings) -> bool:
    """近似 Adaptive-RAG 的复杂度判定：长度 + 疑问词启发式。"""
    if len(q) >= 18:
        return True
    return any(h in q for h in COMPLEX_HINTS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--embed", default="real", choices=["hash", "real"])
    ap.add_argument("--out", default="results/baselines.json")
    args = ap.parse_args()

    s = Settings.from_env()
    emb = build_embedder(s) if args.embed == "real" else HashEmbedder(s.embed_dim)
    store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))
    answerer = LLMAnswerer(s)
    if not s.api_key:
        print("需要 DEEPSEEK_API_KEY（adaptive 以外的基线可离线跑，crag 需要）")
        return 1

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    names = ["bm25_k3", "dense_k5", "hybrid_k5", "adaptive", "crag", "ours"]
    rows = []
    t0 = time.perf_counter()

    for i, item in enumerate(items, 1):
        q, golds = item["question"], item["answers"]
        qv = emb.embed([q])[0]
        rec = {}

        def score(chunks, extra_tokens=0):
            text = "".join(c.text for c in chunks)
            hit = int(any(norm(g) in norm(text) for g in golds))
            return hit, tokens_of(chunks) + extra_tokens

        rec["bm25_k3"] = score([c for c, _ in store.search_bm25(q, 3)])
        rec["dense_k5"] = score([c for c, _ in store.search_vector_precomputed(qv, 5)])
        rec["hybrid_k5"] = score([c for c, _ in store.search_hybrid_precomputed(q, qv, 5, alpha=0.2)])

        if is_complex(q, s):
            rec["adaptive"] = score([c for c, _ in store.search_hybrid_precomputed(q, qv, 5, alpha=0.2)])
        else:
            rec["adaptive"] = score([c for c, _ in store.search_bm25(q, 1)])

        # CRAG 近似：先检索，判相关性，bad 就改写重检
        chunks = [c for c, _ in store.search_hybrid_precomputed(q, qv, 5, alpha=0.2)]
        verdict = judge(s, q, "".join(c.text for c in chunks))
        if verdict == "bad":
            sub = answerer.rewrite_query(q) or ""
            q2 = f"{q} {sub}"
            chunks = [c for c, _ in store.search_hybrid_precomputed(q2, emb.embed([q2])[0], 5, alpha=0.2)]
            rec["crag"] = score(chunks, extra_tokens=120)
        else:
            rec["crag"] = score(chunks, extra_tokens=60)

        # 我们的策略：改写门控（置信度低才改写）+ 混合
        base = store.search_hybrid_precomputed(q, qv, 3, alpha=0.2)
        s1 = base[0][1] if base else 0.0
        s2 = base[1][1] if len(base) > 1 else 0.0
        conf = (s1 - s2) / s1 if s1 > 0 else 0.0
        if conf < 0.25:
            sub = answerer.rewrite_query(q) or ""
            q2 = f"{q} {sub}"
            chunks = [c for c, _ in store.search_hybrid_precomputed(q2, emb.embed([q2])[0], 3, alpha=0.2)]
            rec["ours"] = score(chunks, extra_tokens=80)
        else:
            rec["ours"] = score([c for c, _ in base])

        rows.append({n: {"hit": rec[n][0], "tokens": rec[n][1]} for n in names})
        if i % 25 == 0:
            print(f"  {i}/{len(items)}")

    n = len(items)
    print(f"\n基线对比（n={n}, {time.perf_counter()-t0:.0f}s）")
    print(f"{'策略':<12}{'召回':>8}{'95% CI':>18}{'平均token':>12}")
    for name in names:
        hits = [r[name]["hit"] for r in rows]
        mean = sum(hits) / n
        rng = random.Random(0)
        boots = sorted(sum(rng.choice(hits) for _ in range(n)) / n for _ in range(1000))
        lo, hi = boots[25], boots[974]
        tok = sum(r[name]["tokens"] for r in rows) / n
        print(f"{name:<12}{mean:>8.4f}{f'[{lo:.3f},{hi:.3f}]':>18}{tok:>12.0f}")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    print(f"明细: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
