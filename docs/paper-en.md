# Budget-Aware Retrieval: Allocating Context Tokens Where They Pay Off

> English manuscript, work in progress. Chinese master: `paper-draft.md`.
> Translated so far: Abstract, Section 1. Sections 2–8 pending.

## Abstract

Retrieval-augmented generation treats the amount of retrieved context as a fixed
hyperparameter, although real budgets are finite and query difficulty varies by orders of
magnitude. We formulate retrieval-depth selection as **budget-constrained submodular
maximization**. Each retrieval action — taking another chunk, switching to hybrid retrieval,
rewriting the query, adding a second hop — carries a cost $c(a)$ and a marginal quality gain
$g(a\mid S)$, and a policy is a subset of actions under a budget $B$. Under diminishing
returns, the quality function is monotone submodular, so greedy selection by gain-per-cost
inherits the classical guarantee: $1-1/e$ under a cardinality budget, $(1-1/e)/2$ under a
cost budget, and $1-1/e$ again once cross-tier enumeration is allowed. The same view yields
two directly implementable consequences: whether query rewriting pays off is governed by the
shadow price of the budget rather than by a fixed rule, and the optimal cascade is a chain of
confidence thresholds whose cutoffs fall as that price rises.

We build a reproducible system from this framework. On a 200-query retrieval benchmark with
bge-m3 embeddings, it attains **0.960** recall at an average context cost of **126 tokens**,
compared with 0.925 at 179 tokens for a corrective-retrieval baseline and 0.910 at 115 tokens
for dense retrieval; all differences are significant under paired bootstrap and McNemar tests
($p<0.05$), and the advantage survives repeated subsampling. On 500 end-to-end queries the
system matches fixed top-3 containment (0.912 vs 0.920, within paired noise) at roughly half
the prompt cost (474 vs 972 tokens). Recall reaches 0.995 and 1.000 on two LongBench retrieval
subsets. On three multi-hop generation benchmarks, retrieval improves answer accuracy
consistently for both a hosted large model and a locally deployed 4B model. Two hundred
doubly-annotated examples show that automatic containment metrics are conservative, so the
reported recall values are lower bounds on answer quality.

**Keywords**: retrieval-augmented generation; context budget; submodular maximization;
adaptive retrieval; cost-aware inference

## 1. Introduction

Retrieval-augmented generation (RAG) has become the default way to ground language models in
external, updatable evidence [Lewis et al., 2020]. In most systems the retrieval depth is a
hyperparameter: a fixed number of passages is retrieved and concatenated into the context
[Robertson and Zaragoza, 2009; Karpukhin et al., 2020]. That default made sense when context
was cheap—retrieving a few more passages cost almost nothing. The cost has since moved
elsewhere. Position-sensitivity experiments show double-digit accuracy differences depending on
where the same evidence lands in the context [Liu et al., 2024], so "retrieve more" is no
longer equivalent to "answer better"; both *how much* to retrieve and *where to put it* have
become resources that must be allocated rather than tuned. A subtler cost is reporting: most
work reports Recall@$k$ at a fixed $k$, while $k$, chunk size and routing depth differ across
methods, so quality–cost curves cannot be stitched together—an apparent recall gain may simply
be more tokens spent. We therefore treat the comparison protocol as part of the method and
report Recall@budget throughout (Section 6.1).

Existing work answers "how much to retrieve" along four lines: adaptive retrieval decides
*whether* and *how many steps* to retrieve (Section 2.1); corrective retrieval handles
retrieval that went wrong (Section 2.2); cost-aware retrieval treats evidence acquisition as a
bill (Section 2.3); and compression, reranking and rewriting change the unit price, ordering and
candidate pool of what has already been fetched (Section 2.4). What these lines share is that
the budget itself stays exogenous: a classifier picks a depth, an evaluator triggers a repair,
a selector picks among priced evidence—but none of them answers "given this budget, which step
deserves the next unit of money." Cost-aware RAG's finding that static selectors are brittle
suggests that **the allocation policy itself deserves a model**.

