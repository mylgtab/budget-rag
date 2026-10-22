"""两位标注者的一致性（Cohen's kappa）与共识对照。

python scripts/kappa.py --a <文件A> --b <文件B>
按 question 对齐，输出一致率、kappa（原始与二次加权）、分歧明细。
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
                return [r for r in csv.DictReader(f) if (r.get("question") or "").strip()]
        except (UnicodeDecodeError, LookupError):
            continue
    raise SystemExit(f"无法识别编码: {path}")


def cohen_kappa(pairs: list[tuple[int, int]], weights: bool = False) -> float:
    n = len(pairs)
    if not n:
        return 0.0
    labels = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    idx = {lab: i for i, lab in enumerate(labels)}
    k = len(labels)
    obs = [[0.0] * k for _ in range(k)]
    for a, b in pairs:
        obs[idx[a]][idx[b]] += 1
    total = float(n)
    w = [[0.0] * k for _ in range(k)]
    for i in range(k):
        for j in range(k):
            if weights and k > 1:
                w[i][j] = 1.0 - ((i - j) ** 2) / ((k - 1) ** 2)
            else:
                w[i][j] = 1.0 if i == j else 0.0
    row = [sum(obs[i]) for i in range(k)]
    col = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    po = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k)) / total
    pe = sum(w[i][j] * row[i] * col[j] for i in range(k) for j in range(k)) / (total * total)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--out", default="results/kappa_report.md")
    args = ap.parse_args()

    A = {norm(r["question"]): r for r in read_rows(Path(args.a)) if (r.get("score") or "").strip() in {"1", "2", "3"}}
    B = {norm(r["question"]): r for r in read_rows(Path(args.b)) if (r.get("score") or "").strip() in {"1", "2", "3"}}
    common = sorted(set(A) & set(B))

    pairs = [(int(A[q]["score"]), int(B[q]["score"])) for q in common]
    exact = sum(1 for a, b in pairs if a == b)
    kappa = cohen_kappa(pairs)
    wkappa = cohen_kappa(pairs, weights=True)

    # 与自动指标对照：两位都判对 / 任一位判对
    both_ok = sum(1 for a, b in pairs if a >= 2 and b >= 2)
    either_ok = sum(1 for a, b in pairs if a >= 2 or b >= 2)
    auto = 0
    for q in common:
        pred, gold = A[q].get("system_answer", ""), A[q].get("reference_answer", "")
        auto += int(bool(norm(pred)) and (norm(pred) in norm(gold) or norm(gold) in norm(pred)))

    n = len(common) or 1
    dist_a = Counter(a for a, _ in pairs)
    dist_b = Counter(b for _, b in pairs)

    lines = [
        "# 标注者一致性",
        "",
        f"- 对齐条目：**{len(common)}**",
        f"- A 分数分布：3 分 {dist_a[3]} / 2 分 {dist_a[2]} / 1 分 {dist_a[1]}",
        f"- B 分数分布：3 分 {dist_b[3]} / 2 分 {dist_b[2]} / 1 分 {dist_b[1]}",
        f"- 完全一致：**{exact}/{len(common)} = {exact / n:.1%}**",
        f"- Cohen's kappa（未加权）：**{kappa:.3f}**",
        f"- Cohen's kappa（二次加权）：**{wkappa:.3f}**",
        "",
        "## 与自动指标对照",
        "",
        f"- 两位都判对：**{both_ok / n:.1%}**",
        f"- 至少一位判对：**{either_ok / n:.1%}**",
        f"- 自动 contain 判对：**{auto / n:.1%}**",
        "",
        "## 分歧明细（只列不一致的）",
        "",
        "| 问题 | A | B | 自动 |",
        "|---|---|---|---|",
    ]
    for q in common:
        a, b = int(A[q]["score"]), int(B[q]["score"])
        if a == b:
            continue
        pred, gold = A[q].get("system_answer", ""), A[q].get("reference_answer", "")
        c = int(bool(norm(pred)) and (norm(pred) in norm(gold) or norm(gold) in norm(pred)))
        lines.append(f"| {A[q]['question'][:28]} | {a} | {b} | {'对' if c else '错'} |")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:20]))
    print(f"\n报告: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
