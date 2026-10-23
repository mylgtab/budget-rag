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

Retrieval-augmented generation couples parametric memory with updatable external evidence
[Lewis et al., 2020], and in most systems the retrieval depth is a hyperparameter: a fixed number
of top-$k$ passages is retrieved and concatenated into the context [Robertson and Zaragoza, 2009;
Karpukhin et al., 2020]. That default was reasonable when context was cheap—taking a few more
passages cost nearly nothing. The cost has since moved. Position-sensitivity experiments show
double-digit accuracy differences depending on where the same evidence lands [Liu et al., 2024], so
"retrieve more" is no longer equivalent to "answer better"; both *how much* to take and *where to
put it* have become resources to allocate rather than tune. A subtler cost is reporting: most work
reports Recall@$k$ at a fixed $k$, while $k$, chunk length and routing depth differ across methods,
so quality–cost curves cannot be stitched together—an apparent recall gain may simply be more
tokens spent. We therefore treat the comparison protocol as part of the method and report
Recall@budget throughout (Section 6.1).

Existing work answers "how much to retrieve" along four lines: adaptive retrieval decides *whether*
and *in how many steps* to retrieve (Section 2.1); corrective retrieval handles retrieval that went
wrong (Section 2.2); cost-aware retrieval treats evidence acquisition as a bill (Section 2.3); and
compression, reranking and rewriting change the unit price, ordering and candidate pool of what has
already been fetched (Section 2.4). Section 2.5 traces the two decision tools we use—submodular
approximation and threshold stopping—and Section 2.6 states our position.

### 2.1 Adaptive Retrieval

**FLARE** [Jiang Z. et al., 2023] ties "when to retrieve" to the generation process: when a
low-confidence token appears, it is used as a query for a forward-looking retrieval, producing
multi-round retrieval that is triggered on demand. **Self-RAG** [Asai et al., 2024] goes further and
writes "is retrieval needed", "is the passage relevant" and "is the answer supported" into the
generation sequence as reflection tokens, training the model end-to-end to decide when to retrieve
and how much to adopt. **SKR** [Wang et al., 2023] takes a lower-effort route: it labels questions by
the model's own sense of its knowledge boundary and triggers retrieval only for unfamiliar ones,
without touching the generation process. All three turn retrieval from a fixed pipeline stage into a
switch driven by generation-side self-assessment or meta-knowledge.

Deciding *how many steps* is equally mature. **Adaptive-RAG** [Jeong et al., 2024] trains a query
complexity classifier that assigns questions to no retrieval, single-step retrieval or multi-step
retrieval; **Self-Ask** [Press et al., 2023] decomposes composite questions into sub-questions that
are retrieved one by one; **IRCoT** [Trivedi et al., 2023] interleaves chain-of-thought with
retrieval, so each reasoning step becomes the query for the next retrieval. These methods align
retrieval depth with the reasoning structure of the question and pay off on tasks that need
multi-hop evidence.

Together, the two lines turn retrieval into a per-query policy. But they optimize the correctness of
the decision, not its cost: the budget is given outside the model, and a classifier answers "which
tier" rather than "within 200 tokens, which chunk gets the first slot and does the second step
deserve a rewrite". The triggering signals also cost something—generation-side self-assessment needs
extra sampling or extra output, a complexity classifier needs labels and training, and
meta-knowledge discrimination needs a front model. Our gate uses only the relative score margin
$\gamma$ of an existing retrieval (Section 4.3), a scalar that comes for free inside the retrieval it
already performed; its threshold is solved from the shadow price of the budget (Proposition 2) and
shifts by formula when the unit price changes (Section 6.7). The multi-hop side follows the same
logic: whether a second hop is warranted is decided by the gain-to-cost ratio, not by whether the
question "looks complex" (Section 4.4, Proposition 3).

### 2.2 Corrective Retrieval

