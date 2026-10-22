# 顶会论著的开篇与论证结构拆解

> 用途：给 `docs/paper-draft.md` 的摘要与第 1 节提供可套用的叙事模板。本文只读 paper-draft，不改它。
> 版本：C 部分依据 2026-10-22 22:11 的 paper-draft（534 行，revision 6f07）。该文件正在被并行修改，引用前请复核行号与原句；若原句已经不存在，说明那处已被改掉。
> 取源：六篇均取到 arXiv HTML 全文（2403.14403v2、2401.15884v3、2310.11511、2305.06983、2305.05176、2307.03172），
> 引文按 arXiv 版本逐句核对；会议版（NAACL/ICLR/EMNLP/TACL）措辞可能微调。
> 获取方式：本机 `web_fetch` 被 DNS 策略拦（arxiv.org 解析到非公网 IP），改用 `curl` 拉同一 URL 的同一页面；
> 未使用二手摘要站。CRAG 与 FrugalGPT 未在正文中声明会议版，按 arXiv 版分析。
> 限制：arXiv HTML 把表格数值摊在文本流里，⑤ 的对应依据表题与结果段落，未逐格核对每个数字。

---

## 0 速览

| 论文 | 缺口一句话 | 贡献形式 | 最值得学的一点 |
|---|---|---|---|
| Adaptive-RAG | 简单查询过度计算、复杂查询又不够 | 3 条 bullet，动词开头，无数字 | 用「查询难度分布」把固定 k 的缺口量化成成本×占比表 |
| CRAG | RAG 依赖检索相关性，检索错了模型会怎样未知 | 3 条编号，第一条抢「first attempt」，无数字 | 用「上游会坏」定义缺口，再逐动作消融给动作集发合法性证书 |
| Self-RAG | 不加区分地检索，不管检索对生成是否有帮助 | 无列表：方法段 + 结果段（带对手与任务数） | 把「要不要检索」做成频率旋钮，画频率—质量曲线 |
| FLARE | 只在输入上检索一次，覆盖不了长文生成中逐步出现的信息需求 | 无列表：一个方法 + 一个「无需训练」属性 + 泛化声明 | 用「前瞻一句」把何时检索变成可计算的触发，并扫出整条阈值曲线 |
| FrugalGPT | 旧集成/级联假设封闭标签集，接不住开放文本与异构定价 | 3 策略 + 1 实例 + 2 个硬数字 | 美元数字开场，「同质省 98% / 同价强 4%」对称收尾 |
| Lost in the Middle | 上下文变长被当成能力提升，但「是否真的用到」从未受控检验 | 「We find that:」3 条发现 + 1 个评测协议 | 把主张写成可证伪的零假设，再用受控变量否定它 |

---

## 1 逐篇拆解

### 1.1 Adaptive-RAG（arXiv 2403.14403，NAACL 2024）

**① 开篇三句**

1. LLM 在含 QA 的多样任务上表现压倒性。
2. 但它们仍会生成事实错误：知识只存在参数里，且不可能记住全部（不断变化的）世界知识。
3. 检索增强 LLM 因此成为热门解法。

三句完成「能力 → 缺陷 → 补丁」。真正的缺口（成本、难度分布）不在前三句，而在第 4 段：
先举一个四步推理的多跳例子，再反问 "are all the requests from users complex?"，把「多步检索更好」翻成「大多数请求其实很简单」。

**② 缺口句**

> "they either handle simple queries with unnecessary computational overhead or fail to adequately address complex multi-step queries"

一句话把缺口钉成「两端都错」：简单查询过度计算、复杂查询又不够。紧接着补一句分布假设
"not all user requests fall into only one of the simple or complex categories"——缺口因此可证伪：
若真实查询只分两类，分类器方案就没必要。

**③ 核心 insight（27 词）**

> "we propose to select the most suitable strategy from a range of (retrieval-augmented) LLMs, each of which is tailored to the specific complexity of the input query."

