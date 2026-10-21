"""建索引：python scripts/ingest.py --docs data/sample_docs [--out index.json]"""

from __future__ import annotations


import argparse
import sys
import io

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.config import Settings          # noqa: E402
from budget_rag.pipeline import RAG             # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="data/sample_docs")
    ap.add_argument("--out", default="index.json")
    args = ap.parse_args()

    docs_dir = Path(args.docs)
    if not docs_dir.exists():
        print(f"找不到目录: {docs_dir}")
        return 1

    texts = {p.name: p.read_text(encoding="utf-8") for p in sorted(docs_dir.glob("*.md"))}
    rag = RAG(Settings.from_env())
    n = rag.ingest(texts)
    rag.store.save(ROOT / args.out)
    print(f"文档 {len(texts)} 篇 → {n} 块，已写入 {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
