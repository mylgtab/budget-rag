"""全文数字终检：把论文里的关键数字与 results/ 下的实验输出对账。

做两件事：
  1) 该出现的数字是否出现（中英各查一遍）
  2) 该消失的旧数字是否还在

python scripts/audit_numbers.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN = ROOT / "docs" / "paper-en.md"
ZH = ROOT / "docs" / "paper-draft.md"

# (标签, 论文里应出现的字符串)
EXPECT = [
    # 内部 301 题主表
    ("BM25 recall", "0.801"),
    ("Dense recall", "0.887"),
    ("Hybrid recall", "0.910"),
    ("fixed k8 recall", "0.904"),
    ("adaptive recall", "0.900"),
    ("adaptive tokens", "244"),
    ("k8 tokens", "289"),
    ("bootstrap saving", "15.5%"),
    ("bootstrap CI low", "11.2%"),
    ("bootstrap CI high", "19.8%"),
    # 保形
    ("conformal 0.80 cov", "0.810"),
    ("conformal 0.85 cov", "0.865"),
    ("conformal 0.90 cov", "0.891"),
    ("conformal budget 0.80", "120"),
    ("conformal budget 0.85", "166"),
    ("conformal budget 0.90", "276"),
    ("conformal sweep max gap", "0.046"),
    ("conformal 0.95 refuse", "28%"),
    # 显著性
    ("Holm p dense-large", "0.0091"),
    ("McNemar wins BM25", "36"),
    ("dense-m3 p", "0.12"),
    # 重叠度
    ("overlap mean", "0.044"),
    ("overlap high ratio", "1.7%"),
    ("overlap LCS max", "9"),
    # 错误分析
    ("misses", "@LANG_MISSES"),
    ("top-1 chunk", "@LANG_TOP1"),
    # 顺序成本
    ("order cost optimum", "0.927"),
    ("order cost greedy optimal", "301/301"),
    # 逐题阈值
    ("perquery recall", "0.887"),
    ("perquery tokens", "242"),
    ("perquery BEIR ndcg", "0.6827"),
    ("perquery BEIR tokens", "1818"),
    # 交换率
    ("exchange 0.80 tokens", "331"),
    ("exchange 0.80 saving", "217"),
    ("exchange rate 0.80", "3.7"),
    ("exchange 0.90 saving", "1050"),
    ("exchange rate 0.90", "18.3"),
    ("prefill ms/token", "2.15"),
    # 官方分类器
    ("classifier accuracy", "43.3"),
    ("classifier faithful", "0.638"),
    ("classifier faithful tokens", "150"),
    ("classifier adapted", "0.844"),
    ("classifier adapted tokens", "160"),
    ("classifier latency", "21 ms"),
    # BEIR 四子集
    ("scifact k8 ndcg", "0.7071"),
    ("scifact k8 tokens", "2615"),
    ("scifact adaptive ndcg", "0.7062"),
    ("scifact adaptive tokens", "1991"),
    ("nfcorpus k8 ndcg", "0.3504"),
    ("nfcorpus adaptive ndcg", "0.3486"),
    ("fiqa k8 ndcg", "0.4356"),
    ("arguana k8 ndcg", "0.3931"),
    ("arguana adaptive tokens", "2177"),
    # 控制台数字
    ("real corpus docs", "312"),
    ("real corpus chunks", "16,823"),
    ("question count", "301"),
]

# 不应再出现的旧数字（正则）
STALE = [
    r"143[- ]?(question|questions|题|道题)",
    r"0\.937",
    r"\|\s*56\s*\|",          # 分类器旧 token
    r"\|\s*66\s*\|",
    r"7[–-]21%",
    r"7%[–-]21%",
    r"\b27%\b(?! )",
    r"7\.2%",
    r"18 wins",
    r"9 of the 143",
    r"134 of 143",
    r"13\.4 token",
]


LANG = {"en": {"@LANG_MISSES": "27 of the 301", "@LANG_TOP1": "202 of 301"},
        "zh": {"@LANG_MISSES": "301 题中漏掉 27 题", "@LANG_TOP1": "301 题中有 202 题"}}


def audit(path: Path, label: str, lang: str) -> int:
    text = path.read_text(encoding="utf-8")
    miss = []
    for tag, s in EXPECT:
        s = LANG[lang].get(s, s)
        if s not in text:
            miss.append(f"{tag}  (期望 {s!r})")
    print(f"\n=== {label}：应出现 {len(EXPECT)} 项，缺 {len(miss)} 项 ===")
    for m in miss:
        print("  ✗", m)

    stale_hits = []
    for pat in STALE:
        for m in re.finditer(pat, text):
            line = text[: m.start()].count("\n") + 1
            snippet = text.splitlines()[line - 1].strip()[:90]
            stale_hits.append(f"L{line}: {snippet}")
    print(f"旧数字残留 {len(stale_hits)} 处")
    for h in stale_hits:
        print("  ⚠", h)
    return len(miss) + len(stale_hits)


def main() -> int:
    bad = audit(EN, "paper-en.md", "en") + audit(ZH, "paper-draft.md", "zh")

    # 结果文件自检：关键 JSON 是否齐全
    need = ["eval_real_b300", "adaptive_sweep", "conformal_sweep_hybrid", "significance_holm",
            "overlap_analysis", "order_dependent_cost", "perquery_tau", "exchange_rate",
            "official_classifier", "official_route_eval", "bootstrap_saving", "pareto_multibudget",
            "beir_adaptive_scifact", "beir_adaptive_nfcorpus", "beir_adaptive_fiqa", "beir_adaptive_arguana"]
    print("\n=== 结果文件 ===")
    missing = [n for n in need if not (ROOT / "results" / f"{n}.json").exists()]
    print("缺失:", missing or "无")
    print(f"\n问题总计: {bad + len(missing)}")
    return 0 if bad + len(missing) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
