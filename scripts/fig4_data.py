"""为图 4 计算预算-召回曲线（三个检索器），存 results/calibration_curves.json。

python scripts/fig4_data.py
"""

from __future__ import annotations

import json
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


def min_hit_budget(ranked, answers, cap: int) -> float:
    used = 0
    for chunk, _ in ranked:
        used += max(1, count_tokens(chunk.text))
        if any(norm(a) in norm(chunk.text) for a in answers):
            return used
        if used >= cap:
            break
    return float("inf")


def main() -> int:
    items = [json.loads(ln) for ln in (ROOT / "data" / "eval_real.jsonl").read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    s = Settings.from_env()
    rag = RAG(s)
    rag.store.load(ROOT / "index_real.json")
    store = rag.store

    s2 = Settings.from_env()
    s2.embed_model = "BAAI/bge-large-en-v1.5"
    rag2 = RAG(s2)
    rag2.store.load(ROOT / "index_real_bgelarge.json")
    store2 = rag2.store

    out = {}
    setups = [("BM25", store.search_bm25), ("Dense (bge-m3)", store.search_vector),
              ("Hybrid (bge-m3)", store.search_hybrid)]
    for name, fn in setups:
        hb = []
        for it in items:
            hb.append(min_hit_budget(fn(it["question"], 200), it["answers"], max(BUDGETS)))
        arr = np.asarray(hb)
        out[name] = [float(np.mean(arr <= b)) for b in BUDGETS]

    hb = []
    for it in items:
        hb.append(min_hit_budget(store2.search_vector(it["question"], 200), it["answers"], max(BUDGETS)))
    arr = np.asarray(hb)
    out["Dense (bge-large)"] = [float(np.mean(arr <= b)) for b in BUDGETS]

    payload = {"budgets": BUDGETS, "curves": out}
    dest = ROOT / "results" / "calibration_curves.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in out.items():
        print(f"{k:<20}" + " ".join(f"{x:.3f}" for x in v))
    print(f"\n写入 {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
