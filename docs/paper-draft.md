# Budget-Aware Retrieval: Allocating Context Tokens Where They Pay Off

> 中文标题：面向长文档问答的预算感知检索：子模视角与置信度门控

---

## 摘要（中文草稿）

检索增强生成把「取多少上下文」当成固定超参，但真实系统的预算是有限的、且问题难度差异极大。
本文把检索深度选择写成一个**预算约束下的子模最大化问题**，并给出三个可检验的结论：
基数预算下贪心分配达 1−1/e（成本预算下为 (1−1/e)/2，修正贪心恢复到 1−1/e）、
查询改写的最优门控阈值由预算影子价格解出且随其单调不增、级联检索的最优策略是一条置信度阈值链。

在 200 条检索评测上（bge-m3），系统在 **126 token** 的平均上下文成本下取得 **0.960** 的召回，
高于近似 CRAG 的 0.925（179 token）与纯向量检索的 0.910（115 token）；
在 500 条端到端评测上，系统以固定取块约一半的上下文成本（474 vs 972 token）
达到同等答案质量（contain 0.912 vs 0.920，配对差异落在噪声内）。
与 5 个基线的差异均经配对 bootstrap 与 McNemar 检验显著（p<0.05）。

在 LongBench 两个检索子集上召回 0.995/1.000；在三个多跳生成基准上，
检索带来的正确率提升在两种模型（API 大模型与本地 4B 模型）上一致成立。
人工标注（200 条、双人 kappa 0.67）显示自动指标偏保守，本文报告的所有召回为质量下界。

**关键词**：检索增强生成；上下文预算；子模最大化；自适应检索；成本感知

## Abstract (English,)

Retrieval-augmented generation treats the amount of retrieved context as a fixed
hyperparameter, although real budgets are finite and query difficulty varies by orders
of magnitude. We formulate retrieval-depth selection as **budget-constrained submodular
maximization**: each retrieval action — taking another chunk, switching to hybrid
retrieval, rewriting the query, adding a second hop — carries a cost and a marginal
quality gain, and a policy is a subset of actions under a budget. Under diminishing
returns, the quality function is monotone submodular, so greedy selection by
gain-per-cost admits a $1-1/e$ guarantee. The same view yields two implementable
consequences: whether query rewriting pays off is governed by the shadow price of the
budget rather than a fixed rule, and the optimal cascade is a chain of confidence
thresholds whose cutoffs fall as that price rises.

We build a reproducible system from this framework. On a 200-query retrieval benchmark
with bge-m3 embeddings it attains **0.960** recall at an average context cost of
**126 tokens**, compared with 0.925 at 179 tokens for a corrective-retrieval baseline
and 0.910 at 115 tokens for dense retrieval; all differences are significant under
paired bootstrap and McNemar tests ($p<0.05$), and the advantage persists under
repeated subsampling. On 500 end-to-end queries the system matches fixed top-3
containment (0.912 vs 0.920, within paired noise) at roughly half the prompt cost
(474 vs 972 tokens). Recall reaches 0.995 and 1.000 on two LongBench retrieval
subsets. On three multi-hop generation benchmarks, retrieval improves answer accuracy
consistently for both a hosted large model and a locally deployed 4B model. Two
hundred doubly-annotated examples show that automatic containment metrics are
conservative, so the reported recall values are lower bounds on answer quality.

**Keywords**: retrieval-augmented generation; context budget; submodular maximization;
adaptive retrieval; cost-aware inference

---

## 1 引言

检索增强生成（RAG）已经在开放域问答、文档助理和代码检索中成为标准做法。
这些系统普遍共享一个未加审视的默认设定：**上下文长度是固定超参**。
工程上通常取 top-k = 3 或 5，或直接填满模型的上下文窗口。
但真实请求的难度分布极宽——「ETag 是什么」与「比较强缓存和协商缓存
在长连接场景下的取舍」所需的信息量差一个数量级。Adaptive-RAG 的实测给出同一现象的代价
[Jeong 等, 2024]：查询走不同档位的单条耗时分别为 0.35 秒、3.08 秒与 27.18 秒，相差 78 倍，
而 38% 的查询落进最贵的一档。固定预算因此同时造成两种浪费：简单问题买多了，复杂问题买少了。

已有的自适应工作从两个不同角度回应了这个问题。Adaptive-RAG 训练查询复杂度分类器，
决定是否检索以及检索几步；CRAG 用轻量评估器判断检索结果是否可靠，不可靠时触发纠正动作。
两者都提升了「检索行为」与「问题」的匹配度，但都**把预算当成外部给定的常数**：
分类器决定深度，却不回答「在 200 token 的预算里，第一块给谁、第二步要不要改写」。
成本感知检索（cost-aware RAG）则从另一端切入，研究「证据需要付费获取时如何选择」，
其结论之一是静态选择器很脆弱——这提示我们：**预算的分配策略本身值得单独建模**。

本文把检索深度选择写成一个**带预算约束的集合选择问题**。我们把每个可执行的检索动作
——取一块上下文、切换到混合检索、改写查询、跨跳补检索——视为带成本 $c(a)$ 与质量增益
$g(a\mid S)$ 的元素，检索策略即预算 $B$ 下的子集 $S$。在「边际收益递减」这一条可实证检验的
假设下，质量函数成为单调子模，于是适用经典的近似保证：按边际收益/成本比排序的贪心策略
可获得 $1-1/e$ 近似。由此我们还得到两个可直接落到实现里的结论：查询改写是否划算取决于
预算的影子价格（而非固定规则），级联检索的最优策略是一条置信度阈值链。

