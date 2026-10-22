"""参数调优：dev 集选参、test 集报告，避免在测试集上调参。

python scripts/tune_params.py --tokens 300
网格：混合权重 alpha × 上下文预算 ctx_tokens
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings               # noqa: E402
from budget_rag.embedding import HashEmbedder, OpenAIEmbedder  # noqa: E402
from budget_rag.metrics import norm                  # noqa: E402
from budget_rag.store import Store                   # noqa: E402
from budget_rag.tokens import count_tokens            # noqa: E402

ALPHAS = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
BUDGETS = [100, 200, 300, 500, 800]


def take_budget(hits, budget: int) -> str:
    ctx, used = [], 0
    for chunk, _ in hits:
        ctx.append(chunk.text)
        used += count_tokens(chunk.text)
        if used >= budget:
            break
    return "".join(ctx)


def recall_at(store: Store, items: list[dict], qvecs: list[list[float]], alpha: float,
              budget: int) -> float:
    hit = 0
    for idx, item in enumerate(items):
        if alpha >= 1.0:
            hits = store.search_bm25(item["question"], len(store.chunks))
        elif alpha <= 0.0:
            hits = store.search_vector_precomputed(qvecs[idx], len(store.chunks))
        else:
            hits = store.search_hybrid_precomputed(item["question"], qvecs[idx], len(store.chunks), alpha=alpha)
        ctx = take_budget(hits, budget)
        hit += any(norm(g) in norm(ctx) for g in item["answers"])
    return hit / (len(items) or 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--dev-ratio", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="results/tune_report.md")
    args = ap.parse_args()

    s = Settings.from_env()
    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()]
    rng = random.Random(args.seed)
    rng.shuffle(items)
    n_dev = int(len(items) * args.dev_ratio)
    dev, test = items[:n_dev], items[n_dev:]

    if s.embed_base and s.embed_key:
        emb = OpenAIEmbedder(s.embed_base, s.embed_model, s.embed_key)
        kind = f"real/{s.embed_model}"
    else:
        emb = HashEmbedder(s.embed_dim)
        kind = "hash"
    store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))

    cache = ROOT / ".cache" / "qvec_all.json"
    cache.parent.mkdir(exist_ok=True)
    if cache.exists():
        qvec_all = json.loads(cache.read_text(encoding="utf-8"))
        if len(qvec_all) < len(items):
            qvec_all = []
    else:
        qvec_all = []
    if not qvec_all:
        qs = [it["question"] for it in items]
        qvec_all = []
        for i in range(0, len(qs), 32):
            qvec_all.extend(emb.embed(qs[i:i + 32]))
        cache.write_text(json.dumps(qvec_all), encoding="utf-8")

    print(f"embedder={kind}  总量={len(items)}  dev={len(dev)}  test={len(test)}")

    rows = []
    for a in ALPHAS:
        for b in BUDGETS:
            rows.append((a, b, 0.0))
    best = None
    print(f"\n{'alpha':>6}{'budget':>8}{'dev recall':>12}")
    for i, (a, b, _) in enumerate(rows):
        r = recall_at(store, dev, qvec_all[: len(dev)], a, b)
        rows[i] = (a, b, r)
        if best is None or r > best[2]:
            best = (a, b, r)
    for a, b, r in rows:
        mark = "  ← best" if (a, b) == (best[0], best[1]) else ""
        print(f"{a:>6.2f}{b:>8}{r:>12.4f}{mark}")

    test_r = recall_at(store, test, qvec_all[len(dev):], best[0], best[1])
    baseline_r = recall_at(store, test, qvec_all[len(dev):], 0.5, 300)

    print(f"\n选定 alpha={best[0]} budget={best[1]}（dev {best[2]:.4f}）")
    print(f"test 召回：调参后 {test_r:.4f}  vs  旧默认(alpha=0.5,budget=300) {baseline_r:.4f}")

    report = [
        "# 参数调优（dev/test 分离）",
        "",
        f"- embedder：`{kind}`",
        f"- 划分：dev {len(dev)} / test {len(test)}（seed={args.seed}）",
        f"- 网格：alpha {ALPHAS} × budget {BUDGETS}",
        "",
        "## dev 集结果",
        "",
        "| alpha \\ budget | " + " | ".join(str(b) for b in BUDGETS) + " |",
        "|---|" + "---|" * len(BUDGETS),
    ]
    grid = {(a, b): r for a, b, r in rows}
    for a in ALPHAS:
        report.append(f"| {a} | " + " | ".join(f"{grid[(a, b)]:.3f}" for b in BUDGETS) + " |")
    report += [
        "",
        "## 选择与验证",
        "",
        f"- dev 最优：**alpha={best[0]}, budget={best[1]}**（dev Recall {best[2]:.4f}）",
        f"- test Recall：**{test_r:.4f}**",
        f"- 旧默认（alpha=0.5, budget=300）在 test 上：{baseline_r:.4f}",
        f"- 提升：**{test_r - baseline_r:+.4f}**",
        "",
        "> 只在 dev 上选参，test 只用于最终报告，避免调参泄漏。",
    ]
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\n报告: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
