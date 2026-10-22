"""运行配置。全部可用环境变量覆盖，方便换模型/换预算。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    # 检索
    top_k: int = 3
    chunk_size: int = 320
    chunk_overlap: int = 60
    chunk_mode: str = field(default_factory=lambda: os.getenv("RAG_CHUNK_MODE", "auto"))  # fixed | sentence | auto

    # auto 模式：上下文预算 ≤ 阈值用句级切块，超过用固定块
    ctx_tokens: int = field(default_factory=lambda: int(os.getenv("RAG_CTX_TOKENS", "300")))
    auto_threshold: int = field(default_factory=lambda: int(os.getenv("RAG_AUTO_THRESHOLD", "500")))

    # 查询改写：off / always / auto（auto=检索置信度低才改写）
    rewrite_mode: str = field(default_factory=lambda: os.getenv("RAG_REWRITE", "off").lower())
    rewrite_threshold: float = field(default_factory=lambda: float(os.getenv("RAG_REWRITE_THRESHOLD", "0.25")))
    embed_dim: int = 256

    # 路由器
    cheap_max_chars: int = 24      # 短问题走便宜路径
    strong_min_chars: int = 60     # 长问题直接走强路径
    budget_rmb: float = 0.01       # 单次查询预算上限

    # 成本模型（元 / 1k tokens），按需改
    price_cheap: float = 0.0005
    price_strong: float = 0.002
    price_embed: float = 0.00002

    # 真实计费（元 / 100 万 tokens），按服务商当前价格改
    price_in: float = field(default_factory=lambda: float(os.getenv("RAG_PRICE_IN", "2.0")))
    price_out: float = field(default_factory=lambda: float(os.getenv("RAG_PRICE_OUT", "8.0")))

    # 模型
    llm_model: str = "deepseek-chat"
    llm_base: str = "https://api.deepseek.com/v1"
    api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))

    # embedding（留空则用离线哈希）
    embed_base: str = field(default_factory=lambda: os.getenv("RAG_EMBED_BASE", ""))
    embed_model: str = field(default_factory=lambda: os.getenv("RAG_EMBED_MODEL", "BAAI/bge-m3"))
    embed_key: str = field(default_factory=lambda: os.getenv("RAG_EMBED_KEY", ""))

    @classmethod
    def from_env(cls) -> "Settings":
        s = cls()
        for name in ("top_k", "chunk_size", "budget_rmb"):
            if (v := os.getenv(f"RAG_{name.upper()}")) is not None:
                setattr(s, name, float(v) if "budget" in name else int(v))
        if m := os.getenv("RAG_MODEL"):
            s.llm_model = m
        return s
