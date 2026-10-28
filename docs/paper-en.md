# Budget-Aware Retrieval: Allocating Context Tokens Where They Pay Off
**Author:** Qiaomu Li ¹
**Affiliation:** ¹ School of Mathematics and Information Science, Zhangjiakou University, Zhangjiakou 075000, Hebei, China
**Corresponding author:** lqm050509@gmail.com
**ORCID:** 0009-0003-7912-3918
## Abstract

Retrieval-augmented generation commonly fixes how much context to retrieve, although queries differ
in difficulty and budgets are finite. We formulate retrieval-depth selection as a budget-constrained
choice among priced actions: adding a chunk, switching to hybrid retrieval, rewriting the query or
taking a second hop. Under monotonicity and diminishing returns the objective is submodular, so greedy
selection inherits a $1-1/e$ guarantee with a cardinality budget, $(1-1/e)/2$ with a cost budget, and
$1-1/e$ with cross-tier enumeration. The budget's shadow price then decides when rewriting pays off and
where a cascade sets its confidence thresholds.

In a controlled synthetic retrieval benchmark of 200 queries, the system reaches 0.960 recall at 126
context tokens, against 0.925 at 179 for a behavioural approximation of corrective retrieval and 0.910
at 115 for dense retrieval ($p<0.05$, bootstrap and McNemar). On 500 synthetic end-to-end queries,
containment is 0.912 versus 0.920 for fixed top-3, within paired noise, at 474 versus 972 prompt
tokens. Retrieval also improves answer accuracy on three multi-hop benchmarks for a local 4B model and on
HotpotQA for a hosted model.

Transfer is selective. Score-margin depth selection saves 1-24% of context tokens at equal nDCG@10 on
three of four BEIR subsets but fails on arguana, and neither sentence-level indexing nor gated rewriting
transfers to English documentation. A split-conformal protocol maps attainable quality targets to
budgets with twenty labelled questions, reports reach rates and declines unreachable targets; empirical
coverage stays within 0.015 of nominal at 120-276 tokens on the hybrid retriever. An audit of 200 doubly annotated
examples suggests automatic containment can miss valid answers, without proving a lower bound.

**Keywords:** retrieval-augmented generation; context budget; submodular maximization; adaptive retrieval; cost-aware inference; large language models

## 1. Introduction

Retrieval-augmented generation (RAG) grounds language models in external, updatable evidence [1]. Many
systems nevertheless retrieve a fixed number of passages [2,3]. That choice can waste context on
straightforward queries while leaving harder ones without sufficient evidence. It can also affect the
answer in less predictable ways: changing the position of identical evidence has produced double-digit
differences in accuracy [4]. More retrieved text is therefore not necessarily better. Nor does
Recall@$k$ alone establish a comparable quality-cost trade-off when systems differ in chunk size,
routing depth or token use. We use Recall@budget to make retrieval comparisons at matched context
budgets (Section 6.1).

Existing approaches address parts of this problem. Adaptive retrieval determines whether and how far to
retrieve; corrective retrieval responds to inadequate evidence; cost-aware selection prices evidence
acquisition; and compression, reranking and rewriting alter the cost, order or candidate pool of
evidence (Sections 2.1-2.4). These mechanisms leave a common allocation question: **given a query and a
remaining budget, which available action merits the next unit of expenditure?** The reported
brittleness of static selectors further motivates making that decision explicit [12].

We model a retrieval policy as a set $S$ of executable actions, each with cost $c(a)$ and marginal
quality gain $g(a\mid S)$, subject to budget $B$. When quality is monotone and gains diminish as
actions accumulate, the resulting objective is submodular. Its approximation guarantees are
conditional on those properties, rather than guarantees that every retrieval corpus satisfies them.
The same formulation links query rewriting to the shadow price of the budget and, under the stated
cascade model, yields a chain of confidence thresholds whose cutoffs decline as that price rises. We
implement the framework and examine both its controlled performance and its limits on public corpora.

Our contributions are fourfold:

1. **A common action model.** We place chunk selection, hybrid retrieval, query rewriting and
   second-hop retrieval in one priced action set. Under the stated conditions, gain-per-cost greedy
   selection attains the cardinality- and cost-budget guarantees above, with cross-tier enumeration
   restoring the stronger bound (Sections 3 and 5).
2. **A price-dependent rewriting rule.** We derive the rewriting threshold $\tau^*(\lambda)$
   (Propositions 2 and 4). In the reported sweep, increasing the unit-price coefficient from 0.25 to 2
   lowers $\tau^*$ from 0.25 to 0 (Section 6.7).
3. **A budget interface.** A twenty-question split-conformal calibration protocol translates attainable
   quality targets into budgets, reports their reach rates and declines targets the retriever cannot
   meet (Section 6.10).
4. **An evaluation of performance and transfer.** A 200-query retrieval benchmark and 500 end-to-end queries assess retrieval and
   generation cost; LongBench subsets and multi-hop benchmarks test additional settings. Evaluation on
   312 official documentation pages and four BEIR subsets distinguishes transferable score-margin depth
   selection from sentence-level indexing and gated rewriting, which do not transfer to English
   documentation. A doubly annotated audit examines the limits of automatic containment metrics
   (Sections 6.1-6.9).

## 2. Related Work

Retrieval-augmented generation (RAG) combines parametric knowledge with external, updatable evidence [1].
Many systems fix retrieval depth, concatenating a predetermined number of top-$k$ passages retrieved by
a sparse or dense retriever into the context [1-3]. This default was reasonable when a few extra passages
cost little. Position-sensitivity experiments, however, show double-digit accuracy differences when
identical evidence appears at different locations in the context [4]: more retrieved evidence need not
improve an answer, and both evidence volume and placement act as resources to allocate rather than
parameters to tune. A subtler cost is reporting. Studies typically report Recall@$k$ for a single $k$,
although chunk lengths, retrieval depths and token costs differ across methods, so quality-cost curves
from different studies cannot be compared directly -- an apparent recall gain may simply be more tokens
spent. We therefore treat the comparison protocol as part of the method and report
Recall@budget throughout (Section 6.1).

Existing work answers "how much to retrieve" along four lines: adaptive retrieval decides *whether*
and *in how many steps* to retrieve (Section 2.1); corrective retrieval handles retrieval that went
wrong (Section 2.2); cost-aware retrieval treats evidence acquisition as a bill (Section 2.3); and
compression, reranking and rewriting change the unit price, ordering and candidate pool of what has
already been fetched (Section 2.4). Section 2.5 traces the two decision tools we use—submodular
approximation and threshold stopping—and Section 2.6 states our position.

### 2.1 Adaptive Retrieval

**FLARE** [5] ties "when to retrieve" to the generation process: when a
low-confidence token appears, it is used as a query for a forward-looking retrieval, producing
multi-round retrieval that is triggered on demand. **Self-RAG** [6] goes further and
writes "is retrieval needed", "is the passage relevant" and "is the answer supported" into the
generation sequence as reflection tokens, training the model end-to-end to decide when to retrieve
and how much to adopt. **SKR** [7] takes a lower-effort route: it labels questions by
the model's own sense of its knowledge boundary and triggers retrieval only for unfamiliar ones,
without touching the generation process. All three turn retrieval from a fixed pipeline stage into a
switch driven by generation-side self-assessment or meta-knowledge.

Deciding *how many steps* is equally mature. **Adaptive-RAG** [8] trains a query
complexity classifier that assigns questions to no retrieval, single-step retrieval or multi-step
retrieval; **Self-Ask** [9] decomposes composite questions into sub-questions that
are retrieved one by one; **IRCoT** [10] interleaves chain-of-thought with
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

**CRAG** [11] inserts a lightweight retrieval evaluator between retrieval and
generation, judges the result as correct, incorrect or ambiguous, and triggers one of three
corrective actions—use it, discard it for web search, or combine both. It is a pipeline-style scheme
that treats retrieval quality as an anomaly to be repaired; later work adds finer-grained
verification, iterative retrieval and adaptive correction, all keeping the
detect–branch–correct structure.

This line acknowledges that retrieval fails, at the price of writing correction as a conditional
branch: whether to correct is decided by the evaluator's verdict, independently of whether the
correction is worth its cost. We fold the corrective actions (rewriting, second-hop retrieval,
reranking) into the same action set and decide by gain-to-cost ratio—picked automatically when the
budget is loose, skipped automatically when it is tight, with no separate correction stage. The two
compose: a CRAG-style evaluator can serve as a prior for $g(a\mid S)$ in our action set—the evaluator
scores, the ordering rule decides.