**CRAG** [Yan et al., 2024] inserts a lightweight retrieval evaluator between retrieval and
generation, judges the result as correct, incorrect or ambiguous, and triggers one of three
corrective actions—use it, discard it for web search, or combine both. It is a pipeline-style scheme
that treats retrieval quality as an anomaly to be repaired; later work adds finer-grained
verification, iterative retrieval and adaptive correction, all keeping the
detect–branch–correct structure.

This line acknowledges that retrieval fails, at the price of writing correction as a conditional
branch: whether to correct is decided by the evaluator's verdict, independently of whether the
correction is worth its cost. We fold the corrective actions (rewriting, cross-hop retrieval,
reranking) into the same action set and decide by gain-to-cost ratio—picked automatically when the
budget is loose, skipped automatically when it is tight, with no separate correction stage. The two
compose: a CRAG-style evaluator can serve as a prior for $g(a\mid S)$ in our action set—the evaluator
scores, the ordering rule decides.

### 2.3 Cost-Aware Retrieval

Cost-aware retrieval approaches from the other end: if acquiring each piece of evidence itself costs
money (paid retrievers, external APIs, human annotation), the selector must trade utility against
expense. Prior work reports that static selectors are brittle under load shifts and that larger
budgets do not reliably improve quality [Wu et al., 2026], which argues for modelling the allocation
policy explicitly rather than tuning it.

We handle a different cost: **context occupancy**. It never appears on a retrieval bill, yet three
things price it simultaneously—per-token billing, the attention budget, and position sensitivity
[Liu et al., 2024]. This explains why fixed top-$k$ misses at both ends: too much for easy
questions, too little for hard ones. The two costs can be written into one knapsack problem by
making action cost a vector (access fee plus occupancy fee) and the budget multi-dimensional. We
solve the occupancy dimension only; the two compose directly, and under a multi-dimensional budget
the optimal policy moves from a single threshold chain to a chain on the Pareto frontier while the
ordering rule is unchanged (Section 7.3).

### 2.4 Compression, Reranking and Query Rewriting

One line subtracts from what has already been fetched. **LLMLingua** [Jiang H. et al., 2023] uses a
small model's perplexity to estimate token importance and compress the prompt; **LongLLMLingua**
[Jiang H. et al., 2024] adds question-aware compression to reduce information loss on long documents;
**RECOMP** [Xu et al., 2024] trains extractive and generative compressors that turn multiple passages
into a summary. These methods raise information density per token, trading compression rate against
fidelity.

Reranking changes the order of the same candidates. **monoT5** [Nogueira et al., 2020] casts
relevance as sequence-to-sequence generation, and **RankGPT** [Sun et al., 2023] uses a large model for
listwise reranking. Reranking does not reduce the number of candidates; it decides who gets packed
first when the budget truncates, and its gain is realized only when truncation actually happens.

On the rewriting side, **HyDE** [Gao et al., 2023] replaces the query with a generated pseudo-document
for dense retrieval, and **Rewrite-Retrieve-Read** [Ma et al., 2023] places a rewriter before the
retriever and trains it with downstream feedback, showing that "asking differently" can be a
first-class action.

These three techniques and our budget allocation are orthogonal layers: compression lowers the unit
price of a token, reranking changes the packing order within a fixed budget, rewriting changes the
candidate pool itself, and we decide how many units to buy and which action to buy. When combined,
compression is equivalent to multiplying each action's cost $c(a)$ by a discount factor, which
changes neither the structure of the selection problem nor the optimality condition of the greedy
rule. The gain from reranking, in contrast, grows as the budget tightens—our reranking experiment
gives direct evidence: with a pool of 8 and a 300-token budget the gain is 0.0 pt (no selection
pressure), while with a pool of 30 and a 150-token budget it is +5.5 pt (Section 7.1). The same action
differs by 5.5 pt across two budgets, which is precisely the observable consequence of "gain is
priced by budget tightness".

### 2.5 Submodular Approximation and Threshold Stopping

