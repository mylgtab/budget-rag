"""路由器：预算决定检索深度，问题特征决定要不要加码。"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ENTITY = re.compile(r"[A-Z]{2,}|\d+年|\d+%|《.+?》")

# 预算三档：钱越少，检索越浅
TIER_TIGHT = 0.002
TIER_NORMAL = 0.01


@dataclass
class Route:
    path: str          # "cheap" | "strong"
    reason: str
    k: int
    hybrid: bool = False


def decide(
    question: str,
    budget: float,
    top_k: int = 3,
    cheap_max: int = 24,
    strong_min: int = 60,
) -> Route:
    q = question.strip()
    reasons: list[str] = []

    if len(q) <= cheap_max:
        reasons.append("短问题")
    if len(q) >= strong_min:
        reasons.append("长问题")
    if len(_ENTITY.findall(q)) >= 2:
        reasons.append("多实体")
    if any(w in q for w in ("为什么", "比较", "分析", "区别")):
        reasons.append("需要推理")

    hard = bool({"长问题", "多实体", "需要推理"} & set(reasons))

    # 预算决定检索深度
    if budget < TIER_TIGHT:
        k, hybrid, tier = 1, False, "紧预算"
    elif budget < TIER_NORMAL:
        k, hybrid, tier = max(1, top_k - 1), False, "常规"
    else:
        k, hybrid, tier = top_k + 2, True, "宽裕"
    reasons.append(tier)

    if hybrid and hard:          # 宽裕档里，难题再多给一点
        k += 1

    return Route(
        path="strong" if (hybrid and hard) else "cheap",
        reason="、".join(reasons),
        k=k,
        hybrid=hybrid,
    )