### 2.3 Cost-Aware Retrieval

Cost-aware retrieval approaches from the other end: if acquiring each piece of evidence itself costs
money (paid retrievers, external APIs, human annotation), the selector must trade utility against
expense. Prior work reports that static selectors are brittle under load shifts and that larger
budgets do not reliably improve quality [12], which argues for modelling the allocation
policy explicitly rather than tuning it.

We handle a different cost: **context occupancy**. It never appears on a retrieval bill, yet three
things price it simultaneously—per-token billing, the attention budget, and position sensitivity
[4]. This explains why fixed top-$k$ misses at both ends: too much for easy
questions, too little for hard ones. The two costs can be written into one knapsack problem by
making action cost a vector (access fee plus occupancy fee) and the budget multi-dimensional. We
solve the occupancy dimension only; the two compose directly, and under a multi-dimensional budget
the optimal policy moves from a single threshold chain to a chain on the Pareto frontier while the
ordering rule is unchanged (Section 7.3).

### 2.4 Compression, Reranking and Query Rewriting

One line subtracts from what has already been fetched. **LLMLingua** [13] uses a
small model's perplexity to estimate token importance and compress the prompt; **LongLLMLingua**
[14] adds question-aware compression to reduce information loss on long documents;
**RECOMP** [15] trains extractive and generative compressors that turn multiple passages
into a summary. These methods raise information density per token, trading compression rate against
fidelity.

Reranking changes the order of the same candidates. **monoT5** [16] casts
relevance as sequence-to-sequence generation, and **RankGPT** [17] uses a large model for
listwise reranking. Reranking does not reduce the number of candidates; it decides who gets packed
first when the budget truncates, and its gain is realized only when truncation actually happens.

On the rewriting side, **HyDE** [18] replaces the query with a generated pseudo-document
for dense retrieval, and **Rewrite-Retrieve-Read** [19] places a rewriter before the
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
and summarization: **MMR** [20] subtracts similarity to already-selected
items from relevance and selects greedily one at a time, while Lin and Bilmes [21] write coverage
and diversity into one family of submodular functions and summarize under a unified objective. The
approximation bound comes from Nemhauser et al. [22]: for a monotone submodular function under a
cardinality constraint, greedy selection by marginal gain is within $1-1/e$ of optimal. With
heterogeneous costs the bound of unit-cost greedy drops to $(1-1/e)/2$; the modified greedy of
Khuller et al. [23] adds local enumeration across tiers and restores $1-1/e$ for the budgeted case.
These results establish that ordering by gain-per-cost is not a heuristic but a bounded
approximation algorithm.

Threshold stopping has long had an optimal-stopping form in statistics: sequential analysis shows
that with increasing costs and observations arriving in stages, the optimal policy is a threshold—
stop when the observation is good enough, continue otherwise [24]. The form was rediscovered
in LLM serving: **FrugalGPT** [25] answers with a cheap model first and decides by
confidence whether to escalate to a stronger and more expensive one, validating threshold routing on
real billing.

We join the two: submodular ordering decides which action to buy next, and the threshold decides when
to stop. We do not reprove the approximation bound—Proposition 1 cites the budgeted result directly
(Section 5); the increment is to replace the selected "elements" with "actions": chunks, hybrid
retrieval, rewriting, reranking and second-hop retrieval share one definition of cost and gain.
Proposition 3 extends the threshold form to retrieval actions: when action costs increase and gains
decrease monotonically with confidence, the optimal policy is again a chain of confidence thresholds,
with thresholds moving monotonically with the budget. The difference from FrugalGPT is the direction
of the constraint: it minimizes cost subject to a quality target, whereas we maximize quality subject
to a budget; the two are dual, and the dual variable is exactly our shadow price $\lambda$. This is
why we can write "what the threshold should be" as a computable formula instead of a hyperparameter to
be searched.

### 2.6 Our Position

**Table 1.** Comparison of representative adaptive-retrieval lines against this work. Table 1 summarises this positioning.

| Line | Decision object | Role of the budget | Trigger signal | Relation to this work |
|---|---|---|---|---|
| Adaptive and multi-hop [5,6,8,9,10] | Whether to retrieve, how many steps | External constant | Generation confidence / complexity classifier / question decomposition | We add "how much to give" and make the second hop a priced action |
| Corrective [11] | Whether the result is trustworthy, how to fix | Not modelled | Fine-tuned evaluator | Corrective actions join the action set and fire by cost-effectiveness; the evaluator serves as a gain prior |
| Cost-aware [12] | Which evidence to buy | Spending cap | Utility-to-cost ratio | Cost becomes context occupancy; composes into a multi-dimensional knapsack |
| Compression and reranking [13,14,15,16,17] | What to delete, who gets packed first | Token cap | — | Orthogonal and composable; compression is a cost discount, reranking is paid by budget tightness |
| Submodular selection [20,22,23] | Selecting a subset from a fixed pool | Cardinality or coverage budget | Marginal gain | Elements become actions: heterogeneous costs, gains estimated online |
| Cascades and thresholds [24,25] | When to escalate to a costlier tier | Threshold / quality constraint | Confidence | We extend the threshold chain to retrieval actions, with thresholds from the shadow price |

Taken together, prior work advances four questions—whether to retrieve, whether retrieval is right,
whether evidence is expensive, and whether context can be deleted—and they share an unstated
assumption: **retrieval behaviour can be chosen independently of the budget**. We supply that layer,
writing the budget as an explicit constraint and the shadow price as an observable quantity, with the
policy derived from their ratio. Which tier, whether to rewrite, whether to second hop and who gets
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

For each query, let $\mathcal{A}$ denote the available retrieval actions and $S \subseteq \mathcal{A}$
the actions selected. Each action $a$ has cost $c(a)$ and marginal gain $g(a \mid S)$ given $S$. We
assume that the quality $Q(S)$ is monotone non-decreasing. Under budget $B$, the policy selects an
action set by solving

$$\max_{S \subseteq \mathcal{A}} Q(S) \quad \text{subject to} \quad \sum_{a \in S} c(a) \le B .$$

The subsequent results rely on two assumptions. Under **(A1)**, marginal gains diminish:
$g(a \mid S) \ge g(a \mid T)$ whenever $S \subseteq T \subseteq \mathcal{A}$ and $a \notin T$.
Under **(A2)**, action costs are additive and independent of execution order.

## 4. Method

Our retrieval layer combines sparse BM25 scoring [2] with dense bi-encoder retrieval [3].

### 4.1 Dual Index and Budgeted Chunk Selection

Long documents are indexed at two granularities (Figure 1). Sentence-level chunks are split on
punctuation and contain roughly 15-40 tokens. Fixed blocks use a sliding 200-token window with a
40-token overlap by default. Sentence-level indexing keeps unrelated sentences out of a retrieved
chunk, which benefits short-sentence corpora such as the Chinese technical notes in Section 6.2;
fixed blocks preserve a coherent window and perform better on English documentation, reaching 0.910
versus 0.718 at a 300-token budget (Section 6.9). Whether both indexes are built is therefore a
corpus-level decision: short-sentence corpora are dual-indexed, while English documentation is
indexed with fixed blocks only. When both exist, the per-query budget $ctx$ (in tokens, equal to
$B$) selects sentence level for $ctx \le 500$ and fixed blocks otherwise.

Chunks are added in descending retrieval-score order until the selected chunks reach the token budget
$B$, without imposing a fixed top-$k$ cutoff. Section 6.9 qualifies this design: on real corpora the
truncation behaves like a well-chosen fixed $k$, and an operational difference appears only when
retrieval depth is chosen per query from the score margin.

### 4.2 Cascade Routing

Routing has three tiers, defined by the admissible cost per thousand tokens. Very tight budgets
(< 0.002 CNY) select one BM25 chunk, medium budgets (0.002-0.01 CNY) select two, and generous budgets
($\ge$ 0.01 CNY) select five chunks from hybrid retrieval. These tiers discretize the greedy
allocation of Proposition 1 and correspond to the knee of the gain-per-cost curve.

### 4.3 Confidence-Gated Query Rewriting

Because rewriting accounts for about half of end-to-end latency (Section 6.8), we invoke it only when
needed. An initial low-cost retrieval provides the relative margin between the top two scores,

$$\gamma = \frac{s_1 - s_2}{s_1}.$$

