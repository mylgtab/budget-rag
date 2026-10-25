"""二维预算：上下文 token 与检索延迟的帕累托前沿。

只测检索侧开销（查询向量化 + 打分），不含生成，避免把 LLM 延迟混进来。
每个方法给出 (平均延迟 ms, 平均 token, recall)，并标出被支配的点。

python scripts/pareto_multibudget.py --budget 300
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

from budget_rag.config import Settings  # noqa: E402
from budget_rag.pipeline import RAG  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def take(ranked, budget: int):
    out, used = [], 0
    for c, s in ranked:
        out.append((c, s))
        used += max(1, count_tokens(c.text))
        if used >= budget:
            break
    return out, used


def hit(chunks, answers) -> int:
    text = norm(" ".join(c.text for c, _ in chunks))
    return int(any(norm(a) in text for a in answers))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--index2", default="index_real_bgelarge.json")
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--index2-model", default="BAAI/bge-large-en-v1.5")
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    s = Settings.from_env()
    rag = RAG(s)
    rag.store.load(ROOT / args.index)
    store = rag.store
    print(f"题 {len(items)} | bge-m3 块 {len(store.chunks)}")

    store2 = None
    if (ROOT / args.index2).exists():
        # 关键：查询必须用与索引一致的编码器，否则向量维度相同会静默出错
        s2 = Settings.from_env()
        s2.embed_model = args.index2_model
        rag2 = RAG(s2)
        rag2.store.load(ROOT / args.index2)
        store2 = rag2.store
        print(f"bge-large 块 {len(store2.chunks)}（编码器 {s2.embed_model}）")

    rows = {}

    def record(name: str, latencies: list[float], toks: list[int], hits: list[int]):
        rows[name] = {
            "latency_ms": statistics.median(latencies),
            "tokens": statistics.mean(toks),
            "recall": statistics.mean(hits),
        }

    # BM25：零向量化开销
    lat, toks, hits = [], [], []
    for it in items:
        t0 = time.perf_counter()
        ranked = store.search_bm25(it["question"], 200)
        dt = (time.perf_counter() - t0) * 1000
        picked, used = take(ranked, args.budget)
        lat.append(dt); toks.append(used); hits.append(hit(picked, it["answers"]))
    record("BM25", lat, toks, hits)

    # bge-m3 向量 / 混合（延迟含查询向量化）
    for name, fn in (("Dense (bge-m3)", store.search_vector), ("Hybrid (bge-m3)", store.search_hybrid)):
        lat, toks, hits = [], [], []
        for it in items:
            t0 = time.perf_counter()
            ranked = fn(it["question"], 200)
            dt = (time.perf_counter() - t0) * 1000
            picked, used = take(ranked, args.budget)
            lat.append(dt); toks.append(used); hits.append(hit(picked, it["answers"]))
        record(name, lat, toks, hits)

    # bge-large 向量
    if store2 is not None:
        lat, toks, hits = [], [], []
        for it in items:
            t0 = time.perf_counter()
            ranked = store2.search_vector(it["question"], 200)
            dt = (time.perf_counter() - t0) * 1000
            picked, used = take(ranked, args.budget)
            lat.append(dt); toks.append(used); hits.append(hit(picked, it["answers"]))
        record("Dense (bge-large)", lat, toks, hits)

    # 自适应混合：token 更少，延迟不变
    lat, toks, hits = [], [], []
    for it in items:
        t0 = time.perf_counter()
        ranked = store.search_hybrid(it["question"], 10)
        if len(ranked) >= 2:
            s1, s2 = ranked[0][1], ranked[1][1]
            margin = (s1 - s2) / s1 if s1 else 0.0
        else:
            margin = 1.0
        k = 4 if margin > 0.05 else 10
        dt = (time.perf_counter() - t0) * 1000
        picked = ranked[:k]
        lat.append(dt)
        toks.append(sum(count_tokens(c.text) for c, _ in picked))
        hits.append(hit(picked, it["answers"]))
    record("Adaptive (bge-m3)", lat, toks, hits)

    print(f"\n{'方法':<20}{'检索延迟 ms':>12}{'token':>8}{'recall':>9}   帕累托")
    for name, r in sorted(rows.items(), key=lambda kv: kv[1]["latency_ms"]):
        dominated = any(
            (o["latency_ms"] <= r["latency_ms"] and o["tokens"] <= r["tokens"]
             and o["recall"] >= r["recall"] and
             (o["latency_ms"] < r["latency_ms"] or o["tokens"] < r["tokens"]))
            for k, o in rows.items() if k != name
        )
        tag = "被支配" if dominated else "★ 前沿"
        print(f"{name:<20}{r['latency_ms']:>12.0f}{r['tokens']:>8.0f}{r['recall']:>9.3f}   {tag}")

    # 两个典型 SLA 下的最优选择
    print("\n给定约束下的最优选择（回忆与成本权衡）")
    for lat_cap in (120, 400, 1000):
        ok = [(k, v) for k, v in rows.items() if v["latency_ms"] <= lat_cap]
        if not ok:
            print(f"  延迟 ≤{lat_cap}ms: 无可行方案")
            continue
        best = max(ok, key=lambda kv: (kv[1]["recall"], -kv[1]["tokens"]))
        print(f"  延迟 ≤{lat_cap}ms: {best[0]}  recall {best[1]['recall']:.3f}  token {best[1]['tokens']:.0f}")
    for tok_cap in (200, 400):
        ok = [(k, v) for k, v in rows.items() if v["tokens"] <= tok_cap]
        if not ok:
            print(f"  token ≤{tok_cap}: 无可行方案")
            continue
        best = max(ok, key=lambda kv: (kv[1]["recall"], -kv[1]["latency_ms"]))
        print(f"  token ≤{tok_cap}: {best[0]}  recall {best[1]['recall']:.3f}  延迟 {best[1]['latency_ms']:.0f}ms")

    out = ROOT / "results" / "pareto_multibudget.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
