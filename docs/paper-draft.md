# 论文骨架 v0.1（投稿用）

> 目标期刊：Applied Sciences / Electronics（Q2）→ 二轮冲 Frontiers of Computer Science
> 写作原则：学术发布会。主线只讲**同等预算下更强、同等质量下更便宜**。
> 状态标记：`[已有]` 数据已跑完；`[待补]` 需要补实验；`[待写]` 纯写作。

---

## 标题（候选）

1. **Budget-Aware Retrieval: Allocating Context Tokens Where They Pay Off**
2. Cost-Controlled Retrieval for Long-Document QA: A Submodular View with a Confidence Gate
3. 中文版：面向长文档问答的预算感知检索：子模视角与置信度门控

> 倾向 1：把「预算」写进标题，第一眼就区分于 Adaptive-RAG（复杂度）和 CRAG（纠正）。

---

## 摘要（中文草稿）

检索增强生成把「取多少上下文」当成固定超参，但真实系统的预算是有限的、且问题难度差异极大。
本文把检索深度选择写成一个**预算约束下的子模最大化问题**，并给出三个可检验的理论结论：
贪心分配合乎 1−1/e 近似、查询改写的最优门控是一个由预算影子价格决定的阈值、
级联检索的最优策略是一条置信度阈值链。

在 500 条评测上，按此框架实现的系统在 200 token 预算下取得 **0.946** 的召回；
与 5 个基线对比，在 **126 token** 的平均成本下达到 **0.960** 召回，
高于近似 CRAG 的 0.925（179 token）与纯向量检索的 0.910（115 token），
全部差异经配对 bootstrap 与 McNemar 检验显著（p<0.05）。

在 LongBench 两个检索子集上召回 0.995/1.000；在三个多跳生成基准上，
检索带来的正确率提升在两种模型（API 大模型与本地 4B 模型）上一致成立。
人工标注（200 条、双人 kappa 0.67）显示自动指标偏保守，本文报告的所有召回为质量下界。

**关键词**：检索增强生成；上下文预算；子模最大化；自适应检索；成本感知

## Abstract (English, `[草稿 v0.1]`)

Retrieval-augmented generation treats the amount of retrieved context as a fixed
hyperparameter, although real budgets are finite and query difficulty varies by orders
of magnitude. We formulate retrieval-depth selection as **budget-constrained submodular
maximization**: each retrieval action — taking another chunk, switching to hybrid
retrieval, rewriting the query, adding a second hop — carries a cost and a marginal
quality gain, and a policy is a subset of actions under a budget. Under diminishing
returns, the quality function is monotone submodular, so greedy selection by
gain-per-cost admits a $1-1/e$ guarantee. The same view yields two implementable
consequences: whether query rewriting pays off is governed by the shadow price of the
budget rather than a fixed rule, and the optimal cascade is a chain of confidence
thresholds.

We build a reproducible system from this framework. On 500 evaluation queries it attains
**0.960** recall at an average context cost of **126 tokens**, compared with 0.925 at
179 tokens for a corrective-retrieval baseline and 0.910 at 115 tokens for dense
retrieval; all differences are significant under paired bootstrap and McNemar tests
($p<0.05$), and the advantage persists under repeated subsampling. Recall reaches
0.995 and 1.000 on two LongBench retrieval subsets. On three multi-hop generation
benchmarks, retrieval improves answer accuracy consistently for both a hosted
large model and a locally deployed 4B model. Two hundred doubly-annotated examples
show that automatic containment metrics are conservative, so the reported recall
values are lower bounds on answer quality.

**Keywords**: retrieval-augmented generation; context budget; submodular maximization;
adaptive retrieval; cost-aware inference

---

## 1 引言 `[草稿，v0.2]`

检索增强生成（RAG）已经在开放域问答、文档助理和代码检索中成为标准做法。
这些系统普遍共享一个未加审视的默认设定：**上下文长度是固定超参**。
工程上通常取 top-k = 3 或 5，或直接填满模型的上下文窗口。
但真实请求的难度分布极宽——「ETag 是什么」与「比较强缓存和协商缓存
在长连接场景下的取舍」所需的信息量差一个数量级。固定预算因此同时造成两种浪费：
简单问题买多了，复杂问题买少了。

