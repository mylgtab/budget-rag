# 投稿材料：Cover Letter 草稿

> 目标刊：*Information Retrieval Journal*（Q2，订阅制、无 APC）。
> 备选：*Expert Systems with Applications*（Q1，免费）、*Applied Intelligence*（Q2，免费）。
> 替换方括号内容后即可用。

---

**To the Editorial Office of *Information Retrieval Journal***

Dear Editors,

We submit the manuscript **"Budget-Aware Retrieval: Allocating Context Tokens Where They
Pay Off"** for consideration as a research article in *Information Retrieval Journal*.

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
cascade is a chain of confidence thresholds. The evaluation protocol reports Recall@budget so
quality and cost stay comparable across methods, and we add a quality-target interface: a
split-conformal rule turns "I need 90% recall" into a token budget with a coverage guarantee, and
refuses targets the retriever cannot reach.

**Main results.** On a controlled benchmark the system reaches **0.960** recall at **126 tokens**,
against 0.925 at 179 tokens for a corrective-retrieval approximation and 0.910 at 115 tokens for
dense retrieval (paired bootstrap and McNemar, p < 0.05). On a real corpus of **312 official
documentation pages** with a **301-question** benchmark, hybrid retrieval reaches 0.910 recall at
a 300-token budget while the difficulty-adaptive rule keeps 0.900 at **244 tokens** (15% saving);
the conformal protocol holds empirical coverage within 0.015 of nominal at 120–276 tokens for
targets 0.80/0.85/0.90. On four BEIR subsets the adaptive rule saves 1–24% of context at equal nDCG@10
(and none on an adversarial benchmark, which we report). We also reproduce the official Adaptive-RAG complexity classifier from its released
labels (43.3% validation accuracy at reduced model scale) and route with it on our benchmark:
it is a strong low-budget baseline (0.844 at 66 tokens) but is dominated once high recall is
required, which is precisely the gap the quality-target interface fills.

**Reproducibility.** All code, evaluation sets and scripts are released under the MIT license
(https://github.com/mylgtab/budget-rag, v1.0.0). A stranger can reproduce the main table in about
thirty minutes: clone, `pip install -e .`, `make check`. The repository ships small data snapshots
so reproduction does not depend on external mirrors, and CI rebuilds and queries the Docker image
on every push.

**Fit.** We believe the work suits *Information Retrieval Journal* because it treats retrieval
depth as an allocation problem with a guarantee, reports cost and quality jointly rather than
separately, and connects the allocation to a deployable calibration interface. Negative results
(sentence-level indexing, gated rewriting, learned routers under label noise) are reported rather
than hidden, as are the boundaries of the guarantee under order-dependent costs.

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
- [ ] 图 1–5 导出 300 dpi PNG/TIFF（仓库里已有 2x PNG）
- [ ] 补 ORCID、单位英文名
- [ ] 检查 Data Availability 链接可访问（GitHub 仓库 public）
- [ ] 摘要不超过期刊词数上限
- [ ] 声明部分（Funding / COI / AI 使用）填好
- [ ] 上传前再跑一次 `make check`，确认数字与论文一致
- [ ] 确认 6.10 的保形结论与 6.16 的官方分类器对照已是最新数字
