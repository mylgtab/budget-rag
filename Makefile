PY ?= python

.PHONY: help install test check ingest eval sweep bench api docker clean all

help:
	@echo "make install  - install dependencies"
	@echo "make test     - run unit tests"
	@echo "make check    - tests + quick eval (fast sanity)"
	@echo "make ingest   - build index"
	@echo "make eval     - run evaluation (500 items)"
	@echo "make sweep    - budget sweep + SVG curve"
	@echo "make bench    - multi-strategy comparison + CI"
	@echo "make api      - start HTTP service"
	@echo "make docker   - build image"
	@echo "make all      - test + ingest + eval + bench"

install:
	$(PY) -m pip install -r requirements.txt

test:
	$(PY) -m unittest discover -s tests -v

check: test
	$(PY) scripts/eval.py --set data/eval_500.jsonl --limit 50

ingest:
	$(PY) scripts/ingest.py --docs data/sample_docs

eval:
	$(PY) scripts/eval.py --set data/eval_500.jsonl --k 3

sweep:
	$(PY) scripts/sweep.py --set data/eval_500.jsonl

bench:
	$(PY) scripts/baselines.py --limit 200

api:
	$(PY) -m uvicorn budget_rag.api:app --app-dir src

docker:
	docker build -t budget-rag:dev .

all: test ingest eval bench

clean:
	rm -rf results index.json __pycache__ src/budget_rag/__pycache__ scripts/__pycache__
