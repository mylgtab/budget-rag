"""答案生成：离线抽取（免费）与 LLM（可选，OpenAI 兼容）。"""

from __future__ import annotations

import json
import re
import urllib.request

from .chunking import split_sentences
from .config import Settings

_WORD = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]")


def _overlap(answer: str, context: str) -> float:
    a = set(_WORD.findall(answer.lower()))
    c = set(_WORD.findall(context.lower()))
    return len(a & c) / (len(a) or 1)


class OfflineAnswerer:
    """从召回块里挑与问题重合度最高的句子，零成本，用来跑通链路与做基线。"""

    name = "offline"

    def answer(self, question: str, contexts: list[str]) -> str:
        best, best_score = "", -1.0
        for ctx in contexts:
            for sent in split_sentences(ctx):
                score = _overlap(question, sent) + 0.001 * len(sent)
                if score > best_score:
                    best, best_score = sent, score
        return best or "（未召回到可用内容）"


class LLMAnswerer:
    """DeepSeek / 任何 OpenAI 兼容接口。没配 key 时请用 OfflineAnswerer。"""

    name = "llm"

    def __init__(self, settings: Settings) -> None:
        if not settings.api_key:
            raise ValueError("缺少 DEEPSEEK_API_KEY")
        self.s = settings

    def answer(self, question: str, contexts: list[str]) -> str:
        prompt = (
            "只根据下面的资料回答，答不出就说不知道，不要编。\n\n"
            + "\n\n".join(f"[{i+1}] {c}" for i, c in enumerate(contexts))
            + f"\n\n问题：{question}"
        )
        body = json.dumps({
            "model": self.s.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 300,
        }).encode()
        req = urllib.request.Request(
            f"{self.s.llm_base}/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {self.s.api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