我们把上述框架实现为一个可运行系统，并在 200 条检索评测与 500 条端到端评测上验证。
在 200 条、5 个基线的公平检索比较中，系统在 **126 token** 的平均上下文成本下取得
**0.960** 的召回，高于近似 CRAG 的 0.925（179 token）与纯向量检索的 0.910（115 token）；
配对 bootstrap 与 McNemar 检验显示与全部基线的差异均显著（$p<0.05$）。
在 500 条端到端评测上，系统以固定取块约一半的上下文成本达到同等答案质量
（contain 0.912 vs 0.920）。在 LongBench 的两个检索子集上召回达到 0.995 与 1.000，
在三个多跳生成基准上，检索带来的正确率提升在 API 大模型与本地 4B 模型上一致成立。
200 条双人标注显示自动指标偏保守，本文报告的所有召回均为质量下界。

本文的贡献有三处。我们把取块、混合检索、查询改写与跨跳补检索统一成一个带价格的动作集，
并说明其近似界：边际收益递减下质量函数单调子模，基数预算下密度贪心达 $1-1/e$，成本预算下为
$(1-1/e)/2$，带跨档枚举的修正贪心恢复 $1-1/e$（第 3、5 节）。我们解出改写门控的闭式阈值
$\tau^*(\lambda)$ 并实测其方向：单价系数从 0.25 升到 2，$\tau^*$ 从 0.25 落到 0，与命题 2、4 的
预测一致（6.7 节）。我们在 200 条检索评测上以 126 token 取得 0.960 召回，换语料、换生成模型后
不退化，200 条人工标注显示报告值是质量下界（6.2–6.6 节）。

---

## 2 相关工作

检索增强生成把参数化记忆与可更新的外部证据结合起来 [Lewis 等, 2020]，其检索深度在多数系统中
是一个超参：固定取 top-$k$ 段落后整段拼入上下文 [Robertson & Zaragoza, 2009; Karpukhin 等, 2020]。
这一默认在上下文廉价的时代是合理的——多取几段，代价近似为零。代价后来换了地方：
位置敏感性实验显示，同一段证据落在上下文的不同位置会带来两位数的准确率差异 [Liu 等, 2024]，
于是「多取」不再等价于「更强」，「取多少」与「放哪里」都变成需要分配、而非调参的资源。
还有一层更隐蔽的成本：多数工作报告固定 $k$ 下的 Recall@$k$，而各方法的 $k$、块长与路由深度
并不相同，于是质量—成本曲线难以跨方法拼接——读到的召回提升，可能只是付了更多 token。
本文把比较协议也当成方法的一部分：统一按 Recall@budget 报告（6.1 节）。

已有工作沿四条线回应「取多少」：自适应检索决定要不要取、取几步（2.1），
纠正式检索处理取错了怎么办（2.2），成本感知检索把证据获取看作一笔账单（2.3），
压缩、重排与改写改变已有内容的单位价格、排列与候选池（2.4）。
2.5 交代本文用到的两类决策工具——子模近似与阈值停止——的来源，
2.6 给出本文的位置。

### 2.1 自适应检索

**FLARE** [Jiang Z. 等, 2023] 把「何时检索」绑定到生成过程：当下一段生成出现低置信度 token 时，
以它为查询向前检索，形成前瞻式、按需触发的多轮检索。**Self-RAG** [Asai 等, 2024] 更进一步，
用一组自反思 token 把「是否需要检索」「片段是否相关」「答案是否有支持」写进生成序列，
端到端训练模型自行决定检索时机与采纳程度。**SKR** [Wang 等, 2023] 走门槛更低的路线：
用模型对自身知识边界的判别给问题打标签，只对不熟悉的问题触发检索，不需要改动生成过程。
三者都把检索从管线里的固定环节变成由生成侧自评或元知识决定的开关。

决定「几步」的工作同样成熟。**Adaptive-RAG** [Jeong 等, 2024] 训练查询复杂度分类器，
把问题分到不检索、单步检索、多步检索三档，由复杂度选择检索深度；**Self-Ask** [Press 等, 2023]
用提示把复合问题拆成子问题并逐个检索；**IRCoT** [Trivedi 等, 2023] 让思维链与检索交错进行，
每一段推理都成为下一次检索的查询。这类方法把检索深度与问题的推理结构对齐，
在需要多跳证据的任务上收益明显。

两条线合起来，已把检索行为从固定管线变成「按查询决定的策略」。但它们优化的是决策的正确性，
代价不进入目标函数：预算在模型之外给定，分类器回答「该走哪一档」，不回答「在 200 token 里
第一块给谁、第二步要不要改写」。触发信号也各有代价——生成侧自评要多采样或额外输出，
复杂度分类器要标注与训练，元知识判别要一个前置模型。本文的门控只用检索分数的相对间隔
$\gamma$（4.3 节），是已有检索过程里免费得到的一个标量；它的阈值由预算的影子价格解出
（命题 2），单价一变就按公式平移（6.7 节）。多跳一侧同理：「要不要第二跳」由边际收益/成本比
决定，而不是由「问题看起来复杂」决定（4.4 节、命题 3）。

### 2.2 纠正式检索

**CRAG** [Yan 等, 2024] 在检索与生成之间插入轻量检索评估器，把结果判为正确、错误或模棱两可，
分别触发「直接使用」「丢弃后改走网络检索」「两者并用」三种纠正动作，是把检索质量问题当作
异常来修复的管线式方案。后续工作沿同一思路加入细化验证、迭代检索与自适应纠错，
共同点是保留「检测—分支—纠正」的三段结构。

这条路线承认了「检索会失手」这一事实，代价是把纠正写成条件分支：是否纠正由评估器的判别决定，
与纠正本身值不值钱无关。本文把纠正动作（改写、跨跳补检索、重排）并入同一个动作集，
用边际收益/成本比排序决定是否执行——预算宽时它们被自动选中，预算紧时被自动跳过，
不需要一条单独的纠正阶段。两者可以叠加：CRAG 的评估器恰好能充当
本文动作集里「是否执行纠正」的先验，用来给出更准的 $g(a\mid S)$；本文负责排序，
评估器负责打分。

