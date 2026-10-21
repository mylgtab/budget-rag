PY ?= python

.PHONY: help install test ingest eval sweep bench api docker clean all

help:
	@echo "make install  - 装依赖"
	@echo "make test     - 单元测试"
	@echo "make ingest   - 建索引"
	@echo "make eval     - 跑评测"
	@echo "make sweep    - 预算扫描 + 曲线"
	@echo "make bench    - 多策略对比 + 置信区间"
	@echo "make api      - 起 HTTP 服务"
	@echo "make docker   - 构建镜像"
	@echo "make all      - 测试 + 建索引 + 评测 + 对比"

install:
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m unittest discover -s tests -v

ingest:
	$(PY) scripts/ingest.py --docs data/sample_docs

eval:
	$(PY) scripts/eval.py --set data/eval_set.jsonl --k 3

sweep:
	$(PY) scripts/sweep.py --set data/eval_set.jsonl

bench:
	$(PY) scripts/bench.py --set data/eval_set.jsonl --out results/easy
	$(PY) scripts/bench.py --set data/eval_hard.jsonl --out results/hard

api:
	$(PY) -m uvicorn budget_rag.api:app --app-dir src --reload

docker:
	docker build -t budget-rag:dev .

all: test ingest eval bench

clean:
	rm -rf results index.json __pycache__ src/budget_rag/__pycache__ scripts/__pycache__