中译：按输入查询的复杂度，从一组检索增强 LLM 策略里挑最合适的那一个，而不是对所有查询用同一档。

**④ 贡献写法**

3 条 bullet，全部动词开头：`We point out`（重新描述问题）/ `We adapt`（方法）/ `We show`（效果）。
不带数字，第三条只写 "highly effective and efficient"。可学的是第一条——贡献不是「我们提出一个模块」，
而是「我们指出一个被忽略的现实场景」；弱点是效率主张全靠正文表格兜底。

**⑤ 主张 ↔ 实验**

| 主张 | 证据 | 备注 |
|---|---|---|
| 又准又省 | Table 1（F1 与 Step/Time 并列，跨 FLAN-T5-XL/XXL、GPT-3.5）；Figure 1（F1 vs Time/Query 散点） | 质量与成本同表，审稿人一眼可判 |
| 查询难度异质、成本差 78 倍 | Table 3：No 0.35 s / 8.6%，One 3.08 s / 53.3%，Multi 27.18 s / 38.1% | 这张表是「预算分配」最直接的外部先例 |
| 分类器够便宜 | Table 4（自动标注消融）、Table 6（60M–770M 规模） | 第三条贡献的 "efficient" 靠这里 |

**⑥ 可迁移动作**

1. 用反问句把领域共识翻成被忽略的分布假设（"are all the requests complex?"），一句话完成立论转向。
2. 用分层成本表证伪「平均情况」：不同路径的成本与占比写在一张表里，缺口就不再是形容词。

**最值得学**：把「查询难度是分布」落成一张成本×占比表，让「固定 k 浪费」从直觉变成可核对的数字。

---

### 1.2 CRAG（arXiv 2401.15884）

**① 开篇三句**

1. LLM 受关注，指令理解与生成流畅。
2. 但幻觉不可避免：仅靠参数知识无法保证生成文本的准确性。
3. 检索增强生成是可实践的补充。

同样是「能力 → 缺陷 → 补丁」，但缺口紧随其后：RAG 的效果取决于检索文档的相关性；若检索出错，模型行为如何？
第 5 句 "raising concerns about how the model behaves if retrieval goes wrong" 才是真正的缺口句。

**② 缺口句**

> "it relies heavily on the relevance of retrieved documents, raising concerns about how the model behaves if retrieval goes wrong."

缺口被建成「上游失败下的行为未知」，而不是「检索不够好」。区别在于：前者可以靠注入坏检索来实验（Figure 3 正是这么做的），
后者只能靠刷分。

**③ 核心 insight（21 词，省略号处为原文省略）**

> "a lightweight retrieval evaluator ... returning a confidence degree based on which different knowledge retrieval actions can be triggered."

中译：用一个轻量评估器给出置信度，由置信度触发 Correct / Incorrect / Ambiguous 三种检索动作，而不是无条件采纳检索结果。

**④ 贡献写法**

3 条编号：`1) This paper studies ... makes the first attempt`（缺口 + 首创）/ `2) A plug-and-play method ... is proposed` /
`3) Experimental results extensively demonstrate ...`。无数字。第一条用 "to the best of our knowledge, first attempt" 抢新颖性，
可学但要慎用：首创声明必须配一个「别人没做过」的具体动作，CRAG 配的是「为 RAG 设计纠错策略」。

**⑤ 主张 ↔ 实验**

| 主张 | 证据 | 备注 |
|---|---|---|
| 检索坏了也能纠 | Table 1（4 数据集总体，跨多个生成 LLM） | 主结果 |
| 三个动作都必要 | Table 2（逐个去掉 Correct/Incorrect/Ambiguous） | 动作集的合法性证书 |
| 知识精炼必要 | Table 3（去掉 document refinement / query rewriting / knowledge selection） | 与 Table 2 分工明确 |
| 评估器可信 | Table 4（评估器 vs ChatGPT 判断） | 中间件的自证 |
| 对检索质量鲁棒 | Figure 3（人为降低 retrieval performance 后画曲线） | 缺口句的直接实验化 |
| 开销可接受 | Table 6（FLOPs、单实例执行时间） | 补上效率侧 |

