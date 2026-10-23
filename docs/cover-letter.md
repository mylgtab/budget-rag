# 投稿材料：Cover Letter 草稿

> 目标刊：Applied Sciences（MDPI）或 Electronics（MDPI）。替换方括号内容后即可用。
> 注意：MDPI 投稿系统里 cover letter 是可选项，但写了更容易被分配到合适的编辑。

---

**To the Editorial Office of *Applied Sciences***

Dear Editors,

We submit the manuscript **"Budget-Aware Retrieval: Allocating Context Tokens Where They
Pay Off"** for consideration as a research article in *Applied Sciences*.

**The problem.** Retrieval-augmented generation treats the amount of retrieved context as a
fixed hyperparameter. In practice the budget is finite and query difficulty varies by orders of
magnitude, so a fixed depth is simultaneously wasteful on easy questions and insufficient on
hard ones. Existing adaptive methods decide *whether* and *how many steps* to retrieve, but keep
the budget exogenous, and therefore do not answer which action deserves the next unit of cost.

**What we do.** We formulate retrieval-depth selection as budget-constrained submodular
maximization over a set of priced actions—taking another chunk, switching to hybrid retrieval,
rewriting the query, adding a second hop. Under an empirically testable diminishing-returns
assumption the quality function is monotone submodular, which yields an approximation guarantee
for density-ordered greedy allocation and two implementable consequences: the rewriting threshold
is set by the shadow price of the budget rather than by a hand-tuned constant, and the optimal
cascade is a chain of confidence thresholds. We also make the evaluation protocol part of the
method by reporting Recall@budget, so quality and cost stay comparable across methods.

**Main results.** Against five baselines under a common budget, the system reaches **0.960**
recall at an average context cost of **126 tokens**, compared with 0.925 at 179 tokens for a
corrective-retrieval approximation and 0.910 at 115 tokens for dense retrieval; all differences
are significant under paired bootstrap and McNemar tests (p < 0.05), and the advantage persists
under repeated subsampling. On 500 end-to-end queries the system matches fixed top-3 containment
at roughly half the prompt cost. Results do not degrade on LongBench retrieval subsets, and the
benefit of retrieval holds for both a hosted large model and a locally deployed 4B model.

**Reproducibility.** All code, evaluation sets and scripts are released under the MIT license
(https://github.com/mylgtab/budget-rag, v1.0.0). A stranger can reproduce the main table in about
thirty minutes: clone, `pip install -e .`, `make check`. The repository ships small data snapshots
so reproduction does not depend on external mirrors, and CI rebuilds and queries the Docker image
on every push.

**Fit.** We believe the work suits *Applied Sciences* because it turns a practical engineering
question—how to spend a fixed inference budget—into a formulation with testable predictions, and
validates it on both a controlled benchmark and public multi-hop datasets. Negative results
(lexical pseudo-relevance feedback, retrieval-free answering, learned routers under label noise)
are reported in the appendix.

This manuscript is original, has not been published elsewhere, and is not under consideration by
another journal. The author declares no conflict of interest. All experiments were run by the
author; generative AI tools assisted with code and drafting, and the author takes full
responsibility for the content.

Thank you for your consideration.

Sincerely,

[姓名]
[单位 / 学院]
[邮箱]
[ORCID（可选）]
[日期]

---

## 投稿前检查表

- [ ] 期刊选定，读一遍 author guidelines（页数、图格式、引用风格）
- [ ] 把作者-年引用转成期刊要求的数字引用 `[1]`
- [ ] 图 1–3 导出 300 dpi PNG/TIFF（仓库里已有 2x PNG）
- [ ] 补 ORCID、单位英文名
- [ ] 检查 Data Availability 链接可访问（GitHub 仓库 public）
- [ ] 摘要不超过期刊词数上限
- [ ] 声明部分（Funding / COI / AI 使用）填好
- [ ] 上传前再跑一次 `make check`，确认数字与论文一致