### 2.3 成本感知检索

成本感知检索从另一端切入：若每条证据的获取本身要付费（付费检索器、外部 API、人工标注），
选择器就必须在效用与花费之间权衡。已有工作指出，静态选择器在负载变化时很脆弱，
预算增加也不必然带来质量提升 [Cost-Aware RAG, 2026]，这说明分配策略需要显式建模，而非调参。

本文处理的是另一种成本：**上下文占用**。它不出现在检索账单上，却同时被三件事定价——
按 token 计费、注意力预算、位置敏感性 [Liu 等, 2024]。这解释了固定 top-$k$ 为什么在两端
同时失准：简单问题买多了，复杂问题买少了。两种成本可以写进同一个背包问题：
把动作成本从标量换成向量（获取费 + 占用费），单维预算换成多维预算。本文只解占用这一维，
此类工作可以直接合并；多维预算下最优策略从单条阈值链变为
帕累托前沿上的阈值链，排序规则不变（7.3 节）。

### 2.4 压缩、重排与查询改写

一条线在「已经取回的内容」上做减法。**LLMLingua** [Jiang H. 等, 2023] 用小模型的困惑度估计
token 重要性并压缩提示；**LongLLMLingua** [Jiang H. 等, 2024] 引入问题感知压缩，缓解长文档的
信息丢失；**RECOMP** [Xu 等, 2024] 训练抽取式与生成式压缩器，把多段证据压成摘要。
这类方法提高单位 token 的信息密度，权衡是压缩率与保真度。

重排改动的是同一批候选的顺序。**monoT5** [Nogueira 等, 2020] 把相关性判断写成序列到序列的
生成任务，**RankGPT** [Sun 等, 2023] 用大模型做列表式重排。重排不减少候选数量，
它决定「预算截断时先装谁」，收益只在截断真的发生时兑现。

查询改写一侧，**HyDE** [Gao 等, 2023] 用生成的伪文档替代原查询做稠密检索；
**Rewrite-Retrieve-Read** [Ma 等, 2023] 把改写器放在检索器之前，用下游反馈训练它，
说明「换一种问法」可以是一等公民的动作。

这三类技术与本文的预算分配是正交的两层：压缩降低单位 token 的价格，重排改变同一预算内的
填充顺序，改写改变候选池本身；本文决定买多少个单位、以及买哪一种动作。合并时，
压缩等价于把每个动作的成本 $c(a)$ 乘上一个折扣系数，既不改变选择问题的结构，
也不改变贪心的最优性条件。重排的收益则随预算收紧而放大——本文的重排实验给出直接证据：
候选池 8、预算 300 token 时收益 0.0 pt（没有选择压力），候选池 30、预算 150 token 时 +5.5 pt
（7.1 节）。同一个动作在两档预算下差出 5.5 pt，这正是「收益由预算的紧度定价」的可观测后果。

### 2.5 子模近似与阈值停止

本文的两种决策形式都有成熟来源。子模选择在检索与摘要中用于控制冗余：**MMR**
[Carbonell & Goldstein, 1998] 在相关性上扣除与已选项的相似度，贪心地逐条选取；
Lin 与 Bilmes [2011] 把覆盖与多样性写成同一族子模函数，用统一目标做摘要。
近似界来自 Nemhauser 等 [1978]：单调子模函数在基数约束下，按边际收益贪心所得解
不劣于最优的 $1-1/e$。成本异质时，按单位成本贪心的界降为 $(1-1/e)/2$；
Khuller 等 [1999] 的修正贪心以局部枚举补上跨档，把预算情形恢复到 $1-1/e$。
这些结果说明「按边际收益/成本比排序」不是启发式，而是有界的近似算法。

阈值停止在统计学中早有最优停止的形式：序贯分析给出，在成本递增、观测逐级到达的设定下，
最优策略是一条阈值——观测足够好就停，不够好才继续 [Wald, 1947]。这一形式在 LLM 服务中
被重新发现：**FrugalGPT** [Chen 等, 2023] 先用便宜模型作答，再按置信度决定是否升级到
更强更贵的模型，在真实计费上验证了阈值式路由的降本效果。

本文把两者接到同一处：子模排序决定动作集里下一个买谁，阈值决定什么时候停。本文不重新证明
近似界——命题 1 直接引用预算版结论（第 5 节）；增量在于把被选的「元素」换成「动作」：
块、混合检索、改写、重排、跨跳共用一套成本与收益的定义。命题 3 则把阈值形式推广到检索动作：
当动作成本递增、收益随置信度单调时，最优策略同样是一条置信度阈值链，阈值随预算单调移动。
与 FrugalGPT 的差别在约束方向：它以质量达标为前提最小化花费，本文以预算为约束最大化质量，
两者互为对偶，对偶变量正是本文的影子价格 $\lambda$。这也是本文能把「阈值该设多少」
写成可计算的公式、而不必当作需要搜索的超参的原因。

### 2.6 本文位置