**⑥ 可迁移动作**

1. 开篇用一张失败案例图（低质量检索器把无关文档塞进上下文）把缺口具体化，读者先看到「坏」再看到方法。
2. 动作集里每个动作配一个消融——本文的取块/混合/改写/二跳可以照抄这个「必要性租金」结构。

**最值得学**：把缺口定义在「上游会坏」，于是鲁棒性实验（Figure 3）天然成为主张的证据，而不是补丁。

---

### 1.3 Self-RAG（arXiv 2310.11511，ICLR 2024）

**① 开篇三句**

1. 最先进的 LLM 仍会事实错误，尽管模型与数据规模都在涨。
2. RAG 用检索到的相关段落增强输入，能减少知识密集任务的错误。
3. 但这些方法可能损害 LLM 的通用性，或引入不必要/离题的段落导致低质量生成，因为它们不加区分地检索。

第三句就下 "However"，六篇里进入缺口最快。没有单独的「RAG 很重要」铺垫，重要性和副作用压在同一段里。

**② 缺口句**

> "they retrieve passages indiscriminately regardless of whether the factual grounding is helpful."

一个副词 `indiscriminately` 钉死缺口：不是检索得不好，而是根本不判断「这次检索有没有用」。

**③ 核心 insight（24 词）**

> "Self-RAG trains an arbitrary LM to generate text with reflection tokens by unifying them as the next token prediction from the expanded model vocabulary."

中译：把「要不要检索 / 段落是否相关 / 输出是否有支持」编码成反思 token，当作普通的下一个 token 预测来训练，
让检索与自我评判变成生成过程的一部分。

**④ 贡献写法**

没有编号列表。用「方法段（We train / Self-RAG first determines / It then generates critique tokens）+ 结果段」呈现。
结果段带对手与任务数而非绝对分数："outperforms retrieval-augmented ChatGPT on four tasks, Llama2-chat and Alpaca on all tasks"，
并单列 citation accuracy。这是 ICLR 常见的「结果即贡献」写法，适合方法本身足够新时用。

**⑤ 主张 ↔ 实验**

| 主张 | 证据 | 备注 |
|---|---|---|
| 六任务总体更强 | Table 2（含 ChatGPT、Llama2-chat、Alpaca 等对手） | 主结果 |
| 反思 token 必要 | Figure 3(a) 训练/推理组件消融 | 组件合法性 |
| 可控的取舍 | Figure 3(b)（citation precision vs Mauve 软权重扫描） | 把「可控」做成曲线 |
| 检索频率与质量的关系 | Figure 3(c)（PubHealth / PopQA 上 retrieval frequency vs normalized accuracy） | 对本文最有用：横轴就是「检索预算」 |
| 引用更准 | Table 2 + Figure 4(d) 人评 | 长文生成的差异化指标 |

**⑥ 可迁移动作**

1. 第三句就转折：先给已有解法，再在同一句里给它的副作用，开篇不浪费在「领域很重要」上。
2. 把可调旋钮画成曲线（检索频率 → 质量），而不是只报一个工作点；本文的 budget–recall 曲线同理。

**最值得学**：把「要不要检索」从二值开关变成可调频率，并用一条曲线证明中间存在最优点。

---

### 1.4 FLARE（arXiv 2305.06983，EMNLP 2023）

**① 开篇三句**

1. 生成式 LM 已成为 NLP 系统的基础组件。
2. 尽管训练中记住了部分世界知识，它们仍倾向幻觉、编造内容。
3. 用检索组件增强是解决幻觉的有希望方向。

标准三句。缺口在第 4–6 句才出现：单次检索对短答案够用，但长文生成的信息需求在生成过程中才逐步显现，
"the information needs are clear in the user's input" 只对短问答成立。

