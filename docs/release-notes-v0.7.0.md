## 亮点

- **忠实度**：100 条中 94% 有原文依据、3% 编造；「答对但无依据」0 条
- **英文子集**：LongBench passage_retrieval_en 上 BM25 与向量均 1.000（天花板效应，照实记录）
- **成本更准**：embedding 真实用量计入成本，`trace.embed_tokens` 可查
- **演示页面**：启动服务后访问 `/ui/`，输入问题即可看到答案、路径、成本与耗时
- **缓存版本化**：改缓存结构或 prompt 后旧条目自动失效

## 试用

```bash
pip install -r requirements.txt
PYTHONPATH=src uvicorn budget_rag.api:app --port 8000
# 浏览器打开 http://127.0.0.1:8000/ui/
```