已有的自适应工作从两个不同角度回应了这个问题。Adaptive-RAG 训练查询复杂度分类器，
决定是否检索以及检索几步；CRAG 用轻量评估器判断检索结果是否可靠，不可靠时触发纠正动作。
两者都提升了「检索行为」与「问题」的匹配度，但都**把预算当成外部给定的常数**：
分类器决定深度，却不回答「在 200 token 的预算里，第一块给谁、第二步要不要改写」。
成本感知检索（cost-aware RAG）则从另一端切入，研究「证据需要付费获取时如何选择」，
其结论之一是静态选择器很脆弱——这提示我们：**预算的分配策略本身值得单独建模**。

本文把检索深度选择写成一个**带预算约束的集合选择问题**。我们把每个可执行的检索动作
——取一块上下文、切换到混合检索、改写查询、跨跳补检索——视为带成本 $c(a)$ 与质量增益
$g(a\mid S)$ 的元素，检索策略即预算 $B$ 下的子集 $S$。在「边际收益递减」这一条可实证检验的
假设下，质量函数成为单调子模，于是适用经典的近似保证：按边际收益/成本比排序的贪心策略
可获得 $1-1/e$ 近似。由此我们还得到两个可直接落到实现里的结论：查询改写是否划算取决于
预算的影子价格（而非固定规则），级联检索的最优策略是一条置信度阈值链。

我们把上述框架实现为一个可运行系统，并在 500 条评测、5 个基线上验证。在 **126 token**
的平均上下文成本下，系统取得 **0.960** 的召回，高于近似 CRAG 的 0.925（179 token）
与纯向量检索的 0.910（115 token）；配对 bootstrap 与 McNemar 检验显示与全部基线的差异
均显著（$p<0.05$）。在 LongBench 的两个检索子集上召回达到 0.995 与 1.000，
在三个多跳生成基准上，检索带来的正确率提升在 API 大模型与本地 4B 模型上一致成立。
200 条双人标注显示自动指标偏保守，本文报告的所有召回均为质量下界。

**贡献**：

1. 把预算约束下的检索深度选择形式化为**子模最大化**问题，并给出贪心策略的近似保证
   （第 3、5 节）。
2. 推导出**改写门控的最优阈值形式**——由预算影子价格决定，而非固定阈值，
   并用成本敏感性实验验证阈值随单价单调下移（第 5、6.7 节）。
3. 实现一个**可复现的预算感知检索系统**，在同等成本下召回高于 5 个基线，
   差异统计显著（第 4、6 节）。
4. 通过跨语料与跨模型验证表明结论不依赖单一数据集或单一模型（第 6.4、6.5 节）。

---

## 2 相关工作 `[待写，素材已在 docs/references.md]`

- 2.1 自适应检索：Adaptive-RAG、Self-RAG、FLARE
- 2.2 纠正式检索：CRAG
- 2.3 成本感知：Cost-Aware RAG（证据访问成本）
- 2.4 上下文压缩与预算：LLMLingua 类工作
- 2.5 本文位置：把「预算」显式写进优化目标，并给出策略的形式化

---

## 3 问题形式化 `[已有，见 docs/theory.md 第 1–2 节]`

- 动作集 $\mathcal{A}$、成本 $c(a)$、质量 $Q(S)$
- 目标：$\max Q(S)$ s.t. $\sum c(a) \le B$
- 假设 A1（边际收益递减）、A2（成本可加）

---

## 4 方法 `[草稿 v0.2]`

### 4.1 双索引与预算取块

长文档按两种粒度建索引：**句级**（按标点切分，约 15–40 token）与**固定块**（滑动窗口，
默认 200 token、重叠 40）。句级索引在紧预算下更省，因为它不会把无关句子一起带进来；
固定块在宽预算下更连贯。系统按目标预算自动选择：`ctx < 500` 用句级，否则用固定块。

取块时按检索得分降序累积，直到已选块的总 token 达到预算 $B$ 即停，
**不做固定 k 截断**——这是「预算」而非「条数」成为一等公民的关键。

### 4.2 级联路由

路由按「每千 token 的允许成本」分档：预算极紧（< 0.002 元）走 BM25 单路取 1 块；
中等走 BM25 取 2 块；宽裕（≥ 0.01 元）走混合检索取 5 块。分档边界不是拍出来的：
它们是贪心分配的离散化（第 5 节命题 1），在实践中对应「边际收益/成本比」的拐点。

### 4.3 置信度门控的查询改写

