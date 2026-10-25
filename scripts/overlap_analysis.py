"""量化「问题是否照抄原文」：计算问题与源文档的 n-gram 重叠。

这是审稿风险 C2（同源偏差）的直接证据：
若问题大量复用原文短语，检索会靠字面撞车命中，分数虚高；
若重叠很低，说明问题确实独立于原文措辞。

指标：
  - 4-gram 覆盖率：问题的 4-gram 中有多少比例出现在源文档
  - 最长公共子串（LCS）长度
  - 与「理想改写」的对照：直接用原句改一个词当问题（上界参照）

python scripts/overlap_analysis.py
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def norm(s: str) -> str:
    return " ".join(str(s).split()).lower()


def ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def longest_common_substring(a: list[str], b: str) -> int:
    """返回 a（词序列）中最长的、出现在 b 里的连续片段的词数。"""
    best = 0
    for i in range(len(a)):
        for j in range(i + best + 1, len(a) + 1):
            frag = " ".join(a[i:j])
            if frag in b:
                best = max(best, j - i)
            else:
                break
    return best


def main() -> int:
    items = [json.loads(ln) for ln in (ROOT / "data" / "eval_real.jsonl").read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    docs = {}
    for it in items:
        if it["doc"] not in docs:
            docs[it["doc"]] = norm((ROOT / "data" / "real_docs" / it["doc"]).read_text(encoding="utf-8"))

    rows = []
    for it in items:
        q_tokens = norm(it["question"]).split()
        doc = docs[it["doc"]]
        g = ngrams(q_tokens, 4)
        if not g:
            continue
        covered = sum(1 for t in g if " ".join(t) in doc) / len(g)
        lcs = longest_common_substring(q_tokens, doc)
        rows.append({"question": it["question"], "doc": it["doc"],
                     "ngram4": covered, "lcs_words": lcs, "len": len(q_tokens)})

    print(f"题 {len(rows)}")
    cov = [r["ngram4"] for r in rows]
    lcs = [r["lcs_words"] for r in rows]
    print(f"4-gram 覆盖率：中位 {statistics.median(cov):.3f}，均值 {statistics.mean(cov):.3f}，最大 {max(cov):.3f}")
    print(f"最长公共子串：中位 {statistics.median(lcs):.0f} 词，最大 {max(lcs)} 词")
    high = [r for r in rows if r["ngram4"] >= 0.5]
    print(f"4-gram 覆盖 ≥50% 的题：{len(high)} 条（{len(high)/len(rows)*100:.1f}%）")
    for r in high[:5]:
        print("   ", round(r["ngram4"], 2), "|", r["question"][:70])

    # 对照：把答案所在句子直接当问题（模拟「照抄」）
    base = []
    for it in items:
        doc_text = docs[it["doc"]]
        ans = norm(it["answers"][0])
        pos = doc_text.find(ans)
        if pos < 0:
            continue
        start = doc_text.rfind(".", 0, pos) + 1
        end = doc_text.find(".", pos)
        sent = doc_text[start:end + 1].strip()
        st = sent.split()
        if len(st) < 4:
            continue
        g2 = ngrams(st, 4)
        base.append(sum(1 for t in g2 if " ".join(t) in doc_text) / len(g2))
    print(f"\n对照（直接把原句当问题）：4-gram 覆盖中位 {statistics.median(base):.3f}")

    out = ROOT / "results" / "overlap_analysis.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        "n": len(rows),
        "ngram4_median": statistics.median(cov),
        "ngram4_mean": statistics.mean(cov),
        "ngram4_max": max(cov),
        "lcs_median": statistics.median(lcs),
        "lcs_max": max(lcs),
        "high_overlap_ratio": len(high) / len(rows),
        "baseline_sentence_median": statistics.median(base) if base else None,
        "rows": rows,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
