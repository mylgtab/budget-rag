## 亮点

- **真实 embedding**：`BAAI/bge-m3` 纯向量 Recall 0.938，比哈希占位高 5.4pt
- **调参纠正**：旧的 `alpha=0.5` 是在全量测试集上扫出来的；改成 dev/test 分离后，
  `alpha=0.2` 在**同预算**下 +1.7pt（0.9257 → 0.9429）
- **LLM 重排对照**：预算截断时 +5.5pt，预算充足时无效（集合没变，只换了顺序）
- 版本号从 0.1.0 修正为 0.5.0，并补上 CHANGELOG

## 复现

```bash
make test                        # 27 个测试
python scripts/tune_params.py    # dev/test 网格调参
python scripts/embed_compare.py  # 哈希 vs 真向量
python scripts/llm_rerank.py     # LLM 重排对照
```
