"""答案生成：离线抽取（免费）与 LLM（可选，OpenAI 兼容）。"""

from __future__ import annotations

import json
import re
import time
import urllib.request

from .chunking import split_sentences
from .cache import DiskCache
from .config import Settings

_WORD = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]")


def _overlap(answer: str, context: str) -> float:
    a = set(_WORD.findall(answer.lower()))
    c = set(_WORD.findall(context.lower()))
    return len(a & c) / (len(a) or 1)


class OfflineAnswerer:
    """从召回块里挑与问题重合度最高的句子，零成本，用来跑通链路与做基线。"""

    name = "offline"
    last_usage: dict | None = None

    def answer(self, question: str, contexts: list[str]) -> str:
        self.last_usage = None
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
        self.last_usage: dict | None = None
        self.last_rewrite_usage: dict | None = None
        self.cache = DiskCache()

    def answer(self, question: str, contexts: list[str]) -> str:
        prompt = (
            "只根据下面的资料回答问题。\n\n"
            "输出要求（重要）：\n"
            "1. 只输出答案本身，不要加「根据资料」「资料[1]」这类前缀，不要解释。\n"
            "2. 如果资料里有一句话正好能回答，就**逐字照抄那一句**，不要改写。\n"
            "3. 资料里没有答案就只回四个字：不知道。\n\n"
            + "\n\n".join(f"[{i+1}] {c}" for i, c in enumerate(contexts))
            + f"\n\n问题：{question}\n答案："
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
        ck = DiskCache.key("answer", self.s.llm_model, prompt)
        if (hit := self.cache.get(ck)) is not None:
            self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0}
            return hit

        last_err: Exception | None = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                break
            except Exception as exc:            # 网络抖动重试，长跑不能一次就崩
                last_err = exc
                time.sleep(1.5 * (attempt + 1))
        else:
            raise RuntimeError(f"调用模型失败（已重试 3 次）: {last_err}") from last_err
        usage = data.get("usage") or {}
        self.last_usage = {
            "prompt_tokens": int(usage.get("prompt_tokens", 0)),
            "completion_tokens": int(usage.get("completion_tokens", 0)),
        }
        text = data["choices"][0]["message"]["content"].strip()
        self.cache.put(ck, text)
        # 兜底清洗：模型偶尔还是会带前缀或引号
        text = re.sub(r"^根据(上述)?资料\s*\[\d+\]\s*[，,：:]\s*", "", text)
        text = re.sub(r"^资料\s*\[\d+\]\s*[，,：:]\s*", "", text)
        text = text.strip().strip("“”\"'").strip()

        # 二次兜底：模型拒答时，逼它从资料里挑最接近的一句
        if text in ("不知道", "不知道。", "") or "不知道" == text.strip("。"):
            text = self._force_quote(contexts, question) or text
        return text

    def _force_quote(self, contexts: list[str], question: str) -> str:
        prompt = (
            "下面资料里一定有一句能部分回答问题。请从资料中挑**最接近**的一句，逐字照抄，"
            "不要解释，不要回答「不知道」，不要加引号。\n\n"
            + "\n".join(f"- {c}" for c in contexts)
            + f"\n\n问题：{question}\n最接近的句子："
        )
        body = json.dumps({
            "model": self.s.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 120,
        }).encode()
        req = urllib.request.Request(
            f"{self.s.llm_base}/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {self.s.api_key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            return ""
        usage = data.get("usage") or {}
        if self.last_usage:                    # 把兜底这一跳的 token 也记进账单
            self.last_usage["prompt_tokens"] += int(usage.get("prompt_tokens", 0))
            self.last_usage["completion_tokens"] += int(usage.get("completion_tokens", 0))
        return data["choices"][0]["message"]["content"].strip().strip("“”\"'")

    def rewrite_query(self, question: str) -> str:
        """把口语化问题改写成适合关键词检索的查询词，用于提升召回。"""
        prompt = (
            "把下面的问题改写成适合关键词检索的查询词。\n"
            "输出 5-10 个词或短语，用空格分隔；保留关键概念，补充同义词；"
            "不要解释，不要标点。\n\n"
            f"问题：{question}\n改写："
        )
        body = json.dumps({
            "model": self.s.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 80,
        }).encode()
        req = urllib.request.Request(
            f"{self.s.llm_base}/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {self.s.api_key}", "Content-Type": "application/json"},
        )
        ck = DiskCache.key("rewrite", self.s.llm_model, prompt)
        if (hit := self.cache.get(ck)) is not None:
            return hit
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                u = data.get("usage") or {}
                self.last_rewrite_usage = {
                    "prompt_tokens": int(u.get("prompt_tokens", 0)),
                    "completion_tokens": int(u.get("completion_tokens", 0)),
                }
                out = data["choices"][0]["message"]["content"].strip()
                self.cache.put(ck, out)
                return out
            except Exception:
                time.sleep(1.5 * (attempt + 1))
        return ""

    def answer_with_usage(self, question: str, contexts: list[str]) -> tuple[str, dict | None]:
        """返回 (答案, 真实 usage)。没有 usage 时返回 None，由调用方回退到估算。"""
        text = self.answer(question, contexts)
        return text, self.last_usage
