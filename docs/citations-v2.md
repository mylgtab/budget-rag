# 参考文献（核实版 v2）

> 核实来源：Crossref（DOI/页码）、ACL Anthology（会议与页码）、软件学报官网（元数据）。
> 每条末尾标 ✅ 已核 / ⚠️ 待核。本机无 CNKI 账号，中文期刊只收已由官网核实的条目。
> 正文现在用「作者-年」占位，投稿时按 GB/T 7714-2015 顺序编码制统一转换。
> 本文件取代 `docs/citations.md` 的条目格式（原清单保留作对照）。

## A 检索增强与上下文

1. LEWIS P, PEREZ E, PIKTUS A, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks[C]//NeurIPS 2020. arXiv:2005.11401. ⚠️ NeurIPS 无 DOI
2. ROBERTSON S, ZARAGOZA H. The probabilistic relevance framework: BM25 and beyond[J]. Foundations and Trends in Information Retrieval, 2009. DOI:10.1561/1500000019 ✅（卷期页码以出版页为准）
3. KARPUKHIN V, OĞUZ B, MIN S, et al. Dense passage retrieval for open-domain question answering[C]//EMNLP 2020: 6769-6781. DOI:10.18653/v1/2020.emnlp-main.550 ✅
4. LIU N F, LIN K, HEWITT J, et al. Lost in the middle: how language models use long contexts[J]. Transactions of the ACL, 2024, 12: 157-173. DOI:10.1162/tacl_a_00638 ✅
5. 张犬俊, 谢杨, 房春荣, 等. 检索增强生成在软件工程中的应用综述[J]. 软件学报, 2026, 37(3): 1316-1339. DOI:10.13328/j.cnki.jos.007567 ✅（知网可查）
6. FENG Z, ZHU K, MA W, et al. 浅谈大模型时代下的检索增强: 发展趋势、挑战与展望[C]//CCL 2024: 151-168. ✅
7. PANG L, DENG J, GU J, et al. 大语言模型时代的信息检索综述[C]//CCL 2024: 98-119. ✅

## B 自适应检索

8. JIANG Z, XU F F, GAO L, et al. Active retrieval augmented generation[C]//EMNLP 2023. arXiv:2305.06983. ⚠️ DOI 待补
9. ASAI A, WU Z, WANG Y, et al. Self-RAG: learning to retrieve, generate, and critique through self-reflection[C]//ICLR 2024. arXiv:2310.11511. ⚠️ ICLR 无 DOI
10. JEONG S, BAEK J, CHO S, et al. Adaptive-RAG: learning to adapt retrieval-augmented large language models through question complexity[C]//NAACL 2024: 7036-7050. DOI:10.18653/v1/2024.naacl-long.389 ✅
11. WANG Y, LI P, SUN M, et al. Self-knowledge guided retrieval augmentation for large language models[C]//Findings of EMNLP 2023: 10303-10315. DOI:10.18653/v1/2023.findings-emnlp.691 ✅
12. PRESS O, ZHANG M, MIN S, et al. Measuring and narrowing the compositionality gap in language models[C]//Findings of EMNLP 2023: 5687-5711. DOI:10.18653/v1/2023.findings-emnlp.378 ✅
13. TRIVEDI H, BALASUBRAMANIAN N, KHOT T, et al. Interleaving retrieval with chain-of-thought reasoning for knowledge-intensive multi-step questions[C]//ACL 2023: 10014-10037. DOI:10.18653/v1/2023.acl-long.557 ✅

## C 纠正式检索

14. YAN S Q, GU J C, ZHU Y, et al. Corrective retrieval augmented generation[J/OL]. arXiv:2401.15884, 2024. ⚠️ 会议版待核（SSRN 版 DOI:10.2139/ssrn.5267341）

## D 成本、压缩与重排

