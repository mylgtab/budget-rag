"""第 0 级：不检索，直接让模型答。用来验证「检索是不是每次都必要」。

灵感来自 Ponytail 的懒惰阶梯（先问「需要存在吗」，再问「怎么实现」）。
python scripts/no_retrieval.py --limit 100
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

from budget_rag.config import Settings        # noqa: E402
from budget_rag.metrics import contain, em, f1  # noqa: E402

PROMPT = "回答下面的问题。答不出就说不知道，不要编。只输出答案本身。\n\n问题：{q}"


def ask(settings: Settings, q: str) -> tuple[str, int]:
    body = json.dumps({
        "model": settings.llm_model,
        "messages": [{"role": "user", "content": PROMPT.format(q=q)}],
        "temperature": 0.0,
        "max_tokens": 150,
    }).encode()
    req = urllib.request.Request(
        f"{settings.llm_base}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {settings.api_key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
            usage = (data.get("usage") or {}).get("total_tokens", 0)
            return data["choices"][0]["message"]["content"].strip(), int(usage)
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return "", 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()

    s = Settings.from_env()
    if not s.api_key:
        print("需要 DEEPSEEK_API_KEY")
        return 1

    items = [json.loads(l) for l in Path(args.set).read_text(encoding="utf-8").splitlines() if l.strip()][: args.limit]
    c = e = f = 0.0
    tokens = 0
    t0 = time.perf_counter()
    for i, item in enumerate(items, 1):
        ans, used = ask(s, item["question"])
        tokens += used
        golds = item["answers"]
        c += max(contain(ans, g) for g in golds)
        e += max(em(ans, g) for g in golds)
        f += max(f1(ans, g) for g in golds)
        if i % 25 == 0:
            print(f"  {i}/{len(items)}")

    n = len(items) or 1
    print(f"\n不检索（n={n}，{time.perf_counter()-t0:.0f}s，{tokens} tokens）")
    print(f"  contain={c/n:.4f}  EM={e/n:.4f}  F1={f/n:.4f}")
    print("  对照：检索 + 生成在同类数据上 contain ≈ 0.92–0.985，平均 450–950 上下文 tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