When $\gamma < \tau$ the retrieval is treated as uncertain: the query is rewritten and retrieval is
repeated with "original question + rewrite terms". The shadow price of the budget determines the
optimal threshold (Proposition 2); the default $\tau = 0.25$ corresponds to pricing a rewrite at about
one strong retrieval. Section 6.7 confirms that $\tau$ falls as the unit price rises.

### 4.4 Multi-Hop Extension

For questions that need two pieces of evidence, a second retrieval hop is added. After the first hop,
the model receives the question plus a summary of the retrieved material and identifies what is still
missing; the second hop then searches for "original question + supplementary query", and the two
result sets are merged with chunk-level deduplication. The supplementary query is model-generated
rather than extracted by a fixed rule, so it can name the missing entity directly.


![Figure 1. System overview](figures/fig1-pipeline.png)

**Figure 1.** System overview. Short-sentence corpora are indexed twice (sentence level and fixed
blocks) and English documentation is indexed with fixed blocks only; when both exist, the per-query
budget decides which one is used (Section 4.1). Routing assigns a tier; the first retrieval yields
the confidence $\gamma$; the gate decides whether to rewrite and re-retrieve; chunks are accumulated
until the budget $B$ is reached; a second hop is enabled when two pieces of evidence are needed.
Dashed edges are optional paths; $c(a)$ and $g(a\mid S)$ are the cost and gain used for ordering.

## 5. Theory

This section states four consequences of the formulation in Section 3. Propositions 1 and 4 are proved
below; Propositions 2 and 3 follow from the shadow-price view and are used operationally in
Sections 4.2-4.3.

**Proposition 1 (approximation bound).** Under A1 (diminishing returns) and A2 (additive costs),
$Q(S)$ is monotone submodular. Greedy selection by marginal gain attains $1-1/e$ under a cardinality
constraint [22]; under a budget constraint the bound of unit-cost greedy drops to $(1-1/e)/2$ and is
recovered to $1-1/e$ with cross-tier enumeration [23]. We instantiate this ordering on the retrieval
action set, and measure the gap to the brute-force optimum in Appendix A.

**Proposition 2 (rewriting gate).** Let $q_0$ and $q_1$ be the quality without and with rewriting, $p$
the probability that rewriting helps, and $c_r$ its cost. Rewriting pays off exactly when
$p(q_1 - q_0) > \lambda c_r$, where $\lambda$ is the shadow price of the budget. Equivalently,
rewriting is triggered below a confidence threshold that is solved from $\lambda$ rather than fixed at
0.25 (Section 4.3).

**Proposition 3 (cascade threshold chain).** Suppose the actions can be ordered by increasing cost,
and that the gain of each action decreases monotonically with confidence. Then the optimal policy
assigns each confidence interval to one tier -- a threshold chain -- and the thresholds move
monotonically with the budget $B$. This explains why cascades work and implies that tier boundaries
should follow the budget (Section 4.2).

**Proposition 4 (monotonicity of the threshold).** Assume **A3**: the rewriting gain
$B(\gamma) = p(\gamma)\Delta q(\gamma)$ is non-increasing in the retrieval confidence $\gamma$.
Then the optimal threshold satisfies $B(\tau^*) = \lambda c_r$, and $\tau^*(\lambda)$ is
non-increasing in $\lambda$.

*Proof.* By Proposition 2 the criterion for rewriting is $B(\gamma) > \lambda c_r$. A3 makes $B$
non-increasing, so the confidences that satisfy the criterion form an interval $[0, \tau^*)$. As
$\lambda$ grows, the right-hand side $\lambda c_r$ grows, the feasible set shrinks, and $\tau^*$
therefore does not increase. At the boundaries, $\lambda c_r \ge B(0)$ gives $\tau^* = 0$ (never
rewrite) and $\lambda c_r \le B(1)$ gives $\tau^* = 1$ (always rewrite). Section 6.7 verifies the
former boundary: when the unit-price coefficient rises to 2, the optimal threshold falls from 0.25 to 0.

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

**Metrics.** Throughout, *recall@budget* is measured under a matched token budget rather than at a
fixed depth: chunks are taken in rank order until their cumulative token count reaches the budget $B$,
and a query counts as retrieved when the gold answer span appears in the selected chunks (for BEIR we
use document-level relevance and report nDCG@10). Token counts are produced by the tokenizer of the
reference model, so a passage of the same text costs the same across methods; monetary cost is read
from the API-reported usage. Reporting at a matched budget is what makes two methods comparable when
their chunk sizes, depths and token accounting differ.

**Hardware.** i7-13650HX, 16 GB RAM, RTX 4060 Laptop 8 GB. API models run over the network, the
local model on the GPU; all retrieval and statistics run on the CPU.

### 6.2 Main Results (Controlled Synthetic Setting)

This subsection reports the controlled setting: a 200-query subset of the 500-question synthetic
benchmark over sixteen technical notes, where every method sees the same corpus and budget. Section 6.9 repeats the
comparison on 312 official documentation pages and on BEIR, and revises two of the claims made here.

Under this controlled setting the proposed system is stronger at equal or lower budget.

**Table 2.** Main results on a 200-query subset of the 500-question synthetic benchmark (800-token budget). Table 2 reports the main comparison.

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

**Table 3.** Seed stability across five 2/3 subsamples. Table 3 reports the stability check.

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

**Table 4.** Ablation: removing each component in turn. Table 4 reports the ablation.

| Removed component | Recall change | Interpretation |
|---|---|---|
| Gate (rewrite on every query) | −3.6 pt | Rewriting helps, but not on every query |
| Hybrid retrieval (BM25 only) | −6.8 pt | Semantic matching carries most of the signal |
| Budget 300 → 100 | −6.1 pt | Budget matters, but must be allocated by difficulty |
| $\alpha$ 0.2 → 0.5 | −1.7 pt | The default weight is not optimal for this corpus |

These numbers come from the controlled synthetic setting of Section 6.2. Figure 3 summarizes the ablation: dropping hybrid retrieval costs the most (−6.8 pt), followed by
tightening the budget (−6.1 pt), so the gains come mainly from semantic matching and budget
allocation, with the gate as a refinement (−3.6 pt).

![Figure 2. Budget versus recall (sentence-level vs fixed blocks)](figures/fig2-budget-recall.png)

**Figure 2.** Recall across token budgets of 80-800 tokens, on the short-sentence synthetic corpus,
for sentence-level chunks and fixed blocks. Sentence-level chunks lead up to 300 tokens (0.912 versus
0.894 at 300) and fixed blocks lead from 500 (0.928 versus 0.918); on English documentation fixed
blocks lead at every budget (Section 6.9). The crossover is therefore a property of short-sentence
corpora, not a universal rule, and the corpus-level decision of Section 4.1 determines whether it
applies.

![Figure 3. Ablation: recall cost of removing each component](figures/fig3-ablation.png)

**Figure 3.** Ablation relative to the full system; the horizontal axis is answer-span recall and
parentheses give the change in percentage points.

### 6.4 Cross-Corpus Check

On the LongBench Chinese retrieval subset our recall is 0.995 against 0.955 for BM25; on the
English subset both reach 1.000. The claim here is that performance does not degrade across
corpora and that the direction of the relative gain is preserved; absolute levels depend on task
difficulty and are not used as a comparison basis.

### 6.5 The Benefit of Retrieval Is Model-Agnostic

One hundred questions per dataset, the same 800-token budget, local Qwen3-4B generation; brackets are
bootstrap 95% intervals.

**Table 5.** Benefit of retrieval across datasets and models (Qwen3-4B, 800-token budget). Table 5 reports per-dataset results.

| Dataset | With retrieval | 95% CI | Without | McNemar p |
|---|---|---|---|---|
| HotpotQA | **0.400** | [0.300, 0.500] | 0.120 | <0.0001 |
| 2WikiMultiHopQA | **0.250** | [0.170, 0.330] | 0.090 | 0.0009 |
| MuSiQue | **0.140** | [0.080, 0.210] | 0.000 | 0.0001 |
| TriviaQA | 0.090 | [0.040, 0.150] | **0.190** | 0.0020 |
| HotpotQA (DeepSeek-V4.1-Flash) | **0.520** | [0.420, 0.620] | 0.230 | <0.0001 |

The standard deviations over five 2/3 subsamples are 0.007, 0.051, 0.034 and 0.019 respectively, so the
ordering does not depend on which questions are drawn.

The first four rows—including the hosted large model—support the claim: on multi-hop tasks retrieval
raises accuracy from 0–0.23 to 0.14–0.52, and the improvement is significant in every case; the direction
is the same for the large and the small model, so the conclusion does not depend on the generator.