We cast retrieval-depth selection as **budget-constrained set selection**. Every executable
retrieval action—taking another chunk, switching to hybrid retrieval, rewriting the query,
adding a cross-hop retrieval—is an element with cost $c(a)$ and marginal gain $g(a\mid S)$; a
policy is a subset $S$ chosen under budget $B$. Under the empirically testable assumption of
diminishing returns, the quality function is monotone submodular, so the classical approximation
guarantees apply to density-ordered greedy selection. Two consequences fall out that can be
implemented directly: whether rewriting pays off depends on the shadow price of the budget
rather than on a fixed rule, and the optimal cascade is a chain of confidence thresholds.

We implement the framework as a running system and evaluate it on a 200-query retrieval
benchmark and a 500-query end-to-end benchmark. Against five baselines under a common budget,
the system reaches **0.960** recall at an average context cost of **126 tokens**, versus 0.925
at 179 tokens for a corrective-retrieval approximation and 0.910 at 115 tokens for dense
retrieval; paired bootstrap and McNemar tests show the differences are significant ($p<0.05$).
On 500 end-to-end queries it matches fixed top-3 containment (0.912 vs 0.920) at roughly half
the prompt cost (474 vs 972 tokens). Recall reaches 0.995 and 1.000 on two LongBench retrieval
subsets, and on three multi-hop generation benchmarks the improvement from retrieval holds for
both a hosted large model and a locally deployed 4B model. Two hundred doubly-annotated
examples indicate that automatic metrics are conservative, so the reported recall is a lower
bound on answer quality.

Our contributions are threefold.

1. We unify chunk selection, hybrid retrieval, query rewriting and cross-hop retrieval into a
   single priced action set and state its approximation bound: under diminishing returns the
   quality function is monotone submodular; density greedy attains $1-1/e$ under a cardinality
   budget and $(1-1/e)/2$ under a cost budget, recovering $1-1/e$ with cross-tier enumeration
   (Sections 3 and 5).
2. We derive a closed-form rewriting threshold $\tau^*(\lambda)$ and verify its direction
   empirically: raising the unit-price coefficient from 0.25 to 2 moves $\tau^*$ from 0.25 to 0,
   as Propositions 2 and 4 predict (Section 6.7).
3. We report 0.960 recall at 126 tokens on a 200-query benchmark, show that the result does not
   degrade across corpora or generator models, and use 200 doubly-annotated examples to show
   that the reported recall is a lower bound (Sections 6.2–6.6).

## 2. Related Work

*Translation pending; see the Chinese master in `paper-draft.md` (Sections 2.1–2.6).*

## 3. Problem Formulation

A query admits a set of retrieval actions $\mathcal{A}$. Action $a$ has cost $c(a)$ and marginal
gain $g(a\mid S)$ given the already selected set $S$, and the quality $Q(S)$ is monotone
non-decreasing. A policy is the solution of

$$\max_{S\subseteq\mathcal{A}} Q(S) \quad \text{s.t.} \quad \sum_{a\in S} c(a) \le B .$$

Two assumptions carry the later results: **A1** diminishing marginal returns, and **A2** costs are
additive and order-independent.

## 4. Method

### 4.1 Dual Index and Budgeted Chunk Selection

Long documents are indexed at two granularities (Figure 1): **sentence level** (split on
punctuation, roughly 15–40 tokens) and **fixed blocks** (sliding window, 200 tokens with 40
overlap by default). Sentence-level indexing is cheaper under tight budgets because it never
drags unrelated sentences in; fixed blocks are more coherent when the budget is generous. The
system picks automatically: sentence level when `ctx < 500`, fixed blocks otherwise.

Chunks are accumulated in descending retrieval score until the selected chunks reach the token
budget $B$, and then the loop stops. There is **no fixed $k$ truncation**—this is what makes the
budget, rather than the count, the first-class quantity.

### 4.2 Cascade Routing

Routing is tiered by the admissible cost per thousand tokens: very tight budgets
(< 0.002 CNY) take one chunk from BM25; medium budgets take two chunks from BM25; generous
budgets (≥ 0.01 CNY) take five chunks from hybrid retrieval. The tier boundaries are not
arbitrary: they are the discretization of the greedy allocation (Proposition 1) and correspond
to the knee of the gain-per-cost curve.

