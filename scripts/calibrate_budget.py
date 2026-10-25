"""质量目标 → 预算 的校准协议与验证。

协议：
  1. 在拟合集（N 条题）上扫预算，得到 recall(B) 的经验曲线
  2. 用饱和指数模型 recall(B) = R_inf * (1 - exp(-B / s)) 拟合，反解出「达到目标 recall 所需预算」
  3. 把该预算用在测试集上，检查：实际 recall 是否达到目标、预算预测误差多大
  4. 重复多次随机划分，报均值与分位数

python scripts/calibrate_budget.py --index index_real.json --targets 0.80 0.85 0.90
python scripts/calibrate_budget.py --method bm25 --targets 0.80 0.85 0.90
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings  # noqa: E402
from budget_rag.pipeline import RAG  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402

BUDGETS = [30, 50, 80, 120, 180, 250, 350, 500, 700, 1000, 1500]


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def recall_at(ranked, answers, budget: int) -> tuple[int, int]:
    """返回 (是否命中, 实际 token)。"""
    used = 0
    for chunk, _ in ranked:
        used += max(1, count_tokens(chunk.text))
        text = norm(chunk.text)
        if any(norm(a) in text for a in answers):
            return 1, used
        if used >= budget:
            break
    return 0, used


def fit_curve(budgets: list[int], recalls: list[float]) -> tuple[float, float]:
    """拟合 R(B) = R_inf (1 - exp(-B/s))，返回 (R_inf, s)。用网格搜索，避免依赖 scipy。"""
    best = (0.0, 1.0, -1e9)
    for r_inf in np.arange(max(recalls) if recalls else 0.5, 1.001, 0.01):
        for s in np.logspace(0.5, 4.5, 120):
            pred = r_inf * (1 - np.exp(-np.asarray(budgets) / s))
            err = -float(np.mean((pred - np.asarray(recalls)) ** 2))
            if err > best[2]:
                best = (float(r_inf), float(s), err)
    return best[0], best[1]


def interp_recall(budgets: list[int], recalls: list[float], b: float) -> float:
    """在经验曲线上线性插值，估计预算 b 处的召回。"""
    if b <= budgets[0]:
        return recalls[0]
    for i in range(1, len(budgets)):
        if b <= budgets[i]:
            x0, x1 = budgets[i - 1], budgets[i]
            y0, y1 = recalls[i - 1], recalls[i]
            return y0 + (y1 - y0) * (b - x0) / max(1e-9, x1 - x0)
    return recalls[-1]


def escalate(pred: float, budgets: list[int], recalls: list[float], target: float,
             factor: float = 1.6, rounds: int = 3) -> float:
    """预测后回验：拟合集上估计的召回不到目标，就按比例加预算（只用拟合集，无泄漏）。"""
    b = pred
    for _ in range(rounds):
        if interp_recall(budgets, recalls, b) >= target:
            break
        b *= factor
    return b


def invert(r_inf: float, s: float, target: float) -> float:
    """达到目标 recall 所需预算；目标超过 R_inf 时返回 inf。"""
    if r_inf <= 0 or target >= r_inf:
        return math.inf
    return -s * math.log(1 - target / r_inf)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--method", default="hybrid", choices=["hybrid", "dense", "bm25"])
    ap.add_argument("--targets", type=float, nargs="*", default=[0.80, 0.85, 0.90])
    ap.add_argument("--n-fit", type=int, default=20)
    ap.add_argument("--repeats", type=int, default=30)
    ap.add_argument("--margins", type=float, nargs="*", default=[0.0, 0.03, 0.05, 0.10])
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rag = RAG(Settings.from_env())
    store = rag.store
    if args.method != "bm25":
        store.load(ROOT / args.index)
        print(f"{args.method}: {len({c.doc for c in store.chunks})} 文档 / {len(store.chunks)} 块")
    else:
        store.load(ROOT / args.index)      # BM25 也需要语料
        print(f"bm25: {len(store.chunks)} 块")

    fn = {"hybrid": store.search_hybrid, "dense": store.search_vector, "bm25": store.search_bm25}[args.method]

    # 预先算好每条题在每个预算档下的命中（命中即停，所以可取最小命中预算）
    print("预计算每题的最小命中预算…")
    hit_budget = []
    for it in items:
        ranked = fn(it["question"], 200)
        hb = math.inf
        used = 0
        for chunk, _ in ranked:
            used += max(1, count_tokens(chunk.text))
            if any(norm(a) in norm(chunk.text) for a in it["answers"]):
                hb = used
                break
            if used >= max(BUDGETS):
                break
        hit_budget.append(hb)
    hit_arr = np.asarray([b if b < math.inf else 1e9 for b in hit_budget])

    def curve_for(idx: list[int], budgets=BUDGETS) -> list[float]:
        sel = hit_arr[idx]
        return [float(np.mean(sel <= b)) for b in budgets]

    rng = random.Random(args.seed)
    results = {(t, m): {"pred": [], "achieved": [], "true_budget": []}
               for t in args.targets for m in args.margins}

    for _ in range(args.repeats):
        idx = list(range(len(items)))
        rng.shuffle(idx)
        fit_idx, test_idx = idx[: args.n_fit], idx[args.n_fit:]
        fit_rec = curve_for(fit_idx)
        r_inf, s = fit_curve(BUDGETS, fit_rec)
        # 保守修正：拟合的上限不能超过拟合集上实际观测到的最大召回（弱检索器最容易高估）
        r_inf = min(r_inf, max(fit_rec) + 0.02)
        for t in args.targets:
            for margin in args.margins:
                goal = min(t + margin, 0.999)
                pred = invert(r_inf, s, goal)
                if not math.isfinite(pred):
                    continue
                pred = escalate(pred, BUDGETS, fit_rec, t)
                test_rec = curve_for(test_idx)
                true_b = None
                for b, r in zip(BUDGETS, test_rec):
                    if r >= t:
                        true_b = b
                        break
                achieved = float(np.mean(hit_arr[test_idx] <= pred))
                results[(t, margin)]["pred"].append(pred)
                results[(t, margin)]["achieved"].append(achieved)
                if true_b:
                    results[(t, margin)]["true_budget"].append(true_b)
            continue
        for t in []:
            pred = invert(r_inf, s, t)
            if not math.isfinite(pred):
                continue
            # 测试集上真实达到该目标所需的预算（用同一组预算档估算）
            test_rec = curve_for(test_idx)
            true_b = None
            for b, r in zip(BUDGETS, test_rec):
                if r >= t:
                    true_b = b
                    break
            achieved = float(np.mean(hit_arr[test_idx] <= pred))
            results[t]["pred"].append(pred)
            results[t]["achieved"].append(achieved)
            if true_b:
                results[t]["true_budget"].append(true_b)

    print(f"\n方法 {args.method} | 拟合集 {args.n_fit} 题 | 重复 {args.repeats} 次")
    print(f"{'目标':>6}{'边际':>7}{'预测预算':>10}{'实际recall':>11}{'达标率':>8}{'真预算':>8}")
    summary = {}
    for t in args.targets:
        for m in args.margins:
            preds = results[(t, m)]["pred"]
            ach = results[(t, m)]["achieved"]
            tru = results[(t, m)]["true_budget"]
            if not preds:
                print(f"{t:>6.2f}{m:>7.2f}   不可达")
                continue
            rate = statistics.mean(1.0 if a >= t else 0.0 for a in ach)
            print(f"{t:>6.2f}{m:>7.2f}{statistics.median(preds):>10.0f}{statistics.mean(ach):>11.3f}"
                  f"{rate:>8.2f}{(statistics.median(tru) if tru else float('nan')):>8.0f}")
            summary[f"{t:.2f}|{m:.2f}"] = {
                "pred_budget_median": statistics.median(preds),
                "achieved_recall_mean": statistics.mean(ach),
                "reach_rate": rate,
                "true_budget_median": statistics.median(tru) if tru else None,
            }

    out = ROOT / "results" / f"calibration_{args.method}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