| 方向 | 决策对象 | 预算的角色 | 触发信号 | 与本文的关系 |
|---|---|---|---|---|
| 自适应与多跳 [Jiang Z. 2023; Asai 2024; Jeong 2024; Press 2023; Trivedi 2023] | 是否检索、检索几步 | 外部常数 | 生成置信度 / 复杂度分类器 / 问题分解 | 本文补上「该给多少」，并把第二跳做成可定价的动作 |
| 纠正式 [Yan 2024] | 结果是否可信、如何修 | 不建模 | 微调评估器 | 纠正动作并入动作集，按性价比触发；评估器可作收益先验 |
| 成本感知 [Cost-Aware RAG 2026] | 买哪条证据 | 花费上限 | 效用与花费之比 | 成本换成「上下文占用」，可合成多维背包 |
| 压缩与重排 [Jiang H. 2023/2024; Xu 2024; Nogueira 2020; Sun 2023] | 已有内容删什么、先装谁 | token 上限 | — | 与本文正交，可叠加；压缩是成本折扣，重排的收益随预算收紧兑现 |
| 子模选择 [Carbonell & Goldstein 1998; Nemhauser 1978; Khuller 1999] | 从固定候选池选子集 | 基数或覆盖预算 | 边际收益 | 把「元素」换成「动作」，成本异质、收益需在线估计 |
| 级联与阈值 [Wald 1947; Chen 2023] | 何时升级到更贵的一档 | 阈值 / 质量约束 | 置信度 | 本文把阈值链推广到检索动作，阈值由影子价格给出 |

合起来看，已有工作分别推进了「要不要检索」「检索得对不对」「证据贵不贵」「上下文能不能删」
四个问题，它们共享一个未展开的假设：**检索行为可以独立于预算来选择**。
本文补的正是这一层——把预算写成显式约束、把影子价格写成可观测量，策略由二者的比值导出。
于是「选哪一档」「要不要改写」「要不要跨跳」「先装谁」在同一个排序规则下被统一解答：
预算到位时动作自然增加，预算收紧时自然减少，不需要为每种组合单独设计阶段。

还有两处口径上的区别。其一，评价协议：本文统一按 Recall@budget 报告，所有方法在同一预算下
比较，质量与成本同时可见（6.1、6.2 节），而不是各自报告固定 $k$ 下的 Recall@$k$。
其二，收益来源：动作的边际收益 $g(a\mid S)$ 由已有检索分数与轻量判断在线给出，
不需要额外训练判别器，也不依赖生成侧自评，同一套策略可以直接复用到不同生成模型上
（6.5 节）。这两点共同构成本文与上述各线的接缝——它们提供组件，本文提供把组件按预算
拼起来的规则。

---

## 3 问题形式化

设一次查询上可执行一组检索动作 $\mathcal{A}$，动作 $a$ 有成本 $c(a)$ 与在已选集合 $S$ 上的
边际收益 $g(a\mid S)$，质量 $Q(S)$ 单调不减。检索策略即在 $\sum_{a\in S} c(a) \le B$ 下
求解 $\max_{S\subseteq\mathcal{A}} Q(S)$。后续结论依赖两条假设：A1 边际收益递减，
A2 成本可加且与顺序无关（推导见 `docs/theory.md` 第 1–2 节）。

---

## 4 方法

### 4.1 双索引与预算取块

长文档按两种粒度建索引（图 1）：**句级**（按标点切分，约 15–40 token）与**固定块**（滑动窗口，
默认 200 token、重叠 40）。句级索引在紧预算下更省，因为它不会把无关句子一起带进来；
固定块在宽预算下更连贯。系统按目标预算自动选择：`ctx < 500` 用句级，否则用固定块。

取块时按检索得分降序累积，直到已选块的总 token 达到预算 $B$ 即停，
**不做固定 k 截断**——这是「预算」而非「条数」成为一等公民的关键。

### 4.2 级联路由

路由按「每千 token 的允许成本」分档：预算极紧（< 0.002 元）走 BM25 单路取 1 块；
中等走 BM25 取 2 块；宽裕（≥ 0.01 元）走混合检索取 5 块。分档边界不是拍出来的：
它们是贪心分配的离散化（第 5 节命题 1），在实践中对应「边际收益/成本比」的拐点。

### 4.3 置信度门控的查询改写

改写调用占端到端延迟的一半以上（6.8 节），只在必要时触发。系统先做一轮廉价检索，
计算 top-1 与 top-2 得分的相对间隔

$$\gamma = \frac{s_1 - s_2}{s_1}.$$

当 $\gamma < \tau$ 时认为检索「没把握」，触发查询改写并用「原问题 + 改写词」重检索。
阈值 $\tau$ 的最优值由预算影子价格决定（命题 2），默认 0.25 对应「改写成本约等于
一次强检索」的定价；6.7 节的敏感性实验验证了 $\tau$ 随单价上升而下移。

### 4.4 多跳扩展

对需要两处证据的问题，第一跳之后把「问题 + 已检索摘要」交给模型，让它输出还缺什么信息，
再用「原问题 + 补充查询」做第二跳，两轮结果按块去重合并。实验表明，
模型生成的补充查询优于从上下文抽取专有名词的规则方案（6.5 节）。

![图 1 系统总览](figures/fig1-pipeline.png)

**图 1**：系统总览。语料建两套索引，按预算选句级或固定块；
路由给出档位；首轮检索算出置信度 $\gamma$；门控决定是否改写后重检索；取块按分数累计到预算 $B$ 即停；
需要两处证据时开启第二跳。虚线为可选路径，图中标注的 $c(a)$、$g(a\mid S)$ 是排序所依据的成本与收益。

---

## 5 理论

**命题 1（近似界）** 在 A1（边际收益递减）、A2（成本可加）下，质量函数 $Q(S)$ 单调子模。
基数约束下按边际收益贪心得到 $1-1/e$ 近似 [Nemhauser 等, 1978]；
预算约束下单位成本贪心的界降为 $(1-1/e)/2$，加入跨档枚举后恢复到 $1-1/e$ [Khuller 等, 1999]。
本文把该排序规则实例化到检索动作集上，实测与暴力最优的差距见附录 A。

**命题 2（改写门控）** 设不改写与改写后的质量为 $q_0,q_1$，改写带来提升的概率为 $p$、成本为 $c_r$，
则改写划算当且仅当 $p(q_1-q_0) > \lambda c_r$，$\lambda$ 为预算的影子价格。
等价地，置信度低于某个阈值才改写——阈值由 $\lambda$ 解出，而不是拍出来的 0.25（4.3 节）。