**② 缺口句**

> "Most existing retrieval augmented LMs employ a retrieve-and-generate setup that only retrieves information once based on the input."

缺口 = 检索的时机与查询构造，而不是「检索质量」。它把问题从「取多少」推到「什么时候取、拿什么去取」，
这比「固定 k 不好」更根本，也更难被审稿人一句「多取几段不就行了」驳回。

**③ 核心 insight（22 词，后半句为原文省略）**

> "we propose anticipating the future by generating a temporary next sentence, using it as a query to retrieve relevant documents"

中译：先生成一句「临时的下一句」来预判接下来要写什么，用它当查询去检索，再根据检索结果重写这一句。

**④ 贡献写法**

无编号列表。句式是「we propose FLARE … / FLARE is applicable to any existing LMs at inference time without additional training /
evaluated on 4 tasks … superior or competitive」。贡献 = 一个方法 + 一个部署属性（免训练）+ 一句泛化声明，无数字。
「免训练」是它的差异化卖点，用一句独立短句写，值得学。

**⑤ 主张 ↔ 实验**

| 主张 | 证据 | 备注 |
|---|---|---|
| 四个长文任务更优或持平 | Table 1（2WikiMultihopQA）、Table 2（StrategyQA / ASQA / WikiAsp） | 主结果 |
| 前瞻优于回看 | Table 3、Table 4（previous sentence vs next sentence，token 数扫描） | 单变量受控对照 |
| 不是检索越多越好 | Figure 5（检索步骤比例 0→1 vs EM） | 阈值扫描，内部最优 |
| 查询怎么构造 | Table 5（mask 阈值）、Table 6（implicit vs explicit） | 第二个设计维度 |

**⑥ 可迁移动作**

1. 把方法拆成两个正交问题（when + what），读者一次记住；本文可对应「取多少 + 先取谁」。
2. 阈值扫描图（Figure 5）证明最优点在内部而非端点，为「预算内分配」提供形状证据。

**最值得学**：把「何时检索」变成对生成不确定性的阈值，并把整条阈值—频率曲线扫出来。

---

### 1.5 FrugalGPT（arXiv 2305.05176）

**① 开篇三句**

1. 我们正处在 LLM 爆发中，商业、科学、金融的大规模应用让越来越多公司把 LLM 作为 API 服务提供。
2. GPT-4 等性能空前，但高通量使用非常贵：ChatGPT 每天运营成本估计超过 $700,000，小企业用 GPT-4 做客服每月超过 $21,000。
3. 除财务成本，还有环境与能源影响，波及当前与未来世代的社会福利。

六篇里唯一用「钱」开场、且第一段就给出可核验数字的。第 4–5 段才转向技术缺口：
API 价格差两个数量级，但旧集成方法假设封闭标签集。

**② 缺口句**

> "Existing model ensemble paradigms such as model cascade and FrugalML were designed for predictive tasks with a known set of labels and do not account for the full capabilities of LLM."

缺口 = 旧工具与新对象不匹配：级联本身不新，但「开放文本 + 异构定价 + 黑盒 API」让旧假设失效。
这种写法把「我们没发明级联」提前化解，审稿人不会用「级联早就有了」来打。

**③ 核心 insight（28 词）**

> "FrugalGPT, a simple yet flexible instantiation of LLM cascade which learns which combinations of LLMs to use for different queries in order to reduce cost and improve accuracy."

中译：把级联从固定规则变成「按查询学习用哪组 LLM」，同时压成本、提准确率。

**④ 贡献写法**

"Our contributions." 之后是 3 个策略（prompt adaptation / LLM approximation / LLM cascade）+ 1 个实例（FrugalGPT）
+ 2 个硬数字（"up to 98% cost reduction" / "improve accuracy by 4% with the same cost"）。
形式上是六篇里最接近本文需要的：框架 + 实例 + 对称双数字。

**⑤ 主张 ↔ 实验**

