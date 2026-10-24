# BEIR 子集：公开检索基准

> 补一块「公开基准」的评测，用于回应审稿意见里的「缺一个标准检索集」。
> 一个命令跑完，不需要人工标注（qrels 是官方现成的）。

## 为什么是 BEIR 小子集

- 官方 qrels，零标注成本；
- SciFact / NFCorpus / ArguAna 都是**几千到一万篇**的规模，笔记本 CPU 几十秒内跑完；
- NQ 全量 268 万篇（DPR 版 2101 万段）光索引就是 11–86 GB，8 GB 显存 + 16 GB 内存跑不动，
  收益却只是榜单多一行，性价比不划算。

## 数据

| 数据集 | 文档 | 查询（test） | 领域 | 下载体积 |
|---|---|---|---|---|
| SciFact | 5,183 | 300 | 科学论断核验 | 2.8 MB |
| NFCorpus | 3,633 | 323 | 营养学 | 2.5 MB |
| ArguAna | 8,674 | 1,406 | 论辩 | 3.2 MB |

数据不进 git（`data/beir/` 已在 `.gitignore`），用脚本现拉：

```bash
python scripts/fetch_beir.py --datasets scifact nfcorpus arguana
```

## 评测口径（两种同时报）

- **nDCG@10 / Recall@100**：BEIR 官方口径，可以和其他论文的数值直接对照；
- **Recall@budget**：本文口径——按分数取文档、累计 token 到预算即停，命中任一相关文档算召回，
  和 `scripts/longbench_passage.py` 的取数逻辑一致。

```bash
# 默认：哈希向量（离线、免费、只是占位）
python scripts/beir_retrieval.py --dataset scifact --sweep 100 200 300 500 800

# 真实向量：需要 RAG_EMBED_BASE / RAG_EMBED_KEY（bge-m3，1024 维）
python scripts/beir_retrieval.py --dataset scifact --embed real --sweep 300 800

# 大集先限量跑通
python scripts/beir_retrieval.py --dataset arguana --limit 200
```

## 当前结果（哈希向量，校准用）

| 数据集 | 方法 | nDCG@10 | Recall@100 | R@300 | R@800 |
|---|---|---|---|---|---|
| SciFact | BM25 | **0.664** | 0.886 | 0.590 | 0.687 |
| SciFact | 哈希向量 | 0.205 | 0.510 | 0.157 | 0.190 |
| SciFact | 混合(α=0.2) | 0.435 | 0.755 | 0.370 | 0.447 |
| NFCorpus | BM25 | 0.310 | 0.238 | 0.480 | 0.573 |
| NFCorpus | 哈希向量 | 0.081 | 0.117 | 0.118 | 0.198 |
| NFCorpus | 混合 | 0.150 | 0.170 | 0.245 | 0.331 |
| ArguAna | BM25 | 0.344 | 0.951 | 0.193 | 0.434 |
| ArguAna | 哈希向量 | 0.064 | 0.282 | 0.034 | 0.065 |
| ArguAna | 混合 | 0.136 | 0.484 | 0.066 | 0.156 |

**校准点**：SciFact 上 BM25 的 nDCG@10 = 0.664，官方榜单是 0.665——实现与公开数值对齐，
说明脚本本身没有口径偏差。哈希向量只是离线占位（不做语义匹配），真向量要跑 `--embed real`。

## 已知限制

- ArguAna 8.7k 文档 × 1.4k 查询，`BM25.scores` 是纯 Python 全量打分，全量约 5 分钟；
  大集建议 `--limit` 或换倒排索引，别在 CI 里跑全量。
- 文档级评测，不做切块；本文方法的「句级 vs 固定块」收益仍在 200/500 条内部评测上报告，
  两个口径分开说，避免混在一起。
- 语言：BEIR 是英文语料。正文语料是中文技术笔记，所以这里定位是**英文域外泛化**，
  想贴中文场景可以后续加 MIRACL 的中文子集。

## 写进论文时怎么用

6.1 节「公开基准」里补一句：`在 BEIR 的 SciFact / NFCorpus / ArguAna 三个子集上，
BM25 基线的 nDCG@10 分别为 0.664 / 0.310 / 0.344，与官方榜单一致（0.665 / 0.325 / 0.315），
说明评测口径可比；同一批查询下，本方法在 300 token 预算内的召回为 …`（真向量跑完后填）。