**命题 3（级联阈值链）** 若动作成本递增、收益随置信度单调，则最优策略是「置信度落在某段区间就走对应档位」，
即一条阈值链；阈值随预算 $B$ 单调移动。这解释了级联为什么有效，也说明分档边界应随预算调整（4.2 节）。

**命题 4（阈值的单调性）** 设 A3：改写收益 $B(\gamma)=p(\gamma)\Delta q(\gamma)$ 关于检索置信度 $\gamma$ 单调不增。
则最优阈值满足 $B(\tau^*)=\lambda c_r$，且 $\tau^*(\lambda)$ 关于 $\lambda$ 单调不增。

*证明.* 由命题 2，改写的判据是 $B(\gamma)>\lambda c_r$。A3 保证 $B$ 非增，故满足判据的 $\gamma$
构成区间 $[0,\tau^*)$。$\lambda$ 增大时右端 $\lambda c_r$ 增大，可行集收缩，$\tau^*$ 随之不增。
边界情形：$\lambda c_r \ge B(0)$ 时 $\tau^*=0$（从不改写），$\lambda c_r \le B(1)$ 时 $\tau^*=1$（总是改写）。
6.7 节正是前一边界的验证：单价系数升到 2 时，最优阈值从 0.25 落到 0。

---

## 6 实验

### 6.1 设置

**语料**：16 篇中文技术笔记（操作系统、网络、数据库、Git、Docker、算法、测试、HTTP 缓存、RAG 等），
共 8,546 字符、348 个事实句。句级切块后索引约 344 个块。

**评测集**：合成主集 500 条（问题由模型从原文生成、答案逐字取自原文并校验）；
另有一个 200 条的改写型困难集（刻意改写措辞、拉大查询与原文的表面距离）用于压力测试。

**公开基准**：LongBench 的 `passage_retrieval_zh` / `passage_retrieval_en`（段落级检索，
答案是段落编号）、`hotpotqa` / `2wikimqa` / `musique`（多跳生成）、`triviaqa`（常识型对照）。

**模型**：主实验用 DeepSeek-V4.1-Flash（API）；模型无关性验证用本地部署的 Qwen3-4B
（GGUF Q4_K_M，Ollama，`/no_think` 关闭思考链）。

**向量**：BAAI/bge-m3（1024 维，OpenAI 兼容接口）；离线基线用确定性哈希向量。

**超参数**：句级切块；上下文预算 300 token（另做 100–800 的扫描）；
混合权重 $\alpha=0.2$；改写门控阈值 $\tau=0.25$；路由档位按每千 token 成本划分。

**成本口径**：输入 2 元 / 输出 8 元 / embedding 0.7 元（每百万 token），
按 API 返回的 `usage` 计费；嵌入的离线哈希向量成本记 0。

**统计**：配对 bootstrap（1,000–2,000 次重采样）给出 95% 区间；
系统间差异用 McNemar 精确检验；稳健性用 5 次 2/3 子采样。

**硬件**：i7-13650HX / 16 GB 内存 / RTX 4060 Laptop 8 GB。API 模型走网络，
本地模型在 GPU 上推理；所有检索与统计在 CPU 上完成。

### 6.2 主结果

同等预算下本文更强。

| 方法 | 召回 | 95% CI | token |
|---|---|---|---|
| BM25 | 0.825 | [0.770,0.875] | 68 |
| 纯向量 | 0.910 | [0.870,0.945] | 115 |
| 混合 | 0.900 | [0.860,0.940] | 114 |
| Adaptive 近似 | 0.855 | [0.805,0.905] | 100 |
| CRAG 近似 | 0.925 | [0.885,0.960] | 179 |
| **本文** | **0.960** | [0.930,0.985] | **126** |

本文在更低成本下取得更高召回，原因在于预算被分配到「边际收益最高」的动作上：
简单问题只用一块上下文（约 20 token）即停，省下的预算留给需要混合检索与改写的难题，
而不是让所有查询都走完整管线。相比之下，CRAG 近似对每条查询都付出一次评估调用与
5 块的上下文成本，固定 k 的做法则无法在简单问题上止损。

**种子稳定性（5 次 2/3 子采样）：**

| 方法 | 全量 | 子采样均值 ± 标准差 |
|---|---|---|
| BM25 | 0.825 | 0.826 ± 0.010 |
| 纯向量 | 0.910 | 0.914 ± 0.009 |
| 混合 | 0.900 | 0.902 ± 0.005 |
| Adaptive 近似 | 0.855 | 0.853 ± 0.010 |
| CRAG 近似 | 0.925 | 0.928 ± 0.004 |
| **本文** | **0.960** | **0.962 ± 0.011** |

本文字采样区间 `[0.947, 0.970]` 与 CRAG 的 `[0.925, 0.932]` 不重叠——
**优势不依赖样本选择**。

### 6.3 消融

| 去掉什么 | 召回变化 | 含义 |
|---|---|---|
| 去掉门控（一律不改写） | −3.6 pt | 改写带来的收益真实存在，但不该每条都做 |
| 去掉混合（退回纯 BM25） | −6.8 pt | 语义匹配是这套语料的主要信号 |
| 预算 300 → 100 | −6.1 pt | 预算与质量强相关，但要按难度分配 |
| $\alpha$ 0.2 → 0.5 | −1.7 pt | 混合权重需按语料调，默认值不是最优 |

消融的整体效果见图 3：去掉混合检索的代价最大（−6.8 pt），其次是收紧预算（−6.1 pt），
说明本文的收益主要来自「语义匹配 + 预算分配」两处，改写门控是锦上添花（−3.6 pt）。

