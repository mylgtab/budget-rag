"""用官方标签训练出的复杂度分类器，在我们的 301 题上做 Adaptive-RAG 式路由并评测。

路由（忠于 Adaptive-RAG）：
  A（简单）  → 不检索
  B（单跳）  → 混合检索 top-5
  C（多跳）  → 混合检索 top-10

另给一个「adapted」变体：A → top-1（因为本文语料每题都需要证据），便于分离
「分类错误」与「策略不匹配」两种损失。

python scripts/official_route_eval.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings  # noqa: E402
from budget_rag.pipeline import RAG  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402

MODEL = ROOT / "models" / "complexity-t5"


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--model", default=str(MODEL))
    args = ap.parse_args()

    import torch
    import transformers
    from transformers import T5ForConditionalGeneration, T5Tokenizer

    if int(transformers.__version__.split(".")[0]) >= 5:
        raise SystemExit("需 transformers 4.x")

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    tok = T5Tokenizer(vocab_file=str(Path(args.model) / "spiece.model"), model_max_length=512, extra_ids=0)
    letter_ids = {tok.encode(c, add_special_tokens=False)[0]: c for c in "ABC"}
    model = T5ForConditionalGeneration.from_pretrained(args.model)
    model.eval()

    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / args.index)
    store = rag.store

    print(f"题 {len(items)}")
    preds = []
    with torch.no_grad():
        for i in range(0, len(items), 32):
            chunk = items[i:i + 32]
            enc = tok([x["question"] for x in chunk], truncation=True, max_length=96,
                      padding=True, return_tensors="pt")
            gen = model.generate(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"],
                                 max_new_tokens=1)
            first = gen[:, 1].tolist() if gen.shape[1] > 1 else gen[:, 0].tolist()
            preds += [letter_ids.get(g, "?") for g in first]
    print("预测分布:", dict(Counter(preds)))

    def evaluate(kmap):
        hits, toks, budget_hits = 0, 0, []
        for it, c in zip(items, preds):
            k = kmap[c]
            if k == 0:
                budget_hits.append(0)
                continue
            used, hit = 0, 0
            for chunk, _ in store.search_hybrid(it["question"], k):
                used += max(1, count_tokens(chunk.text))   # 整个上下文都计入，不提前停
                if any(norm(a) in norm(chunk.text) for a in it["answers"]):
                    hit = 1
            hits += hit
            toks += used
            budget_hits.append(hit)
        return hits / len(items), toks / len(items)

    faithful = {"A": 0, "B": 5, "C": 10}
    adapted = {"A": 1, "B": 5, "C": 10}
    r1, t1 = evaluate(faithful)
    r2, t2 = evaluate(adapted)
    print(f"忠实路由（A=不检索）  recall {r1:.3f} | 平均 token {t1:.0f}")
    print(f"适配路由（A=top-1）   recall {r2:.3f} | 平均 token {t2:.0f}")

    out = ROOT / "results" / "official_route_eval.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        "n": len(items), "class_distribution": dict(Counter(preds)),
        "faithful": {"recall": r1, "tokens": t1},
        "adapted": {"recall": r2, "tokens": t2},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("写入", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
