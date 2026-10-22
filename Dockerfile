FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 依赖先装，利用层缓存
COPY requirements.txt requirements.lock ./
RUN pip install --no-cache-dir -r requirements.txt

# 只拷运行所需内容（大文件由 .dockerignore 排除）
COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY data/sample_docs ./data/sample_docs
COPY data/eval_set.jsonl data/eval_500.jsonl ./data/

RUN pip install --no-cache-dir -e . && \
    python scripts/ingest.py --docs data/sample_docs

# 非 root 运行
RUN useradd -m -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"

CMD ["uvicorn", "budget_rag.api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