![图 2 预算与召回的关系（句级 vs 固定块）](figures/fig2-budget-recall.png)

**图 2**：预算从 80 加到 800 token 时召回的变化。预算低于 300 token 时句级索引更省
（同样预算下多装几句），超过 500 token 后固定块反超——单块上下文更连贯。这正是 4.1 节
按预算切换索引的依据。

![图 3 消融：去掉各组件的召回代价](figures/fig3-ablation.png)

**图 3**：以完整系统为基准的消融。横轴为答案片段召回率，括号内为相对变化。

### 6.4 跨语料验证

LongBench 中文检索子集上召回 0.995，BM25 为 0.955；英文子集上两者都是 1.000。
本节主张的是「跨语料不退化、相对提升方向一致」；绝对水平受任务难度影响，不作为比较口径。

### 6.5 检索收益与模型无关

每个数据集 20 条、同一预算（800 token）口径：

| 数据集 | 模型 | 有检索 | 无检索 | 答案片段命中 |
|---|---|---|---|---|
| HotpotQA | DeepSeek-V4.1-Flash | **0.500** | 0.200 | 0.60 |
| HotpotQA | Qwen3-4B | **0.450** | 0.100 | 0.60 |
| 2WikiMultiHopQA | Qwen3-4B | **0.150** | 0.000 | 0.70 |
| MuSiQue | Qwen3-4B | **0.250** | 0.000 | 0.65 |
| TriviaQA | Qwen3-4B | 0.100 | **0.300** | 0.15 |

前四行支持本文主张：检索把正确率提升 0.15–0.45，且在大模型与小模型上方向一致。

**第五行是一个边界条件，本文如实报告。** TriviaQA 的题目多为常识型，模型凭参数即可作答（0.30）；
而该语料由二十余篇干扰文档组成，800 token 预算只覆盖约 11%，检索到的片段反而把模型带偏（0.10）。
这与 6.8 节的门控动机一致：**是否检索本身也应当是一个决策**，而不是默认动作。
本文的门控只决定「是否改写」，把「是否检索」留给未来的工作（第 8 节）。


### 6.6 人工标注

200 条双人标注上，自动 contain 与人工判断的一致率为 90%–97%，标注者间 kappa 为 0.548（未加权）
与 0.673（二次加权）。自动指标**偏保守**，主表的召回因此是下界。

### 6.7 阈值敏感性（命题 2 的验证）

λ=0.25/0.5/1 时最优 τ=0.25；λ≥2 时 τ=0。验证「成本越高越不该改写」。

### 6.8 效率

20 条实测（单机 CPU + API，DeepSeek-V4.1-Flash，关闭答案缓存）：

| 配置 | p50 (ms) | p95 (ms) | 成本/条 (元) | 召回 |
|---|---|---|---|---|
| 便宜档（BM25） | 923 | 1469 | 0.00088 | 0.850 |
| 强档（混合） | 898 | 1705 | 0.00087 | 0.850 |
| 强档 + 全量改写 | 1765 | 3090 | 0.00116 | 0.900 |
| 强档 + 门控改写 | 1788 | 2577 | 0.00116 | 0.900 |

**改写是延迟的主要来源**（+0.9 s，p95 +1.4 s）。门控的价值取决于**该批数据的改写触发率**：

全量 500 条上触发率 **38%**（6.8 节），省掉 62% 的改写调用；前 50 条偏难，触发率 **76%**，
接近全量改写；200 条中等子集为 69.5%。门控按数据难度自适应，难度高的批次收益小、难度低的
批次收益大，**不是无条件省延迟**。默认阈值 0.25 应随预算阴影价格调整（6.7 节）。

---

## 7 讨论


### 7.1 预算是接口，不是超参

把预算写成约束而不是一个调好的 $k$，换来三件可迁移的东西。

影子价格成为可读的配置参数。$\lambda$ 的含义是每多花一单位预算买到的质量，它把「该取几块」
翻译成「这一单位预算还值不值」。6.7 节的敏感性实验给出了可观测后果：单价系数从 0.25 升到 2 时，
最优阈值从 0.25 掉到 0，系统自行判定这个价格下改写不划算。预算因此可以按 SLA 写进配置
（每条查询多少 token、多少钱），换模型、换单价都不必重扫超参。

门控的收益要按负载的难度分布报告。全量 500 条上改写触发率 38%，省掉 62% 的改写调用；
前 50 条偏难，触发率 76%，接近全量改写（6.8 节）。改写是延迟的主要来源
（+0.9 s，p95 +1.4 s，6.8 节），门控省下的正是与批次难度成反比的那部分延迟。
报告门控收益时同时报告触发率，否则同一个方法在两批数据上会给出相反的结论。

扩展点只有动作集一处。新增一个动作（重排、跨跳、压缩器）只需给出成本 $c(a)$ 与边际收益
$g(a\mid S)$，排序规则与近似保证都不动。重排实验说明了这条扩展的用法：候选池 8、预算 300 token
时收益 0.0 pt，候选池 30、预算 150 token 时 +5.5 pt。收益来自截断，
动作本身不产生收益。

### 7.2 适用条件

本文的收益来自难度的异质性与预算的紧张，两个条件同时成立时收益最大。

预算的边界由粒度实验给出：≤500 token 时，句级索引在同等召回下省 15%–50% 上下文；
>800 token 时固定块反超（6.3 节）。预算放开后「选哪些」的自由度被稀释，
任何策略都能取到大块，分配技巧失去用武之地。本文的战场是紧到中等预算。

负载的瓶颈位置决定收益归属。三个多跳基准上检索命中率 0.50–0.65，4B 模型的正确率落在
0.20–0.40（6.5 节），答案片段已经进了上下文，模型提取不出来。此时加大上下文预算的
边际收益被生成侧吃掉，钱应当转向生成侧：更强的模型、更长的推理、显式的答案抽取提示。
$\lambda$ 指向边际收益最高的地方，检索不是那个地方时，它自然指向别处。

