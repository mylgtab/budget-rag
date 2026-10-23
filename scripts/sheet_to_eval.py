"""把填好的出题表格转成评测集 JSONL。

python scripts/sheet_to_eval.py [--sheet docs/question-sheet.csv] [--out data/eval_real.jsonl]
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEP = "；;|"


def split_answers(raw: str) -> list[str]:
    parts = [p.strip() for p in raw.replace("|", "；").replace(";", "；").split("；")]
    return [p for p in parts if p]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default="docs/question-sheet.csv")
    ap.add_argument("--out", default="data/eval_real.jsonl")
    args = ap.parse_args()

    sheet = ROOT / args.sheet
    if not sheet.exists():
        print(f"找不到表格: {sheet}")
        return 1

    rows = list(csv.DictReader(sheet.read_text(encoding="utf-8-sig").splitlines()))
    out_rows: list[dict] = []
    skipped = 0

    for r in rows:
        doc = (r.get("文档") or "").strip()
        if not doc:
            continue
        for i in range(1, 9):
            q = (r.get(f"问题{i}") or "").strip()
            a = (r.get(f"答案{i}") or "").strip()
            if not q and not a:
                continue
            if not q or not a:
                print(f"⚠ {doc} 第 {i} 组只填了一半，已跳过")
                skipped += 1
                continue
            out_rows.append({"question": q, "answers": split_answers(a), "doc": doc})

    if not out_rows:
        print("表格里还没有题目")
        return 1

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for row in out_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    dist = Counter(r["doc"] for r in out_rows)
    print(f"写出 {len(out_rows)} 题（跳过 {skipped} 处半填）→ {args.out}")
    print(f"覆盖文档 {len(dist)} 篇，平均 {len(out_rows) / max(1, len(dist)):.1f} 题/篇")
    thin = [d for d, n in dist.items() if n < 2]
    if thin:
        print(f"⚠ 少于 2 题的文档 {len(thin)} 篇: {thin[:5]}")
    print("\n下一步：python scripts/check_eval_set.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
