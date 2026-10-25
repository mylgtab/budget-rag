"""用官方 released silver 标签训练 Adaptive-RAG 式复杂度分类器（T5 seq2seq，手写训练循环）。

对齐官方格式：输入是**纯问题**（无前缀），输出单个字母 A/B/C。
官方用 T5-large；本脚本默认 t5-small（CPU 可训），规模差异在论文附录如实标注。

必须在 transformers 4.x 下运行（5.x 的 T5Tokenizer 不支持 spiece.model，会把字母判成 unk）：
  D:\\AAAAAgongju\\venvs\\t5train\\Scripts\\python.exe scripts/train_complexity_classifier.py

评估按 token id 比对（不依赖 decode），避免子词边界干扰。
"""

from __future__ import annotations

import argparse
import json
import random
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(r"D:\AAAAAgongju\third_party\Adaptive-RAG\_extract\classifier\data\musique_hotpot_wiki2_nq_tqa_sqd")
LOCAL = ROOT / "models" / "t5-small-local"
OUT = ROOT / "models" / "complexity-t5"


def load(p: Path) -> list[dict]:
    return json.loads(p.read_text(encoding="utf-8"))


def batches(rows, bs, tok, max_len=96):
    for i in range(0, len(rows), bs):
        chunk = rows[i:i + bs]
        enc = tok([r["question"] for r in chunk], truncation=True, max_length=max_len,
                  padding=True, return_tensors="pt")
        lab = tok([r["answer"] for r in chunk], padding=True, return_tensors="pt")
        labels = lab["input_ids"].clone()
        labels[labels == tok.pad_token_id] = -100
        yield enc["input_ids"], enc["attention_mask"], labels


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=str(LOCAL))
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    import torch
    import transformers
    from transformers import T5ForConditionalGeneration, T5Tokenizer

    if int(transformers.__version__.split(".")[0]) >= 5:
        raise SystemExit("请在 transformers 4.x 环境运行（见文件头注释）")

    train = load(DATA / "gpt" / "binary_silver" / "train.json")
    valid = load(DATA / "gpt" / "silver" / "valid.json")
    random.Random(7).shuffle(train)
    random.Random(7).shuffle(valid)
    if args.limit:
        train = train[: args.limit]
        valid = valid[: min(1000, args.limit // 2)]
    print(f"train {len(train)} / valid {len(valid)}")
    print("labels:", dict(Counter(r["answer"] for r in train)))

    model_dir = Path(args.model)
    tok = T5Tokenizer(vocab_file=str(model_dir / "spiece.model"), model_max_length=512, extra_ids=0)
    print("字母 token id:", {c: tok.encode(c, add_special_tokens=False)[0] for c in "ABC"})
    model = T5ForConditionalGeneration.from_pretrained(str(model_dir))
    model.train()

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    t0, step, losses = time.time(), 0, []
    for ep in range(args.epochs):
        for ids, mask, labels in batches(train, args.batch, tok):
            out = model(input_ids=ids, attention_mask=mask, labels=labels)
            loss = out.loss
            loss.backward()
            opt.step()
            opt.zero_grad()
            step += 1
            losses.append(float(loss))
            if step % 40 == 0:
                print(f"  step {step} loss {sum(losses[-40:]) / 40:.4f} ({time.time() - t0:.0f}s)")
        print(f"epoch {ep + 1} done, {time.time() - t0:.0f}s")

    # 评估：生成一个 token，直接比对字母 id
    letter_ids = {tok.encode(c, add_special_tokens=False)[0]: c for c in "ABC"}
    model.eval()
    ok, cursor = 0, 0
    with torch.no_grad():
        for ids, mask, _ in batches(valid, args.batch * 2, tok):
            chunk = valid[cursor: cursor + len(ids)]
            cursor += len(ids)
            gen = model.generate(input_ids=ids, attention_mask=mask, max_new_tokens=1)
            first = gen[:, 1].tolist() if gen.shape[1] > 1 else gen[:, 0].tolist()
            ok += sum(1 for g, r in zip(first, chunk)
                      if letter_ids.get(g) == r["answer"].upper())
    acc = ok / max(1, len(valid))
    print(f"\n验证集准确率 {acc:.4f}（{ok}/{len(valid)}）")

    Path(args.out).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.out)
    tok.save_pretrained(args.out)
    (ROOT / "results" / "official_classifier.json").write_text(json.dumps({
        "base_model": "t5-small (official uses T5-large)",
        "epochs": args.epochs, "n_train": len(train), "n_valid": len(valid),
        "accuracy": acc, "labels": dict(Counter(r["answer"] for r in train)),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("模型已保存:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
