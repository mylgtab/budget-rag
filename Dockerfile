FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY scripts ./scripts
COPY data ./data

# 构建索引（离线哈希 embedding，不需要任何 key）
RUN python scripts/ingest.py --docs data/sample_docs

EXPOSE 8000
CMD ["uvicorn", "budget_rag.api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
