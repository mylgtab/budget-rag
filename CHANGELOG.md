# Changelog

所有值得一提的改动都记在这里。版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## v0.10.0 — 2026-10-22

**第二跳的构造策略对比**

- `scripts/multihop.py` 增加 `entity` 模式：从第一跳抽专有名词做补充查询
- 结果：模型生成 0.640 > 实体抽取 0.580 > 单轮 0.560
- 实体方案 token 878（比模型方案省 33%），可作低成本折中
- 记录测量噪声：单轮两次测到 0.540 / 0.560，约 ±2pt

## v0.9.0 — 2026-10-22

**多跳检索**

- 新增 `scripts/multihop.py`：单轮 vs 两跳（模型生成补充查询）对照
- HotpotQA 50 条：contain 0.540 → 0.620，EM 0.400 → 0.500，命中率 0.640 → 0.720
- 代价：平均 token 658 → 1315（约 2 倍）
- 记录残留问题：仍有 28% 的题两跳都未命中，补充查询需要更可靠的构造方式

## v0.8.0 — 2026-10-22

**生成质量的外部验证**

- 新增 `scripts/longbench_qa.py`：检索 → 生成 → 判定的完整链路，支持 rag / none 对照
- HotpotQA（50 条）：RAG contain 0.540 vs 不检索 0.200，检索命中率 0.64
- 记录失败模式：漏检 36%、找到但没答对约 10%
- embedding 请求分批（每批 32 条），修复长文档建索引时的超时

## v0.7.0 — 2026-10-22

**评估补全与可用性**

- 忠实度评估：100 条中 supported 94% / unsupported 3%（新增 `scripts/faithfulness.py`）
- LongBench 英文子集：BM25 与向量均 1.000（记录天花板效应）
- 成本模型纳入 embedding 真实用量（`RAG_PRICE_EMBED`），trace 增加 `embed_tokens`
- token 估算校准系数 `RAG_TOKEN_FACTOR`（DeepSeek 实测约 0.54，默认关闭）
- 演示页面：`/ui/` 单页界面，显示路径、成本、上下文与耗时
- 缓存版本化：`CACHE_VERSION` 进 key，改结构后旧条目自动失效

## v0.6.0 — 2026-10-22

**可用性与可信度**

- API 加 Bearer 鉴权与每 IP 令牌桶限流（`RAG_API_TOKEN` / `RAG_RATE_LIMIT`）
- 多 seed 自助重采样：Recall 0.8580 ± 0.0148（修正「只打乱顺序没有方差」的错误）
- token 校准：tiktoken 对中文高估约 84%，账单改用 API `usage`
- 接 LongBench `passage_retrieval_zh`：向量 0.995 vs BM25 0.955（跨语料验证）
- 向量缓存 SQLite 化：冷 46.6s → 热 4.6s
- 测试 27 → 42 个（API 鉴权/限流、LongBench 解析、缓存往返）
- 借鉴 Ponytail 的懒惰阶梯做「第 0 级不检索」实验（负结果，记录在案）

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
