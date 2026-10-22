## 亮点

- **完整链路**：`scripts/longbench_qa.py` 支持 `rag` / `none` 两种模式对照
- **HotpotQA 50 条**：RAG contain 0.540 vs 不检索 0.200（2.7 倍），EM 0.400 vs 0.140
- **失败模式写清楚**：漏检 36%、找到但没答对约 10% —— 下一步该做多跳检索
- 修复长文档建索引超时：embedding 每批 32 条

## 说明

HotpotQA 上绝对值远低于合成集（0.92），这是正常的：
真实多跳题需要同时定位两处事实，800 token 只覆盖 13k 上下文的 6%。

```bash
python scripts/fetch_longbench.py --subsets hotpotqa
python scripts/longbench_qa.py --file data/longbench/hotpotqa.jsonl --limit 50
```