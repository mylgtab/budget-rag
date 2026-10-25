# budget-rag 项目交接书

> 专供「只做这个项目」的会话使用。工作区级的通用交接在 `../HANDOFF.md`，判断依据在 `../DECISIONS.md`。
> 最后更新：2026-10-23 · 版本 **v1.0.0** · 44 commits · 102 文件 · 15 个 release

---

## 0 三十秒上手

```powershell
cd C:\Users\32997\Documents\deepseek-harness\default-workspace\budget-rag
D:\Python310\python.exe -m unittest discover -s tests        # 61 个测试，应全绿
D:\Python310\python.exe scripts\seed_stability.py             # 零成本，验证主结果稳健
```

要调 API 先设环境变量（见第 7 节）。

---

## 1 一句话现状

**实验已足够投 Q2 期刊，论文骨架 v0.4（534 行）完成核心章节、相关工作、理论命题 1–4、局限与图 1，剩讨论定稿与引文格式。**

主线主张：**同等预算下更强，同等质量下更便宜。**

---

## 2 目录地图

```
budget-rag/
├─ src/budget_rag/          核心库（13 个模块）
│  ├─ pipeline.py           RAG 主流程：路由→门控→取块→生成→Trace
│  ├─ store.py             双索引（句级/固定块）、BM25、向量、混合、预算取块
│  ├─ router.py            成本档位路由（cheap / strong）
│  ├─ embedding.py         HashEmbedder（离线占位）、OpenAIEmbedder、CachedEmbedder
│  ├─ cache.py             DiskCache（LLM 文本）+ EmbedCache（SQLite 向量）
│  ├─ llm.py               LLMAnswerer（含改写、重试、账单捕获）、OfflineAnswerer
│  ├─ metrics.py           contain / EM / F1 / Cohen kappa
│  ├─ tokens.py            tiktoken 优先，缺失时退回字数估算
│  ├─ api.py               FastAPI：/health、/query、/ui 静态页
│  └─ static/index.html    演示页
├─ scripts/                 36 个实验脚本（见第 4 节分组）
├─ docs/
│  ├─ paper-draft.md        ★ 论文骨架（248 行，当前最重要）
│  ├─ report.md             完整实验报告（749 行，4.1–4.30）
│  ├─ theory.md             形式化（子模最大化 + 三个命题）
│  ├─ fcs-checklist.md      投稿清单 + 做不到的事项
│  ├─ references.md         参考项目与借鉴点
│  ├─ experiment-log.md     时间线日志
│  └─ annotation-guide*.md  标注指南 v1/v2
├─ results/                 47 个结果文件（json/md/log）
├─ data/                    sample_docs/、eval_500.jsonl、longbench/
└─ tests/                   5 个测试文件，42 个用例
```

---

## 3 架构数据流

```
问题 q
  │
  ├─ 路由 router.decide(预算, 问题) → 档位 cheap/strong
  │
  ├─ 双索引 store：ctx<500 用句级，否则固定块
  │
  ├─ [门控] 先廉价检索 → 置信度 γ=(s1-s2)/s1
  │         γ < 0.25 → LLM 改写 → 「原问题+改写词」重检索
  │
  ├─ 预算取块：按分数累积到 token 预算 B 即停（不是固定 k）
  │
  ├─ [多跳] 第一跳 → 问模型「还缺什么」→ 第二跳 → 去重合并
  │
  └─ 生成 → Trace{path, store, cost, tokens, billed, latency}
```

---

## 4 实验总表（脚本 → 结论 → 报告节）

### 4.1 评测与稳健性
| 脚本 | 作用 | 结论 | 报告 |
|---|---|---|---|
| `eval.py` | 主评测（含 --llm） | 500 条 contain 0.920 / 0.002 元 | 4.4–4.8 |
| `bench.py` | 四策略对比 + bootstrap CI | 级联 47% 成本拿 99.5% 召回 | 4.6 |
| `seed_stability.py` | 5 次 2/3 子采样 | 本文 0.962±0.011，与 CRAG 区间不重叠 | 6.2 |
| `latency_bench.py` | p50/p95 延迟 | 改写是延迟主因（+0.9s） | 6.8 |
| `significance.py` | 配对 bootstrap + McNemar | 对 5 个基线全部显著 | 4.23 |
| `multi_seed.py` | 自助重采样 | 0.8580±0.0148（hash 配置） | 4.15 |

