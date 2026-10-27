# Reproducing the tables and figures

Every number in the paper is produced by a script in `scripts/` and stored in `results/*.json`.
`python scripts/audit_numbers.py` cross-checks the manuscript against those files and exits non-zero
if any number drifts.

Version: **v1.1.0** (tag on the public repository).

## Quick start

```bash
pip install -e .            # CPU-only dependencies
make check                  # unit tests
python scripts/audit_numbers.py
```

Embeddings are served by an OpenAI-compatible endpoint; set:

```bash
export RAG_EMBED_BASE=https://api.siliconflow.cn/v1
export RAG_EMBED_MODEL=BAAI/bge-m3
export RAG_EMBED_KEY=<your key>
```

## Table → script → output

| Table | Script | Output |
|---|---|---|
| 1 (comparison of lines) | — | conceptual, no experiment |
| 2 (controlled synthetic results) | `scripts/baselines.py` | `results/baselines.json` |
| 3 (seed stability) | `scripts/seed_stability.py` | `results/` (reads `baselines.json`) |
| 4 (ablation) | `scripts/sweep.py`, `scripts/tune_alpha.py`, `scripts/rewrite_gate.py`, `scripts/llm_rewrite_test.py` | `results/` component sweeps |
| 5 (model-agnostic benefit) | `scripts/multihop.py` | `results/multihop.json` |
| 6 (efficiency) | `scripts/latency_bench.py` | `results/latency.json` |
| 7 (internal benchmark, 301 questions) | `scripts/eval_real.py --budget 300 --index index_real.json` | `results/eval_real_b300.json` |
| 8 (BEIR, four subsets) | `scripts/fetch_beir.py` then `scripts/beir_adaptive.py --dataset <name> --embed real --limit 0` | `results/beir_adaptive_<name>.json` |
| 9 (conformal coverage) | `scripts/conformal_sweep.py --method hybrid\|dense\|bm25` | `results/conformal_sweep_<method>.json` |
| 10 (operating points) | `scripts/pareto_multibudget.py`, `scripts/official_route_eval.py` | `results/pareto_multibudget.json`, `results/official_route_eval.json` |
| 11 (official classifier) | `scripts/train_complexity_classifier.py` then `scripts/official_route_eval.py` | `results/official_classifier.json`, `results/official_route_eval.json` |
| 12 (per-query thresholds) | `scripts/perquery_tau.py`; BEIR part: `scripts/beir_adaptive.py --dataset scifact` | `results/perquery_tau.json`, `results/beir_adaptive_scifact.json` |
| 13 (margin quartiles) | `scripts/margin_sufficiency.py` | `results/margin_sufficiency.json` |

## Figure → script

| Figure | Script |
|---|---|
| 1 (pipeline) | `scripts/make_paper_figures.py` |
| 2 (budget–recall) | `scripts/make_paper_figures.py` |
| 3 (ablation) | `scripts/make_paper_figures.py` |
| 4 (calibration curves) | `scripts/fig4_data.py` then `scripts/fig4_calibration.py` |
| 5 (conformal coverage diagnostic) | `scripts/conformal_sweep.py --method hybrid` then `scripts/fig5_conformal.py` |

## Other numbers cited in the text

| Claim | Script | Output |
|---|---|---|
| Bootstrap CI for the adaptive saving (15.5%, CI [11.2, 19.8]) | `scripts/bootstrap_saving.py` | `results/bootstrap_saving.json` |
| McNemar + Holm correction | `scripts/significance_holm.py --budget 300` | `results/significance_holm.json` |
| Question–source overlap (median 0.000) | `scripts/overlap_analysis.py` | `results/overlap_analysis.json` |
| Order-dependent costs (§6.15) | `scripts/order_dependent_cost.py` | `results/order_dependent_cost.json` |
| Tokens-per-ms exchange rate (§6.12) | `scripts/exchange_rate.py` | `results/exchange_rate.json` |
| Sentence vs fixed indexing (§6.9) | `scripts/sentence_index_eval.py` | `results/sentence_index_eval.json` |
| Official classifier validation accuracy (43.3%) | `scripts/train_complexity_classifier.py` (needs transformers 4.x) | `results/official_classifier.json` |

## Notes

- The 301-question benchmark is `data/eval_real.jsonl`; the 312-document corpus is `data/real_docs/`.
- BEIR data is fetched by `scripts/fetch_beir.py`; embeddings are cached next to each dataset.
- The complexity classifier is trained in a separate environment: `transformers 4.x` is required
  (the T5 tokenizer in 5.x does not accept `spiece.model`).
- `scripts/github_proxy.py` is a local workaround for restricted networks and is not part of any result.
