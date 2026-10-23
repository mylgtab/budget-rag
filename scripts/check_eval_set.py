"""检查人工题集：答案是否逐字出现在对应文档里。

用法：
    python scripts/check_eval_set.py --set data/eval_real.jsonl
    python scripts/check_eval_set.py --set data/eval_real.jsonl --docs data/real_docs

每条 JSONL：{"question": "...", "answers": ["..."], "doc": "docker-volumes.md"}
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(s: str) -> str:
    return "".join(s.split()).lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--docs", default="data/real_docs")
    ap.add_argument("--min-per-doc", type=int, default=2)
    args = ap.parse_args()

    path = ROOT / args.set
    if not path.exists():
        print(f"找不到题集: {path}")
        return 1

    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            rows.append((i, json.loads(line)))
        except json.JSONDecodeError as e:
            print(f"❌ 第 {i} 行不是合法 JSON: {e}")
            return 1

    docs_dir = ROOT / args.docs
    cache: dict[str, str] = {}
    problems = 0

    print(f"题集: {args.set}  共 {len(rows)} 题\n")

    for line_no, r in rows:
        q = r.get("question", "").strip()
        answers = r.get("answers") or []
        doc = r.get("doc", "").strip()
        issue = None

        if len(q.split()) < 4:
            issue = "问题太短"
        elif not answers:
            issue = "没有答案"
        elif doc not in cache:
            f = docs_dir / doc
            if not f.exists():
                issue = f"文档不存在: {doc}"
            else:
                cache[doc] = norm(f.read_text(encoding="utf-8"))
        if not issue and doc in cache:
            if not any(norm(a) in cache[doc] for a in answers):
                issue = "答案不在该文档里（需逐字匹配）"
        if not issue and any(len(str(a).split()) > 8 for a in answers):
            issue = f"答案偏长（{max(len(str(a).split()) for a in answers)} 词），建议 ≤8 词"

        if issue:
            problems += 1
            print(f"❌ L{line_no}: {issue}\n   Q: {q[:80]}\n   A: {answers}")

    # 覆盖度
    dist = Counter(r.get("doc", "?") for _, r in rows)
    print(f"\n覆盖文档: {len(dist)} 篇")
    short = [d for d, n in dist.items() if n < args.min_per_doc]
    if short:
        print(f"⚠ 少于 {args.min_per_doc} 题: {len(short)} 篇 → {short[:8]}")

    # 重复
    qs = [r.get("question", "").strip().lower() for _, r in rows]
    dup = [k for k, v in Counter(qs).items() if v > 1]
    if dup:
        problems += len(dup)
        print(f"❌ 重复问题 {len(dup)} 条: {dup[:3]}")

    print("\n" + "=" * 50)
    if problems:
        print(f"结果：{problems} 处需要修")
        return 1
    print("结果：通过（答案均可逐字匹配、无重复）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