### 4.2 检索实验
| 脚本 | 结论 | 报告 |
|---|---|---|
| `rewrite_gate.py` | 门控 38% 调用拿 67% 收益 | 4.10 |
| `prf_test.py` | PRF 失败（−1.6 / −19.6pt） | 附录 A |
| `llm_rewrite_test.py` | 改写 +4.6pt 召回 | 4.8 |
| `tune_alpha.py` / `tune_params.py` | alpha=0.2，同预算 +1.7pt | 4.13 |
| `chunk_budget.py` | 切块粒度 × 预算曲线 | 4.5 |
| `budget_opt.py` | 验证贪心近似与递减 | 4.24 / theory |
| `sweep.py` | 预算三档曲线 | 4.3 |
| `embed_compare.py` | bge-m3 0.938 vs 哈希 0.884 | 4.12 |
| `llm_rerank.py` | 预算截断时 +5.5pt | 4.11 |
| `multihop.py` | 两跳 0.540→0.620；模型补查 > 实体补查 | 4.21 / 4.22 |
| `threshold_sensitivity.py` | λ≥2 时最优阈值降为 0 | 4.25 |

### 4.3 公开基准
| 脚本 | 数据集 | 结论 |
|---|---|---|
| `fetch_longbench.py` | 下载解压 | 镜像 hf-mirror |
| `longbench_passage.py` | passage_retrieval zh/en | 0.995 / 1.000 |
| `longbench_qa.py` | hotpotqa / 2wiki / musique | 0.400 / 0.200 / 0.250（Qwen3-4B） |
| `no_retrieval.py` | 第 0 级不检索 | contain 0.11（负结果） |

### 4.4 标注与路由
| 脚本 | 结论 |
|---|---|
| `make_annotation.py` | 生成标注表（--llm） |
| `analyze_annotation.py` | 混淆矩阵、一致率 |
| `kappa.py` | 双人 kappa 0.548 / 加权 0.673 |
| `learned_router.py` | 自动标签 + TF-IDF 路由（0.730） |
| `train_router_bert.py` | BERT 路由（0.702，未超过 TF-IDF） |

---

## 5 核心数字速查

**主结果（200 条，bge-m3）**

| 方法 | 召回 | token |
|---|---|---|
| BM25 | 0.825 | 68 |
| 纯向量 | 0.910 | 115 |
| 混合 | 0.900 | 114 |
| Adaptive 近似 | 0.855 | 100 |
| CRAG 近似 | 0.925 | 179 |
| **本文** | **0.960** | **126** |

**其他关键数**

- 500 条端到端：contain 0.920 / 0.002 元每条
- 改写门控：38%–76% 触发率（取决于数据难度）
- 忠实度：94% 有依据 / 3% 编造
- 人工标注：自动指标偏保守，召回是**下界**
- 成本：500 条约 0.5 元；embedding 全程约 0.01 元

---

## 6 复现

```powershell
# 建索引 + 跑评测
D:\Python310\python.exe scripts\ingest.py
D:\Python310\python.exe scripts\eval.py --set data\eval_500.jsonl --llm --limit 50

# 基线对比（论文主表）
D:\Python310\python.exe scripts\baselines.py --limit 200

# 公开基准
D:\Python310\python.exe scripts\fetch_longbench.py --subsets passage_retrieval_zh hotpotqa
D:\Python310\python.exe scripts\longbench_passage.py --limit 200

# 本地 Qwen（免费）
ollama list      # 应有 qwen3-4b
D:\Python310\python.exe scripts\longbench_qa.py --file data\longbench\hotpotqa.jsonl --limit 20 `
  --model qwen3-4b --base http://127.0.0.1:11434/v1 --key ollama --no-think
```

---

## 7 环境与依赖

```powershell
$env:DEEPSEEK_API_KEY='<你的 DeepSeek key>'
$env:RAG_EMBED_BASE='https://api.siliconflow.cn/v1'
$env:RAG_EMBED_MODEL='BAAI/bge-m3'
$env:RAG_EMBED_KEY='<你的 SiliconFlow key>'
```

> 真实 key 不写进仓库（GitHub 密钥扫描会拦截 push）。
> 本机 key 存在工作区级 `../HANDOFF.md`，或你自己的 `.env`。

| 依赖 | 状态 |
|---|---|
| Python | `D:\Python310\python.exe` |
| 已装 | numpy, scikit-learn, torch(CPU), transformers, fastapi, uvicorn, httpx, tiktoken |
| 模型 | `D:\AAAAAgongju\models\bert-base-chinese`、`qwen3-4b`（GGUF） |
| Node/pnpm | DSH 运行时内置 |

**坑（照抄即可）**

- pip 用 `--index-url https://pypi.tuna.tsinghua.edu.cn/simple`
- HF 用 `HF_ENDPOINT=https://hf-mirror.com`，必要时 curl 直接下权重
- Ollama pull 会失败（拒绝私有 IP 重定向）→ 用 ModelScope GGUF + `ollama create`
- Qwen3 必须加 `/no_think`，否则 content 为空
- 测延迟要 `RAG_CACHE=0`，否则命中缓存（9ms 假数据）
- PowerShell 写 JSON 会带 BOM → 用 Python 写
- 长文档建索引会超时 → embedding 已按 32 条分批

