"""顺序/分组相关成本下的预算分配：打折后贪心还成不成立？

成本模型：
    同一文档的第一块按全价 p 计费，后续块按 d·p 计费（d 为缓存/前缀复用折扣）。
    于是 cost(S) 不再是「每块独立相加」，而是依赖「这篇文档此前取过几块」。

理论后果：
    A2（成本可加）被破坏。Khuller 等人的 (1-1/e)/2 与跨档恢复 1-1/e 都建立在可加成本上；
    一旦成本随选择变化，贪心的近似保证不再自动成立。

实验：
    对每道题，只在 top-8 候选块上做（2^8 = 256 个子集可穷举），比较
      ① 真成本贪心（按收益/真实边际成本排序）
      ② 朴素贪心（按收益/token 排序，忽略折扣，先取再算钱）
      ③ 穷举最优
    指标：最优率、平均召回差、预算超支率。

python scripts/order_dependent_cost.py --discounts 1.0 0.7 0.5 0.3
"""

from __future__ import annotations

import argparse
import json
import itertools
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings  # noqa: E402
from budget_rag.pipeline import RAG  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402

TOP = 12


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def set_cost(subset: list[int], chunks: list, discount: float) -> float:
    """按「同文档首块全价、后续打折」计算真实成本。"""
    seen: dict[str, int] = {}
    total = 0.0
    for i in subset:
        c = chunks[i]
        toks = max(1, count_tokens(c.text))
        if seen.get(c.doc, 0) == 0:
            total += toks
        else:
            total += toks * discount
        seen[c.doc] = seen.get(c.doc, 0) + 1
    return total


def set_hit(subset: list[int], chunks: list, answers) -> int:
    text = norm(" ".join(chunks[i].text for i in subset))
    return int(any(norm(a) in text for a in answers))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--discounts", type=float, nargs="*", default=[1.0, 0.7, 0.5, 0.3])
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / args.index)
    store = rag.store

    print(f"题 {len(items)} | 预算 {args.budget} | 每题候选 {TOP}（穷举 2^{TOP} = 4096）")
    ranked = [store.search_hybrid(it["question"], TOP)[:TOP] for it in items]
    chunks = [[c for c, _ in r] for r in ranked]

    repeat = sum(1 for cs in chunks if len({c.doc for c in cs}) < len(cs)) / max(1, len(chunks))
    print(f"候选里出现同文档多块的题占比：{repeat*100:.0f}%")

    rows = []
    for d in args.discounts:
        best_hit, greedy_hit, naive_hit = [], [], []
        greedy_opt, over_budget = 0, 0
        for it, cs in zip(items, chunks):
            n = len(cs)
            subsets = []
            for k in range(n + 1):
                for comb in itertools.combinations(range(n), k):
                    cost = set_cost(list(comb), cs, d)
                    if cost <= args.budget:
                        subsets.append((set_hit(list(comb), cs, it["answers"]), -cost, comb))
            if not subsets:
                continue
            opt_hit = max(s[0] for s in subsets)
            # 真成本贪心：每次挑「命中增量/真实边际成本」最高的块
            chosen: list[int] = []
            cur = 0
            while True:
                best = None
                for i in range(n):
                    if i in chosen:
                        continue
                    cand = chosen + [i]
                    cost = set_cost(cand, cs, d)
                    if cost > args.budget:
                        continue
                    gain = set_hit(cand, cs, it["answers"]) - set_hit(chosen, cs, it["answers"])
                    key = (gain / max(1e-6, cost - cur), -cost)
                    if best is None or key > best[0]:
                        best = (key, i, cost)
                if best is None or best[0][0] <= 0:
                    break
                chosen.append(best[1])
                cur = best[2]
            g_hit = set_hit(chosen, cs, it["answers"])
            # 朴素贪心：按 token 计费（忽略折扣）排序取块，最后才结算
            naive, spent = [], 0
            for i in range(n):                      # 分数顺序
                toks = max(1, count_tokens(cs[i].text))
                if spent + toks > args.budget:
                    break
                naive.append(i)
                spent += toks
            real = set_cost(naive, cs, d)
            if real > args.budget * 1.001:
                over_budget += 1
            n_hit = set_hit(naive, cs, it["answers"])
            best_hit.append(opt_hit)
            greedy_hit.append(g_hit)
            naive_hit.append(n_hit)
            if g_hit >= opt_hit:
                greedy_opt += 1
        n = len(best_hit)
        print(f"\n折扣 d={d:.1f}")
        print(f"  穷举最优平均召回 {statistics.mean(best_hit):.3f} | 真成本贪心 {statistics.mean(greedy_hit):.3f} "
              f"| 朴素贪心 {statistics.mean(naive_hit):.3f}")
        print(f"  贪心达到最优的题数 {greedy_opt}/{n} ({greedy_opt/n*100:.0f}%) | 朴素贪心超支 {over_budget}/{n}")
        rows.append({"discount": d, "optimal": statistics.mean(best_hit),
                     "greedy": statistics.mean(greedy_hit), "naive": statistics.mean(naive_hit),
                     "greedy_optimal_rate": greedy_opt / n, "naive_over_budget_rate": over_budget / n})

    out = ROOT / "results" / "order_dependent_cost.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