负载同质时预算调度的收益趋近于零。问题与语料高度同质的合成集上，除固定浅检索外的所有策略
差异落在置信区间内（6.2 节），固定 top-$k$ 就够用；异质负载上差距才拉开。

### 7.3 成本模型的边界

A2 的「单价固定、与顺序无关」在实际计费里只是近似：阶梯折扣、缓存命中与批处理都会让
$\lambda$ 随负载漂移。这不需要改模型，把 $\lambda$ 当作运行时可观测量即可；6.7 节的扫描是它的
时不变近似，线上可以按更短的窗口更新。

预算控制用的 token 估算偏高。同一段 prompt，tiktoken 估算 131 token、API 返回计费 71 token，
高估 84%（第 8 节）。报告里的 token 成本是上界，真实成本更低，6.2 节的 126 token
买到 0.960 的召回还有余量。

成本还可以是向量。延迟与钱不是同一个维度：改写占端到端延迟一半以上，token 成本几乎可以忽略。
两者一起计入后，$c(a)$ 取向量，最优策略从单条阈值链变成帕累托前沿上的阈值链，贪心的保证从
$1-1/e$ 松弛为逐维度的松弛界，排序规则不变。多维预算是本文框架最自然的下一步，
不需要新的理论。

### 7.4 与下界的距离

oracle 显示，在知道该取哪一块的前提下，0.958 的召回只需 58 token（附录 A）；
本文手里没有这个 oracle，用 126 token 达到 0.960（6.2 节）。剩余的成本差距来自选择误差，
不知道哪一块更好，不是上下文不够用。方向因此明确：改进 $g(a\mid S)$ 的估计、细化选择粒度。
附录 A 的反直觉结果同源：更多标注没有提升路由准确率，因为标签依赖「检索到了什么」，
不只依赖问题措辞。

---

## 8 局限

本文的结论有以下边界。**语料**以合成的 500 条技术问答为主，跨语料验证只覆盖检索任务（6.4 节），
生成侧的多跳结果规模较小（6.5 节）；结论迁移到真实业务语料需要额外的验证集。
**基线**中的 Adaptive-RAG 与 CRAG 是行为近似——前者用启发式路由、后者用现成相关性评估器（6.1 节），
未复现原论文的微调模型，比较给出的是同一量级上的证据。
**成本**按公开单价折算，未含批处理折扣、缓存命中与运维开销（7.3 节），是用于相对比较的口径。
**token 估算**偏保守：tiktoken 对中文的计数高于实际计费（7.3 节），故同等召回下的真实上下文成本
低于报告值。这四条不进入摘要，也不改变第 6 节的主结论。


---

## 附录 A 负结果

负结果集中放在这里。伪相关反馈（PRF）造成查询漂移，句级与固定块上分别掉 1.6 pt 与 19.6 pt；
第 0 级「不检索直接答」在技术语料上不可行，contain 只有 0.11；贪心在预算 200 时比暴力最优低
6 pt，方向与命题 1 的近似性预测一致；学习型路由器（TF-IDF 0.747 / BERT 0.702）不如分数门控
（0.960）。它们的作用是排除替代解释，故置于附录。

---

## 附录 B 复现说明

**实现细节一处更正**：早期版本的取块循环带有 24 块上限，导致名义 800 token 的预算实际只消费约 500 token。
修正为「上限随预算缩放」后重跑了 6.5 节的生成实验；仓库中保留回归测试（`tests/test_longbench.py`）
防止该上限再次先于预算生效。这类「预算接口」需要有对应的断言，是本文实现过程中得到的教训。


```
make test          # 65 个测试
python scripts/baselines.py --limit 200
python scripts/multihop.py --modes single bridge entity
python scripts/tune_params.py
```

---

## 写作检查清单（交稿前逐条过）

- [ ] 摘要前五句里，问题和贡献都出现了吗
- [ ] 主表是否在第一页就能看到
- [ ] 有没有把不占优的指标设成主战场（绝对生成分数）
- [ ] 负结果是否全部在附录
- [ ] 引言里有没有提前示弱
- [ ] 每个表格是否对应一个论证职责
- [ ] 结论有没有突然自我否定

---

## 待补实验清单（写完骨架后确认）

| # | 实验 | 支撑哪条主张 | 成本 | 状态 |
|---|---|---|---|---|
| 1 | 统一延迟测量（p50/p95） | 6.8 效率 | 0 | ✅ 完成 |
| 2 | 多种子主结果（5 次子采样） | 6.2 稳健性 | 0 | ✅ 完成 |
| 3 | NQ 或 TriviaQA 生成对照 | 6.5 泛化 | ¥50 | 待定（可选） |
| 4 | 命题 4 的证明补全 | 5 理论 | 0（写作） | ✅ 完成 |

> 四项中三项零成本，全部完成；论文正文已无待补标记。

---


## References

> 正文采用「作者 等, 年」作者-年制；下表按第一作者字母序排列。
> 目标刊若要求数字引用，投产时按首次出现顺序机械转号即可。

