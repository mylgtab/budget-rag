# Knowledge-Based Systems（KBS）投稿包

> 目标：Elsevier 订阅制发表，**不付 APC**。若被误选 Open Access，APC 约 3,400 美元——投稿时务必选
> 「Subscription」路线。
>
> ⚠️ 链接以官网核对为准（本机 VPN 关闭，未能实时验证）。

## 一、期刊基本信息

| 项 | 内容 |
|---|---|
| 全称 | Knowledge-Based Systems |
| 出版方 | Elsevier |
| ISSN | 0950-7051 |
| 分区 | JCR Q1（计算机·人工智能） |
| 投稿系统 | Editorial Manager：`https://www.editorialmanager.com/knosys/` |
| 期刊主页 | `https://www.sciencedirect.com/journal/knowledge-based-systems` |
| 费用 | 订阅制**免费**；选 OA 才收 APC |
| 一审周期 | 通常 2–4 个月（Elsevier 平均偏慢） |

## 二、KBS 与 MDPI 的六处差异

| 项 | MDPI | **KBS** | 我们的现状 |
|---|---|---|---|
| 摘要长度 | ~200 词 | **≤250 词** | 有 197 词版 ✅ |
| Highlights | 不要求 | **要 3–5 条，每条 ≤85 字符** | 需新写 |
| 参考文献 | MDPI 数字 | Elsevier 数字（差不多） | 已转 ✅ |
| 图片 | 可嵌入正文 | 建议**单独上传**，300 dpi | 有 PNG 2× ✅ |
| 声明 | Declarations 段 | **Declaration of Interest + CRediT** | 有雏形，需改格式 |
| 审稿 | 单盲 | 视期刊设置（可能匿名审） | 备一份匿名版以防万一 |

## 三、Highlights（5 条，每条 ≤85 字符）

> 已按字符数校验，可直接粘贴。

1. Retrieval depth is cast as budget-constrained submodular maximization over priced actions.
2. Gain-per-cost greedy inherits 1−1/e guarantees under cardinality and cost budgets.
3. Rewriting is gated by the budget's shadow price, not by a fixed confidence threshold.
4. 0.960 recall at 126 tokens, beating corrective retrieval (0.925 at 179) and dense (0.910 at 115).
5. A reproducible open-source system with 65 tests and CI; negative results are reported.

## 四、Cover Letter（KBS 版）

Dear Editors,

We submit the manuscript **"Budget-Aware Retrieval: Allocating Context Tokens Where They Pay Off"**
for consideration as a research article in *Knowledge-Based Systems*.

**Problem.** Knowledge-based systems that retrieve external evidence usually treat retrieval depth as
a fixed hyperparameter. Real budgets are finite and question difficulty varies by orders of magnitude,
so a fixed depth is wasteful on easy queries and insufficient on hard ones. Existing adaptive methods
decide whether and how many steps to retrieve, but keep the budget exogenous: none of them answers
which action deserves the next unit of budget.

**Contribution.** We formulate retrieval-depth selection as budget-constrained submodular maximization
over a set of priced actions—taking another chunk, switching to hybrid retrieval, rewriting the query,
adding a second hop. Under diminishing returns the objective is monotone submodular, so gain-per-cost
greedy inherits the classical guarantees. Two implementable consequences follow: a closed-form rewriting
threshold governed by the shadow price of the budget, and an optimal cascade that is a chain of
confidence thresholds. Experiments verify both directions.

**New since the first draft.** The evaluation now runs on 312 official documentation pages (16,823
chunks) and on three BEIR subsets (scifact, nfcorpus, fiqa). On real documentation the system matches a
hybrid retriever at equal budget, and the transferable gain is a **7-21% reduction in context tokens**
from margin-based adaptive depth; on BEIR scifact the reduction reaches 27%. We also add a calibration
protocol that turns a **quality target** into a budget: twenty labelled questions predict the required
budget within 1.1-1.6x of the oracle and meet the target 76-93% of the time, while unreachable targets
are refused. A measurement of the latency-token exchange rate (4.0-13.4 tokens per millisecond of
retrieval, against 2.15 ms per token of prefill on CPU) shows when that trade pays.

**Results.** Against five baselines under a common budget, the system reaches 0.960 recall at 126
tokens, versus 0.925 at 179 for an approximation of corrective retrieval and 0.910 at 115 for dense
retrieval (paired bootstrap and McNemar, p < 0.05). On 500 end-to-end queries it matches fixed top-3
containment at about half the prompt cost. Results do not degrade on LongBench retrieval subsets, and
retrieval improves multi-hop accuracy for a locally deployed 4B model and for a hosted large model.

**Scope fit.** The paper contributes a decision framework for knowledge acquisition under resource
constraints—what to acquire, in which order, and when to stop—together with guarantees and an
open-source implementation, which we believe matches the journal's interest in knowledge-based
methods that are both principled and deployable.

**Reproducibility.** Code, evaluation sets and scripts are released under the MIT license
(`https://github.com/mylgtab/budget-rag`, v1.0.0). A stranger can reproduce the main table in about
thirty minutes. Negative results are reported in an appendix.

The manuscript is original, is not under consideration elsewhere, and the author declares no conflict
of interest.

Sincerely,
Qiaomu Li
School of Mathematics and Information Science, Zhangjiakou University, Zhangjiakou 075000, China
lqm050509@gmail.com — ORCID 0009-0003-7912-3918

## 五、Declaration of Interest

> 粘贴到系统对应字段。

The author declares that he has no known competing financial interests or personal relationships that
could have appeared to influence the work reported in this paper.

## 六、CRediT Author Statement

**Qiaomu Li:** Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation,
Data curation, Writing – original draft, Writing – review & editing, Visualization.

## 七、投稿前必做（KBS 特有）

| # | 事项 | 状态 |
|---|---|---|
| 1 | 摘要换成 ≤250 词版 | ✅ 有（197 词） |
| 2 | 生成 Highlights | ✅ 见上 |
| 3 | **出匿名版正文**（去掉姓名/单位/ORCID/致谢） | ❌ 待做 |
| 4 | 图片单独导出 300 dpi | ✅ PNG 2× 可用 |
| 5 | 参考文献核对 Elsevier 风格 | 🟡 基本符合 |
| 6 | 检查 Data Availability 链接可访问 | ✅ |
| 7 | 系统里选 **Subscription**，不选 OA | ❌ 需注意 |

## 八、本鲸的判断

KBS 的审稿人比 MDPI 严，最可能挑的两条是：

1. **语料太小**（C1）——344 个块的检索任务，KBS 审稿人大概率要求真实语料
2. **创新性偏组合**（A1）——子模框架是标准工具

所以投 KBS 前，**C1（换真实语料）建议先做**。MDPI 可以带着小语料投，KBS 不太行。

## 九、费用核对

| 路线 | 费用 |
|---|---|
| Subscription（订阅制） | **0** |
| Open Access | 约 3,400 美元（≈2.4 万元） |

投稿系统最后一步会让你勾选，**默认常是 OA，要手动改成 Subscription**。
