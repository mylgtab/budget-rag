"""生成人工标注表：抽样 100 条，跑出系统答案，留空给标注员打分。

python scripts/make_annotation.py --n 100
产出：results/annotation_sheet.csv + docs/annotation-guide.md
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings          # noqa: E402
from budget_rag.llm import LLMAnswerer, OfflineAnswerer  # noqa: E402
from budget_rag.pipeline import RAG             # noqa: E402

GUIDE = """# 标注说明（给标注员看）

## 你要做什么

下面这张表里有 100 条问答。每条给了：

- `question`：用户问的问题
- `system_answer`：系统给出的答案
- `reference_answer`：参考答案（来自原文）

你要做**一件事**：在 `score` 列给 `system_answer` 打 1 / 2 / 3 分。

## 打分标准

| 分数 | 含义 | 例子 |
|---|---|---|
| **3** | 意思正确、信息完整 | 参考答案说的是「强缓存不发请求」，系统答「不请求，直接读缓存」 |
| **2** | 方向对，但缺关键信息或多说了错话 | 答了「会发请求确认」，方向错但提到了缓存 |
| **1** | 答错、答非所问、空白 | 「未召回到可用内容」 |

## 三条规矩

1. **独立判断**，不要问别人，也别猜「系统想说什么」。
2. **只看意思**，不要因为措辞不同就扣分。同义改写算 3 分。
3. 拿不准就选 2，并在 `note` 里写一句为什么。

## 不需要做的

- 不用改系统答案
- 不用查资料（想查也可以，`data/sample_docs/` 里有原始文档）
- 不用管格式、标点

## 交付

填完存成 `annotation_<你的名字>.csv`，发回给项目作者。

**预计用时：100 条约 1.5–2 小时。**
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_500.jsonl")
    ap.add_argument("--docs", default="data/sample_docs")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", default="results/annotation_sheet.csv")
    ap.add_argument("--llm", action="store_true", help="用真实模型作答（需 API key）")
    args = ap.parse_args()

    settings = Settings.from_env()
    rag = RAG(settings, LLMAnswerer(settings) if args.llm else OfflineAnswerer())
    rag.ingest({p.name: p.read_text(encoding="utf-8") for p in sorted(Path(args.docs).glob("*.md"))})

    items = [line for line in Path(args.set).read_text(encoding="utf-8").splitlines() if line.strip()]
    random.Random(args.seed).shuffle(items)
    import json
    picked = [json.loads(x) for x in items[: args.n]]

    rows = []
    for i, item in enumerate(picked, 1):
        out = rag.query(item["question"])
        rows.append({
            "id": i,
            "question": item["question"],
            "system_answer": out["answer"],
            "reference_answer": item["answers"][0],
            "doc": item["doc"],
            "score": "",
            "note": "",
        })

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8-sig") as f:      # BOM 让 Excel 正确显示中文
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    guide = ROOT / "docs" / "annotation-guide.md"
    guide.write_text(GUIDE, encoding="utf-8")
    print(f"标注表: {out}（{len(rows)} 条）\n说明: {guide}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