**The fourth row is a significant negative effect, reported as measured.** TriviaQA questions are
largely commonsense, so the model answers from its parameters; the corpus consists of twenty-odd
distractor passages and an 800-token budget covers about 11% of it, so the retrieved fragments pull the
model off course—an effect that is significant at n = 100 (0.090 vs 0.190, p = 0.002). This says that
**whether to retrieve is itself a decision**, complementary to our gate, which only decides whether to
rewrite. Upgrading the gate into a "retrieve or not" decision is the natural next step (Section 8).

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

**Table 6.** End-to-end efficiency on twenty queries with the answer cache disabled. Table 6 reports latency and cost.

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

### 6.9 Real Documents and Public Benchmarks

The main table above rests on sixteen synthetic technical notes, which is small. This section replaces
the corpus with 312 official documentation pages (Docker 147, Redis 89, Kubernetes 43, Grafana 19,
Prometheus 14; 1.9M characters, 16,823 chunks) and adds four BEIR subsets for public-protocol validation.

**Internal benchmark (301 questions, document-level recall)**

**Table 7.** Internal benchmark: 301 questions, document-level recall. Table 7 reports the internal benchmark.

| Method | Recall | mean tokens |
|---|---|---|
| BM25 | 0.801 | 318 |
| Dense (bge-m3) | 0.887 | 318 |
| Hybrid (alpha=0.2) | **0.910** | 318 |
| Ours (budget-300 truncation) | 0.910 | 318 |
| Fixed k=8 | 0.904 | 289 |
| **Ours (difficulty-adaptive, k=4/10)** | **0.900** | **244** |

Paired bootstrapping over the 301 questions puts the recall difference at -0.003 (95% CI
[-0.020, +0.010], p = 0.81) and the token saving at **15.5%** (95% CI [11.2%, 19.8%]): the rule is
statistically indistinguishable from fixed k = 8 on quality while using 11-20% fewer tokens.

**BEIR (public protocol, document level)**

We run four BEIR subsets through the same pipeline (bge-m3 embeddings, hybrid alpha = 0.2, chunk size
200) and use fixed k = 8 as the reference; the adaptive configuration is the cheapest one whose
nDCG@10 stays within 0.002 of that baseline. All queries are used, without subsampling.

**Table 8.** BEIR results on four subsets, all queries, fixed k = 8 as reference. Table 8 reports the BEIR results.

| Dataset | Fixed k=8 nDCG@10 | tokens | Adaptive nDCG@10 | tokens | Saving |
|---|---|---|---|---|---|
| scifact | 0.7071 | 2615 | 0.7062 | 1991 | 24% |
| nfcorpus | 0.3504 | 2747 | 0.3486 | 2571 | 6% |
| fiqa | 0.4356 | 1999 | 0.4350 | 1978 | 1% |
| arguana | 0.3931 | 1879 | 0.3959 | 2177 | -16% |

The saving is largest where the corpus is small and the margin distribution is bimodal (scifact),
shrinks as the corpus grows and margins flatten (fiqa has 57,638 documents), and reverses on
arguana, an adversarially constructed benchmark where every adaptive setting we tried spent more
tokens for an offsetting gain. The margin signal therefore orders queries by difficulty on natural
corpora but not on adversarially built ones. We report that failure instead of tuning tau per dataset
to hide it. scidocs was also run but is excluded: its documents are long enough that the embedding
endpoint truncates them, which depresses absolute nDCG for every method equally.

**Significance on real documentation.** At a 300-token budget the paired comparison on the 301 At a 300-token budget the paired comparison on the 301
questions is mixed, and we report it as such. Hybrid beats BM25 decisively (36 wins, 3 losses,
McNemar p < 0.0001, surviving Holm correction for three comparisons) and also beats dense bge-large
(25 wins, 8 losses, p = 0.0046, Holm-adjusted 0.0091), but ties dense bge-m3 (11 wins, 4 losses,
p = 0.12). On this corpus the system therefore matches the strongest dense retriever rather than
surpassing it; the contribution in this setting is the cost side, not the accuracy side.

Three revised conclusions. First, the transferable gain is **difficulty-adaptive depth**: at equal
recall or hit rate it saves 1-24% of context, the saving tracking how many queries can be
answered confidently (24% on scifact, 6% on nfcorpus, 1% on fiqa, where a 57k-document corpus
flattens the score margins, and none on the adversarial arguana set). Second, **token-based truncation alone carries
no advantage**: on the internal benchmark fixed k=8 reaches the same recall as budget-300 truncation
(294 vs 318 tokens), so the difference comes from deciding how many chunks each query needs, not from
stopping at a token count. Third, **sentence-level indexing and gated rewriting do not transfer**: on
English documentation the sentence index scores 0.718 against 0.910 for fixed blocks, and gated
rewriting 0.874 against 0.910, so those claims must be restricted to short-sentence Chinese corpora
where question and document wording diverge.

The claim of this paper is therefore revised: **on heterogeneous loads where a single k is hard to
preset, deciding retrieval depth from the retrieval-score margin saves substantial context at no
measurable loss of quality.** The high recall observed on the synthetic corpus is a controlled-setting
result and is not claimed to generalize.

### 6.10 From a Budget to a Quality Target

Users do not ask for "300 tokens"; they ask for "90% recall". Turning the second into the first is a
calibration problem, and it admits a distribution-free solution with a finite-sample guarantee.

**Protocol (split conformal).** Sample N labelled questions (N = 20), record for each the smallest
budget at which the answer span enters the context, and set the budget to the ceil((N+1)(1-alpha))-th
smallest of those values; alpha = 1 - T for a target T. If the required order statistic is infinite --
that is, the calibration sample never reaches the target -- the protocol reports the target as
unreachable instead of returning a number. Under exchangeability of calibration and test questions,
the resulting budget covers a new question with probability at least 1 - alpha, so the expected recall
is at least T. One hundred random splits separate calibration from evaluation.

**Table 9.** Conformal calibration: coverage at three targets and two weaker retrievers. Table 9 reports empirical coverage.

| Retriever | Target | Budget (median) | Empirical coverage | Nominal | Gap |
|---|---|---|---|---|---|
| Hybrid (bge-m3) | 0.80 | 120 | 0.810 | 0.800 | +0.010 |
| Hybrid (bge-m3) | 0.85 | 166 | 0.865 | 0.850 | +0.015 |
| Hybrid (bge-m3) | 0.90 | 276 | 0.891 | 0.900 | -0.009 |
| Dense (bge-large-en) | 0.80 | 238 | 0.802 | 0.800 | +0.002 |
| Dense (bge-large-en) | 0.90 | 548 | 0.880 | 0.900 | -0.020 |
| BM25 | 0.80 | 368 | 0.789 | 0.800 | -0.011 |
| BM25 | 0.90 | 708 | 0.848 | 0.900 | -0.052 |

Three findings follow. First, on the strongest retriever the guarantee holds: empirical coverage tracks
the nominal level within 0.015 at all three targets, and the budgets (120-276 tokens) stay well below
what a fixed k = 8 needs for the same recall (289 tokens). Second, calibration is retriever-specific:
under bge-large-en the gap at 0.90 widens to -0.020 and under BM25 to -0.052 with a 55% refusal rate at
that target, so a change of retriever requires recalibration and an honest refusal path. Third, a
saturating-curve variant with a safety margin reaches a similar reach rate but needs a hand-tuned
margin and gives no guarantee, so the conformal form is preferred.

The guarantee holds across the range rather than at three points. Sweeping alpha from 0.05 to 0.50
moves nominal coverage from 0.95 to 0.50, and empirical coverage tracks it within 0.046: 0.922 at
0.95, 0.891 at 0.90, 0.865 at 0.85, 0.810 at 0.80, 0.754 at 0.75, 0.699 at 0.70, 0.646 at 0.60 and
0.524 at 0.50 (Figure 5). The one systematic gap is the far tail: at nominal 0.95, 28% of calibration
samples never reach the target and the protocol refuses rather than under-covers, and among the samples
that do return a budget the median is 664 tokens.

![Figure 5. Coverage diagnostic](figures/fig5-conformal.png)

**Figure 5.** Empirical coverage against nominal coverage for the conformal protocol on the hybrid
retriever, sweeping alpha from 0.05 to 0.50. The grey diagonal is nominal = empirical; vertical bars
mark the 5th percentile of coverage across 100 random splits; labels give the median budget and the
refusal rate.

![Figure 4. Calibration curves and reach rate](figures/fig4-calibration.png)