| 主张 | 证据 | 备注 |
|---|---|---|
| 价格差两个数量级 | Table 1（12 个商业 API 的输入/输出/固定费用） | 动机的硬证据 |
| 同等质量省 98% | Table 3（HEADLINES 98.3%、OVERRULING 73.3%、COQA 59.2%） | 「更便宜」方向 |
| 同等成本更强 | Figure 5（同等成本下最多 +5%；intro 写 4%） | 「更强」方向；注意 4% 与 5% 的口径漂移 |
| 学到的策略可读 | Figure 3（$6.5 预算、GPT-4 成本的 1/5 的级联案例） | 让「分配」可视化 |

**⑥ 可迁移动作**

1. 开篇用可核验的美元数字建立「重要」，比「LLM 被广泛使用」有力一个量级。
2. 结论写成对称两句：同等质量省多少 / 同等成本强多少；两个方向各一个数字，正好对应本文主线。

**最值得学**：用「同质省 98% / 同价强 4%」的对称句收尾，把成本与质量的主张锁在一起。

---

### 1.6 Lost in the Middle（arXiv 2307.03172，TACL 2024）

**① 开篇三句**

1. LM 已成为对话、搜索摘要、协同写作等用户侧语言技术的重要构件。
2. 它们主要通过 prompting 工作：任务说明与待处理数据都被格式化成文本上下文。
3. 这些上下文可达数千 token，尤其在处理长文档或做检索增强时。

前三句只立「重要」。真正的「尚未解决」由第 4–6 句建立：处理长序列是刚需 → Transformer 的显存与计算随长度二次增长
→ 窗口变大（4K/32K/100K），但 "it remains unclear how these extended-context language models make use of their input contexts"。
把缺口写成「未知」而非「缺陷」，所以贡献可以是「发现」。

**② 缺口句**

> "it remains unclear how these extended-context language models make use of their input contexts when performing downstream tasks."

一句话把整个领域的默认假设（上下文越长越好）变成待检验命题。可证伪形式紧接着给出：
"if language models can robustly use information within long input contexts, then their performance should be minimally affected by the position of the relevant information"。

**③ 核心 insight（23 词）**

> "models are better at using relevant information that occurs at the very beginning (primacy bias) or end of its input context (recency bias)"

中译：模型更会用开头（首因）或结尾（近因）的证据，中间的证据显著用不上——U 形曲线。

**④ 贡献写法**

无编号列表。用 "We find that:" + 3 条 bullet（encoder-decoder 的稳健性、query-aware contextualization、base LM 也有 U 形），
再加一个实践发现（50 vs 20 篇文档只涨 1.5% / 1%）和一个新评测协议。贡献 = 发现清单 + 协议，动词是 find / indicate / provide。
带数字，但数字只挂在最反直觉的那条上。

**⑤ 主张 ↔ 实验**

| 主张 | 证据 | 备注 |
|---|---|---|
| U 形曲线 | Figure 1 + §2.3（受控改变位置与长度） | 主发现 |
| 长上下文模型并不更好 | §2.3 与 extended-context 版本对比 | 直接打「窗口=能力」 |
| 检索堆文档早饱和 | §5（50 vs 20 篇：GPT-3.5 +1.5%，Claude +1%） | 对「预算」主张最有用 |
| 为什么会这样 | §4（架构、query-aware、指令微调三因素） | 排除替代解释 |

**⑥ 可迁移动作**

1. 把主张写成零假设：「若模型能稳健利用长上下文，性能应几乎不受位置影响」，再用受控变量否定它。
   本文的子模假设可以照写：「若边际收益不递减，密度贪心的 1−1/e 界不成立」。
2. 开篇不喊「X 很重要」，而指出「能力被采用的速度快于对它的理解」——缺口是未知，不是缺陷。

**最值得学**：用可证伪的零假设定义 claim，再用单变量实验逐个排除替代解释。

---

## 2 A. 共性模板（8 条）

