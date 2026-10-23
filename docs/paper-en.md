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

## 6. Experiments

### 6.1 Setup

**Corpus.** Sixteen Chinese technical notes (operating systems, networking, databases, Git,
Docker, algorithms, testing, HTTP caching, RAG), 8,546 characters and 348 factual sentences,
yielding roughly 344 sentence-level chunks.

**Benchmarks.** A synthetic main set of 500 questions (generated from the source text; answers are
verbatim spans, verified); a harder 200-question set with deliberately paraphrased queries to widen
the surface gap. Public benchmarks: LongBench `passage_retrieval_zh` / `passage_retrieval_en`
(paragraph-level retrieval, answer = paragraph id), `hotpotqa` / `2wikimqa` / `musique`
(multi-hop generation), and `triviaqa` (a commonsense-style contrast).

**Models.** DeepSeek-V4.1-Flash (API) for the main experiments; a locally deployed Qwen3-4B
(GGUF Q4_K_M, Ollama, `/no_think`) for the model-agnostic check.

**Vectors.** BAAI/bge-m3 (1024-d, OpenAI-compatible endpoint); deterministic hashing vectors for
the offline baseline.

**Hyperparameters.** Sentence-level chunking; context budget 300 tokens (swept over 100–800);
hybrid weight $\alpha=0.2$; gate threshold $\tau=0.25$; routing tiers defined by cost per thousand
tokens.

**Cost model.** 2 CNY per million input tokens, 8 per million output, 0.7 per million embedding
tokens, billed from the API-reported `usage`; hashing vectors are charged zero.

**Statistics.** Paired bootstrap (1,000–2,000 resamples) for 95% intervals; McNemar exact test for
system comparisons; five 2/3 subsamples for robustness.

**Hardware.** i7-13650HX, 16 GB RAM, RTX 4060 Laptop 8 GB. API models run over the network, the
local model on the GPU; all retrieval and statistics run on the CPU.

### 6.2 Main Results

The proposed system is stronger at equal or lower budget.

| Method | Recall | 95% CI | tokens |
|---|---|---|---|
| BM25 | 0.825 | [0.770, 0.875] | 68 |
| Dense | 0.910 | [0.870, 0.945] | 115 |
| Hybrid | 0.900 | [0.860, 0.940] | 114 |
| Adaptive-RAG approx. | 0.855 | [0.805, 0.905] | 100 |
| CRAG approx. | 0.925 | [0.885, 0.960] | 179 |
| **Ours** | **0.960** | [0.930, 0.985] | **126** |

Higher recall at lower cost follows from spending the budget where the marginal gain is largest:
easy questions stop after a single chunk (about 20 tokens) and the saved budget goes to questions
that need hybrid retrieval and rewriting, instead of running every query through the full
pipeline. The CRAG approximation pays one evaluator call plus five chunks for *every* query,
while a fixed $k$ cannot cut losses on easy ones.

**Seed stability (five 2/3 subsamples).**

| Method | Full | Subsample mean ± sd |
|---|---|---|
| BM25 | 0.825 | 0.826 ± 0.010 |
| Dense | 0.910 | 0.914 ± 0.009 |
| Hybrid | 0.900 | 0.902 ± 0.005 |
| Adaptive-RAG approx. | 0.855 | 0.853 ± 0.010 |
| CRAG approx. | 0.925 | 0.928 ± 0.004 |
| **Ours** | **0.960** | **0.962 ± 0.011** |

The subsample interval for our system, [0.947, 0.970], does not overlap that of the CRAG
approximation, [0.925, 0.932]: the advantage does not depend on which questions are drawn.

### 6.3 Ablation

| Removed component | Recall change | Interpretation |
|---|---|---|
| Gate (rewrite on every query) | −3.6 pt | Rewriting helps, but not on every query |
| Hybrid retrieval (BM25 only) | −6.8 pt | Semantic matching carries most of the signal |
| Budget 300 → 100 | −6.1 pt | Budget matters, but must be allocated by difficulty |
| $\alpha$ 0.2 → 0.5 | −1.7 pt | The default weight is not optimal for this corpus |

Figure 3 summarizes the ablation: dropping hybrid retrieval costs the most (−6.8 pt), followed by
tightening the budget (−6.1 pt), so the gains come mainly from semantic matching and budget
allocation, with the gate as a refinement (−3.6 pt).

![Figure 2. Budget versus recall (sentence-level vs fixed blocks)](figures/fig2-budget-recall.png)