**Figure 4.** (A) Recall against context budget for four retrievers on the 301-question benchmark; the
dashed lines mark the 0.80, 0.85 and 0.90 targets. (B) Reach rate against the safety margin for the
curve-based variant, shown for comparison with the conformal protocol of this section.

### 6.11 Why a Second Budget Does Not Bind

Real systems are constrained by tokens, latency and money at once, so one may ask whether a scalar
budget is an oversimplification. We measured the retrieval side directly on the 301-question benchmark:
BM25 takes 16 ms, dense retrieval 45 ms (including query encoding) and hybrid retrieval 73 ms, while
generation takes 898 ms at p50 (Section 6.8). Retrieval therefore accounts for at most 7.5% of
end-to-end latency, and the three cost dimensions are collinear in this setting: money is a fixed
multiple of tokens, prefill latency is close to linear in context length, and the spread across
retrievers (16-70 ms) is too small to move a latency budget.
The resulting operating points, including the official classifier of Section 6.16, are:

**Table 10.** Operating points of all policies, including the official classifier of Section 6.16. Table 10 lists the operating points.

| Policy | Recall | mean tokens | mean latency (ms) |
|---|---|---|---|
| Official classifier (faithful) | 0.638 | 150 | 74 |
| Official classifier (adapted) | 0.844 | 160 | 74 |
| BM25 top-8 | 0.801 | 318 | 16 |
| Dense bge-m3 top-8 | 0.887 | 318 | 45 |
| **Ours (adaptive k=4/10)** | **0.900** | **244** | 72 |
| Hybrid top-8 | 0.910 | 318 | 73 |

Latency here is retrieval only; the classifier adds 21 ms of CPU inference and nothing else. Every
policy therefore lands between 16 and 74 ms, an order of magnitude below the 898 ms of generation, so
latency does not create a second binding constraint. On the token-recall plane the learned classifier
is an interior point (0.844 at 160 tokens) rather than an extreme: fixed top-3 is cheaper and top-5
more accurate, while our gate and fixed top-8 occupy the high-recall end at 244 and 318 tokens.



The only action with a distinct cost vector is query rewriting, which adds both tokens and about
870 ms of latency. On this corpus it also lowers recall (0.874 against 0.910), so it is dominated in
every two-dimensional budget. A second dimension would only bind when a component carries a different
cost shape: per-call web search fees, routing between models of different price and quality, or an
end-to-end latency SLA tight enough to exclude rewriting outright. The scalar budget is therefore not a
simplification of the problem but the correct model for this operating regime, and we state the
conditions under which it would have to be extended.

### 6.12 The Exchange Rate between Retrieval Time and Context Length

Section 6.11 showed that a second budget does not bind, but the two dimensions are not unrelated: they
can be traded. At equal recall, a stronger retriever needs less context. On the 301-question benchmark,
reaching 0.80 recall costs BM25 331 tokens at 16 ms but hybrid retrieval 114 tokens at 74 ms, so 58 ms
of retrieval time buys 217 tokens, an exchange rate of **3.7 tokens per millisecond**; at a 0.90 target
the same swap saves 1050 tokens, or **18.3 tokens per millisecond**.

Whether the trade is worth it depends on what a token costs downstream. Measuring prompt prefill
directly with a local Ollama deployment (`prompt_eval_duration`, randomised prompts to defeat prefix
caching) gives 195 ms for 100 prompt tokens, 570 ms for 300, 1194 ms for 600 and 2125 ms for 1000, a
slope of **2.15 ms per token** on CPU. The net gain from swapping to the stronger retriever is then 467
ms at a 0.80 target and 2258 ms at 0.90, against 58 ms of extra retrieval.

The break-even condition is r * p > 1, where r is the exchange rate in tokens per millisecond and p is
the prefill cost per token. On this machine 3.7 * 2.15 = 8.0, so the swap always pays. On a GPU where
prefill costs about 0.1 ms per token the product falls to 0.37 at a 0.80 target, so the swap stops
paying there but remains profitable at 0.90 (1.83). The trade is therefore computable rather than
qualitative, and it explains the conclusion of Section 6.11 from the other side: retrieval time is so
cheap relative to context that spending it is almost always right.

### 6.13 How the Questions Were Written, and How Much They Overlap the Sources

The 301 questions come from two sources: six were written by the author in Chinese and translated, the
remainder were drafted from the documentation and then checked by the author against the source
passage, with the answer required to appear verbatim in the document. Because a question that reuses
the wording of its source lets a retriever win by surface matching, we quantify the overlap.

For every question we compute the fraction of its 4-grams that occur in the source document, and the
longest run of words shared with it. Median 4-gram coverage is **0.000** (mean 0.044); only 5 of 301
questions (1.7%) exceed 0.50, all of them short definitional questions such as "What is a container?";
the longest shared run is 2 words at the median and 9 at the maximum. As
a control, using the answer-bearing source sentence itself as the query yields median coverage
**1.000**. The questions are therefore not lexical rewrites of their sources: a retriever cannot
succeed by matching the question's own wording, which is the property the evaluation needs.

### 6.14 Where the Errors Come From

At a 300-token budget the hybrid retriever misses 27 of the 301 questions. In every one of those
cases the answer span **does exist** in the target document, so the failures are ranking failures
rather than data errors: the correct passage was in the corpus but did not make it into the budget.
The misses concentrate on short, low-signal answers -- a bare number (`0.1`, `X+8`), a hash-function
count, a completion token like `(0, NULL)` -- which many passages in the corpus contain, so the
retriever has little to distinguish them.

On the multi-hop generation benchmarks the failure mode is different: across 300 questions every output
was non-empty, and the errors are **wrong-entity substitutions** rather than refusals. For example the
comparison question "which case was brought first, Miller v. California or Gates v. Collier" is answered
with the second case, and "where was the wife of Francis I Rakoczi born" is answered with the place she
lived. Retrieval hit the answer span 0.51-0.69 of the time while accuracy was 0.14-0.52, so roughly
half of the remaining gap is lost on the generation side, not in retrieval.

The practical reading is that neither more context nor a larger budget fixes these two failure modes:
the first needs better ranking of short answers, the second better entity disambiguation and two-hop
evidence composition.

### 6.15 Order-Dependent Costs: the Guarantee Breaks, the Decisions Do Not

Assumption A2 treats costs as additive and order-independent. Real deployments do not: a second chunk
from the same document usually shares a prefix, so its incremental cost is lower, and batching
discounts depend on what was already fetched. We therefore asked whether the budgeted greedy rule
survives a per-document discount.

**Theory first.** With "first chunk of a document at full price, later chunks at d times the price",
the cost of a set becomes submodular rather than modular: marginal cost drops from p to d*p after the
first chunk of a document. The bounds of Section 5 (Khuller et al.) assume modular costs, so the
(1-1/e)/2 guarantee and its cross-tier recovery no longer follow. This is a genuine gap, not a
technicality.

**Experiment.** On the 301 questions we restricted each query to its top-12 candidates and enumerated
all 2^12 subsets, computing the true discounted cost and the achieved recall for d in {1.0, 0.7, 0.5,
0.3}. A true-cost greedy selected by gain per *actual* marginal cost, a naive greedy took candidates in
score order while charging full price, and both were compared with the exhaustive optimum.

The three policies agree on quality at every discount: mean recall 0.927 for the exhaustive optimum and
for the true-cost greedy, 0.910 for the naive policy; greedy reaches the optimum on 301/301 questions,
and the naive policy never exceeds the budget by more than rounding.
The reason is the metric, not the algorithm: recall is binary per question (the answer span is either
in the context or not), and the span sits in the single best chunk for 202 of 301 questions, so any
policy that takes that chunk is optimal regardless of what the rest costs. Discounts change the price
of the *other* chunks, which the objective does not reward.

The practical reading is twofold. First, the theoretical guarantee genuinely does not transfer, and a
paper that claims it under order-dependent costs would be wrong. Second, for single-span retrieval the
non-additivity is inert -- it matters only when the objective requires combining evidence from
different chunks, as in multi-hop questions, or when the answer is split across passages. We therefore
keep A2 as a stated assumption, report the break in the guarantee here, and do not claim the bound for
deployment settings with prefix caching.

### 6.16 Reproducing the Official Complexity Classifier

The strongest criticism of a routing paper is that it never runs the routing baseline it compares with.
Appendix C approximates the behaviour with TF-IDF and BERT classifiers; here we replace that with a
model trained by the official recipe on the official labels.

