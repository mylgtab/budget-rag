"""合成评测集：让模型从文档里抽问答，答案必须是原文句子。

用法：
    set DEEPSEEK_API_KEY=sk-xxx
    python scripts/gen_eval.py --docs data/sample_docs --n 20 --out data/eval_set.jsonl
    python scripts/gen_eval.py --hard --out data/eval_hard.jsonl
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from budget_rag.config import Settings          # noqa: E402

PROMPT = """从下面的文档里提取 {n} 组问答对，用于检索评测。

硬性要求：
1. question 是用户会自然提出的问题，不要出现「根据文档」「文中提到」这类词。
2. answer 必须是文档中的一个完整句子，**逐字照抄**，一个字都不能改。
3. 每组问答只考一个点，不要合并多个事实。

只输出 JSON 数组，不要解释，不要 markdown 代码块：
[{{"question": "...", "answer": "..."}}]

文档（{name}）：
{text}
"""

HARD_HINT = """额外要求（重要）：question 里**不要出现原文的专有名词和关键术语**，
用同义改写或口语化描述来提问；答案仍然必须逐字照抄原文中的完整句子。
例如原文讲「强缓存命中时浏览器不会发请求」，问句写成「什么时候打开网页完全不找服务器要东西」。

"""


def call_llm(settings: Settings, prompt: str) -> str:
    body = json.dumps({
        "model": settings.llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "max_tokens": 3000,
    }).encode()
    req = urllib.request.Request(
        f"{settings.llm_base}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {settings.api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def parse_pairs(raw: str) -> list[dict]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        raw = raw[raw.find("["):] if "[" in raw else raw
    start, end = raw.find("["), raw.rfind("]")
    if start < 0 or end < 0:
        return []
    try:
        return json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="data/sample_docs")
    ap.add_argument("--n", type=int, default=20, help="每篇文档生成多少条")
    ap.add_argument("--out", default="data/eval_set.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--hard", action="store_true", help="改写题：问句不照抄原文用词")
    args = ap.parse_args()

    settings = Settings.from_env()
    if not settings.api_key:
        print("缺少 DEEPSEEK_API_KEY")
        return 1

    rows: list[dict] = []
    for doc in sorted(Path(args.docs).glob("*.md")):
        text = doc.read_text(encoding="utf-8")
        print(f"生成中: {doc.name}", end="", flush=True)
        prompt = PROMPT.format(n=args.n, name=doc.name, text=text)
        if args.hard:
            prompt = HARD_HINT + prompt
        try:
            raw = call_llm(settings, prompt)
            pairs = parse_pairs(raw)
        except Exception as exc:                       # 网络/解析失败不中断
            print(f"  失败: {exc}")
            continue

        kept = 0
        for p in pairs:
            q, a = str(p.get("question", "")).strip(), str(p.get("answer", "")).strip()
            if not q or not a or a not in text:        # 答案必须逐字来自原文
                continue
            rows.append({"question": q, "answers": [a], "doc": doc.name})
            kept += 1
        print(f"  {kept}/{len(pairs)} 条合格")

    random.Random(args.seed).shuffle(rows)
    out = Path(args.out)
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    print(f"\n共 {len(rows)} 条 → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