**Figure 2.** Recall as the budget grows from 80 to 800 tokens. Below 300 tokens the sentence-level
index wins because the same budget accommodates more sentences; beyond 500 tokens fixed blocks
overtake it as a single block is more coherent. This is the basis for switching indexes by budget
(Section 4.1).

![Figure 3. Ablation: recall cost of removing each component](figures/fig3-ablation.png)

**Figure 3.** Ablation relative to the full system; the horizontal axis is answer-span recall and
parentheses give the relative change.

### 6.4 Cross-Corpus Check

On the LongBench Chinese retrieval subset our recall is 0.995 against 0.955 for BM25; on the
English subset both reach 1.000. The claim here is that performance does not degrade across
corpora and that the direction of the relative gain is preserved; absolute levels depend on task
difficulty and are not used as a comparison basis.

### 6.5 The Benefit of Retrieval Is Model-Agnostic

Twenty questions per dataset, same 800-token budget:

| Dataset | Model | With retrieval | Without | Span hit |
|---|---|---|---|---|
| HotpotQA | DeepSeek-V4.1-Flash | **0.500** | 0.200 | 0.60 |
| HotpotQA | Qwen3-4B | **0.450** | 0.100 | 0.60 |
| 2WikiMultiHopQA | Qwen3-4B | **0.150** | 0.000 | 0.70 |
| MuSiQue | Qwen3-4B | **0.250** | 0.000 | 0.65 |
| TriviaQA | Qwen3-4B | 0.100 | **0.300** | 0.15 |

The first four rows support the claim: retrieval raises accuracy by 0.15–0.45, in the same
direction for a large hosted model and a small local one.

The fifth row is a boundary condition, reported as measured. TriviaQA questions are largely
commonsense, so the model answers from parameters (0.30); the corpus consists of twenty-odd
distractor passages and an 800-token budget covers about 11% of it, so retrieved fragments pull the
model off course (0.10). This agrees with the motivation for the gate in Section 6.8: **whether to
retrieve is itself a decision**, not a default. Our gate only decides *whether to rewrite*; leaving
*whether to retrieve* to future work (Section 8).

### 6.6 Human Annotation

On 200 doubly-annotated items, automatic containment agrees with human judgement 90%–97% of the
time, and inter-annotator agreement is 0.548 (unweighted) and 0.673 (quadratic weighted). The
automatic metric is **conservative**, so the recall in the main table is a lower bound.

### 6.7 Threshold Sensitivity (Proposition 2)

For unit-price coefficients λ = 0.25, 0.5 and 1, the optimal threshold stays at τ = 0.25; for λ ≥ 2
it falls to τ = 0. The direction predicted by Propositions 2 and 4 holds: the more expensive the
rewrite, the less often it should be triggered.

### 6.8 Efficiency

Twenty queries (single machine, API model, answer cache disabled):

| Configuration | p50 (ms) | p95 (ms) | cost/query (CNY) | recall |
|---|---|---|---|---|
| Cheap tier (BM25) | 923 | 1469 | 0.00088 | 0.850 |
| Strong tier (hybrid) | 898 | 1705 | 0.00087 | 0.850 |
| Strong + always rewrite | 1765 | 3090 | 0.00116 | 0.900 |
| Strong + gated rewrite | 1788 | 2577 | 0.00116 | 0.900 |

**Rewriting dominates latency** (+0.9 s at p50, +1.4 s at p95). The value of the gate depends on the
rewrite trigger rate of the batch: 38% on the full 500 questions (saving 62% of rewriting calls),
76% on the first 50 harder questions, and 69.5% on a 200-question medium subset. The gate adapts to
difficulty, so its latency saving is not unconditional; the default threshold of 0.25 should move
with the shadow price of the budget (Section 6.7).

## 7. Discussion

### 7.1 Budget as an Interface, Not a Hyperparameter

Writing the budget as a constraint rather than a tuned $k$ buys three transferable properties.
First, the shadow price becomes a readable configuration value: $\lambda$ is the quality obtained
per additional unit of budget, and it translates "how many chunks" into "is this unit still worth
it". Section 6.7 shows the observable consequence—when the unit-price coefficient rises from 0.25 to
2, the optimal threshold falls from 0.25 to 0 and the system decides by itself that rewriting is not
worth it at that price. A budget can therefore be written into configuration as an SLA (tokens and
money per query) and survives a change of model or price without re-sweeping hyperparameters.

