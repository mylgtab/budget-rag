# 成本感知检索：预算、级联与评测基线

> 工作草稿（v0.3）。所有数字可用 `make all` 复现。

## 摘要

长文档问答中，检索深度与上下文长度直接决定 token 成本，但并非每个问题都值得深检索。
我们实现了一个预算可调的 RAG 检索层，比较四种策略：固定浅检索、固定深检索、按全局预算路由、
以及按置信度级联升级。在 200 条合成问答上，级联策略在改写题集上取得 0.970 的 Recall@3，
成本为固定深检索的 47%；在原始问句集上与深检索持平，成本为 33%。
我们也报告一个负结果：在词汇重合度高的合成集上，简单 BM25 top-3 已接近饱和，
与深检索的差距落在置信区间内，说明**合成数据不足以区分策略**。

## Abstract

Retrieval depth dominates the token cost of document QA, yet not every question deserves a deep
retrieval pass. We implement a budget-aware retrieval layer and compare four policies: fixed
shallow, fixed deep, global-budget routing, and confidence-based cascading. On 200 synthesized
questions, the cascade reaches 0.970 Recall@3 on a paraphrased split at 47% of the deep-retrieval
cost, and matches deep retrieval on the literal split at 33% of the cost. We also report a negative
result: on lexically overlapping synthetic data, plain BM25 top-3 already saturates, so differences
between policies fall inside the confidence interval — synthetic data cannot separate them.

## 1 问题

RAG 的成本由两部分构成：检索回来的上下文 token，以及生成答案的 token。
固定 top-k 的做法对所有问题一视同仁，简单问题被过度检索，难问题又召回不足。

设单次查询预算为 `B`，我们希望在这个预算内最大化 Recall@k，同时让实际花费尽量靠近 `B` 而不是超过它。

## 2 方法

**2.1 预算三档（`adaptive-budget`）**
按 `B` 划分检索深度：紧预算 `k=1` 纯 BM25；常规 `k=2` BM25；宽裕 `k=5` 混合检索（BM25 与向量归一化加权）。
问题长度、实体数、是否含比较类词汇决定是否额外加码。

**2.2 置信度级联（`cascade-conf`）**
先做 BM25 `k=2`，计算 top1 与 top2 的相对差距 `(s1-s2)/s1`；
若差距小于阈值（默认 0.25），认为检索拿不准，升级为混合检索 `k=5`；否则直接返回。
这样成本随问题难度自动分摊，而不是随全局预算。

**2.3 成本模型**
按 1k token 计价：BM25 档 0.0005 元，混合档 0.002 元。
上下文 token 按字数/1.5 粗估。该模型是简化假设，见第 6 节。

## 3 实验设置

- 语料：10 篇技术笔记（操作系统、网络、数据库、Python、Git、Docker、算法、测试、HTTP 缓存、RAG），共 200 条事实句
- 评测集 A（literal）：模型从原文抽问，答案逐字来自原文，200 条
- 评测集 B（paraphrased）：额外要求问句不出现原文术语，200 条
- 指标：Recall@k（答案句是否进入召回上下文）、EM、F1、每 query 成本、p95 延迟
- 置信区间：对逐条结果做 1000 次自助重采样，取 95% 区间
- 生成模型：DeepSeek-V4.1-Flash；检索与打分为纯 CPU、无外部依赖

## 4 结果

### 4.1 原始问句集（literal, n=200）

| 策略 | Recall@3 (95% CI) | F1 | cost/q (元) |
|---|---|---|---|
| `naive-bm25-k3` | 0.980 [0.960, 0.995] | 0.859 | 0.000291 |
| `fixed-bm25-k1` | 0.911 [0.871, 0.946] | 0.876 | 0.000105 |
| `fixed-hybrid-k5` | 0.980 [0.960, 0.995] | 0.860 | 0.001936 |
| `adaptive-budget` | 0.980 [0.960, 0.995] | 0.860 | 0.001976 |
| `cascade-conf` | 0.980 [0.960, 0.995] | 0.869 | 0.000644 |

### 4.2 改写问句集（paraphrased, n=200）

| 策略 | Recall@3 (95% CI) | F1 | cost/q (元) |
|---|---|---|---|
| `naive-bm25-k3` | 0.965 [0.935, 0.990] | 0.764 | 0.000295 |
| `fixed-bm25-k1` | 0.855 [0.810, 0.900] | 0.753 | 0.000105 |
| `fixed-hybrid-k5` | 0.975 [0.955, 0.995] | 0.757 | 0.001942 |
| `adaptive-budget` | 0.975 [0.955, 0.995] | 0.757 | 0.001995 |
| `cascade-conf` | 0.970 [0.945, 0.990] | 0.761 | 0.000917 |

### 4.3 真实模型作答（202 条，账单 token）

前两节用离线抽取作答（零成本），只衡量检索。本节让模型读上下文生成答案，
token 数直接取自 API 返回的 `usage`，成本按 2 元/百万输入、8 元/百万输出计算。

| 版本 | 改动 | EM | Contain | F1 | 输入/输出 token | cost/q |
|---|---|---|---|---|---|---|
| v1 | 提示词只说「根据资料回答」 | 0.228 | 0.624 | 0.805 | 892.8 / 17.8 | 0.001928 元 |
| v2 | 要求「只输出答案、逐字照抄」+ 前缀清洗 | **0.520** | **0.985** | 0.813 | 957.8 / 11.4 | 0.002007 元 |

**EM 翻倍，Contain 达到 98.5%。** 但要注意：v1 的 EM 低不是答错，而是模型加了
「根据资料[1]，」前缀并改写措辞；Contain 指标（预测与标准答案互相包含）才反映真实质量。
这也说明**单看 EM 会低估系统**，评估指标本身需要被审视。

全套 202 条跑一次约 3 分钟、花 0.4 元。

## 5 讨论

**5.1 级联在改写集上位于前沿。**
0.970 与深检索的 0.975 相差 0.5 个百分点，但成本只有 47%。
在原始问句集上，级联与深检索同为 0.980，成本只有 33%——不过此时 naive top-3 也能做到 0.980，
说明该集合的区分度不足。

**5.2 负结果：合成集饱和。**
两个集合上，除 `fixed-bm25-k1` 外的所有策略，Recall 差异都落在置信区间内。
原因很直接：问题由同一批句子生成，词汇高度重合，BM25 几乎总能命中。
这提示我们后续必须换真实数据集，否则任何「策略更优」的结论都不可信。

**5.3 预算路由的局限。**
`adaptive-budget` 在预算宽裕时等价于全量深检索，因此成本和 `fixed-hybrid-k5` 几乎一致。
全局预算只控制「平均花多少」，控制不了「哪里该多花」——这正是级联要解决的问题。

## 6 局限

1. 语料与问题均为合成，存在同源偏差，指标绝对值不可外推
2. embedding 为离线哈希占位，尚未接入真实语义模型
3. 成本按固定单价粗估，未接入真实计费账单
4. 单机 CPU 评测，延迟数字不代表生产环境
5. 只测了 Recall/EM/F1，未做人工偏好或答案忠实度评估

## 7 下一步

1. 接入 LongBench / Natural Questions 子集，重跑全部策略
2. 接入真实 embedding 与 reranker，验证混合检索的增益
3. 级联阈值在开发集上搜索，而不是手设
4. 多 seed 划分，报告均值与方差
5. 补一份人工标注的 100 条，校准自动指标