15. JIANG H, WU Q, LIN C Y, et al. LLMLingua: compressing prompts for accelerated inference of large language models[C]//EMNLP 2023: 13358-13376. DOI:10.18653/v1/2023.emnlp-main.825 ✅
16. JIANG H, WU Q, LUO X, et al. LongLLMLingua: accelerating and enhancing LLMs in long context scenarios via prompt compression[C]//ACL 2024: 1658-1677. DOI:10.18653/v1/2024.acl-long.91 ✅
17. XU F, SHI W, CHOI E. RECOMP: improving retrieval-augmented LMs with compression and selective augmentation[C]//ICLR 2024. arXiv:2310.04408. ⚠️ ICLR 无 DOI
18. CHEN L, ZAHARIA M, ZOU J. FrugalGPT: how to use large language models while reducing cost and improving performance[J/OL]. arXiv:2305.05176, 2023. ⚠️ TMLR 收录信息待核
19. GAO L, MA X, LIN J, et al. Precise zero-shot dense retrieval without relevance labels[C]//ACL 2023: 1762-1777. DOI:10.18653/v1/2023.acl-long.99 ✅
20. MA X, GONG Y, HE P, et al. Query rewriting in retrieval-augmented large language models[C]//EMNLP 2023. DOI:10.18653/v1/2023.emnlp-main.322 ✅（Rewrite-Retrieve-Read 路线的完整版；ACL 2023 短文版 DOI 待核）
21. NOGUEIRA R, JIANG Z, PRADEEP R, et al. Document ranking with a pretrained sequence-to-sequence model[C]//Findings of EMNLP 2020: 708-718. DOI:10.18653/v1/2020.findings-emnlp.63 ✅
22. SUN W, YAN L, MA X, et al. Is ChatGPT good at search? Investigating large language models as re-ranking agents[C]//EMNLP 2023: 14918-14937. DOI:10.18653/v1/2023.emnlp-main.923 ✅

## E 子模、阈值与成本感知

23. NEMHAUSER G L, WOLSEY L A, FISHER M L. An analysis of approximations for maximizing submodular set functions—I[J]. Mathematical Programming, 1978, 14(1): 265-294. DOI:10.1007/BF01588971 ✅
24. KHULLER S, MOSS A, NAOR J. The budgeted maximum coverage problem[J]. Information Processing Letters, 1999, 70(1): 39-45. DOI:10.1016/S0020-0190(99)00031-9 ✅
25. CARBONELL J, GOLDSTEIN J. The use of MMR, diversity-based reranking for reordering documents and producing summaries[C]//SIGIR 1998: 335-336. ⚠️ 原版 DOI 待核（重印版 DOI:10.1145/3130348.3130369 ✅）
26. LIN H, BILMES J. A class of submodular functions for document summarization[C]//ACL-HLT 2011: 510-520. ACL Anthology: P11-1055. ⚠️ 无 DOI
27. WALD A. Sequential analysis[M]. New York: Wiley, 1947. ⚠️ 无 DOI
28. Cost-aware RAG[J/OL]. arXiv:2606.02245, 2026. ⚠️ 作者与标题待从原文补（本条来源为 `docs/references.md`）

## 知网补录（本机无账号，需登录后导出）

知网「高级检索」可直接粘贴的检索式：

1. `SU=('检索增强生成'+'RAG') AND SU=('大语言模型'+'LLM') AND LY=软件学报`
2. `SU=('检索增强') AND SU=('上下文'+'成本'+'预算') AND LY=计算机学报`
3. `SU=('检索增强生成') AND SU=('综述'+'进展') AND LY=计算机研究与发展`
4. `SU=('自适应检索'+'多跳问答') AND SU=('查询改写'+'重排')`

导出时选「参考文献格式 → GB/T 7714-2015」，勾选「包含 DOI 与 URL」。

## 中科院分区与来源核验

- 分区查「中科院文献情报中心期刊分区表」官方小程序，或机构订阅的分区数据库；会议论文不入分区，按 CCF 等级核验。
- 现有清单的 CCF 等级：ACL / EMNLP / NAACL / Findings 为 B 类，ICLR 与 TACL 为 A 类，TACL 为 A 类期刊；《软件学报》为 CCF-A 中文期刊。
- 结论：英文引文以 CCF-B 及以上为主，中文补到 3–5 篇即可满足 Q2 期刊的引文结构。

## 待核清单（投稿前逐条消掉）

- [ ] 8 FLARE 的 EMNLP 2023 页码与 DOI（ACL Anthology 检索「Active Retrieval Augmented Generation」）
- [ ] 9、17 ICLR 2024 条目改为会议版格式（无 DOI，写 OpenReview 链接）
- [ ] 14 CRAG 是否已有正式发表版本；若无，保留 arXiv 并注明
- [ ] 18 FrugalGPT 的 TMLR 卷期
- [ ] 20 Rewrite-Retrieve-Read 的 ACL 2023 原版 DOI，或改用 EMNLP 版并改正文措辞
- [ ] 25 MMR 1998 原版 DOI
- [ ] 28 Cost-Aware RAG 的作者、标题、出处
- [ ] 中文文献补到 3–5 篇（用上面的知网检索式）
