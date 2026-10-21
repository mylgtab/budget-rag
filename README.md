# budget-rag

> 成本感知的长文档问答检索：简单问题走便宜路径，难题才升级重排与大模型。

## 为什么做

长文档 RAG 的账单大头不是回答，是**检索冗余**：每次都召回 top-k、每次都用最强模型。
这个项目把「检索深度」和「模型档位」都变成**可预算的旋钮**，并给出一条
`召回率 ↑ / 每 query 成本 ↓` 的权衡曲线。

## 架构

```
 question
    │
    ├─ 查询分析 (长度/词稀有度/是否含实体)
    │
    ├─ 路由器 ── cheap ──> BM25 top-k ─┐
    │            └ strong ─> hybrid + rerank ─┤
    │                                        │
    ├─ 检索结果 + 打分 ─────────────────────┤
    │                                        ▼
    └─ 答案生成：offline(抽取) / LLM(可选) ──> answer + trace
```

每次查询都会输出 `trace`：走了哪条路、召回了几块、花了多少钱、耗时多少。

## 快速开始

```bash
# 1. 环境（Python 3.10+，默认零第三方依赖即可跑通离线模式）
python -m venv .venv && .venv\Scripts\activate     # Windows
# source .venv/bin/activate                       # Linux/macOS

# 2. 建索引
python scripts/ingest.py --docs data/sample_docs

# 3. 跑评测（离线，不花钱）
python scripts/eval.py --set data/eval_set.jsonl --k 3

# 4. 起服务（需要 fastapi/uvicorn）
pip install -r requirements.txt
uvicorn budget_rag.api:app --app-dir src --reload
```

接真实模型（可选）：

```bash
set DEEPSEEK_API_KEY=sk-xxx          # Windows
export DEEPSEEK_API_KEY=sk-xxx       # Linux/macOS
python scripts/eval.py --set data/eval_set.jsonl --llm
```

## 策略对比

![bench](docs/figures/bench.svg)

改写问句集（200 条，问句不照抄原文用词）上的表现：

| 策略 | Recall@3 (95% CI) | cost/query |
|---|---|---|
| `naive-bm25-k3` | 0.965 [0.935, 0.990] | 0.000295 元 |
| `fixed-hybrid-k5` | 0.975 [0.955, 0.995] | 0.001942 元 |
| `cascade-conf` | 0.970 [0.945, 0.990] | 0.000917 元 |

级联策略用 **47% 的成本**拿到深检索 99.5% 的召回。完整实验见 [docs/report.md](docs/report.md)，
其中也写了一个负结果：合成集上各策略差异落在置信区间内，必须换真实数据集才能下结论。

复现：`python scripts/bench.py --set data/eval_hard.jsonl`

## 接真实 embedding

默认的 `HashEmbedder` 是**离线占位**（零依赖，保证克隆下来就能跑）。换成真实模型只要三个环境变量：

```bash
export RAG_EMBED_BASE=https://api.siliconflow.cn/v1
export RAG_EMBED_MODEL=BAAI/bge-m3
export RAG_EMBED_KEY=sk-xxx
```

任何 OpenAI 兼容的 `/embeddings` 接口都能接（SiliconFlow、通义、本地 vLLM 都行）。
没配 key 时自动退回哈希实现，不会报错。

## 数据

- `data/sample_docs/`：3 篇示例文档，拿来跑通流程
- `data/eval_set.jsonl`：每行 `{"question": ..., "answers": [...], "doc": ...}`
- 想扩到真实数据，换掉这两处即可，代码不用改

## 评测指标

| 指标 | 含义 |
|---|---|
| Recall@k | 命中答案所在块的比例 |
| EM / F1 | 答案与标注的精确/词级重合 |
| cost/q | 每 query 估算成本（元） |
| p95 latency | 95 分位延迟（ms） |

## 预算–效果权衡

![tradeoff](docs/figures/tradeoff.svg)

| 档位 | budget | Recall@3 | cost/query |
|---|---|---|---|
| 紧预算（k=1, BM25） | 0.0005 – 0.001 | 0.9109 | 0.000105 元 |
| 常规（k=2, BM25） | 0.002 – 0.005 | 0.9604 | 0.000196 元 |
| 宽裕（k=5, 混合检索） | 0.010 – 0.050 | 0.9802 | 0.001976 元 |

从中间档升到宽裕档，Recall 只涨 **2 个百分点**，成本却涨 **10 倍**——
所以默认预算放在常规档，难题再单独加码。

复现：`python scripts/sweep.py --set data/eval_set.jsonl`

## 目录

```
src/budget_rag/    核心库（离线可跑，零依赖）
scripts/           ingest / eval
data/              样例文档与评测集
tests/             unittest，标准库即可
docs/              架构与实验记录
```

## 路线图

- [ ] 混合检索（BM25 + 向量）与重排预算
- [ ] 真实 embedding 接入（OpenAI 兼容）
- [ ] 评测集扩到 200 条
- [ ] 成本-召回曲线图（matplotlib）
- [ ] Docker 一键起

## License

MIT
