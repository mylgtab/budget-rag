"""句级索引 vs 固定块：在 301 题上只测混合检索，结果单独落盘（不覆盖主表）。

python scripts/sentence_index_eval.py
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings  # noqa: E402
from budget_rag.pipeline import RAG  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def evaluate(items, store, k: int | None = None, budget: int | None = None):
    hits, toks = [], []
    for it in items:
        used, hit = 0, 0
        for chunk, _ in store.search_hybrid(it["question"], k or 50):
            used += max(1, count_tokens(chunk.text))
            if any(norm(a) in norm(chunk.text) for a in it["answers"]):
                hit = 1
            if budget is not None and used >= budget:
                break
        hits.append(hit)
        toks.append(used)
    return statistics.mean(hits), statistics.mean(toks)


def main() -> int:
    items = [json.loads(ln) for ln in (ROOT / "data" / "eval_real.jsonl").read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rows = {}
    for name, index in (("sentence", "index_real_sentence.json"), ("fixed", "index_real.json")):
        rag = RAG(Settings.from_env())
        rag.store.load(ROOT / index)
        r300, t300 = evaluate(items, rag.store, budget=300)
        r8, t8 = evaluate(items, rag.store, k=8)
        rows[name] = {"budget300": {"recall": r300, "tokens": t300},
                      "k8": {"recall": r8, "tokens": t8},
                      "chunks": len(rag.store.chunks)}
        print(f"{name:<9} chunks {len(rag.store.chunks):>6} | budget300 {r300:.3f}@{t300:.0f} | k8 {r8:.3f}@{t8:.0f}")

    out = ROOT / "results" / "sentence_index_eval.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print("写入", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
