# Changelog

所有值得一提的改动都记在这里。版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## v0.5.0 — 2026-10-22

**检索质量与可信度**

- 接入真实 embedding（`BAAI/bge-m3`，1024 维），纯向量 Recall 0.938，比哈希占位高 5.4pt
- 混合权重改为 dev/test 分离调参：`alpha=0.2` 在同预算下 +1.7pt（旧默认 0.5 是在测试集上扫的，已纠正）
- 用对话模型做重排的对照实验：预算截断时 +5.5pt，预算充足时无效
- 新增 `scripts/embed_compare.py` / `tune_alpha.py` / `tune_params.py` / `llm_rerank.py`
- 报告补 4.11–4.13 三节（重排、真实 embedding、调参）

## v0.4.0 — 2026-10-22

**工程加固**

- token 计数接入 tiktoken（未安装时自动退回估算）
- 答案与改写结果落盘缓存，重复问题不再花钱
- 测试从 8 个扩到 27 个，覆盖门控、预算检索、缓存、kappa
- 指标收进 `metrics.py`，修复 F1 分词 bug（`norm()` 去空格导致英文粘连）
- README 加终端演示 GIF

## v0.3.0 — 2026-10-21

**四策略对比与报告**

- `scripts/bench.py`：naive / fixed-k / adaptive / cascade 同表对比 + 1000 次自助法置信区间
- 级联检索：47% 成本拿到深检索 99.5% 召回
- 新增改写题集 `eval_hard.jsonl`
- Dockerfile + Makefile
- `docs/report.md`：中文正文 + 英文摘要（含负结果讨论）

## v0.2.0 — 2026-10-21

**数据与曲线**

- 评测集扩到 202 条（10 篇文档，LLM 合成 + 答案逐字校验）
- 预算三档：Recall 0.911 / 0.960 / 0.980，对应成本 0.000105 / 0.000196 / 0.001976 元
- `scripts/sweep.py`：零依赖输出 SVG 曲线
- 新增 OpenAI 兼容 embedding 适配层

## v0.1.0 — 2026-10-21

**首个可运行版本**

- FastAPI + BM25 / 向量 / 混合检索
- 成本感知路由（cheap / strong）
- 离线评测：Recall@3 / EM / F1 / cost / p95
- 8 个单元测试 + CI 四组矩阵
