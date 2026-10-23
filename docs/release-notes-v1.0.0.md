# v1.0.0

**含义：一个陌生人能在 30 分钟内复现主结果，且接口从此稳定。**

## 验收（可重复）

| 检查 | 结果 |
|---|---|
| 从零克隆 | 4.7 MB / 124 文件 |
| `pip install -e .` | 通过 |
| 单元测试 | 65 个全绿 |
| 覆盖率 | **90%**（CI 门槛 80%） |
| CI 矩阵 | ubuntu/windows × 3.10/3.12 |
| Docker | 构建 → 起容器 → 健康检查 → 真实 `/query` 通过 |
| 数据快照 | 6 个 LongBench 子集 × 15 条入库，不依赖外部镜像 |

## 接口稳定性承诺

- `GET /v1/health`、`POST /v1/query` 字段与语义不做破坏性变更
- `trace` 只增字段
- 评测 JSONL 字段保持兼容

## 科学结果

- 200 条主表：**0.960 @ 126 token** vs CRAG 近似 0.925 @ 179、纯向量 0.910 @ 115
- 配对 bootstrap + McNemar 全显著；5 次子采样区间与 CRAG 不重叠
- 三个多跳基准验证检索必要性；200 条双人标注 + 忠实度 94%
- 形式化（子模最大化 + 三命题）与 P1–P3 实验验证

## 快速开始

```bash
git clone https://github.com/mylgtab/budget-rag.git && cd budget-rag
python -m pip install -e ".[dev]"
make check
```

详见 [docs/quickstart.md](docs/quickstart.md)。

## 已知边界

暴力向量检索、基线为行为近似、合成语料为主、成本按公开单价换算。