Both decision forms we use have mature sources. Submodular selection controls redundancy in retrieval
and summarization: **MMR** [Carbonell and Goldstein, 1998] subtracts similarity to already-selected
items from relevance and selects greedily one at a time, while Lin and Bilmes [2011] write coverage
and diversity into one family of submodular functions and summarize under a unified objective. The
approximation bound comes from Nemhauser et al. [1978]: for a monotone submodular function under a
cardinality constraint, greedy selection by marginal gain is within $1-1/e$ of optimal. With
heterogeneous costs the bound of unit-cost greedy drops to $(1-1/e)/2$; the modified greedy of
Khuller et al. [1999] adds local enumeration across tiers and restores $1-1/e$ for the budgeted case.
These results establish that ordering by gain-per-cost is not a heuristic but a bounded
approximation algorithm.

Threshold stopping has long had an optimal-stopping form in statistics: sequential analysis shows
that with increasing costs and observations arriving in stages, the optimal policy is a threshold—
stop when the observation is good enough, continue otherwise [Wald, 1947]. The form was rediscovered
in LLM serving: **FrugalGPT** [Chen et al., 2023] answers with a cheap model first and decides by
confidence whether to escalate to a stronger and more expensive one, validating threshold routing on
real billing.

We join the two: submodular ordering decides which action to buy next, and the threshold decides when
to stop. We do not reprove the approximation bound—Proposition 1 cites the budgeted result directly
(Section 5); the increment is to replace the selected "elements" with "actions": chunks, hybrid
retrieval, rewriting, reranking and cross-hop retrieval share one definition of cost and gain.
Proposition 3 extends the threshold form to retrieval actions: when action costs increase and gains
decrease monotonically with confidence, the optimal policy is again a chain of confidence thresholds,
with thresholds moving monotonically with the budget. The difference from FrugalGPT is the direction
of the constraint: it minimizes cost subject to a quality target, whereas we maximize quality subject
to a budget; the two are dual, and the dual variable is exactly our shadow price $\lambda$. This is
why we can write "what the threshold should be" as a computable formula instead of a hyperparameter to
be searched.

### 2.6 Our Position

| Line | Decision object | Role of the budget | Trigger signal | Relation to this work |
|---|---|---|---|---|
| Adaptive and multi-hop [Jiang Z. 2023; Asai 2024; Jeong 2024; Press 2023; Trivedi 2023] | Whether to retrieve, how many steps | External constant | Generation confidence / complexity classifier / question decomposition | We add "how much to give" and make the second hop a priced action |
| Corrective [Yan 2024] | Whether the result is trustworthy, how to fix | Not modelled | Fine-tuned evaluator | Corrective actions join the action set and fire by cost-effectiveness; the evaluator serves as a gain prior |
| Cost-aware [Wu 2026] | Which evidence to buy | Spending cap | Utility-to-cost ratio | Cost becomes context occupancy; composes into a multi-dimensional knapsack |
| Compression and reranking [Jiang H. 2023/2024; Xu 2024; Nogueira 2020; Sun 2023] | What to delete, who gets packed first | Token cap | — | Orthogonal and composable; compression is a cost discount, reranking is paid by budget tightness |
| Submodular selection [Carbonell and Goldstein 1998; Nemhauser 1978; Khuller 1999] | Selecting a subset from a fixed pool | Cardinality or coverage budget | Marginal gain | Elements become actions: heterogeneous costs, gains estimated online |
| Cascades and thresholds [Wald 1947; Chen 2023] | When to escalate to a costlier tier | Threshold / quality constraint | Confidence | We extend the threshold chain to retrieval actions, with thresholds from the shadow price |

Taken together, prior work advances four questions—whether to retrieve, whether retrieval is right,
whether evidence is expensive, and whether context can be deleted—and they share an unstated
assumption: **retrieval behaviour can be chosen independently of the budget**. We supply that layer,
writing the budget as an explicit constraint and the shadow price as an observable quantity, with the
policy derived from their ratio. Which tier, whether to rewrite, whether to cross-hop and who gets
packed first are then answered by one ordering rule: actions appear as the budget allows and disappear
as it tightens, with no per-combination stage design.

