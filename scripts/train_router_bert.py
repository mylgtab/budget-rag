"""用 BERT 微调路由器，替代 TF-IDF 版本。

输入 results/router_rows.json（learned_router.py 生成），5 折交叉验证，
输出准确率与三种策略的召回/成本。

python scripts/train_router_bert.py --model google-bert/bert-base-chinese --epochs 4
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.model_selection import StratifiedKFold
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
saved = {}


class QSet(Dataset):
    def __init__(self, texts, labels, tok, max_len):
        self.enc = tok(texts, truncation=True, max_length=max_len, padding=True)
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, i):
        item = {k: torch.tensor(v[i]) for k, v in self.enc.items()}
        item["labels"] = torch.tensor(self.labels[i])
        return item


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", default="results/router_rows.json")
    ap.add_argument("--model", default="google-bert/bert-base-chinese")
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--max-len", type=int, default=64)
    ap.add_argument("--out", default="results/router_bert.json")
    args = ap.parse_args()

    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    rows = json.loads((ROOT / args.rows).read_text(encoding="utf-8"))
    X = [r["q"] for r in rows]
    y = np.array([r["label"] for r in rows])
    print(f"n={len(X)} 标签分布={np.bincount(y, minlength=4).tolist()}")

    tok = AutoTokenizer.from_pretrained(args.model)
    pred = np.zeros_like(y)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)

    for fold, (tr, te) in enumerate(skf.split(X, y), 1):
        model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=4)
        opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
        ds = QSet([X[i] for i in tr], y[tr].tolist(), tok, args.max_len)
        dl = DataLoader(ds, batch_size=args.batch, shuffle=True)
        model.train()
        for ep in range(args.epochs):
            total = 0.0
            for batch in dl:
                opt.zero_grad()
                out = model(**batch)
                out.loss.backward()
                opt.step()
                total += float(out.loss)
            print(f"  fold {fold} epoch {ep+1} loss={total/max(1,len(dl)):.4f}")

        model.eval()
        te_ds = QSet([X[i] for i in te], y[te].tolist(), tok, args.max_len)
        te_dl = DataLoader(te_ds, batch_size=32)
        got = []
        with torch.no_grad():
            for batch in te_dl:
                logits = model(**batch).logits
                got.extend(logits.argmax(-1).tolist())
        pred[te] = np.array(got)

    acc = float((pred == y).mean())
    print(f"\nBERT 5 折准确率: {acc:.4f}（TF-IDF 基线 0.7467）")

    def policy(action_of):
        hit = tok_sum = 0
        for r, a in zip(rows, action_of):
            if a == 0:
                hit += r["k1_hit"]
                tok_sum += r["k1_tok"]
            elif a == 1:
                hit += r["h5_hit"]
                tok_sum += r["h5_tok"]
            else:
                hit += r["rw_hit"]
                tok_sum += r["rw_tok"] or r["h5_tok"]
        return hit / len(rows), tok_sum / len(rows)

    mapping = {0: 0, 1: 1, 2: 2, 3: 2}
    print(f"\n{'策略':<20}{'召回':>8}{'平均token':>12}")
    out = {}
    for name, acts in {
        "fixed": [1] * len(rows),
        "heuristic": [2 if r["conf"] < 0.25 else 1 for r in rows],
        "bert": [mapping[int(p)] for p in pred],
        "oracle": [mapping[int(t)] for t in y],
    }.items():
        r, t = policy(acts)
        out[name] = {"recall": r, "tokens": t}
        print(f"{name:<20}{r:>8.4f}{t:>12.0f}")

    (ROOT / args.out).write_text(json.dumps({"acc": acc, "strategies": out,
                                             "dist": np.bincount(y, minlength=4).tolist()},
                                            ensure_ascii=False), encoding="utf-8")
    print(f"\n结果: {ROOT / args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
