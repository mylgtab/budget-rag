"""学习型路由器 vs 启发式门控。

标签自动生成（不需要人工）：对每道题找出「能召回答案的最小动作」
  0 = BM25 取 1 块就够
  1 = 要混合取 5 块
  2 = 只有改写后才够
  3 = 都找不到

然后用问题文本训练分类器（TF-IDF + 逻辑回归），交叉验证后比较三种策略：
  fixed     ：全部走混合 k=5
  heuristic ：top1/top2 分数间隔 < 0.25 才改写
  learned   ：按预测类别选动作
  oracle    ：按真实类别选动作（上界）

python scripts/learned_router.py --limit 500
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings                # noqa: E402
from budget_rag.embedding import HashEmbedder, build_embedder  # noqa: E402
from budget_rag.llm import LLMAnswerer                # noqa: E402
from budget_rag.metrics import norm                   # noqa: E402
from budget_rag.store import Store                    # noqa: E402
from budget_rag.tokens import count_tokens             # noqa: E402


def hit(chunks, golds) -> int:
    text = "".join(c.text for c in chunks)
    return int(any(norm(g) in norm(text) for g in golds))


def toks(chunks) -> int:
    return sum(count_tokens(c.text) for c in chunks)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--embed", default="real", choices=["hash", "real"])
    ap.add_argument("--out", default="results/learned_router.json")
    args = ap.parse_args()

    s = Settings.from_env()
    if not s.api_key:
        print("需要 DEEPSEEK_API_KEY（生成标签要改写）")
        return 1
    emb = build_embedder(s) if args.embed == "real" else HashEmbedder(s.embed_dim)
    store = Store(emb, s.chunk_size, s.chunk_overlap, "sentence")
    for p in sorted((ROOT / "data" / "sample_docs").glob("*.md")):
        store.add_document(p.name, p.read_text(encoding="utf-8"))
    answerer = LLMAnswerer(s)

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    rows = []
    for i, item in enumerate(items, 1):
        q, golds = item["question"], item["answers"]
        qv = emb.embed([q])[0]
        k1 = [c for c, _ in store.search_bm25(q, 1)]
        h5p = store.search_hybrid_precomputed(q, qv, 5, alpha=0.2)
        h5 = [c for c, _ in h5p]
        conf = ((h5p[0][1] - h5p[1][1]) / h5p[0][1]) if len(h5p) > 1 and h5p[0][1] > 0 else 0.0

        sub = answerer.rewrite_query(q) or ""
        q2 = f"{q} {sub}"
        rwp = store.search_hybrid_precomputed(q2, emb.embed([q2])[0], 5, alpha=0.2)
        rw = [c for c, _ in rwp]
        rw_tokens = toks(rw) + 80

        h1 = hit(k1, golds)
        h5h = hit(h5, golds)
        hr = hit(rw, golds)
        label = 0 if h1 else (1 if h5h else (2 if hr else 3))
        rows.append({"q": q, "label": label, "conf": conf, "gold": golds[0],
                     "k1_tok": toks(k1), "h5_tok": toks(h5), "rw_tok": rw_tokens,
                     "k1_hit": h1, "h5_hit": h5h, "rw_hit": hr})
        if i % 50 == 0:
            print(f"  {i}/{len(items)}")

    y = np.array([r["label"] for r in rows])
    X = [r["q"] for r in rows]
    print(f"\nn={len(rows)}  标签分布: {np.bincount(y, minlength=4).tolist()}（0=易 1=中 2=难 3=全失败）")

    clf = make_pipeline(TfidfVectorizer(analyzer="char_wb", ngram_range=(1, 3), min_df=1),
                        LogisticRegression(max_iter=1000, C=4.0))
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)
    pred = np.zeros_like(y)
    for tr, te in skf.split(X, y):
        clf.fit([X[i] for i in tr], y[tr])
        pred[te] = clf.predict([X[i] for i in te])

    acc = float((pred == y).mean())
    print(f"分类器 5 折准确率: {acc:.4f}")

    # 策略评估
    def policy(action_of):
        hit_n = tok_sum = 0
        for r, a in zip(rows, action_of):
            if a == 0:
                hit_n += r["k1_hit"]
                tok_sum += r["k1_tok"]
            elif a == 1:
                hit_n += r["h5_hit"]
                tok_sum += r["h5_tok"]
            else:
                hit_n += r["rw_hit"]
                tok_sum += r["rw_tok"] or r["h5_tok"]
        return hit_n / len(rows), tok_sum / len(rows)

    mapping = {0: 0, 1: 1, 2: 2, 3: 2}
    strategies = {
        "fixed(全部混合k5)": [1] * len(rows),
        "heuristic(间隔门控)": [2 if r["conf"] < 0.25 else 1 for r in rows],
        "learned(分类器)": [mapping[int(p)] for p in pred],
        "oracle(真实标签)": [mapping[int(t)] for t in y],
    }

    print(f"\n{'策略':<20}{'召回':>8}{'平均token':>12}")
    out = {}
    for name, acts in strategies.items():
        r, t = policy(acts)
        out[name] = {"recall": r, "tokens": t}
        print(f"{name:<20}{r:>8.4f}{t:>12.0f}")

    (ROOT / "results" / "router_rows.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    (ROOT / args.out).write_text(json.dumps({"n": len(rows), "acc": acc,
                                             "label_dist": np.bincount(y, minlength=4).tolist(),
                                             "strategies": out}, ensure_ascii=False), encoding="utf-8")
    print(f"\n明细: {ROOT / args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
