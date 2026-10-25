"""延迟与 token 的交换率：在同等召回下，多花多少毫秒能省多少 token。

思路：不同检索器的 (延迟, 达到目标召回所需 token) 不同，
于是可以用「多花的延迟」去换「少取的上下文」。交换率 = Δtoken / Δms。

可选：用本地 Ollama 实测生成侧「每 token 的 prefill 毫秒数」，
把交换率换算成端到端净收益。

python scripts/exchange_rate.py --target 0.80 0.85 0.90
python scripts/exchange_rate.py --target 0.80 --measure-prefill
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings  # noqa: E402
from budget_rag.pipeline import RAG  # noqa: E402
from budget_rag.tokens import count_tokens  # noqa: E402


def norm(s: str) -> str:
    return "".join(str(s).split()).lower()


def min_hit_budget(ranked, answers, cap: int = 1500) -> float:
    used = 0
    for chunk, _ in ranked:
        used += max(1, count_tokens(chunk.text))
        if any(norm(a) in norm(chunk.text) for a in answers):
            return used
        if used >= cap:
            break
    return float("inf")


def budget_for(items, fn, target: float) -> tuple[float, float]:
    """返回 (达到 target 所需预算的中位, 该检索器的中位延迟 ms)。"""
    hits, lat = [], []
    for it in items:
        t0 = time.perf_counter()
        ranked = fn(it["question"], 200)
        lat.append((time.perf_counter() - t0) * 1000)
        hits.append(min_hit_budget(ranked, it["answers"]))
    arr = sorted(hits)
    n = len(arr)
    need = arr[min(n - 1, int(target * n))]
    return need if need < 1e8 else float("nan"), statistics.median(lat)


def measure_prefill(base: str, model: str, tokens_list: list[int]) -> dict[int, float]:
    """用本地 Ollama 测 prefill 耗时（读 prompt_eval_duration，随机词避免前缀缓存）。"""
    import random

    rng = random.Random(0)

    def once(n: int) -> float:
        words = [f"w{rng.randrange(10**6)}" for _ in range(max(4, n))]
        body = json.dumps({
            "model": model,
            "prompt": " ".join(words) + " Reply OK.",
            "stream": False,
            "options": {"num_predict": 1, "temperature": 0},
        }).encode()
        req = urllib.request.Request(f"{base}/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as resp:
            d = json.loads(resp.read())
        ns = d.get("prompt_eval_duration") or 0
        cnt = d.get("prompt_eval_count") or 0
        if not ns or not cnt:
            raise RuntimeError("响应里没有 prompt_eval 计时")
        return ns / 1e6

    try:
        once(200)
        once(200)                      # 热身：首次含模型加载
    except Exception as e:  # noqa: BLE001
        print(f"  Ollama 不可用（{e}），跳过 prefill 测量")
        return {}

    out = {}
    for n in tokens_list:
        try:
            out[n] = statistics.median([once(n) for _ in range(3)])
        except Exception as e:  # noqa: BLE001
            print(f"  Ollama 调用失败（{e}）")
            return {}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="data/eval_real.jsonl")
    ap.add_argument("--index", default="index_real.json")
    ap.add_argument("--index2", default="index_real_bgelarge.json")
    ap.add_argument("--targets", type=float, nargs="*", default=[0.80, 0.85, 0.90])
    ap.add_argument("--measure-prefill", action="store_true")
    ap.add_argument("--ollama", default="http://127.0.0.1:11434")
    ap.add_argument("--model", default="qwen3-4b")
    args = ap.parse_args()

    items = [json.loads(ln) for ln in (ROOT / args.set).read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    rag = RAG(Settings.from_env())
    rag.store.load(ROOT / args.index)
    store = rag.store

    store2 = None
    if (ROOT / args.index2).exists():
        s2 = Settings.from_env()
        s2.embed_model = "BAAI/bge-large-en-v1.5"
        rag2 = RAG(s2)
        rag2.store.load(ROOT / args.index2)
        store2 = rag2.store

    methods = [("BM25", store.search_bm25), ("Hybrid", store.search_hybrid)]
    if store2 is not None:
        methods.append(("Dense-large", store2.search_vector))

    table = {}
    for name, fn in methods:
        table[name] = {}
        for t in args.targets:
            need, lat = budget_for(items, fn, t)
            table[name][f"{t:.2f}"] = {"budget": need, "latency_ms": lat}
        print(f"{name:<12} " + "  ".join(
            f"T={t}:{table[name][f'{t:.2f}']['budget']:.0f}tok/{table[name][f'{t:.2f}']['latency_ms']:.0f}ms"
            for t in args.targets))

    print("\n同召回下的交换（以 Hybrid 为参照）")
    print(f"{'目标':>6}{'对比':>14}{'多花 ms':>10}{'省下 token':>12}{'交换率 tok/ms':>15}")
    exchange = []
    for t in args.targets:
        key = f"{t:.2f}"
        base = table["Hybrid"][key]
        for name in ("BM25", "Dense-large"):
            if name not in table:
                continue
            o = table[name][key]
            d_ms = base["latency_ms"] - o["latency_ms"]
            d_tok = o["budget"] - base["budget"]
            if d_ms == 0 or d_tok != d_tok:  # nan 或零
                continue
            rate = d_tok / d_ms
            print(f"{t:>6.2f}{name:>14}{d_ms:>10.0f}{d_tok:>12.0f}{rate:>15.1f}")
            exchange.append({"target": t, "vs": name, "delta_ms": d_ms,
                             "delta_tokens": d_tok, "tokens_per_ms": rate})

    prefill = {}
    if args.measure_prefill:
        print("\n本地生成侧 prefill 实测（Ollama）")
        prefill = measure_prefill(args.ollama, args.model, [100, 300, 600, 1000])
        if prefill:
            xs = list(prefill); ys = [prefill[x] for x in xs]
            n = len(xs)
            mx, my = sum(xs) / n, sum(ys) / n
            b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
            print("  prompt token → prefill 耗时 ms: " + ", ".join(f"{k}:{v:.0f}" for k, v in prefill.items()))
            print(f"  prefill 斜率 ≈ {b:.3f} ms/token")
            for e in exchange:
                saved_ms = e["delta_tokens"] * b
                net = saved_ms - e["delta_ms"]
                print(f"  目标 {e['target']:.2f} 换 {e['vs']}: 省 {e['delta_tokens']:.0f} token "
                      f"≈ {saved_ms:.0f} ms 生成时间，多花 {e['delta_ms']:.0f} ms 检索 → 净 {net:+.0f} ms")
                e["saved_ms_by_prefill"] = saved_ms
                e["net_ms"] = net

    out = ROOT / "results" / "exchange_rate.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"table": table, "exchange": exchange, "prefill": prefill},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