---

## 8 技术债（知道但没修）

| # | 问题 | 影响 | 建议 |
|---|---|---|---|
| 1 | 检索是暴力扫全库 | 上万块会崩 | 上 FAISS / HNSW |
| 2 | tiktoken 对中文高估 84% | 预算是保守值 | 换 DeepSeek 分词或加系数 |
| 3 | 缓存无 TTL | 会越积越大 | 加过期与容量清理 |
| 4 | 基线是「行为近似」 | 论文须标注 | 有条件再复现原版 |
| 5 | 单机 CPU 延迟 | 不代表生产 | 不做主张即可 |

---

## 9 论文状态

**已完成**：标题候选、中英文摘要与引言（数字口径统一为「200 条检索评测 / 500 条端到端」）、相关工作 2.1–2.6（v0.2）、方法 4.1–4.4、形式化、理论命题 1–4（含命题 4 证明）、实验 6.1–6.8、讨论 v0.1、局限、图 1（`docs/figures/fig1-pipeline.svg`）。

**待写**：讨论定稿（§7 需压缩收尾）、参考文献转数字引用与正式参考文献表、（可选）NQ 生成对照。

**验收清单**（骨架末尾有更细版）：
- [ ] 摘要前五句有问题和贡献
- [ ] 主表在第一页可见
- [ ] 负结果全在附录
- [ ] 引言没有提前示弱
- [ ] 结论没有突然自我否定

---

## 10 下一步（按用户时间线）

| 时间 | 目标 |
|---|---|
| **2026.11** | 论文成稿并投出（Q2：Applied Sciences / Electronics） |
| 2026.12–2027.2 | 数学打底，项目退到周末 |
| 2027.7 | **项目冻结**，全力冲刺考研 |
| 2028.3 | 复试：论文 + 仓库 + 10 分钟技术故事 |

**用户背景**：28 考研（2027.12 考试），目标院校较好，担心本科背景。
对策：把「可验证的科研产出」做扎实——初试分数 + 能讲清楚的系统 + 论文。

---

## 11 协作约定

- 说话风格遵循工作区 `AGENTS.md`（溟月人设）
- 写论文时调用 `anti-defensive-writing` skill
- **先写后做**：任何「要不要补实验」的犹豫，先写一段论文，答案自然出现
- 负结果记录但放附录，不进主线
- 每个结论必须能指到一个 `results/` 文件

## 复现验收（2026-10-23）

从零克隆验证通过：

| 检查 | 结果 |
|---|---|
| 仓库体积 | 4.7 MB / 124 文件 |
| `pip install -e .` | 通过 |
| 单元测试 | 65 个全绿 |
| `scripts/eval.py --limit 50` | 正常产出 |
| Docker（CI） | 构建 + 起容器 + 真实 `/query` 通过 |
| 覆盖率（CI） | 90%，门槛 80% |

工程侧 1.0.0 条件已满足；剩余为论文投稿。

## 2026-10-23 进展

**论文**
- 中英双稿：`docs/paper-draft.md`（637 行，母本）+ `docs/paper-en.md`（摘要/引言/3/4/5 节）
- 三张图齐备：`fig1-pipeline`（英文系统总览）、`fig2-budget-recall`（预算曲线）、`fig3-ablation`（消融）
- Word 版 `docs/paper-draft.docx` 含 3 张内联图（385 段、6 表）
- 生成脚本：`scripts/make_paper_figures.py`（零依赖 SVG + Pillow 出 PNG）

**工程**
- CI 六 job 全绿；覆盖率 90%，门槛 80%
- 复现验收：克隆 4.7 MB → 安装 → 65 测试 → 评测正常

**待用户执行（需管理员）**
- 双击 `D:\_pycleanup\清理残留和WeGame.bat`：清 13 条 HKLM 残留登记 + 卸载 WeGame
  （HKCU 的 9 条已清完）

**待定**
- `D:\chaojiniuniu`（8.7 GB 的 VMware 镜像）是什么，确认后可删