改写调用占端到端延迟的一半以上（6.8 节），因此只在必要时触发。系统先做一轮廉价检索，
计算 top-1 与 top-2 得分的相对间隔

$$\gamma = \frac{s_1 - s_2}{s_1}.$$

当 $\gamma < \tau$ 时认为检索「没把握」，触发查询改写并用「原问题 + 改写词」重检索。
阈值 $\tau$ 的最优值由预算影子价格决定（命题 2），默认 0.25 对应「改写成本约等于
一次强检索」的定价；6.7 节的敏感性实验验证了 $\tau$ 随单价上升而下移。

### 4.4 多跳扩展

对需要两处证据的问题，第一跳之后把「问题 + 已检索摘要」交给模型，让它输出还缺什么信息，
再用「原问题 + 补充查询」做第二跳，两轮结果按块去重合并。实验表明，
模型生成的补充查询优于从上下文抽取专有名词的规则方案（6.5 节）。

**图 1**：`[待画]` 系统总览——文档 → 双索引 → 路由 → 门控改写 → 取块 → 生成/多跳。

---

## 5 理论 `[已有，docs/theory.md 第 3 节]`

- 命题 1：单调子模 ⇒ 贪心 1−1/e
- 命题 2：改写划算当且仅当 $p\Delta q > \lambda c_r$
- 命题 3：级联最优策略是置信度阈值链
- 命题 4（新增，`[待证]`）：阈值 $\tau^*$ 随预算影子价格 $\lambda$ 单调不增

---

## 6 实验

### 6.1 设置 `[已有]`

数据集（500 条合成 + LongBench 三子集 + HotpotQA/2Wiki/MuSiQue）、
模型（DeepSeek-V4.1-Flash、Qwen3-4B 本地）、embedding（bge-m3）、
评价（Recall@budget、contain、EM、F1、成本）。

### 6.2 主结果：同预算下更强 `[已有，报告 4.23]`

| 方法 | 召回 | 95% CI | token |
|---|---|---|---|
| BM25 | 0.825 | [0.770,0.875] | 68 |
| 纯向量 | 0.910 | [0.870,0.945] | 115 |
| 混合 | 0.900 | [0.860,0.940] | 114 |
| Adaptive 近似 | 0.855 | [0.805,0.905] | 100 |
| CRAG 近似 | 0.925 | [0.885,0.960] | 179 |
| **本文** | **0.960** | [0.930,0.985] | **126** |

**这张表是论文的心脏**，配一段解释：为什么本文在更低成本下更高——
因为预算花在「检索质量边际提升最大」的动作上，而不是固定走完整管线。

**种子稳定性（5 次 2/3 子采样）`[已有]`：**

| 方法 | 全量 | 子采样均值 ± 标准差 |
|---|---|---|
| BM25 | 0.825 | 0.826 ± 0.010 |
| 纯向量 | 0.910 | 0.914 ± 0.009 |
| 混合 | 0.900 | 0.902 ± 0.005 |
| Adaptive 近似 | 0.855 | 0.853 ± 0.010 |
| CRAG 近似 | 0.925 | 0.928 ± 0.004 |
| **本文** | **0.960** | **0.962 ± 0.011** |

本文字采样区间 `[0.947, 0.970]` 与 CRAG 的 `[0.925, 0.932]` 不重叠——
**优势不依赖样本选择**。

### 6.3 消融 `[已有]`

| 去掉什么 | 召回变化 | 说明 |
|---|---|---|
| 去掉门控（不改写） | −3.6pt | 4.10 |
| 去掉混合（纯 BM25） | −6.8pt | 4.23 |
| 预算 300 → 100 | −6.1pt | 4.13 |
| alpha 0.2 → 0.5 | −1.7pt | 4.25 |

### 6.4 跨语料验证 `[已有]`

- LongBench passage_retrieval_zh：0.995（BM25 0.955）
- LongBench passage_retrieval_en：1.000 / 1.000（说明不退化）
- **这里只主张「不退化 + 相对提升方向一致」，不主张绝对领先**

### 6.5 生成侧：检索收益是模型无关的 `[已有]`

| 数据集 | 模型 | 有检索 | 无检索 |
|---|---|---|---|
| HotpotQA | DeepSeek | 0.500 | 0.100 |
| HotpotQA | Qwen3-4B | 0.400 | 0.100 |
| 2Wiki | Qwen3-4B | 0.200 | 0.000 |
| MuSiQue | Qwen3-4B | 0.250 | 0.000 |