Adaptive-RAG does not release a checkpoint, but its repository ships the silver training labels
(A/B/C complexity) that its own classifier is trained on: 3,817 training and 1,431 validation
questions. We trained the same T5 sequence-to-sequence objective on those labels. Our run uses
t5-small with six epochs on CPU rather than the paper's T5-large on GPU, and reaches **43.3%**
three-way accuracy on the released validation split (the majority class alone accounts for about 40%),
so it is a faithful mechanism reproduction at reduced model scale, not the original model.

We then applied the classifier to our 301 questions and routed with the paper's own mapping: A (simple)
takes no context, B (single-hop) retrieves five passages, C (multi-hop) retrieves ten.

**Table 11.** Routing results of the official complexity classifier on the 301 questions. Table 11 reports the routed results.

| Method | Recall | mean tokens |
|---|---|---|
| Official classifier (faithful: A = no retrieval) | 0.638 | 150 |
| Official classifier (adapted: A = top-1 passage) | 0.844 | 160 |
| Hybrid top-3 | 0.824 | 108 |
| **Ours (difficulty-adaptive, k=4/10)** | **0.900** | **244** |
| Hybrid top-8 | 0.904 | 289 |

The classifier assigns 83 questions to A, 189 to B and 29 to C. Its operating points sit between
fixed-depth retrieval points: 0.844 at 160 tokens falls between top-3 (0.824 at 108) and top-5 (0.890
at 180), so it neither dominates fixed depth nor reaches the high-recall regime, where an A prediction
removes the evidence outright. Its routing is also fixed: there is no knob that trades tokens for a
target recall. That is precisely the interface Section 6.10 provides and this baseline lacks, which is
why the two are complementary rather than competing -- the classifier picks one operating point from a
learned prior, the conformal protocol certifies a target quality at whatever budget that costs.

### 6.17 Per-Query Thresholds: Tested, No Gain

The depth rule of Section 6.6 uses one global threshold tau on the normalised margin
gamma = (s1 - s2) / s1, which has to be re-tuned when the corpus changes (0.12 on scifact, 0.20 on
nfcorpus). A per-query rule would remove that constant, so we tested the obvious one: stop where the
query's own score list drops sharply. Concretely, take the smallest k with
(s_k - s_{k+1}) / s1 >= delta, capped at k = 10, and sweep delta.

**Table 12.** Per-query threshold sweep: nDCG@10, tokens and saving against fixed k = 8. Table 12 reports the sweep.

| delta | recall | mean tokens | saving vs k=8 | mean k |
|---|---|---|---|---|
| 0.02 | 0.870 | 188 | 35% | 5.3 |
| 0.03 | 0.887 | 242 | 16% | 6.8 |
| 0.05 | 0.894 | 309 | -7% | 8.6 |
| 0.10 | 0.910 | 354 | -23% | 9.8 |

No setting beats the global threshold. The closest point, delta = 0.03, saves 16% of context but
loses 1.7 recall points (0.887 against 0.904 at fixed k = 8), whereas the global rule reaches 0.900
at 244 tokens, a loss of only 0.4 points. Above delta = 0.05 the rule simply stops early almost
never and costs more than fixed depth.

The reason is visible in the definition: hybrid scores are already normalised per query, so the
absolute gap (s1 - s2)/s1 is a comparable statistic across queries, while the *incremental* drop
between adjacent chunks adds noise -- one flat pair of scores is enough to trigger or suppress a cut.
We therefore keep the global threshold and report the per-query variant as a negative result; the
recalibration cost stays a stated limitation rather than being papered over by a rule that does not
work.

The same rule transfers to BEIR scifact, and fails there too: delta = 0.02 scores nDCG@10 0.6827 at
1818 tokens (30% fewer tokens, 2.4 points below fixed k = 8), delta = 0.03 scores 0.6895 at 2271
(13%), against 0.7071 at 2615 for fixed k = 8; the global threshold keeps nDCG@10 at 0.7062 while
saving 24%. The per-query drop is therefore not a substitute
for the global margin threshold on either the internal benchmark or the public one.



### 6.18 Is the Margin a Sufficient Statistic? An Empirical Test

The threshold rule of Section 6.6 treats gamma as a difficulty signal, but says nothing about *why*
it should work. The assumption it needs is that the marginal value of another chunk decreases as
gamma grows: confident queries gain little from depth, uncertain ones gain a lot. That is a
statement about the score distribution, and it can be tested before it is proved.

We split the 301 questions into gamma quartiles and compare recall at k = 4 and k = 10 within each
quartile.

**Table 13.** Marginal gain by margin quartile: recall at k = 4 and k = 10 within each quartile. Table 13 reports the quartile analysis.

| gamma quartile | n | recall k=4 | recall k=10 | delta (10-4) |
|---|---|---|---|---|
| Q1 (gamma <= 0.023) | 75 | 0.760 | 0.853 | 0.093 |
| Q2 | 75 | 0.840 | 0.907 | 0.067 |
| Q3 | 75 | 0.880 | 0.893 | 0.013 |
| Q4 (gamma > 0.117) | 76 | 0.974 | 0.987 | 0.013 |

The marginal gain is monotone decreasing in gamma: 0.093, 0.067, 0.013, 0.013. Queries the margin
calls confident gain almost nothing from six more chunks, and queries it calls uncertain gain most.
The empirical premise of the threshold rule therefore holds on this corpus.

We are careful about what this does and does not establish. It does **not** prove that gamma is a
sufficient statistic: a statistic can predict the average gain within a bin while failing to order
queries inside it, and the argument says nothing about the adversarial case of Section 6.9, where
the relation reverses. What it does show is that the assumption behind the threshold is not
vacuous, that its strength is roughly the shape one would assume, and that a formal treatment --
deriving marginal value from a Plackett-Luce or exponential-family model and bounding the threshold
rule's suboptimality -- has an empirically falsifiable target to aim at.

---

## 7. Discussion

### 7.1 Budget as an Interface, Not a Hyperparameter

Writing the budget as a constraint rather than a tuned $k$ buys three transferable properties.

The strongest transferable finding is narrower than the original framing. On 312 documentation pages and BEIR scifact, truncating by tokens buys nothing over a well-chosen fixed $k$ (294 versus 318 tokens at equal recall). What does transfer is deciding the depth per query from the retrieval-score margin: at equal hit rate that saves 1-24% of context on natural corpora, and nothing on an adversarial one (Section 6.9). The mechanism is therefore "how many chunks does *this* query need", not "stop at a token count".

First, the shadow price becomes a readable configuration value: $\lambda$ is the quality obtained per additional unit of budget, and it translates "how many chunks" into "is this unit still worth it". Section 6.7 shows the observable consequence—when the unit-price coefficient rises from 0.25 to 2, the optimal threshold falls from 0.25 to 0 and the system decides by itself that rewriting is not worth it at that price. A budget can therefore be written into configuration as an SLA (tokens and money per query) and survives a change of model or price without re-sweeping hyperparameters.

Second, the benefit of the gate must be reported together with the difficulty distribution of the load. It saves 62% of rewriting calls at a 38% trigger rate on the full set, but only 24% at 76% on the hard subset. Since rewriting dominates latency, what the gate saves is exactly the latency that scales inversely with batch difficulty; reporting a gate benefit without the trigger rate can make the same method look like opposite conclusions on two batches.

Third, the extension point is the action set alone. Adding an action (reranking, second hop retrieval, a compressor) only requires stating its cost $c(a)$ and marginal gain $g(a\mid S)$; the ordering rule and the approximation bound are unchanged. The reranking experiment illustrates the usage: with a pool of 8 and a 300-token budget the gain is 0.0 pt, whereas with a pool of 30 and a 150-token budget it is +5.5 pt. The gain comes from truncation, not from the action itself.

### 7.2 When It Applies

The gains come from heterogeneity in difficulty and tightness of budget; they are largest when both hold. Granularity experiments bound the budget regime: at or below 500 tokens the sentence-level index saves 15%–50% of context at equal recall, while above 800 tokens fixed blocks overtake it (Section 6.3). With a loose budget, freedom in *which* chunks to take is diluted—any policy can afford large blocks and allocation stops mattering.

Where the bottleneck sits decides where the gain lands. On the three multi-hop benchmarks retrieval hits the answer span 0.51–0.69 of the time, yet a 4B model answers correctly only 0.14–0.40 (Section 6.5): the evidence is already in the context and the generator fails to use it. Additional context budget is then absorbed by the generation side, and the money should move there—a stronger model, longer reasoning, an explicit extraction prompt. $\lambda$ points wherever marginal gain is highest; when that is not retrieval, it points elsewhere.