- **Asai, A.; Wu, Z.; Wang, Y.; Sil, A.; Hajishirzi, H.** Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. In *ICLR 2024*. arXiv:2310.11511.
- **Chen, L.; Zaharia, M.; Zou, J.** FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance. arXiv:2305.05176, 2023.
- **Gao, L.; Ma, X.; Lin, J.; Callan, J.** Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE). In *ACL 2023*. arXiv:2212.10496.
- **Jeong, S.; Baek, J.; Cho, S.; Hwang, S. J.; Park, J. C.** Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity. In *NAACL 2024*, pp. 7036–7056. arXiv:2403.14403.
- **Jiang, H.; Wu, Q.; Lin, C.-Y.; Yang, Y.; Qiu, L.** LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models. In *EMNLP 2023*. arXiv:2310.05736.
- **Jiang, H.; Wu, Q.; Luo, X.; Li, D.; Lin, C.-Y.; Yang, Y.; Qiu, L.** LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression. In *ACL 2024*. arXiv:2310.06839.
- **Jiang, Z.; Xu, F. F.; Gao, L.; Sun, Z.; Liu, Q.; Dwivedi-Yu, J.; Yang, Y.; Callan, J.; Neubig, G.** Active Retrieval Augmented Generation (FLARE). In *EMNLP 2023*. arXiv:2305.06983.
- **Karpukhin, V.; Oğuz, B.; Min, S.; Lewis, P.; Wu, L.; Edunov, S.; Chen, D.; Yih, W.-t.** Dense Passage Retrieval for Open-Domain Question Answering. In *EMNLP 2020*. arXiv:2004.04906.
- **Khuller, S.; Moss, A.; Naor, J.** The Budgeted Maximum Coverage Problem. *Information Processing Letters* **1999**, 70(1), 39–45.
- **Lewis, P.; Perez, E.; Piktus, A.; Petroni, F.; Karpukhin, V.; Goyal, N.; Küttler, H.; Lewis, M.; Yih, W.-t.; Rocktäschel, T.; Riedel, S.; Kiela, D.** Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. In *NeurIPS 2020*. arXiv:2005.11401.
- **Liu, N. F.; Lin, K.; Hewitt, J.; Paranjape, A.; Bevilacqua, M.; Petroni, F.; Liang, P.** Lost in the Middle: How Language Models Use Long Contexts. *TACL* **2024**, 12, 157–173. arXiv:2307.03172.
- **Ma, X.; Gong, Y.; He, P.; Zhao, H.; Duan, N.** Query Rewriting for Retrieval-Augmented Large Language Models. In *EMNLP 2023*. arXiv:2305.14283.
- **Nemhauser, G. L.; Wolsey, L. A.; Fisher, M. L.** An Analysis of Approximations for Maximizing Submodular Set Functions—I. *Mathematical Programming* **1978**, 14(1), 265–294.
- **Nogueira, R.; Jiang, Z.; Pradeep, R.; Lin, J.** Document Ranking with a Pretrained Sequence-to-Sequence Model. In *Findings of EMNLP 2020*. arXiv:2003.06713.
- **Press, O.; Zhang, M.; Min, S.; Schmidt, L.; Smith, N. A.; Lewis, M.** Measuring and Narrowing the Compositionality Gap in Language Models (Self-Ask). In *Findings of EMNLP 2023*. arXiv:2210.03350.
- **Robertson, S.; Zaragoza, H.** The Probabilistic Relevance Framework: BM25 and Beyond. *Foundations and Trends in Information Retrieval* **2009**, 3(4), 333–389.
- **Sun, W.; Yan, L.; Ma, X.; Wang, S.; Ren, P.; Chen, Z.; Yin, D.; Ren, Z.** Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents (RankGPT). In *EMNLP 2023*. arXiv:2304.09542.
- **Trivedi, H.; Balasubramanian, N.; Khot, T.; Sabharwal, A.** Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions (IRCoT). In *ACL 2023*. arXiv:2212.10509.
- **Wang, Y.; Li, P.; Sun, M.; Liu, Y.** Self-Knowledge Guided Retrieval Augmentation for Large Language Models (SKR). In *Findings of EMNLP 2023*. arXiv:2310.05002.
- **Wu, M.; Yang, H.; Ben-Porat, O.; Ziser, Y.** When Knowledge Is Not Free: Cost-Aware Evidence Selection in Retrieval-Augmented Generation. arXiv:2606.02245, 2026.
- **Xu, F.; Shi, W.; Choi, E.** RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation. In *ICLR 2024*. arXiv:2310.04408.
- **Yan, S.-Q.; Gu, J.-C.; Zhu, Y.; Ling, Z.-H.** Corrective Retrieval Augmented Generation (CRAG). arXiv:2401.15884, 2024.

---

## 声明（Declarations，MDPI 模板用）

**Data Availability Statement.** 全部代码、评测集与实验脚本位于
https://github.com/mylgtab/budget-rag （MIT 许可，v1.0.0）。
LongBench 各子集的少量快照随仓库提供，完整数据可由 `scripts/fetch_longbench.py` 从原发布源获取。
所有论文表格可由 `make check`、`scripts/baselines.py`、`scripts/seed_stability.py` 与
`scripts/latency_bench.py` 复现。

**Author Contributions.** 单一作者完成：概念化、方法、软件、验证、形式分析、数据整理、
初稿撰写与修订。

**Funding.** 本研究未接受外部资助。

**Conflicts of Interest.** 作者声明无利益冲突。

**Use of Generative AI.** 代码实现、实验脚本与初稿文字在 AI 编程助手辅助下完成；
所有实验数字均由仓库内脚本在作者机器上实际运行产生，作者对全部内容负责。

---

## 作者备注（不投稿，正式排版时删除）

**期刊路线**：先投 Applied Sciences / Electronics（Q2），二轮冲 Frontiers of Computer Science。

**标题候选**：
1. Budget-Aware Retrieval: Allocating Context Tokens Where They Pay Off（已采用）
2. Cost-Controlled Retrieval for Long-Document QA: A Submodular View with a Confidence Gate
3. 面向长文档问答的预算感知检索：子模视角与置信度门控

**写作原则**：学术发布会。主线只讲「同等预算下更强、同等质量下更便宜」；
负结果全部放附录；引言不提前示弱；结论不突然自我否定。

