# 出题指南（写完 150 题就能重跑主表）

## 为什么要你自己写

审稿风险里最硬的一条是「合成问题有同源偏差」——问题由模型从原文生成，措辞和原文高度重合，
检索靠词面就能命中，分数虚高。

**你用自己的话问**，问题里不带原文的专有短语，这个偏差就没了。这是这篇论文能不能过审的关键一步。

## 五条规则

### 1. 用你自己的话问，别抄原文词序

原文：`The Prometheus server runs in a Docker container and is accessible on port 9090.`

| | 写法 |
|---|---|
| ✅ 好 | `Which port does the metrics service listen on?` |
| ❌ 差 | `Which port is the Prometheus server accessible on?`（照抄原文短语） |

### 2. 答案必须是原文里**逐字出现**的片段，不超过 8 个词（英文）/ 12 个字（中文）

程序用字符串匹配判定对错，所以答案要能在文档里原样搜到。

| | 写法 |
|---|---|
| ✅ 好 | `9090`、`DaemonSet`、`OnFailure`、`60-minute` |
| ❌ 差 | `the port 9090, which is exposed by the Docker daemon server`（太长，且不是原句片段） |

### 3. 一个问题只问一个事实

拆开问，别做「是什么、怎么配、为什么」三合一。

### 4. 问题要能独立看懂

不要用「它」「这段」「上面的字段」。假设读者没看过原文。

### 5. 尽量别出是非题

`Does X support Y?` 这种猜中概率 50%，区分度低。
优先用：**What / Which / How many / How long / Why / What happens if**。

## 好例子（原文 → 问题 → 答案）

| 原文 | 问题 | 答案 |
|---|---|---|
| `A DaemonSet ensures that all (or some) Nodes run a copy of a Pod.` | `Which Kubernetes object keeps one Pod copy on every node?` | `DaemonSet` |
| `The metrics endpoint has a 60-minute cache by default.` | `How long is the metrics endpoint cache by default?` | `60-minute` |
| `If the Pod restartPolicy is set to Always, the init containers use restartPolicy OnFailure.` | `If a Pod restarts always, which restart policy do init containers inherit?` | `OnFailure` |
| `Multi-stage builds are recommended for all types of applications.` | `For which kinds of applications are multi-stage builds recommended?` | `all types of applications` |
| `The name of a DaemonSet object must be a valid DNS subdomain name.` | `What naming rule applies to DaemonSet object names?` | `valid DNS subdomain name` |

## 操作流程

1. 打开 `docs/question-sheet.csv`（Excel / WPS 都行）
2. 每行一篇文档，左边给你 3 条候选事实句
3. 每行填 **3–4 组**「问题 + 答案」
4. 存回同一个文件（保持 CSV、UTF-8）
5. 转换 + 校验：

```bash
python scripts/sheet_to_eval.py            # CSV → data/eval_real.jsonl
python scripts/check_eval_set.py           # 查答案是否逐字存在、有无重复
```

6. 出问题就改表格，再跑一遍，直到全绿

## 工作量

| 项 | 数量 |
|---|---|
| 文档 | 45 篇 |
| 每篇 | 3–4 题 |
| 合计 | **150 题左右** |
| 每天 | 10 篇（约 40 题，1 小时） |
| 周期 | **4–5 天** |

## 常见错误

| 错误 | 后果 |
|---|---|
| 答案写成解释句 | 校验报「答案不在文档里」 |
| 两个问题问同一句 | 校验报重复 |
| 只在 10 篇文档里出题 | 覆盖度不足，检索面太窄 |
| 问题里带答案词 | 问题本身泄露答案（如 `What does DaemonSet ensure?`） |

## 完成后

告诉本鲸，本鲸会：
1. 跑校验，把不合规的标出来
2. 在真实语料上重跑主表、消融、外部基准
3. 更新论文数字
4. **然后提醒你去找人润色英文**
