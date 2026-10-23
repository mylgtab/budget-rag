"""润色后自检：抓「润色把诚实边界磨掉」的五类问题。

用法：
    python scripts/check_polish.py --cand 新的段落.md
    python scripts/check_polish.py --cand new_abstract.md --section abstract --journal mdpi
    python scripts/check_polish.py --cand new_intro.md --ref docs/paper-en.md

检查项：
    1. 数字：小数是否在登记表内（防止 0.9060 这类笔误）
    2. 限定词：同一章节在参考稿里有、润色稿里没有 → 大概率被磨掉
    3. 过度概括：主语范围被放大、结论被拔高
    4. 术语：cross-hop / Recall@k / chunks 等与摘要不一致
    5. 长度：摘要按期刊上限（MDPI 200 / KBS 250），正文不限制

退出码：0 = 全过；1 = 有必须处理项。
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 论文里合法的小数（改错一个就会变红）
KNOWN_NUMBERS = {
    "0.960", "0.925", "0.910", "0.825", "0.900", "0.855", "0.912", "0.920",
    "0.995", "1.000", "0.400", "0.520", "0.250", "0.140", "0.120", "0.090", "0.230",
    "0.300", "0.450", "0.150", "0.500", "0.000",
    "0.25", "0.2", "0.5", "0.75", "0.747", "0.702", "0.730", "0.548", "0.673",
    "0.05", "0.01", "0.002", "0.001", "1.000", "0.995", "0.958", "0.894",
    "0.1", "0.3", "0.4", "0.6", "0.7", "0.8", "0.9",
}

HEDGES = {
    "approximation": "基线的诚实限定（我们没复现原版）",
    "approximate": "同上",
    "within paired noise": "承认端到端是平手，不是赢",
    "lower bound": "自动指标偏保守，报告值是下界",
    "conservative": "同上",
    "not reproduced": "复现边界",
    "behavioural": "基线是行为近似",
    "behavioral": "基线是行为近似",
    "survives repeated subsampling": "稳健性主张的证据",
    "does not depend": "稳健性主张",
    "at most": "上界表述",
    "only": "范围限定",
}

OVERCLAIM = [
    (r"both a hosted large model and a locally deployed 4B model", "大模型只跑了 HotpotQA"),
    (r"on three multi-hop generation benchmarks for both", "大模型未跑三个基准"),
    (r"\bconsistently\b", "「一致」需要每个基准都成立"),
    (r"\ball baselines\b", "有基线未达显著"),
    (r"\boutperforms?\b", "未说明预算是否相同"),
    (r"state[- ]of[- ]the[- ]art", "本文未与 SOTA 系统比较"),
    (r"\bproves?\b", "实验只能支持，不能证明"),
    (r"\bestablishes?\b", "结论强度过高"),
    (r"\bzero[- ]shot\b", "未做 zero-shot 设定"),
    (r"\bnovel\b", "「新颖」是评价词，不是事实"),
]

TERM_FIX = {
    "cross-hop": "second hop",
    "second-hop retrieval": "second hop",
    "Recall@k": "Recall@$k$",
    "Recall@K": "Recall@$k$",
}

ABSTRACT_LIMITS = {"mdpi": 200, "kbs": 250, "elsevier": 250, "generic": None}


def clean(text: str) -> str:
    """去掉引用编号、章节号、年份、公式，避免数字误报。"""
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\[[\d,\s]+\]", " ", text)
    text = re.sub(r"Sections?\s+\d+(?:\.\d+)?(?:[–\-]\d+(?:\.\d+)?)?", " ", text)
    text = re.sub(r"\b(?:19|20)\d\d\b", " ", text)
    text = re.sub(r"[#*`>|]", " ", text)
    return text


def section_of(text: str, heading: str | None = None) -> str:
    """取候选文本对应的参考章节；找不到就返回全文。"""
    if not heading:
        return text
    key = heading.strip().lstrip("#").strip().lower()
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("#") and key in ln.strip().lower():
            start = i
            break
    if start is None:
        return text
    out = []
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        out.append(ln)
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", required=True, help="润色后的段落文件")
    ap.add_argument("--ref", default="docs/paper-en.md", help="参考正文")
    ap.add_argument("--journal", default="generic", choices=list(ABSTRACT_LIMITS))
    args = ap.parse_args()

    cand_path = Path(args.cand)
    if not cand_path.is_absolute():
        cand_path = ROOT / cand_path
    raw = cand_path.read_text(encoding="utf-8")
    cand = clean(raw)
    ref = clean((ROOT / args.ref).read_text(encoding="utf-8"))

    heading = next((ln for ln in raw.splitlines() if ln.strip().startswith("#")), None)
    ref_sec = clean(section_of((ROOT / args.ref).read_text(encoding="utf-8"), heading))

    fails: list[str] = []
    warns: list[str] = []

    print("=" * 64)
    print(f"自检：{cand_path.name}" + (f"  [{heading.strip()}]" if heading else ""))
    print("=" * 64)

    # 1 数字
    decimals = set(re.findall(r"\b\d+\.\d+\b", cand))
    unknown = sorted(d for d in decimals if d not in KNOWN_NUMBERS and not d.startswith("0.00"))
    print("\n[1] 数字")
    if unknown:
        warns.append(f"未登记的小数: {unknown}")
        print(f"  ⚠ 未登记: {unknown} → 新数字先登记，笔误改回")
    else:
        print("  ✅ 小数全部在登记表内")

    # 2 限定词（只比对应章节）
    print("\n[2] 限定词（同章节内丢失）")
    lost = [(p, w) for p, w in HEDGES.items()
            if p.lower() in ref_sec.lower() and p.lower() not in cand.lower()]
    if lost:
        for p, w in lost:
            fails.append(f"限定词丢失: {p}（{w}）")
            print(f"  ❌ 丢失: {p}  ← {w}")
    else:
        print("  ✅ 无丢失")

    # 3 过度概括
    print("\n[3] 主语范围 / 结论强度")
    hit = False
    for pat, why in OVERCLAIM:
        m = re.search(pat, cand, flags=re.I)
        if m:
            hit = True
            fails.append(f"过度概括: {m.group(0)}（{why}）")
            print(f"  ❌ 命中: {m.group(0)}  ← {why}")
    if not hit:
        print("  ✅ 未命中")

    # 4 术语
    print("\n[4] 术语一致性")
    t_hit = False
    for bad, good in TERM_FIX.items():
        if bad in cand:
            t_hit = True
            warns.append(f"术语不统一: {bad} → {good}")
            print(f"  ⚠ {bad} → 建议 {good}")
    if not t_hit:
        print("  ✅ 无违规")

    # 5 长度（只对摘要/节选有意义）
    limit = ABSTRACT_LIMITS[args.journal]
    words = len(re.findall(r"[A-Za-z0-9\-−]+", cand))
    print(f"\n[5] 长度：{words} 词", end="")
    if limit:
        print(f"（{args.journal} 上限 {limit}）")
        if words > limit:
            fails.append(f"超长: {words} > {limit}")
            print(f"  ❌ 超上限 {words - limit} 词")
        else:
            print("  ✅ 在限内")
    else:
        print("（正文不设限）")

    print("\n" + "=" * 64)
    if fails:
        print(f"结果：{len(fails)} 项必须处理，{len(warns)} 项建议")
        for f in fails:
            print(f"  ❌ {f}")
        for w in warns:
            print(f"  ⚠ {w}")
        print("=" * 64)
        return 1
    print(f"结果：通过（{len(warns)} 项建议）")
    for w in warns:
        print(f"  ⚠ {w}")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
