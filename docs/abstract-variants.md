# 摘要版本对照

三种长度的现成版本，按目标期刊取用。**英文主稿 `paper-en.md` 用完整版**。

**期刊上限参考**

| 期刊 | 摘要上限 | 用哪个版本 |
|---|---|---|
| Applied Sciences（MDPI） | 约 200 词 | 200 词版 |
| Knowledge-Based Systems（Elsevier） | 约 250 词 | 250 词版 |
| Expert Systems with Applications | 约 250 词 | 250 词版 |
| 中文期刊 / 复试材料 | 无硬限 | 中文版 |

---

## 200 词版（MDPI，实计 188 词）

Retrieval-augmented generation usually fixes how much context to retrieve, although budgets are
finite and query difficulty varies widely. We formulate retrieval-depth selection as
budget-constrained submodular maximization over priced actions—another chunk, hybrid retrieval, query
rewriting, a second hop—and show that gain-per-cost greedy inherits the classical 1−1/e guarantee when
returns diminish. Two consequences follow: rewriting should be gated by the shadow price of the budget
rather than a fixed rule, and the optimal cascade is a chain of confidence thresholds. On a 200-query
benchmark the system reaches 0.960 recall at 126 tokens, versus 0.925 at 179 for a corrective baseline
and 0.910 at 115 for dense retrieval (p<0.05); on 500 end-to-end queries it matches fixed top-3
containment at about half the prompt cost (474 versus 972 tokens). Recall is 0.995 and 1.000 on two
LongBench retrieval subsets, retrieval improves multi-hop accuracy for a locally deployed 4B model and
for a hosted large model on HotpotQA, and 200 doubly-annotated examples show the automatic metric is
conservative. Budget-aware depth selection is thus a practical route to better accuracy at lower
context cost.

---

## 250 词版（Elsevier，实计 197 词）

Retrieval-augmented generation typically treats the amount of retrieved context as a fixed
hyperparameter, yet inference budgets are finite and query difficulty varies by orders of magnitude. We
formulate retrieval-depth selection as budget-constrained submodular maximization over priced
actions—another chunk, hybrid retrieval, query rewriting, a second hop. Because quality exhibits
diminishing returns, the objective is monotone submodular, so gain-per-cost greedy inherits the
classical guarantees ($1-1/e$ under a cardinality budget, $(1-1/e)/2$ under a cost budget). This view
yields two implementable consequences: whether rewriting pays off follows from the shadow price of the
budget rather than a fixed rule, and the optimal cascade is a chain of confidence thresholds. On a
200-query benchmark with bge-m3 embeddings the system attains 0.960 recall at 126 tokens, against 0.925
at 179 for a corrective baseline and 0.910 at 115 for dense retrieval; the differences are significant
under paired bootstrap and McNemar tests ($p<0.05$) and survive repeated subsampling. On 500 end-to-end
queries it matches fixed top-3 containment at roughly half the prompt cost, and recall reaches 0.995
and 1.000 on two LongBench retrieval subsets. Two hundred doubly-annotated examples show the automatic
metric is conservative.

---

## 中文版

检索增强生成通常把「取多少上下文」当成固定超参，但真实系统的预算有限、问题难度差异极大。本文把检索深度选择写成预算约束下的子模最大化：每个检索动作（再取一块、切混合检索、改写查询、加一跳）都有成本与边际收益，策略即预算下的动作子集。在边际收益递减下质量函数单调子模，按「收益/成本」贪心即可继承 $1-1/e$ 的近似保证。由此得到两个可直接落地的结论：改写是否划算由预算的影子价格决定，而非固定规则；最优级联是一条置信度阈值链。在 200 条检索评测上，系统以 126 token 的平均上下文取得 0.960 召回，高于纠正式基线（0.925，179 token）与稠密检索（0.910，115 token）；差异在配对 bootstrap 与 McNemar 检验下显著，且经重复子采样仍成立。在 500 条端到端评测上，系统以约一半的 prompt 成本达到固定 top-3 的同等质量；两个 LongBench 检索子集上召回为 0.995 与 1.000；在三个多跳生成基准上检索提升本地 4B 模型与托管大模型的正确率；200 条双人标注显示自动指标偏保守，故报告值为召回下界。上述结果表明，预算感知的检索深度选择是「更低成本、更高准确率」的一条可行路径。
