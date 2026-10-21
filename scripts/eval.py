"""评测：Recall@k / EM / F1 / 成本 / 延迟。

python scripts/eval.py --set data/eval_set.jsonl --k 3 [--llm] [--out results]
"""

from __future__ import annotations


import argparse
import json
import re
import sys
import io

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings          # noqa: E402
from budget_rag.llm import LLMAnswerer, OfflineAnswerer  # noqa: E402
from budget_rag.pipeline import RAG             # noqa: E402

_WORD = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]")


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s.strip().lower())


def f1(pred: str, gold: str) -> float:
    p, g = _WORD.findall(norm(pred)), _WORD.findall(norm(gold))
    if not p or not g:
        return float(norm(pred) == norm(gold))
    common = 0
    gs = list(g)
    for t in p:
        if t in gs:
            gs.remove(t)
            common += 1
    if common == 0:
        return 0.0
    prec, rec = common / len(p), common / len(g)
    return 2 * prec * rec / (prec + rec)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_set.jsonl")
    ap.add_argument("--docs", default="data/sample_docs")
    ap.add_argument("--index", default="index.json")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--llm", action="store_true", help="用真实模型（需 DEEPSEEK_API_KEY）")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 条，试水用")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    settings = Settings.from_env()
    settings.top_k = args.k
    rag = RAG(settings, LLMAnswerer(settings) if args.llm else OfflineAnswerer())

    idx = ROOT / args.index
    if idx.exists():
        rag.store.load(idx)
    else:
        docs = Path(args.docs)
        rag.ingest({p.name: p.read_text(encoding="utf-8") for p in sorted(docs.glob("*.md"))})

    rows = []
    lines = [l for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        lines = lines[: args.limit]
    for line in lines:
        if not line.strip():
            continue
        item = json.loads(line)
        out = rag.query(item["question"])
        tr = out["trace"]
        golds = item["answers"]
        hit = 0.0
        if rag.store.chunks:
            st = rag.stores.get(tr.get("store", ""), rag.store)
            ctx = "".join(c.text for c in st.chunks if f"{c.doc}#{c.idx}" in tr["docs"])
            hit = float(any(norm(g) in norm(ctx) for g in golds))
        rows.append({
            "question": item["question"],
            "answer": out["answer"],
            "gold": golds[0],
            "recall@k": hit,
            "em": float(any(norm(out["answer"]) == norm(g) for g in golds)),
            "contain": float(any(
                norm(out["answer"]) and (norm(out["answer"]) in norm(g) or norm(g) in norm(out["answer"]))
                for g in golds)),
            "f1": max(f1(out["answer"], g) for g in golds),
            **tr,
        })

    n = len(rows) or 1
    summary = {
        "n": len(rows),
        f"recall@{args.k}": round(sum(r["recall@k"] for r in rows) / n, 4),
        "em": round(sum(r["em"] for r in rows) / n, 4),
        "contain": round(sum(r["contain"] for r in rows) / n, 4),
        "f1": round(sum(r["f1"] for r in rows) / n, 4),
        "cost_rmb": round(sum(r["cost_rmb"] for r in rows) / n, 6),
        "prompt_tokens": round(sum(r.get("prompt_tokens", 0) for r in rows) / n, 1),
        "completion_tokens": round(sum(r.get("completion_tokens", 0) for r in rows) / n, 1),
        "billed_pct": round(sum(1 for r in rows if r.get("billed")) / n, 3),
        "p95_latency_ms": round(sorted(r["latency_ms"] for r in rows)[max(0, int(n * 0.95) - 1)], 1),
        "path_mix": {p: sum(1 for r in rows if r["path"] == p) for p in ("cheap", "strong")},
    }

    outdir = ROOT / args.out
    outdir.mkdir(exist_ok=True)
    (outdir / "details.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["| 问题 | 路径 | Recall | F1 | 成本(元) | 延迟(ms) |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['question'][:18]} | {r['path']} | {r['recall@k']:.0f} | {r['f1']:.2f} | "
                     f"{r['cost_rmb']:.5f} | {r['latency_ms']:.0f} |")
    lines += ["", "**汇总**", "", "```json", json.dumps(summary, ensure_ascii=False, indent=2), "```"]
    (outdir / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\n明细: {outdir / 'details.json'}  汇总: {outdir / 'summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
