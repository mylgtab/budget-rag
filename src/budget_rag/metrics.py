"""评测指标：contain / EM / F1 / Cohen's kappa。

放进库里而不是脚本里，测试才能直接 import。
"""

from __future__ import annotations

import re

_WORD = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]")


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def contain(pred: str, gold: str) -> float:
    p, g = norm(pred), norm(gold)
    if not p or not g:
        return 0.0
    return float(p in g or g in p)


def em(pred: str, gold: str) -> float:
    return float(norm(pred) == norm(gold))


def f1(pred: str, gold: str) -> float:
    # 注意：不能用 norm()，它去空格会把英文单词粘在一起
    p, g = _WORD.findall(str(pred).lower()), _WORD.findall(str(gold).lower())
    if not p or not g:
        return float(norm(pred) == norm(gold))
    gs, common = list(g), 0
    for t in p:
        if t in gs:
            gs.remove(t)
            common += 1
    if common == 0:
        return 0.0
    prec, rec = common / len(p), common / len(g)
    return 2 * prec * rec / (prec + rec)


def cohen_kappa(pairs: list[tuple[int, int]], weights: bool = False) -> float:
    """pairs 是两位标注员对同一批条目的评分对。weights=True 时用二次加权。"""
    n = len(pairs)
    if not n:
        return 0.0
    labels = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    k = len(labels)
    idx = {lab: i for i, lab in enumerate(labels)}
    obs = [[0.0] * k for _ in range(k)]
    for a, b in pairs:
        obs[idx[a]][idx[b]] += 1
    w = [[0.0] * k for _ in range(k)]
    for i in range(k):
        for j in range(k):
            if weights and k > 1:
                w[i][j] = 1.0 - ((i - j) ** 2) / ((k - 1) ** 2)
            else:
                w[i][j] = 1.0 if i == j else 0.0
    row = [sum(obs[i]) for i in range(k)]
    col = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    po = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k)) / n
    pe = sum(w[i][j] * row[i] * col[j] for i in range(k) for j in range(k)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0