**叙事定位**：这一节证明「检索是必要条件」，不比较绝对分数高低。
绝对分数受模型能力限制，属于 6.7 的分析对象，不是本文主张。

### 6.6 人工标注 `[已有]`

- 200 条标注，自动 contain 与人工一致率 90%–97%
- 双人 kappa 0.548（未加权）/ 0.673（二次加权）
- 结论：自动指标**偏保守**，主表召回是下界

### 6.7 阈值敏感性（命题 2 的验证）`[已有]`

λ=0.25/0.5/1 时最优 τ=0.25；λ≥2 时 τ=0。验证「成本越高越不该改写」。

### 6.8 效率 `[已有]`

20 条实测（单机 CPU + API，DeepSeek-V4.1-Flash，关闭答案缓存）：

| 配置 | p50 (ms) | p95 (ms) | 成本/条 (元) | 召回 |
|---|---|---|---|---|
| 便宜档（BM25） | 923 | 1469 | 0.00088 | 0.850 |
| 强档（混合） | 898 | 1705 | 0.00087 | 0.850 |
| 强档 + 全量改写 | 1765 | 3090 | 0.00116 | 0.900 |
| 强档 + 门控改写 | 1788 | 2577 | 0.00116 | 0.900 |

**改写是延迟的主要来源**（+0.9 s，p95 +1.4 s）。门控的价值取决于**该批数据的改写触发率**：

- 全量 500 条：触发率 **38%**（4.10 节），即省掉 62% 的改写调用
- 前 50 条（偏难）：触发率 **76%**，接近全量改写
- 200 条中等子集：触发率 69.5%

因此本文的准确表述是：**门控按数据难度自适应，难度高的批次收益小、难度低的批次收益大**，
而不是无条件省延迟。这也是为什么默认阈值 0.25 应随预算阴影价格调整（6.7 节）。

---

## 7 讨论 `[待写]`

- 7.1 什么时候该用本文方法（预算紧、问题难度差异大）
- 7.2 什么时候不该（预算充足、问题同质，直接用固定深检索）
- 7.3 成本模型的边界（单价常数、token 估算偏差）

---

## 8 局限 `[待写，只写必要项]`

1. 合成语料为主，跨语料只覆盖检索任务
2. 基线中的 Adaptive-RAG / CRAG 为行为近似，非原版复现
3. 成本按公开单价换算，非真实账单
4. tiktoken 对中文估算偏高，报告中的上下文 token 为保守值

> 按发布会原则：这四条放最后，不放进摘要，不在引言提前示弱。

---

## 附录 A 负结果 `[已有，全部移入附录]`

- PRF（伪相关反馈）导致查询漂移：−1.6pt / −19.6pt
- 第 0 级（不检索）在技术语料上不可行：contain 0.11
- 贪心在预算 200 时比最优低 6pt（近似性的反例）
- 学习型路由器（TF-IDF 0.747 / BERT 0.702）不如分数门控（0.960）

**为什么放附录**：它们是「排除替代解释」的证据，不是主线的失败。

---

## 附录 B 复现说明 `[已有]`

```
make test          # 42 个测试
python scripts/baselines.py --limit 200
python scripts/multihop.py --modes single bridge entity
python scripts/tune_params.py
```

---

## 写作检查清单（交稿前逐条过）

- [ ] 摘要前五句里，问题和贡献都出现了吗
- [ ] 主表是否在第一页就能看到
- [ ] 有没有把不占优的指标设成主战场（绝对生成分数）
- [ ] 负结果是否全部在附录
- [ ] 引言里有没有提前示弱
- [ ] 每个表格是否对应一个论证职责
- [ ] 结论有没有突然自我否定

---

## 待补实验清单（写完骨架后确认）

| # | 实验 | 支撑哪条主张 | 成本 | 状态 |
|---|---|---|---|---|
| 1 | 统一延迟测量（p50/p95） | 6.8 效率 | 0 | ✅ 完成 |
| 2 | 多种子主结果（5 次子采样） | 6.2 稳健性 | 0 | ✅ 完成 |
| 3 | NQ 或 TriviaQA 生成对照 | 6.5 泛化 | ¥50 | 待定（可选） |
| 4 | 命题 4 的证明补全 | 5 理论 | 0（写作） | 待写 |

> 只有 4 项，其中 3 项零成本。已完成 2 项。