### 4.3 Confidence-Gated Query Rewriting

Rewriting accounts for more than half of the end-to-end latency (Section 6.8), so it is triggered
only when needed. The system first runs a cheap retrieval and computes the relative margin
between the top-1 and top-2 scores,

$$\gamma = \frac{s_1 - s_2}{s_1}.$$

When $\gamma < \tau$ the retrieval is deemed uncertain, the query is rewritten, and retrieval is
repeated with "original question + rewrite terms". The optimal threshold is set by the shadow
price of the budget (Proposition 2); the default 0.25 corresponds to pricing a rewrite at about
one strong retrieval. The sensitivity experiment in Section 6.7 confirms that $\tau$ moves down as
the unit price rises.

### 4.4 Multi-Hop Extension

For questions that need two pieces of evidence, after the first hop the model is given the
question plus a summary of what was retrieved and asked what is still missing; a second hop then
runs with "original question + supplementary query", and the two result sets are merged with
chunk-level deduplication. Model-generated supplementary queries outperform rule-based extraction
of proper nouns from the context (Section 6.5).

**Figure 1.** System overview (`docs/figures/fig1-pipeline.svg`). The corpus is indexed twice;
the budget selects sentence level or fixed blocks; routing assigns a tier; the first retrieval
yields the confidence $\gamma$; the gate decides whether to rewrite and re-retrieve; chunks are
accumulated until the budget $B$ is reached; a second hop is enabled when two pieces of evidence
are needed. Dashed edges are optional paths; $c(a)$ and $g(a\mid S)$ are the cost and gain used
for ordering.

## 5. Theory

**Proposition 1 (approximation bound).** Under A1 (diminishing returns) and A2 (additive costs),
$Q(S)$ is monotone submodular. Greedy selection by marginal gain attains $1-1/e$ under a
cardinality constraint [Nemhauser et al., 1978]; under a budget constraint the bound of
unit-cost greedy drops to $(1-1/e)/2$ and is recovered to $1-1/e$ with cross-tier enumeration
[Khuller et al., 1999]. We instantiate this ordering on the retrieval action set; the gap to the
brute-force optimum is measured in Appendix A.

**Proposition 2 (rewriting gate).** Let $q_0$ and $q_1$ be the quality without and with
rewriting, $p$ the probability that rewriting helps, and $c_r$ its cost. Rewriting pays off if and
only if $p(q_1-q_0) > \lambda c_r$, where $\lambda$ is the shadow price of the budget.
Equivalently, rewriting should be triggered below a confidence threshold, and that threshold is
solved from $\lambda$ rather than fixed at 0.25 (Section 4.3).

**Proposition 3 (cascade threshold chain).** If action costs increase and gains decrease
monotonically with confidence, the optimal policy assigns each confidence interval to a tier—a
threshold chain—and the thresholds move monotonically with the budget $B$. This explains why
cascades work and implies that tier boundaries should follow the budget (Section 4.2).

**Proposition 4 (monotonicity of the threshold).** Assume **A3**: the rewriting gain
$B(\gamma)=p(\gamma)\Delta q(\gamma)$ is non-increasing in the retrieval confidence $\gamma$.
Then the optimal threshold satisfies $B(\tau^*)=\lambda c_r$, and $\tau^*(\lambda)$ is
non-increasing in $\lambda$.

*Proof.* By Proposition 2 the criterion for rewriting is $B(\gamma)>\lambda c_r$. A3 makes $B$
non-increasing, so the confidences that satisfy the criterion form an interval $[0,\tau^*)$. As
$\lambda$ grows the right-hand side $\lambda c_r$ grows, the feasible set shrinks, and
$\tau^*$ therefore does not increase. In the boundary cases $\lambda c_r \ge B(0)$ gives
$\tau^*=0$ (never rewrite) and $\lambda c_r \le B(1)$ gives $\tau^*=1$ (always rewrite).
Section 6.7 verifies the former boundary: when the unit-price coefficient rises to 2, the optimal
threshold falls from 0.25 to 0.

<!-- Sections 6–8 and appendices to be translated. -->