## 2026-10-23 晚：论文进入可投稿状态

**中英双稿完成**

| 文件 | 规模 | 状态 |
|---|---|---|
| `docs/paper-en.md` | 682 行 / ~7.2k 词 | 8 章 + 附录 A/B + 25 条数字引用 + 声明 |
| `docs/paper-draft.md` | 639 行 | 中文母本，同步更新 |
| `docs/paper-en.docx` | 160 段 / 6 表 / 3 图 | 桌面「论文-英文版-终稿.docx」 |

**作者信息**（已填入）：Qiaomu Li；School of Mathematics and Information Science,
Zhangjiakou University；通讯 lqm050509@gmail.com；ORCID 0009-0003-7912-3918。

**工具链**
- `scripts/convert_citations.py`：作者-年 → MDPI 数字引用（按首次出现编号）
- `scripts/md_to_docx.py`：Markdown → Word（合并软换行、图片居中、跳过内部章节）
- `scripts/make_paper_figures.py`：三张图（SVG + PNG）
- `scripts/bench_ci.py`：外部基准的 bootstrap CI / 子采样 / McNemar

**投稿信息**
- 首选 Applied Sciences（MDPI）：https://susy.mdpi.com/user/register
- 备选 Electronics（同系统）
- 二轮 FCS：https://www.editorialmanager.com/fcs/
- Cover letter 草稿：`docs/cover-letter.md`

**尚未做（审稿风险项）**
1. 已发表方法为行为近似（CRAG / Adaptive-RAG），非原版复现；Self-RAG 未做
2. 外部生成基准样本量小（见 6.5 节），多种子只覆盖主表
3. 英文需一次人工通读

## 2026-10-24 夜：真实语料 + BEIR + 论文一致性修订

**语料**：312 篇官方文档（Docker 147 / Redis 89 / K8s 43 / Grafana 19 / Prometheus 14），
190 万字符，16,823 块。抓取脚本 `fetch_real_docs.py` 支持多项目并行。

**题集**：143 题（作者 6 + 本鲸 137），全部逐字校验通过。

**索引**：向量改 numpy 矩阵乘、落盘改 JSON+npz（41 MB），新增 6 个回归测试（71 通过）。

**关键结果**
| 评测 | 结论 |
|---|---|
| 内部 143 题 | Hybrid 0.937；固定 k8 0.930@294；自适应 k4/10 → 0.930@251（省 14%） |
| BEIR scifact 300 查询 | 自适应 0.7086 nDCG / 0.850 hit @2393 token（对 k10 省 27%） |
| BEIR nfcorpus 150 查询 | 省 7%（文档短） |

**三个否定结果**（已写进论文 6.9 与 8）
1. 句级索引在英文文档上 0.647 vs 固定块 0.922
2. 门控改写 0.902 vs 0.922
3. 按 token 截断对固定 k8 无优势（318 vs 294）

**论文**：新增 6.9「真实文档与公开基准」；4.1/6.2/6.3/7.1/8 全部对齐；
摘要补 BEIR 一句并标注受控设定。中英双稿、Word 8 表 3 图。

**修掉的 bug**：`RAG()` 之前永远用 OfflineAnswerer，API key 不生效 → 门控改写从未真正运行。

## 2026-10-25：一致性修订 + 两个新小节 + 图 4

**新增**
- 6.10 质量目标 → 预算的校准协议（20 条标注，达标率 76–93%，不可达拒绝）
- 6.11 第二维为什么不咬合（检索 16–70 ms vs 生成 898 ms，检索仅占 7.2%）
- 6.12 检索时间与上下文的交换率（4.0–13.4 token/ms；prefill 2.15 ms/token；净赚 4–17 倍）
- 图 4：四检索器预算-召回曲线 + 达标率-安全边际

**一致性修订**
- 4.1 句级索引限定中文短句语料；6.2 标注受控合成设定；6.3 消融同
- 8 局限扩到七条（主表为受控设定、τ 全局常数、仅两个 BEIR）
- 摘要补两条结论（自适应 7–21%、质量目标→预算）

**工程**
- Store 向量化 + npz 索引（16,823 块）
- scripts：calibrate_budget / fig4_data / fig4_calibration / pareto_multibudget /
  exchange_rate / beir_adaptive / adaptive_sweep / github_proxy
- 75 测试；CI 6 job 全绿
- CI 曾因 requirements 缺 numpy 失败，已修（加 numpy + skipUnless）