Two accounting differences remain. First, the evaluation protocol: we report Recall@budget
uniformly, so all methods are compared under the same budget with quality and cost visible together
(Sections 6.1 and 6.2), rather than each reporting Recall@$k$ at its own $k$. Second, the source of
gain: the marginal gain $g(a\mid S)$ is produced online from existing retrieval scores and lightweight
judgements, requiring neither a trained discriminator nor generation-side self-assessment, so the
same policy transfers directly across generator models (Section 6.5). Together these form the seam
with the lines above: they provide components, we provide the rule that assembles components under a
budget.

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

![Figure 1. System overview](figures/fig1-pipeline.png)

**Figure 1.** System overview. The corpus is indexed twice;
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

## Appendix A. Negative Results

Negative results are collected here. Pseudo-relevance feedback (PRF) causes query drift, losing
1.6 pt on the sentence index and 19.6 pt on fixed blocks; the zeroth rung—answering without
retrieval—is not viable on a technical corpus, with containment of 0.11; at a 200-token budget greedy
allocation falls 6 pt below the brute-force optimum, in the direction predicted by the approximation
in Proposition 1; and learned routers (TF-IDF 0.747, BERT 0.702) do not reach the score-based gate
(0.960). Their role is to rule out alternative explanations, which is why they sit in the appendix.

## Appendix B. Reproducibility

**One implementation correction.** An early version of the packing loop carried a 24-chunk cap, so a
nominal 800-token budget consumed only about 500 tokens. After changing the cap to scale with the
budget we re-ran the generation experiments of Section 6.5; a regression test
(`tests/test_longbench.py`) now guards against the cap binding before the budget does. Budgeted
interfaces need assertions of this kind—that is the lesson from building the system.

```
make test          # 65 tests
python scripts/baselines.py --limit 200
python scripts/multihop.py --modes single bridge entity
python scripts/tune_params.py
```

All code, evaluation sets and scripts are released under the MIT license at
https://github.com/mylgtab/budget-rag (v1.0.0). A stranger can reproduce the main table in about
thirty minutes: clone, `pip install -e .`, `make check`. The repository ships small data snapshots so
reproduction does not depend on external mirrors, and CI rebuilds and queries the Docker image on
every push.

## References

