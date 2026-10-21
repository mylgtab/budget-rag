"""路由器：按问题特征和预算决定走便宜还是强路径。"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ENTITY = re.compile(r"[A-Z]{2,}|\d+年|\d+%|《.+?》")


@dataclass
class Route:
    path: str          # "cheap" | "strong"
    reason: str
    k: int


def decide(question: str, budget: float, top_k: int = 3, cheap_max: int = 24, strong_min: int = 60) -> Route:
    q = question.strip()
    reasons: list[str] = []

    if len(q) <= cheap_max:
        reasons.append("短问题")
    if len(q) >= strong_min:
        reasons.append("长问题")
    if len(_ENTITY.findall(q)) >= 2:
        reasons.append("多实体")
    if "为什么" in q or "比较" in q or "分析" in q:
        reasons.append("需要推理")

    strong = bool({"长问题", "多实体", "需要推理"} & set(reasons))
    path = "strong" if strong else "cheap"

    # 预算收口：钱不够就退回便宜路径
    if path == "strong" and budget < 0.005:
        path, reasons = "cheap", reasons + ["预算不足降级"]

    k = top_k + 2 if path == "strong" else max(1, top_k - 1)
    return Route(path=path, reason="、".join(reasons) or "默认", k=k)
