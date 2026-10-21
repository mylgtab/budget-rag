"""分析人工标注表：与自动指标对照，输出混淆矩阵与一致性。

python scripts/analyze_annotation.py --csv <标注文件>
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def read_rows(path: Path) -> list[dict]:
    for enc in ("utf-8-sig", "gbk", "utf-8"):
        try:
            with path.open("r", encoding=enc, newline="") as f:
                return [r for r in csv.DictReader(f) if (r.get("id") or "").strip()]
        except (UnicodeDecodeError, LookupError):
            continue
    raise SystemExit(f"无法识别编码: {path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", default="results/annotation_report.md")
    args = ap.parse_args()

    rows = read_rows(Path(args.csv))
    total = len(rows)
    scored = []
    bad = []
    for r in rows:
        s = (r.get("score") or "").strip()
        if s in {"1", "2", "3"}:
            scored.append((int(s), r))
        else:
            bad.append(r.get("id"))

    if not scored:
        print("没有有效的 score（应为 1/2/3）")
        return 1

    dist = Counter(s for s, _ in scored)
    human_ok = sum(1 for s, _ in scored if s >= 2) / len(scored)

    # 自动指标：从表里已有文本重算，保证与标注同一批题
    auto_contain = 0
    auto_em = 0
    confusion = Counter()
    for s, r in scored:
        pred, gold = r.get("system_answer", ""), r.get("reference_answer", "")
        c = int(bool(norm(pred)) and (norm(pred) in norm(gold) or norm(gold) in norm(pred)))
        e = int(norm(pred) == norm(gold))
        auto_contain += c
        auto_em += e
        confusion[(s, c)] += 1

    n = len(scored)
    lines = [
        "# 人工标注分析",
        "",
        f"- 标注条数：**{n}**" + (f"（{len(bad)} 条未填，已跳过）" if bad else ""),
        f"- 分数分布：3 分 {dist[3]} / 2 分 {dist[2]} / 1 分 {dist[1]}",
        f"- 人工判定正确（≥2 分）：**{human_ok:.1%}**",
        f"- 自动 contain 判定正确：**{auto_contain / n:.1%}**",
        f"- 自动 EM 判定正确：**{auto_em / n:.1%}**",
        "",
        "## 混淆矩阵（行=人工分，列=自动 contain）",
        "",
        "| 人工 \\ 自动 | 判对 | 判错 |",
        "|---|---|---|",
    ]
    for s in (3, 2, 1):
        lines.append(f"| {s} 分 | {confusion[(s, 1)]} | {confusion[(s, 0)]} |")

    tp = sum(v for (s, c), v in confusion.items() if s >= 2 and c == 1)
    tn = sum(v for (s, c), v in confusion.items() if s == 1 and c == 0)
    fp = sum(v for (s, c), v in confusion.items() if s == 1 and c == 1)
    fn = sum(v for (s, c), v in confusion.items() if s >= 2 and c == 0)
    agree = (tp + tn) / n

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    lines += [
        "",
        "## 自动指标 vs 人工",
        "",
        f"- 一致率：**{agree:.1%}**",
        f"- 自动判「对」时人工也判对（精确率）：**{precision:.1%}**",
        f"- 人工判对里被自动抓到的比例（召回率）：**{recall:.1%}**",
        "",
        f"误判明细：自动说对但人工说错 {fp} 条；自动说错但人工说对 {fn} 条。",
    ]

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n报告: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