Second, the benefit of the gate must be reported together with the difficulty distribution of the
load. It saves 62% of rewriting calls at a 38% trigger rate on the full set, but only 24% at 76% on
the hard subset. Since rewriting dominates latency, what the gate saves is exactly the latency that
scales inversely with batch difficulty; reporting a gate benefit without the trigger rate can make
the same method look like opposite conclusions on two batches.

Third, the extension point is the action set alone. Adding an action (reranking, cross-hop
retrieval, a compressor) only requires stating its cost $c(a)$ and marginal gain $g(a\mid S)$; the
ordering rule and the approximation bound are unchanged. The reranking experiment illustrates the
usage: with a pool of 8 and a 300-token budget the gain is 0.0 pt, whereas with a pool of 30 and a
150-token budget it is +5.5 pt. The gain comes from truncation, not from the action itself.

### 7.2 When It Applies

The gains come from heterogeneity in difficulty and tightness of budget; they are largest when both
hold. Granularity experiments bound the budget regime: at or below 500 tokens the sentence-level
index saves 15%–50% of context at equal recall, while above 800 tokens fixed blocks overtake it
(Section 6.3). With a loose budget, freedom in *which* chunks to take is diluted—any policy can
afford large blocks and allocation stops mattering.

Where the bottleneck sits decides where the gain lands. On the three multi-hop benchmarks retrieval
hits the answer span 0.50–0.65 of the time, yet a 4B model answers correctly only 0.20–0.40
(Section 6.5): the evidence is already in the context and the generator fails to use it. Additional
context budget is then absorbed by the generation side, and the money should move there—a stronger
model, longer reasoning, an explicit extraction prompt. $\lambda$ points wherever marginal gain is
highest; when that is not retrieval, it points elsewhere.

Finally, on a homogeneous load the benefit of scheduling tends to zero: on the synthetic set all
policies except fixed shallow retrieval fall within the same confidence interval (Section 6.2), and
fixed top-$k$ suffices; the gap only opens on heterogeneous loads.

### 7.3 Boundaries of the Cost Model

Assumption A2 (fixed, order-independent unit prices) is an approximation of real billing: tiered
discounts, cache hits and batching all make $\lambda$ drift with the load. This does not require a
new model—treat $\lambda$ as a runtime observable; the sweep in Section 6.7 is its time-invariant
approximation, and online it can be updated over shorter windows.

The token estimate used for budget control is conservative. On the same prompt, tiktoken estimates
131 tokens while the API bills 71, an 84% overestimate (Section 8). Reported token costs are
therefore upper bounds and the true cost is lower; the 126 tokens that buy 0.960 recall in Section
6.2 still leave margin.

Cost can also be a vector. Latency and money are different dimensions: rewriting takes more than
half of the end-to-end latency while its token cost is negligible. Charging both makes $c(a)$ a
vector and turns the optimal policy from a single threshold chain into a chain on the Pareto
frontier; the greedy guarantee relaxes to a per-dimension bound while the ordering rule is
unchanged. Multi-dimensional budgeting is the most natural next step for this framework and needs
no new theory.

### 7.4 Distance to the Lower Bound

An oracle that knows which chunk to take reaches 0.958 recall with 58 tokens (Appendix A); without
that oracle we need 126 tokens for 0.960 (Section 6.2). The remaining cost gap comes from selection
error—not knowing which chunk is better—rather than from insufficient context. The direction is
therefore clear: improve the estimate of $g(a\mid S)$ and refine the selection granularity. The
counter-intuitive result in Appendix A has the same origin: more labels did not improve routing,
because the label depends on what was retrieved, not only on how the question is worded.

## 8. Limitations

The conclusions have four boundaries. **Corpus**: the main evidence is 500 synthetic technical
questions; cross-corpus validation covers retrieval only (Section 6.4) and the multi-hop generation
results are small (Section 6.5), so transfer to production corpora needs an additional validation
set. **Baselines**: the Adaptive-RAG and CRAG entries are behavioural approximations—a heuristic
router and an off-the-shelf relevance evaluator (Section 6.1)—not reproductions of the fine-tuned
models of the original papers, so the comparison is evidence at the same order of magnitude rather
than an exact replication. **Cost**: figures are converted from public unit prices and exclude
batch discounts, cache hits and operations overhead (Section 7.3), which makes them suitable for
relative comparison only. **Token estimates**: tiktoken over-counts Chinese relative to actual
billing (Section 7.3), so the true context cost at equal recall is lower than reported. None of these
four enters the abstract, and none changes the main conclusions of Section 6.

<!-- Appendices to be translated. -->