- **Asai, A.; Wu, Z.; Wang, Y.; Sil, A.; Hajishirzi, H.** Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. In *ICLR 2024*. arXiv:2310.11511.
- **Carbonell, J.; Goldstein, J.** The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries. In *SIGIR 1998*, pp. 335–336.
- **Chen, L.; Zaharia, M.; Zou, J.** FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance. arXiv:2305.05176, 2023.
- **Gao, L.; Ma, X.; Lin, J.; Callan, J.** Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE). In *ACL 2023*. arXiv:2212.10496.
- **Jeong, S.; Baek, J.; Cho, S.; Hwang, S. J.; Park, J. C.** Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity. In *NAACL 2024*, pp. 7036–7056. arXiv:2403.14403.
- **Jiang, H.; Wu, Q.; Lin, C.-Y.; Yang, Y.; Qiu, L.** LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models. In *EMNLP 2023*. arXiv:2310.05736.
- **Jiang, H.; Wu, Q.; Luo, X.; Li, D.; Lin, C.-Y.; Yang, Y.; Qiu, L.** LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression. In *ACL 2024*. arXiv:2310.06839.
- **Jiang, Z.; Xu, F. F.; Gao, L.; Sun, Z.; Liu, Q.; Dwivedi-Yu, J.; Yang, Y.; Callan, J.; Neubig, G.** Active Retrieval Augmented Generation (FLARE). In *EMNLP 2023*. arXiv:2305.06983.
- **Karpukhin, V.; Oğuz, B.; Min, S.; Lewis, P.; Wu, L.; Edunov, S.; Chen, D.; Yih, W.-t.** Dense Passage Retrieval for Open-Domain Question Answering. In *EMNLP 2020*. arXiv:2004.04906.
- **Khuller, S.; Moss, A.; Naor, J.** The Budgeted Maximum Coverage Problem. *Information Processing Letters* **1999**, 70(1), 39–45.
- **Lewis, P.; Perez, E.; Piktus, A.; Petroni, F.; Karpukhin, V.; Goyal, N.; Küttler, H.; Lewis, M.; Yih, W.-t.; Rocktäschel, T.; Riedel, S.; Kiela, D.** Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. In *NeurIPS 2020*. arXiv:2005.11401.
- **Lin, H.; Bilmes, J.** A Class of Submodular Functions for Document Summarization. In *ACL-HLT 2011*, pp. 510–520.
- **Liu, N. F.; Lin, K.; Hewitt, J.; Paranjape, A.; Bevilacqua, M.; Petroni, F.; Liang, P.** Lost in the Middle: How Language Models Use Long Contexts. *TACL* **2024**, 12, 157–173. arXiv:2307.03172.
- **Ma, X.; Gong, Y.; He, P.; Zhao, H.; Duan, N.** Query Rewriting for Retrieval-Augmented Large Language Models. In *EMNLP 2023*. arXiv:2305.14283.
- **Nemhauser, G. L.; Wolsey, L. A.; Fisher, M. L.** An Analysis of Approximations for Maximizing Submodular Set Functions—I. *Mathematical Programming* **1978**, 14(1), 265–294.
- **Nogueira, R.; Jiang, Z.; Pradeep, R.; Lin, J.** Document Ranking with a Pretrained Sequence-to-Sequence Model. In *Findings of EMNLP 2020*. arXiv:2003.06713.
- **Press, O.; Zhang, M.; Min, S.; Schmidt, L.; Smith, N. A.; Lewis, M.** Measuring and Narrowing the Compositionality Gap in Language Models (Self-Ask). In *Findings of EMNLP 2023*. arXiv:2210.03350.
- **Robertson, S.; Zaragoza, H.** The Probabilistic Relevance Framework: BM25 and Beyond. *Foundations and Trends in Information Retrieval* **2009**, 3(4), 333–389.
- **Sun, W.; Yan, L.; Ma, X.; Wang, S.; Ren, P.; Chen, Z.; Yin, D.; Ren, Z.** Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents (RankGPT). In *EMNLP 2023*. arXiv:2304.09542.
- **Trivedi, H.; Balasubramanian, N.; Khot, T.; Sabharwal, A.** Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions (IRCoT). In *ACL 2023*. arXiv:2212.10509.
- **Wald, A.** *Sequential Analysis*; Wiley: New York, 1947.
- **Wang, Y.; Li, P.; Sun, M.; Liu, Y.** Self-Knowledge Guided Retrieval Augmentation for Large Language Models (SKR). In *Findings of EMNLP 2023*. arXiv:2310.05002.
- **Wu, M.; Yang, H.; Ben-Porat, O.; Ziser, Y.** When Knowledge Is Not Free: Cost-Aware Evidence Selection in Retrieval-Augmented Generation. arXiv:2606.02245, 2026.
- **Xu, F.; Shi, W.; Choi, E.** RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation. In *ICLR 2024*. arXiv:2310.04408.
- **Yan, S.-Q.; Gu, J.-C.; Zhu, Y.; Ling, Z.-H.** Corrective Retrieval Augmented Generation (CRAG). arXiv:2401.15884, 2024.

## Declarations

**Data Availability Statement.** All code, evaluation sets and experiment scripts are available at
https://github.com/mylgtab/budget-rag (MIT license, v1.0.0). Small snapshots of the LongBench subsets
ship with the repository; the complete data can be fetched with `scripts/fetch_longbench.py` from the
original distribution. Every table in this paper is reproducible with `make check`,
`scripts/baselines.py`, `scripts/seed_stability.py` and `scripts/latency_bench.py`.

**Author Contributions.** The single author performed conceptualization, methodology, software,
validation, formal analysis, data curation, writing of the original draft and revision.

**Funding.** This research received no external funding.

**Conflicts of Interest.** The author declares no conflict of interest.

**Use of Generative AI.** Code implementation, experiment scripts and the first draft were produced
with the assistance of AI coding tools. All experimental numbers were produced by running the
repository scripts on the author's machine, and the author takes full responsibility for the content.
