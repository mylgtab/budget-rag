# -*- coding: utf-8 -*-
"""Query dblp for the 25 bibliography entries; dump candidates to JSON."""
import io, json, time, urllib.parse, urllib.request

PROXY = "http://127.0.0.1:7890"
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
)
opener.addheaders = [("User-Agent", "Mozilla/5.0 (bibliography-check)")]

QUERIES = [
    "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
    "The Probabilistic Relevance Framework BM25 and Beyond",
    "Dense Passage Retrieval for Open-Domain Question Answering",
    "Lost in the Middle How Language Models Use Long Contexts",
    "Active Retrieval Augmented Generation",
    "Self-RAG Learning to Retrieve Generate and Critique",
    "Adaptive-RAG Learning to Adapt Retrieval-Augmented Large Language Models",
    "Corrective Retrieval Augmented Generation",
    "LLMLingua Compressing Prompts for Accelerated Inference",
    "LongLLMLingua Accelerating and Enhancing LLMs in Long Context",
    "RECOMP Improving Retrieval-Augmented LMs with Compression",
    "Precise Zero-Shot Dense Retrieval without Relevance Labels",
    "FrugalGPT How to Use Large Language Models While Reducing Cost",
    "An analysis of approximations for maximizing submodular set functions",
    "The budgeted maximum coverage problem",
    "Self-Knowledge Guided Retrieval Augmentation",
    "Measuring and Narrowing the Compositionality Gap in Language Models",
    "Interleaving Retrieval with Chain-of-Thought Reasoning",
    "Document Ranking with a Pretrained Sequence-to-Sequence Model",
    "Is ChatGPT Good at Search",
    "Rewrite-Retrieve-Read Query Rewriting for Retrieval-Augmented",
    "The Use of MMR Diversity-Based Reranking for Reordering Documents",
    "A Class of Submodular Functions for Document Summarization",
    "Sequential Analysis Wald",
    "Cost-Aware Retrieval-Augmented Generation",
]

out = []
for q in QUERIES:
    url = ("https://dblp.org/search/publ/api?q=" + urllib.parse.quote(q)
           + "&format=json&h=4")
    rec = {"q": q, "hits": []}
    try:
        with opener.open(url, timeout=25) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        hits = data.get("result", {}).get("hits", {}).get("hit", [])
        for h in hits:
            i = h.get("info", {})
            rec["hits"].append({
                "title": i.get("title"),
                "venue": i.get("venue"),
                "year": i.get("year"),
                "type": i.get("type"),
                "volume": i.get("volume"),
                "pages": i.get("pages"),
                "doi": i.get("doi"),
                "ee": i.get("ee"),
                "key": i.get("key"),
            })
    except Exception as e:
        rec["error"] = repr(e)[:200]
    out.append(rec)
    time.sleep(1.2)

io.open("docs/.dblp_raw.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("done", sum(1 for r in out if r.get("hits")), "/", len(out))