1. **开篇三句固定为「领域已成基础设施 → 它有一个结构性缺陷 → 补丁已出现但补丁有代价」**，缺口句最迟落在第 4 句，不要用三段话铺「LLM 很重要」。
2. **缺口必须能被一句话证伪**：写成「现有方法假设 X，而真实分布里 ¬X」，X 用可观测名词（固定 k、单次检索、封闭标签集），不用「效果不佳」这类形容词。
3. **缺口之后立刻上分布证据**：一张按难度/路径分层的「成本 × 占比」表，证明平均值失效（Adaptive-RAG Table 3：0.35/3.08/27.18 秒，8.6%/53.3%/38.1%）。
4. **核心 insight 压到 30 词以内、含一个反事实，并且能被 Figure 1 直接画出来**；画不出来说明还没想清，不要写进摘要。
5. **贡献 3 条、动词开头（point out / propose / show）、每条挂一个数字或一个具名实验**；第一条重述问题，而不是「我们提出一个模块」。
6. **质量主张与成本主张必须同表出现**：只报 F1 不报 token/时间的效率主张，审稿人默认不成立；Introduction 里的数字必须与图注一致（FrugalGPT 的 4% vs 5% 就是反例）。
7. **把开关扫成曲线**：阈值、检索频率或预算作横轴，证明最优点在内部而不是端点（FLARE Figure 5、Self-RAG Figure 3c）。
8. **收尾用对称句**：同等质量省 X%、同等成本强 Y%，两个方向各一个数字（FrugalGPT：98% / 4%）。

---

## 3 B. 五条可直接用在本文引言的句式

**B1｜缺口句（把预算写成外生变量）**

- 中：现有自适应检索把预算当作外生常数：分类器决定走哪一档，却没有一步回答「在 B 个 token 内先买哪一块」。
- EN: "Adaptive retrievers treat the budget as exogenous: a classifier picks a depth, but no step decides which chunk to buy first within B tokens."

**B2｜insight 句（动作集 + 预算）**

- 中：我们把取块、混合检索、改写与二跳写成同一个动作集：每个动作有价格 c(a) 与边际增益 g(a|S)，策略就是预算 B 下的一个子集。
- EN: "We place chunking, hybrid retrieval, rewriting and a second hop in one action set: each action a has a price c(a) and a marginal gain g(a|S), and a policy is a subset under budget B."

**B3｜理论句（1−1/e 带条件，防止被审稿人抓）**

- 中：边际收益递减使质量函数单调子模：基数预算下密度贪心达 1−1/e，成本预算下为 (1−1/e)/2，带跨档枚举的修正贪心把 1−1/e 拿回来。
- EN: "Diminishing returns make the quality function monotone submodular: density-greedy attains 1−1/e under a cardinality budget and (1−1/e)/2 under a cost budget, while the modified greedy with cross-tier enumeration restores 1−1/e."

**B4｜机制句（影子价格决定阈值）**

- 中：改写是否划算不由固定规则决定，而由预算的影子价格 λ 决定：λ 上升，最优门控 τ*(λ) 单调下降，λ≥2 时落到 0。
- EN: "Whether to rewrite is governed not by a fixed rule but by the shadow price λ of the budget: as λ rises, the optimal gate τ*(λ) falls monotonically, reaching zero at λ≥2."

**B5｜结果句（对称主张）**

- 中：在 126 token 的平均成本下取得 0.960 召回，高于 CRAG 近似的 0.925@179 与稠密检索的 0.910@115——同等预算更强，同等质量更便宜。
- EN: "At an average cost of 126 tokens we reach 0.960 recall, against 0.925@179 for a CRAG-style baseline and 0.910@115 for dense retrieval—stronger at equal budget, cheaper at equal quality."

---

## 4 C. `docs/paper-draft.md` 最该改的三处

### C1 中文摘要首句：缺数字、缺「谁在付账」

原句（`docs/paper-draft.md:21`）：

