"""校准 token 估算：把 tiktoken 的估算和 API 返回的 usage 对比。

结论会写进报告：预算控制用估算没问题，账单必须用 usage。
python scripts/token_check.py --n 10
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import urllib.request

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "src"))

from budget_rag.config import Settings          # noqa: E402
from budget_rag.tokens import backend, count_tokens  # noqa: E402

PROMPT = ("只根据资料回答问题。资料：缓存命中率决定缓存收益；索引能加速查询。" * 3
          + "\n问题：缓存收益由什么决定？\n答案：")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    args = ap.parse_args()

    s = Settings.from_env()
    if not s.api_key:
        print("需要 DEEPSEEK_API_KEY")
        return 1

    est = count_tokens(PROMPT)
    errors = []
    billed = []
    for _ in range(args.n):
        body = json.dumps({
            "model": s.llm_model,
            "messages": [{"role": "user", "content": PROMPT}],
            "temperature": 0.0,
            "max_tokens": 16,
        }).encode()
        req = urllib.request.Request(
            f"{s.llm_base}/chat/completions", data=body,
            headers={"Authorization": f"Bearer {s.api_key}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        u = data.get("usage") or {}
        prompt_tokens = int(u.get("prompt_tokens", 0))
        if prompt_tokens:
            billed.append(prompt_tokens)
            errors.append(abs(prompt_tokens - est) / prompt_tokens)

    if not billed:
        print("没拿到 usage")
        return 1

    mae = statistics.mean(errors)
    print(f"tokenizer : {backend()}")
    print(f"估算      : {est} tokens")
    print(f"实际(均值): {statistics.mean(billed):.1f} tokens")
    print(f"相对误差  : {mae:.1%}（{args.n} 次）")
    print("\n结论：估算可用于预算控制（误差在可接受范围），但对外报成本必须用 usage。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