Finally, on a homogeneous load the benefit of scheduling tends to zero: on the synthetic set all policies except fixed shallow retrieval fall within the same confidence interval (Section 6.2), and fixed top-$k$ suffices; the gap only opens on heterogeneous loads.

### 7.3 Boundaries of the Cost Model

Assumption A2 (fixed, order-independent unit prices) is an approximation of real billing: tiered discounts, cache hits and batching all make $\lambda$ drift with the load. This does not require a new model—treat $\lambda$ as a runtime observable; the sweep in Section 6.7 is its time-invariant approximation, and online it can be updated over shorter windows.

The token estimate used for budget control is conservative. On the same prompt, tiktoken estimates 131 tokens while the API bills 71, an 84% overestimate (Section 8). Reported token costs are therefore upper bounds and the true cost is lower; the 126 tokens that buy 0.960 recall in Section 6.2 still leave margin.

Cost can also be a vector. Latency and money are different dimensions: rewriting takes about half of the end-to-end latency while its token cost is negligible. Charging both makes $c(a)$ a vector and turns the optimal policy from a single threshold chain into a chain on the Pareto frontier; the greedy guarantee relaxes to a per-dimension bound while the ordering rule is unchanged. Multi-dimensional budgeting is the most natural next step for this framework and needs no new theory.

### 7.4 Distance to the Lower Bound

An oracle that knows which chunk to take reaches 0.958 recall with 58 tokens (Appendix A); without that oracle we need 126 tokens for 0.960 (Section 6.2). The remaining cost gap comes from selection error—not knowing which chunk is better—rather than from insufficient context. The direction is therefore clear: improve the estimate of $g(a\mid S)$ and refine the selection granularity. The counter-intuitive result in Appendix A has the same origin: more labels did not improve routing, because the label depends on what was retrieved, not only on how the question is worded.

## 8. Limitations

The conclusions have seven boundaries. Corpus: the main evidence is 500 synthetic technical questions; cross-corpus validation covers retrieval only (Section 6.4) and the multi-hop generation results are small (Section 6.5), so transfer to production corpora needs an additional validation set. Baselines: the Adaptive-RAG and CRAG entries are behavioural approximations—a heuristic router and an off-the-shelf relevance evaluator (Section 6.1)—not reproductions of the fine-tuned models of the original papers, so the comparison is evidence at the same order of magnitude rather than an exact replication (Appendix C documents what was and was not reproduced). Cost: figures are converted from public unit prices and exclude batch discounts, cache hits and operations overhead (Section 7.3), which makes them suitable for relative comparison only. Token estimates: tiktoken over-counts Chinese relative to actual billing (Section 7.3), so the true context cost at equal recall is lower than reported. None of these four enters the abstract. Three further boundaries emerged when the corpus was enlarged. Main table: the 0.960 figure of Section 6.2 is a controlled synthetic setting; on real documentation the system ties a hybrid retriever (0.910) and the transferable gain is the 1–24% context saving of Section 6.9. Adaptive threshold: tau is a single global constant tuned per corpus (0.12 on scifact, 0.20 on nfcorpus). A per-query rule was tested and fails (Section 6.17), so recalibration remains a manual step. Public benchmarks: four BEIR subsets were run and one of them (arguana) shows no saving at all, so the gain is corpus-dependent (1–24%) rather than universal.

## 9. Conclusion

We formulated retrieval-depth selection as budget-constrained submodular maximization over priced
actions, and derived two implementable consequences: the rewriting threshold is set by the shadow price
of the budget, and the optimal cascade is a chain of confidence thresholds. On the controlled benchmark
the resulting system reaches 0.960 recall at 126 tokens; on 312 official documentation pages it reaches
0.910 recall at a 300-token budget, statistically indistinguishable from fixed depth at 11-20% fewer
tokens; on four BEIR subsets the same rule saves 1-24% of context at equal nDCG@10, and fails on an
adversarially constructed one, which we report. A split-conformal layer turns a recall target into a
budget with a coverage guarantee, and refuses targets a retriever cannot reach.

We also stated when the margin can be trusted: under a high-confidence regime and a non-thickening tail
(Appendix D), with two counterexamples marking exactly where each condition is necessary. The broader
lesson is that the context budget is better treated as an interface than as a hyperparameter: given a
target and twenty labelled questions, a system can certify what it promises, and say so when it cannot.

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
https://github.com/mylgtab/budget-rag (v1.1.0). A stranger can reproduce the main table in about
thirty minutes: clone, `pip install -e .`, `make check`. The repository ships small data snapshots so
reproduction does not depend on external mirrors, and CI rebuilds and queries the Docker image on
every push.

## Appendix C. Reproduction Notes for the Baselines

The two adaptive baselines in this paper are behavioural approximations rather than exact
reproductions. We state what was reproduced, and why we stopped there, so that readers can judge the
scope of the evidence.

**What the official code requires.** The official Adaptive-RAG repository ships four components: an
Elasticsearch retrieval service, a separate LLM serving process, execution scripts for the three
strategies (zero, single, multi), and a T5 classifier over three complexity labels
(`classifier/run_classifier.py`, classes A/B/C). Its dependencies are pinned to an older environment
(`torch>=1.7,<2.0`, a fixed transformers commit, `elasticsearch==7.9.1`, conda with Python 3.8), and
training the T5-large classifier does not fit on the 8 GB GPU used here.

**What we reproduced.** The core of the official classifier is that complexity labels are generated
automatically from the outcomes of running the three strategies. We follow the same construction on
our own benchmark—recording the smallest action that retrieves the answer as the complexity class
(one chunk / five hybrid chunks / requires rewriting)—which yields a 222/52/17/9 split, and train two
classifiers on it (TF-IDF and BERT, accuracy 0.747 and 0.702). The label construction and the
discrimination task therefore match the original; the model scale and environment do not.

**On the CRAG side** we likewise reproduce the behaviour: an off-the-shelf model judges whether the
retrieved context suffices (good / partial / bad), and a `bad` verdict triggers a rewritten query and
a second retrieval, mirroring the original correct / incorrect / ambiguous branches. The original uses
a fine-tuned lightweight evaluator; we use a general-purpose model.

**What was not reproduced, and why.** The Elasticsearch retrieval service and the LLM serving process
require separate service deployments and Linux scripts, and fine-tuning T5-large requires more memory
than is available. On the single Windows machine used for this work neither could be completed. The
comparison in Section 6.2 should therefore be read as evidence at the same order of magnitude, not as
a digit-for-digit match to the original paper.

**The conclusion from this level of reproduction is still informative.** With the label construction
matching the original, text-based classifiers (0.747 / 0.702) remain below the score-based gate
(0.960): the gap comes from the *source of the signal*, not from model scale or implementation detail.
Swapping in the original T5-large would be expected to raise classifier accuracy while leaving that
conclusion unchanged.

---

## Appendix D. Why the Margin Predicts Diminishing Returns

Section 6.18 shows empirically that the marginal value of another chunk decreases in the margin. This
appendix states the conditions under which that relation can be proved, and shows with two
counterexamples that each condition is necessary. We prove the two-chunk (k = 1) case; the general case
is stated as a conjecture supported by the measurements of Section 6.18.

**D.1 Notation.** As in Section 6.6: `p_i` is the conditional probability that chunk i contains the
answer given that chunks 1..i-1 do not; `Q(S_k) = P(E_k)`; `Δ_k = Q(S_{k+1}) − Q(S_k)`;
`γ = (s_1 − s_2)/s_1`.

**Lemma D.1.** Under the independence assumption of Section 6.6,
`Q(S_k) = 1 − ∏_{i≤k}(1−p_i)` and `Δ_k = (1 − Q(S_k)) · p_{k+1}`.

*Proof.* `1 − Q(S_k) = P(answer outside first k) = ∏_{i≤k}(1−p_i)` by independence; subtracting
`Q(S_k)` from `Q(S_{k+1})` leaves `∏_{i≤k}(1−p_i) · p_{k+1}`. ∎

The coefficient is `1−Q`, not `Q`: the gain can only come from the part not yet covered.

**Lemma D.2.** If `p_1 ≥ p_2 ≥ … ≥ p_K`, then for any fixed query `Δ_k` decreases in k.

*Proof.* `Δ_{k+1} = ∏_{i≤k+1}(1−p_i)·p_{k+2} ≤ ∏_{i≤k}(1−p_i)·p_{k+1} = Δ_k`, because
`1−p_{k+1} ≤ 1` and `p_{k+2} ≤ p_{k+1}`. ∎

