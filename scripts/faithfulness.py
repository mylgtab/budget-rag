"""忠实度评估：答案是否真的被检索到的资料支持（而不是模型自己编的）。

做法：跑 RAG 拿到答案 + 上下文，再让裁判模型判定。
python scripts/faithfulness.py --limit 100
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings          # noqa: E402
from budget_rag.llm import LLMAnswerer          # noqa: E402
from budget_rag.metrics import contain, em, f1  # noqa: E402
from budget_rag.pipeline import RAG             # noqa: E402

JUDGE = """判断「答案」是否被「资料」支持。

只输出 JSON：{{"verdict": "supported|partial|unsupported", "reason": "一句话"}}
- supported：资料里能直接找到答案的依据
- partial：资料只支持一部分，或需要推断
- unsupported：资料里没有依据，答案可能是编的

资料：
{ctx}

问题：{q}
答案：{a}
"""


def _post(settings: Settings, prompt: str) -> dict:
    body = json.dumps({
        "model": settings.llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 120,
    }).encode()
    req = urllib.request.Request(
        f"{settings.llm_base}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {settings.api_key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
            return {"text": data["choices"][0]["message"]["content"],
                    "tokens": int((data.get("usage") or {}).get("total_tokens", 0))}
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return {"text": "", "tokens": 0}


def parse_verdict(text: str) -> str:
    t = text.lower()
    for key in ("unsupported", "partial", "supported"):
        if key in t:
            return key
    return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--docs", default="data/sample_docs")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--out", default="results/faithfulness.json")
    args = ap.parse_args()

    s = Settings.from_env()
    if not s.api_key:
        print("需要 DEEPSEEK_API_KEY")
        return 1

    rag = RAG(s, LLMAnswerer(s))
    rag.ingest({p.name: p.read_text(encoding="utf-8") for p in sorted((ROOT / args.docs).glob("*.md"))})

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    rows = []
    t0 = time.perf_counter()
    for i, item in enumerate(items, 1):
        out = rag.query(item["question"])
        answer = out["answer"]
        ctx = "".join(
            c.text for c in rag.store.chunks if f"{c.doc}#{c.idx}" in out["trace"]["docs"]
        )
        judge = _post(s, JUDGE.format(ctx=ctx[:4000], q=item["question"], a=answer))
        rows.append({
            "question": item["question"],
            "answer": answer,
            "gold": item["answers"][0],
            "verdict": parse_verdict(judge["text"]),
            "reason": judge["text"][:200],
            "contain": max(contain(answer, g) for g in item["answers"]),
            "em": max(em(answer, g) for g in item["answers"]),
            "f1": max(f1(answer, g) for g in item["answers"]),
            "judge_tokens": judge["tokens"],
        })
        if i % 20 == 0:
            print(f"  {i}/{len(items)}")

    n = len(rows) or 1
    from collections import Counter

    dist = Counter(r["verdict"] for r in rows)
    supported = dist["supported"] / n
    print(f"\n忠实度（n={n}，{time.perf_counter()-t0:.0f}s）")
    print(f"  supported  : {supported:.4f}")
    print(f"  partial    : {dist['partial']/n:.4f}")
    print(f"  unsupported: {dist['unsupported']/n:.4f}   ← 编答案的比例")
    print(f"  contain    : {sum(r['contain'] for r in rows)/n:.4f}  （对照）")
    print(f"  F1         : {sum(r['f1'] for r in rows)/n:.4f}")

    # 交叉：答对了但没依据的（碰巧猜中）；答错但有依据的（理解错）
    lucky = sum(1 for r in rows if r["contain"] >= 0.999 and r["verdict"] != "supported")
    grounded_wrong = sum(1 for r in rows if r["contain"] < 0.999 and r["verdict"] == "supported")
    print(f"  答对但依据不足: {lucky}   答错但有依据: {grounded_wrong}")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n明细: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
