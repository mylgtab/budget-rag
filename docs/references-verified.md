# 参考文献核验记录

> 核验日期：2026-10-23
> 方法：arXiv 编号请求 `arxiv.org/abs/<id>`（HTTP 200 且标题可取）、期刊论文走 Crossref、
> ACL 系列走 ACL Anthology。可复跑：`python scripts/verify_refs.py`

## 结论

**25 条全部可查证，无编造条目。**

| # | 类型 | 标识 | 核验结果 |
|---|---|---|---|
| 1 | Lewis et al. 2020 RAG | arXiv:2005.11401 | ✅ 标题一致 |
| 2 | Robertson & Zaragoza 2009 BM25 | Crossref | ✅ |
| 3 | Karpukhin et al. 2020 DPR | arXiv:2004.04906 | ✅ |
| 4 | Liu et al. 2024 Lost in the Middle | arXiv:2307.03172 | ✅ |
| 5 | Jiang Z. et al. 2023 FLARE | arXiv:2305.06983 | ✅ |
| 6 | Asai et al. 2024 Self-RAG | arXiv:2310.11511 | ✅ |
| 7 | Wang et al. 2023 SKR | arXiv:2310.05002 | ✅ |
| 8 | Jeong et al. 2024 Adaptive-RAG | arXiv:2403.14403 | ✅ |
| 9 | Press et al. 2023 Self-Ask | arXiv:2210.03350 | ✅ |
| 10 | Trivedi et al. 2023 IRCoT | arXiv:2212.10509 | ✅ |
| 11 | Yan et al. 2024 CRAG | arXiv:2401.15884 | ✅ |
| 12 | Wu et al. 2026 Cost-Aware RAG | arXiv:2606.02245 | ✅（2026 新论文，首次请求超时，重试 200） |
| 13 | Jiang H. et al. 2023 LLMLingua | arXiv:2310.05736 | ✅ |
| 14 | Jiang H. et al. 2024 LongLLMLingua | arXiv:2310.06839 | ✅ |
| 15 | Xu et al. 2024 RECOMP | arXiv:2310.04408 | ✅ |
| 16 | Nogueira et al. 2020 monoT5 | arXiv:2003.06713 | ✅ |
| 17 | Sun et al. 2023 RankGPT | arXiv:2304.09542 | ✅ |
| 18 | Gao et al. 2023 HyDE | arXiv:2212.10496 | ✅ |
| 19 | Ma et al. 2023 Rewrite-Retrieve-Read | arXiv:2305.14283 | ✅ |
| 20 | Carbonell & Goldstein 1998 MMR | Crossref | ✅（Crossref 命中 2017 重印版，原版为 SIGIR 1998） |
| 21 | Lin & Bilmes 2011 子模摘要 | ACL Anthology P11-1052 | ✅（Crossref 未收录 ACL 论文，故走 Anthology） |
| 22 | Nemhauser et al. 1978 子模近似 | Crossref | ✅ |
| 23 | Khuller et al. 1999 预算最大覆盖 | Crossref | ✅ |
| 24 | Wald 1947 Sequential Analysis | Crossref | ✅ |
| 25 | Chen et al. 2023 FrugalGPT | arXiv:2305.05176 | ✅ |

## 仍需人工核对的两层

1. **条目存在 ≠ 引用内容对得上**。例如第 12 条用于支撑「成本感知检索里静态选择器很脆弱」，
   投稿前应读其摘要确认该论断确实来自该文。
2. **细节**：页码、卷期、会议地点这类，Crossref/Anthology 页面上都能查，交稿前逐条对一遍。

## 复跑方式

```bash
python scripts/verify_refs.py
```

输出 25 行 ✅/❌。任何一条 ❌ 都说明编号或标题对不上，需要改。