**环境坑**
- 本机 DNS 把 github.com 解析到 20.205.243.166（不可达）。
  VPN 关闭时用 `scripts/github_proxy.py` 起本地 CONNECT 代理（固定 140.82.112.3），
  `git -c http.proxy=http://127.0.0.1:8899 push`。VPN 开启时可直连。

## 2026-10-25 下午：四个空位收尾 + 三个风险关闭

**空位完成度**
- 空位 3 多维预算 → 6.11（第二维不咬合）+ 6.12（交换率 4–13 tok/ms，prefill 2.15 ms/token）
- 空位 4 质量目标接口 → 6.10（split conformal，覆盖误差 ≤0.015，图 5 对角线诊断）
- 空位 2 顺序成本 → 6.15（理论界失效、二值召回下决策不变）
- 空位 1 间隔充分性 → 未做（理论，留待作者）

**风险关闭**
- C2 同源偏差：6.13，4-gram 覆盖中位 0.000、LCS 中位 2 词，对照照抄句 1.000
- D2 多重比较：6.9，McNemar + Holm（Hybrid 胜 BM25，与 Dense 持平）
- G5 定性错误分析：6.14（9/143 漏检为排序失败；多跳全为选错实体）

**新增脚本**
overlap_analysis / significance_holm / order_dependent_cost / conformal_sweep /
fig5_conformal / exchange_rate / conformal_calibration

**论文规模**：5 图 9 表，6.1–6.15 共 15 个小节

## 2026-10-25 晚间：题集扩到 301、官方分类器、四子集 BEIR、三处口径修正

**数据规模**
- 题集 143 → **301**（新增 158 题，覆盖 Docker/Redis/Grafana/Prometheus/K8s；答案逐字校验全过）
- 全部依赖题数的实验已重跑（主表、保形、重叠度、错误分析、顺序成本、交换率、Pareto、图 4/5）

**新结果**
- 主表 301 题：BM25 0.801 / Dense 0.887 / Hybrid 0.910 / k8 0.904@289 / 自适应 0.900@244
- bootstrap：召回差 −0.003（95% CI [−0.020, +0.010]，p=0.81），节省 **15.5%**（CI [11.2%, 19.8%]）
- Holm：胜 BM25（p<1e-4）与 Dense-large（Holm 0.0091），与 Dense-m3 持平（p=0.12）
- 保形（301）：0.80/0.85/0.90 → 120/166/276 token，覆盖偏差 ≤0.015；α 扫描最大偏差 0.046
- BEIR 四子集：scifact 24%、nfcorpus 6%、fiqa 1%、**arguana −16%（失败，如实报告）**
- 官方分类器（6.16）：用官方 released 标签训 t5-small，验证 43.3%；路由 0.638@150 / 0.844@160
- 逐题阈值（6.17）：δ 扫描全面劣于全局 τ，内部与 BEIR 上一致（负结果）

**三处口径修正（重要）**
- 分类器 token 原来「命中即停」，低估；修正后 56/66 → 150/160，结论从「低预算端点」改为「内部点」
- eval_real 固定写 `results/eval_real_b300.json`，换索引跑会覆盖主表 → 句级对比改用
  `scripts/sentence_index_eval.py` 单独落盘
- 论文里 0.647/0.922 的句级索引数字无结果文件可查 → 重建句级索引（38,542 块）重测：
  **0.718 vs 0.910**，门控改写 0.874 vs 0.910，全部同步

**新增脚本**
train_complexity_classifier / official_route_eval / perquery_tau / bootstrap_saving /
audit_numbers / sentence_index_eval / beir_adaptive（新增 perquery 扫描）

**数字终检**
`python scripts/audit_numbers.py` → 中英各 56 项应出现数字全中，旧数字残留 0，结果文件齐全。

**环境坑（新增）**
- transformers 5.x 的 T5Tokenizer 不认 spiece.model（A/B/C 全判成同一个 unk 词元），
  训练要用 `D:\AAAAAgongju\venvs\t5train`（transformers 4.44.2）
- HF 的 resolve/CDN 被墙，权重走 `hf-mirror.com`；`special_tokens_map.json` 在 t5-small 上 404，删掉即可
- DSH 插件装在 `~/.dsh/profiles/desktop`（package.json 的 dsh.profile.bundles + pnpm add）；
  桌面有 `DSH插件回滚.bat`

**仍未做**
- 英文润色（作者找人）
- CRAG evaluator 复现（官方未放 checkpoint；需自训，成本高于收益）
- 空位 1（间隔充分性的理论刻画）
- 投稿前：引用转数字格式、图转 300dpi、Data Availability 核对
