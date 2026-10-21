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
