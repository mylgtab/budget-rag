## 亮点

- **多跳检索**：先检索一轮 → 让模型说「还缺什么」→ 再检索一轮 → 合并作答
- **HotpotQA 50 条**：contain **0.540 → 0.620**，EM **0.400 → 0.500**，命中率 **0.640 → 0.720**
- 代价：平均 token 658 → 1315（约 2 倍）
- 保留问题：仍有 28% 的题两跳都没命中

## 用法

```bash
python scripts/multihop.py --file data/longbench/hotpotqa.jsonl --limit 50
```