# -*- coding: utf-8 -*-
"""Crossref lookups for the bibliography; dump compact JSON."""
import io, json, time, urllib.parse, urllib.request, difflib

PROXY = "http://127.0.0.1:7890"
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
)
opener.addheaders = [("User-Agent", "bibliography-check/1.0 (mailto:author@example.org)")]

TITLES = [
 "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
 "The Probabilistic Relevance Framework: BM25 and Beyond",
 "Dense Passage Retrieval for Open-Domain Question Answering",
 "Lost in the Middle: How Language Models Use Long Contexts",
 "Active Retrieval Augmented Generation",
 "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection",
 "Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity",
 "Corrective Retrieval Augmented Generation",
 "LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models",
 "LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression",
 "RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation",
 "Precise Zero-Shot Dense Retrieval without Relevance Labels",
 "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance",
 "An analysis of approximations for maximizing submodular set functions",
 "The budgeted maximum coverage problem",
 "Self-Knowledge Guided Retrieval Augmentation for Large Language Models",
 "Measuring and Narrowing the Compositionality Gap in Language Models",
 "Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions",
 "Document Ranking with a Pretrained Sequence-to-Sequence Model",
 "Is ChatGPT Good at Search? Investigating Large Language Models as Re-Ranking Agents",
 "Rewrite-Retrieve-Read: Query Rewriting for Retrieval-Augmented Large Language Models",
 "The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries",
 "A Class of Submodular Functions for Document Summarization",
]
SELECT = "DOI,title,container-title,issued,author,page,volume,type,publisher"

def q(params):
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    with opener.open(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

out = []
for t in TITLES:
    rec = {"q": t}
    try:
        d = q({"query.bibliographic": t, "rows": 3, "select": SELECT})
        items = d["message"]["items"]
        best = None
        for it in items:
            tt = (it.get("title") or [""])[0]
            sim = difflib.SequenceMatcher(None, t.lower(), tt.lower()).ratio()
            if best is None or sim > best[0]:
                best = (sim, it)
        if best:
            sim, it = best
            rec.update({
                "sim": round(sim, 3),
                "title": (it.get("title") or [""])[0],
                "container": (it.get("container-title") or [""])[0],
                "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
                "doi": it.get("DOI"),
                "volume": it.get("volume"),
                "page": it.get("page"),
                "type": it.get("type"),
                "authors": [
                    (a.get("family") or "") + " " + (a.get("given") or "")
                    for a in (it.get("author") or [])[:6]
                ],
            })
    except Exception as e:
        rec["error"] = repr(e)[:160]
    out.append(rec)
    time.sleep(0.4)

cn = []
for cnq in [
    {"query.bibliographic": "检索增强生成", "query.container-title": "软件学报", "rows": 5},
    {"query.bibliographic": "检索增强生成", "query.container-title": "计算机学报", "rows": 5},
    {"query.bibliographic": "检索增强生成", "query.container-title": "计算机研究与发展", "rows": 5},
    {"query.bibliographic": "大语言模型 检索增强 综述", "query.container-title": "中文信息学报", "rows": 5},
]:
    try:
        d = q(dict(cnq, select=SELECT))
        for it in d["message"]["items"]:
            cn.append({
                "q": cnq["query.container-title"],
                "title": (it.get("title") or [""])[0],
                "container": (it.get("container-title") or [""])[0],
                "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
                "doi": it.get("DOI"),
                "volume": it.get("volume"),
                "page": it.get("page"),
                "authors": [(a.get("family") or "") for a in (it.get("author") or [])[:4]],
            })
    except Exception as e:
        cn.append({"q": cnq["query.container-title"], "error": repr(e)[:120]})
    time.sleep(0.4)

io.open("docs/.xref_raw.json", "w", encoding="utf-8").write(
    json.dumps({"en": out, "cn": cn}, ensure_ascii=False, indent=1))
ok = sum(1 for r in out if r.get("sim", 0) >= 0.85)
print("matched", ok, "/", len(out), "cn", len(cn))