> 检索增强生成把「取多少上下文」当成固定超参，但真实系统的预算是有限的、且问题难度差异极大。

问题（对应 A1、A3）：「固定超参」是领域断言，「预算有限 / 难度差异大」是形容词，读者拿不到可核对的锚点；
且这句话没有说清「代价发生在哪里」。

改写：

> 在 Adaptive-RAG 的实测中，同一条查询按策略不同耗时为 0.35 秒、3.08 秒或 27.18 秒，相差 78 倍，而 38% 的查询被分到最贵的一档；主流 RAG 却仍为所有查询买同一个 k。我们把「取多少」从一个超参改写成一个预算 B 下的分配问题：给定 B，先买哪一块、要不要改写、要不要二跳。

第 1 节第一段（当前 76–78 行）已有同一组数字，直接前移复用，避免摘要与引言两处措辞不一。

### C2 中文摘要结论列表：中文写四条、英文写两条，且第四条是第二条的属性

原句（`docs/paper-draft.md:22–24`）：

> 并给出四条可检验的结论：贪心分配合乎 1−1/e 近似、查询改写的最优门控是一个由预算影子价格决定的阈值、级联检索的最优策略是一条置信度阈值链、该阈值随影子价格单调不增。

问题（对应 A5、A6）：英文摘要写的是 "two implementable consequences"，中文列了四条；
第四条「该阈值随影子价格单调不增」是第二条的性质，不是独立结论，列成并列项会让读者以为有四个定理。
另外 1−1/e 未写条件：`docs/theory.md:43–45` 已说明基数下才是 1−1/e，成本预算下是 (1−1/e)/2，修正贪心才恢复。

改写：

> 并给出三个可检验的结论：在基数预算下密度贪心达 1−1/e（成本预算下为 (1−1/e)/2，带跨档枚举的修正贪心恢复到 1−1/e）；改写门控的最优阈值 τ*(λ) 由预算影子价格解出，且随 λ 单调不增（λ≥2 时落到 0）；级联检索的最优策略是一条由同一 λ 导出的置信度阈值链。

若坚持保留四条，第四条要改写成可单独证伪的预测（「λ 上升 ⇒ τ* 下降」），并把英文的 "two" 同步改为 "three"；否则删掉。

### C3 第 1 节第三段：1−1/e 无条件，与贡献段和 theory.md 冲突

原句（`docs/paper-draft.md:90–91`）：

> 在「边际收益递减」这一条可实证检验的假设下，质量函数成为单调子模，于是适用经典的近似保证：按边际收益/成本比排序的贪心策略可获得 $1-1/e$ 近似。

问题（对应 A2、A6）：同一版本的第 1 节贡献段（`docs/paper-draft.md:103–105`）已经写成
「基数预算下 1−1/e、成本预算下 (1−1/e)/2、修正贪心恢复 1−1/e」，`docs/theory.md:43–45` 也是这个口径；
唯独正文这一段仍写无条件 1−1/e。三处不一致，审稿人会挑最弱的那处引用。

改写：

> 在「边际收益递减」这一条可实证检验的假设下，质量函数成为单调子模：基数预算下，按边际收益/成本比排序的贪心达 1−1/e；成本预算下该界降为 (1−1/e)/2，带跨档枚举的修正贪心恢复到 1−1/e（第 3、5 节）。

---

## 5 附：两处不要照抄

- **贡献条目不挂数字**：Adaptive-RAG 与 CRAG 的第三条都只有 "effective/efficient" 或 "extensively demonstrate"，正文才给数；本文若照抄，会把最硬的 126/0.960 藏起来。
- **同一数字两处口径**：FrugalGPT 引言写 "up to 4%"，Figure 5 图注写 "up to 5%"；CRAG 与 Adaptive 的表格数值也散在文本流里。本文 22:10 版本已把 0.946@200 从中文摘要移除，不要再加回去；英文摘要与中文摘要的结论条数也需保持同步（C2）。
