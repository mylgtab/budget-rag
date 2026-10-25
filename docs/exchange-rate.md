# 延迟与 token 的交换率（本地实测）

> 问题：多花检索时间，能不能省下上下文 token？比值多少？怎么测？
> 脚本：`python scripts/exchange_rate.py --targets 0.80 0.90 --measure-prefill`

## 一、怎么定义「交换率」

不同检索器在**同等召回**下需要的上下文长度不同：

```
BM25    T=0.80 → 325 token，检索 17 ms
Hybrid  T=0.80 →  87 token，检索 77 ms
```

从 BM25 换到 Hybrid：**多花 60 ms，少取 238 token**。

```
交换率 = 省下的 token / 多花的毫秒 = 4.0 token/ms
```

## 二、检索侧交换率（143 题，312 篇文档）

| 目标召回 | 换哪个 | 多花 ms | 省下 token | 交换率 |
|---|---|---|---|---|
| 0.80 | BM25 → Hybrid | 60 | 238 | **4.0 tok/ms** |
| 0.80 | Dense-large → Hybrid | 33 | 61 | 1.8 tok/ms |
| 0.90 | BM25 → Hybrid | 60 | 810 | **13.4 tok/ms** |
| 0.90 | Dense-large → Hybrid | 32 | 204 | 6.3 tok/ms |

**目标越严，swap 越划算**：要 0.90 时必须堆 token，而换更好的检索器能省得多。

## 三、生成侧：每 token 多少钱（本地 Ollama 实测）

用 Ollama 的 `prompt_eval_duration` 精确测 prefill（随机 prompt，避免前缀缓存）：

| 上下文 token | prefill 耗时 |
|---|---|
| 100 | 195 ms |
| 300 | 570 ms |
| 600 | 1194 ms |
| 1000 | 2125 ms |

**斜率 ≈ 2.15 ms/token**（本机 Qwen3-4B，CPU 推理）。

## 四、净收益计算

| 目标 | 换法 | 省下 prefill | 多花检索 | **净收益** |
|---|---|---|---|---|
| 0.80 | BM25 → Hybrid | 512 ms | 57 ms | **+455 ms** |
| 0.90 | BM25 → Hybrid | 1743 ms | 57 ms | **+1686 ms** |
| 0.90 | Dense-large → Hybrid | 439 ms | 29 ms | **+410 ms** |

**结论：花几毫秒到几十毫秒的检索时间，换掉几百到上千 token 的 prefill，净赚 4–17 倍。**

## 五、盈亏平衡点

设 prefill 单价为 p ms/token，交换率为 r tok/ms：

- 划算条件：`r × p > 1`
- 本机实测：`4.0 × 2.15 = 8.6 ≫ 1` → 稳赚
- 即使换成 GPU（p ≈ 0.1 ms/token）：`4.0 × 0.1 = 0.4 < 1` → 在 T=0.80 时**不划算**
- 但 T=0.90 时 `13.4 × 0.1 = 1.34 > 1` → 仍然划算

**所以「什么时候该换」取决于目标召回与硬件**，不是一个固定答案。

## 六、为什么这条重要

它把「延迟 vs token」从定性讨论变成可计算：

- 本地 4B 模型：几乎所有情况都该用更好的检索器
- 云端大模型（prefill 极快）：只在严格目标下才值得
- 这解释了 6.11 的结论为什么成立：**检索延迟太便宜，永远值得花**，真正贵的维度是上下文

## 七、复现

```bash
# 只测检索侧（几秒）
python scripts/exchange_rate.py --targets 0.80 0.90

# 加上本地 prefill 实测（需要 Ollama 已启动）
python scripts/exchange_rate.py --targets 0.80 0.90 --measure-prefill
```
