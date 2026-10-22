"""验证预算分配理论：边际收益递减 + 贪心 vs 暴力最优。

动作集（检索层面，质量用「答案片段是否被召回」）：
  bm25_k1 / bm25_k3 / bm25_k6 / hybrid_k3 / rewrite_k3

每个动作给出一个块集合；子集的质量 = 各动作块文本合并后是否含答案。
成本 = 各动作上下文 token 之和（保守近似，忽略重叠）+ 改写调用的等效 token。

python scripts/budget_opt.py --limit 100 --embed real
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings                # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.llm import LLMAnswerer                # noqa: E402
from budget_rag.metrics import norm                   # noqa: E402
from budget_rag.store import Store                    # noqa: E402
from budget_rag.tokens import count_tokens             # noqa: E402

ACTIONS = ["bm25_k1", "bm25_k3", "bm25_k6", "hybrid_k3", "rewrite_k3"]
EXTRA_TOKENS = {"rewrite_k3": 80}      # 一次改写调用的等效 token


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--embed", default="hash", choices=["hash", "real"])
    args = ap.parse_args()

    s = Settings.from_env()
    emb = build_embedder(s) if args.embed == "real" else HashEmbedder(s.embed_dim)
    store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    answerer = LLMAnswerer(s) if s.api_key else None

    texts: dict[str, list[str]] = {a: [] for a in ACTIONS}
    toks: dict[str, list[int]] = {a: [] for a in ACTIONS}
    hits: dict[str, int] = {a: 0 for a in ACTIONS}

    for i, item in enumerate(items, 1):
        q, golds = item["question"], item["answers"]
        qv = emb.embed([q])[0]

        def pack(chunks):
            return "".join(c.text for c in chunks), sum(count_tokens(c.text) for c in chunks)

        sets = {
            "bm25_k1": store.search_bm25(q, 1),
            "bm25_k3": store.search_bm25(q, 3),
            "bm25_k6": store.search_bm25(q, 6),
            "hybrid_k3": store.search_hybrid_precomputed(q, qv, 3, alpha=0.2),
        }
        sub = answerer.rewrite_query(q) if answerer else ""
        q2 = f"{q} {sub}" if sub else q
        sets["rewrite_k3"] = store.search_hybrid_precomputed(q2, emb.embed([q2])[0], 3, alpha=0.2)

        for a in ACTIONS:
            text, t = pack([c for c, _ in sets[a]])
            texts[a].append(text)
            toks[a].append(t + EXTRA_TOKENS.get(a, 0))
            hits[a] += int(any(norm(g) in norm(text) for g in golds))

        if i % 25 == 0:
            print(f"  {i}/{len(items)}")

    n = len(items)
    print(f"\n单动作（n={n}）")
    for a in ACTIONS:
        print(f"  {a:<12} recall={hits[a]/n:.4f}  tokens={sum(toks[a])/n:7.0f}")

    # 所有非空子集
    table = []
    for r in range(1, len(ACTIONS) + 1):
        for sub in itertools.combinations(ACTIONS, r):
            q_hit = 0
            cost = 0.0
            for idx, item in enumerate(items):
                merged = "".join(texts[a][idx] for a in sub)
                q_hit += int(any(norm(g) in norm(merged) for g in item["answers"]))
                cost += sum(toks[a][idx] for a in sub)
            table.append({"subset": sub, "quality": q_hit / n, "cost": cost / n})

    table.sort(key=lambda r: (r["cost"], -r["quality"]))

    # 贪心：按 边际收益/成本 排序
    chosen: list[str] = []
    remaining = set(ACTIONS)
    q_cur, c_cur = 0.0, 0.0
    path = []
    while remaining:
        best = None
        for a in remaining:
            trial = tuple(chosen + [a])
            row = next(r for r in table if set(r["subset"]) == set(trial))
            dq = row["quality"] - q_cur
            dc = row["cost"] - c_cur
            ratio = dq / dc if dc > 0 else 0.0
            if best is None or ratio > best[2]:
                best = (a, row, ratio)
        a, row, ratio = best
        chosen.append(a)
        remaining.discard(a)
        path.append((a, row["quality"], row["cost"], ratio))
        q_cur, c_cur = row["quality"], row["cost"]

    print("\n贪心路径（按 边际收益/成本 降序）")
    print(f"{'动作':<14}{'质量':>8}{'成本':>8}{'边际收益/成本':>14}")
    prev_q = prev_c = 0.0
    for a, q, c, ratio in path:
        print(f"{a:<14}{q:>8.4f}{c:>8.0f}{ratio:>14.4f}")
        prev_q, prev_c = q, c

    # 递减检验
    ratios = [r for _, _, _, r in path]
    print(f"\n边际收益/成本序列: {[round(x, 4) for x in ratios]}")
    print(f"A1（递减）成立: {all(ratios[i] >= ratios[i+1] - 1e-9 for i in range(len(ratios)-1))}")

    # 贪心 vs 暴力
    print("\n贪心 vs 暴力最优（同成本上限）")
    print(f"{'预算':>8}{'贪心':>8}{'最优':>8}{'差距':>8}")
    for budget in (60, 120, 200, 300, 500):
        feasible = [r for r in table if r["cost"] <= budget]
        if not feasible:
            continue
        best_q = max(r["quality"] for r in feasible)
        greedy_q = 0.0
        for a, q, c, _ in path:
            if c <= budget:
                greedy_q = max(greedy_q, q)
        print(f"{budget:>8}{greedy_q:>8.4f}{best_q:>8.4f}{best_q - greedy_q:>8.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
