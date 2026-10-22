## 亮点

- **API 可用性**：Bearer 鉴权 + 每 IP 令牌桶限流（429），`/health` 仍开放
- **多 seed 方差**：Recall 0.8580 ± 0.0148；修正了「只打乱顺序」的错误做法
- **token 校准**：tiktoken 对中文高估约 84%，账单一律用 API `usage`
- **跨语料验证**：LongBench passage_retrieval_zh，向量 0.995 vs BM25 0.955
- **第 0 级检索**（借鉴 Ponytail）：不检索 contain 只有 0.11，证明检索净收益 +80pt
- 测试 27 → 42

## 复现

```bash
make test
python scripts/multi_seed.py --seeds 5
python scripts/token_check.py
python scripts/no_retrieval.py --limit 100
```