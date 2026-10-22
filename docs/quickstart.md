# 五分钟上手

目标：**30 分钟内复现 README 首页那张主表**。全程无需 GPU。

## 0 前提

- Python 3.10+
- 一个 DeepSeek API key（可选：不填则跑离线抽取模式，主表的检索召回不受影响）
- 一个 OpenAI 兼容的 embedding key（可选：不填则用离线哈希向量，指标会低约 5pt）

## 1 安装（1 分钟）

```bash
git clone https://github.com/mylgtab/budget-rag.git
cd budget-rag
python -m pip install -e ".[dev]"
```

想完全复现作者环境（含精确版本）用 `requirements.lock`：

```bash
python -m pip install -r requirements.lock
```

## 2 自检（30 秒）

```bash
make check
```

预期：44 个测试全绿，随后跑 50 条离线评测，最后一行类似

```
【offline】n=50 recall@3=0.9xx em=0.xx f1=0.xx cost=0.000xxx
```

## 3 跑主表（5–10 分钟）

```bash
export DEEPSEEK_API_KEY=sk-...
export RAG_EMBED_BASE=https://api.siliconflow.cn/v1
export RAG_EMBED_MODEL=BAAI/bge-m3
export RAG_EMBED_KEY=sk-...

make bench            # = scripts/baselines.py --limit 200
```

预期输出（与 README 首页一致）：

| 策略 | 召回 | token |
|---|---|---|
| bm25_k3 | 0.825 | 68 |
| dense_k5 | 0.910 | 115 |
| hybrid_k5 | 0.900 | 114 |
| adaptive | 0.855 | 100 |
| crag | 0.925 | 179 |
| **ours** | **0.960** | **126** |

## 4 起服务看界面（1 分钟）

```bash
make api
# 打开 http://127.0.0.1:8000/ui/
```

输入问题即可看到答案、走了哪条路径、真实成本与上下文 token。
没有 `index.json` 时会自动用 `data/sample_docs` 建索引。

## 5 跑公开基准（可选，本地模型零成本）

```bash
python scripts/fetch_longbench.py --subsets hotpotqa 2wikimqa musique
python scripts/longbench_qa.py --file data/longbench/hotpotqa.jsonl --limit 20
```

仓库里还带了每类 15 条的小样本快照 `data/longbench_sample/`，
点开即可看格式，不需要先下载 111 MB 的原始包。

本地模型（可选）：`ollama create qwen3-4b -f <Modelfile>` 后

```bash
python scripts/longbench_qa.py --file data/longbench/hotpotqa.jsonl --limit 20 \
  --model qwen3-4b --base http://127.0.0.1:11434/v1 --key ollama --no-think
```

## 常见坑

| 现象 | 原因 / 解法 |
|---|---|
| `tiktoken` 装不上 | 可以不装，代码自动退回字数估算 |
| embedding 请求 400 | 空文本或批太大；本仓库已按 32 条分批 |
| 延迟 9 ms 假数据 | 答案命中缓存；测延迟要 `RAG_CACHE=0` |
| `make bench` 很慢 | 200 条 × 6 策略 × LLM 调用；先 `--limit 20` 试 |
| 中文显示乱码（Windows 控制台） | `chcp 65001` 或 `set PYTHONIOENCODING=utf-8` |
| 代理环境拉不动模型 | HuggingFace 用 `HF_ENDPOINT=https://hf-mirror.com` |

## 接下来读什么

- 论文草稿：`docs/paper-draft.md`（Word 版 `docs/paper-draft.docx`）
- 全部实验与负结果：`docs/report.md`
- 形式化与三个命题：`docs/theory.md`
- 代码结构与环境坑：[`HANDOFF.md`](../HANDOFF.md)