**D.2 The cross-query theorem (k = 1).** Write
`Δ_1 = (1−p_1)·p_2 = ρ·p_1(1−p_1)` with `ρ := p_2/p_1`. The conclusion needs more than `p_1` growing.

*Assumptions.* **(M1)** the ranking scores order utilities; **(M2)** the conditional hit
probabilities decrease with rank, `p_1 ≥ p_2 ≥ … ≥ p_K`; **(M3)** `p_1 = g(γ)` with g increasing;
**(H1)** `p_1 ≥ 1/2`; **(H2)** `ρ` is non-increasing in `p_1`.

*Theorem.* Under M1, M3, H1, H2, `Δ_1` is non-increasing in γ. (M2 is not needed for k = 1; it is used in Lemma D.2.)

*Proof.* Take two queries q, q' with `p_1(q) ≤ p_1(q')`, both ≥ 1/2. By H2, `ρ(q') ≤ ρ(q)`. Let
`h(p) = p(1−p)`. Then
`Δ_1(q') − Δ_1(q) = ρ(q')h(p_1(q')) − ρ(q)h(p_1(q)) ≤ ρ(q)[h(p_1(q')) − h(p_1(q))]`,
using `ρ(q') ≤ ρ(q)` and `ρ ≥ 0`. Since `h'(p) = 1−2p ≤ 0` on `[1/2, 1]`, `h(p_1(q')) ≤ h(p_1(q))`,
so the difference is at most zero. With M3, larger γ implies larger `p_1`, hence smaller `Δ_1`. ∎

**D.3 Counterexample 1: M1 + M3 do not suffice.** Let `p_i ≡ θ` (constant). Then `ρ = 1` and
`Δ_1 = θ(1−θ)`, so `dΔ_1/dθ = 1−2θ`. For `θ < 1/2` the marginal gain *increases* with confidence,
opposite to the theorem. This is why H1 (the high-confidence region) cannot be dropped. Note that this
example violates M2, so it shows only that M1 + M3 are insufficient.

**D.4 Counterexample 2: H2 is essential.** Let `p_1 = θ`, `p_2 = θ²`, and `p_i = 0` for `i ≥ 3`. Then
M1, M2 (`θ² ≤ θ`), M3 and H1 (for `θ ∈ [1/2, 2/3)`) all hold, but
`Δ_1 = (1−θ)θ²` and `dΔ_1/dθ = θ(2−3θ) > 0` for `θ < 2/3`. The conclusion therefore fails **even
when every assumption except H2 is satisfied**: H2 is not a technical add-on but a necessary condition.
It is also the condition that the adversarial corpus of Section 6.9 violates.

**D.5 The general case (k ≥ 2).** We state the natural extension as a conjecture: if for every j the
ratio `ρ_j := p_{j+1}/p_j` is non-increasing in `p_1` and `p_1 ≥ 1/2`, then `Δ_k` is non-increasing in
γ for all k. Section 6.18 provides numerical support (the marginal gain falls 0.093 → 0.067 → 0.013 →
0.013 across γ quartiles), but we do not claim a proof; a full treatment must control the joint
behaviour of the ratios `ρ_j`, which the two-chunk argument does not.

## References

1. **Lewis, P.; Perez, E.; Piktus, A.; Petroni, F.; Karpukhin, V.; Goyal, N.; Küttler, H.; Lewis, M.; Yih, W.-t.; Rocktäschel, T.; Riedel, S.; Kiela, D.** Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. In *NeurIPS 2020*. arXiv:2005.11401.
2. **Robertson, S.; Zaragoza, H.** The Probabilistic Relevance Framework: BM25 and Beyond. *Foundations and Trends in Information Retrieval* **2009**, 3(4), 333–389.
3. **Karpukhin, V.; Oğuz, B.; Min, S.; Lewis, P.; Wu, L.; Edunov, S.; Chen, D.; Yih, W.-t.** Dense Passage Retrieval for Open-Domain Question Answering. In *EMNLP 2020*. arXiv:2004.04906.
4. **Liu, N. F.; Lin, K.; Hewitt, J.; Paranjape, A.; Bevilacqua, M.; Petroni, F.; Liang, P.** Lost in the Middle: How Language Models Use Long Contexts. *TACL* **2024**, 12, 157–173. arXiv:2307.03172.
5. **Jiang, Z.; Xu, F. F.; Gao, L.; Sun, Z.; Liu, Q.; Dwivedi-Yu, J.; Yang, Y.; Callan, J.; Neubig, G.** Active Retrieval Augmented Generation (FLARE). In *EMNLP 2023*. arXiv:2305.06983.
6. **Asai, A.; Wu, Z.; Wang, Y.; Sil, A.; Hajishirzi, H.** Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. In *ICLR 2024*. arXiv:2310.11511.
7. **Wang, Y.; Li, P.; Sun, M.; Liu, Y.** Self-Knowledge Guided Retrieval Augmentation for Large Language Models (SKR). In *Findings of EMNLP 2023*. arXiv:2310.05002.
8. **Jeong, S.; Baek, J.; Cho, S.; Hwang, S. J.; Park, J. C.** Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity. In *NAACL 2024*, pp. 7036–7056. arXiv:2403.14403.
9. **Press, O.; Zhang, M.; Min, S.; Schmidt, L.; Smith, N. A.; Lewis, M.** Measuring and Narrowing the Compositionality Gap in Language Models (Self-Ask). In *Findings of EMNLP 2023*. arXiv:2210.03350.
10. **Trivedi, H.; Balasubramanian, N.; Khot, T.; Sabharwal, A.** Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions (IRCoT). In *ACL 2023*. arXiv:2212.10509.
11. **Yan, S.-Q.; Gu, J.-C.; Zhu, Y.; Ling, Z.-H.** Corrective Retrieval Augmented Generation (CRAG). arXiv:2401.15884, 2024.
12. **Wu, M.; Yang, H.; Ben-Porat, O.; Ziser, Y.** When Knowledge Is Not Free: Cost-Aware Evidence Selection in Retrieval-Augmented Generation. arXiv:2606.02245, 2026.
13. **Jiang, H.; Wu, Q.; Lin, C.-Y.; Yang, Y.; Qiu, L.** LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models. In *EMNLP 2023*. arXiv:2310.05736.
14. **Jiang, H.; Wu, Q.; Luo, X.; Li, D.; Lin, C.-Y.; Yang, Y.; Qiu, L.** LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression. In *ACL 2024*. arXiv:2310.06839.
15. **Xu, F.; Shi, W.; Choi, E.** RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation. In *ICLR 2024*. arXiv:2310.04408.
16. **Nogueira, R.; Jiang, Z.; Pradeep, R.; Lin, J.** Document Ranking with a Pretrained Sequence-to-Sequence Model. In *Findings of EMNLP 2020*. arXiv:2003.06713.
17. **Sun, W.; Yan, L.; Ma, X.; Wang, S.; Ren, P.; Chen, Z.; Yin, D.; Ren, Z.** Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents (RankGPT). In *EMNLP 2023*. arXiv:2304.09542.
18. **Gao, L.; Ma, X.; Lin, J.; Callan, J.** Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE). In *ACL 2023*. arXiv:2212.10496.
19. **Ma, X.; Gong, Y.; He, P.; Zhao, H.; Duan, N.** Query Rewriting for Retrieval-Augmented Large Language Models. In *EMNLP 2023*. arXiv:2305.14283.
20. **Carbonell, J.; Goldstein, J.** The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries. In *SIGIR 1998*, pp. 335–336.
21. **Lin, H.; Bilmes, J.** A Class of Submodular Functions for Document Summarization. In *ACL-HLT 2011*, pp. 510–520. Available: https://aclanthology.org/P11-1052/
22. **Nemhauser, G. L.; Wolsey, L. A.; Fisher, M. L.** An Analysis of Approximations for Maximizing Submodular Set Functions—I. *Mathematical Programming* **1978**, 14(1), 265–294.
23. **Khuller, S.; Moss, A.; Naor, J.** The Budgeted Maximum Coverage Problem. *Information Processing Letters* **1999**, 70(1), 39–45.
24. **Wald, A.** *Sequential Analysis*; Wiley: New York, 1947.
25. **Chen, L.; Zaharia, M.; Zou, J.** FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance. arXiv:2305.05176, 2023.

## Declarations

**Data Availability Statement.** All code, evaluation sets and experiment scripts are available at
https://github.com/mylgtab/budget-rag (MIT license, v1.1.0). Small snapshots of the LongBench subsets
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
