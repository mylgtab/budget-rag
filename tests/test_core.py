"""冒烟测试：python -m unittest discover -s tests"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.bm25 import BM25              # noqa: E402
from budget_rag.chunking import chunk_text   # noqa: E402
from budget_rag.config import Settings       # noqa: E402
from budget_rag.pipeline import RAG          # noqa: E402
from budget_rag.router import decide         # noqa: E402


class TestChunking(unittest.TestCase):
    def test_short_text_single_chunk(self):
        self.assertEqual(chunk_text("一句话。", 100), ["一句话。"])

    def test_long_text_split(self):
        text = "这是一个测试句子。" * 100
        chunks = chunk_text(text, 80, 20)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(c) <= 100 for c in chunks))

    def test_empty(self):
        self.assertEqual(chunk_text("   "), [])


class TestBM25(unittest.TestCase):
    def test_rank_relevant_first(self):
        docs = ["数据库索引是 B+ 树", "今天天气很好", "索引可以加速查询"]
        bm = BM25(docs)
        top = bm.top_k("索引", 1)[0][0]
        self.assertIn(top, (0, 2))


class TestRouter(unittest.TestCase):
    def test_short_goes_cheap(self):
        self.assertEqual(decide("ETag 是什么？", 0.01).path, "cheap")

    def test_long_goes_strong(self):
        q = "请比较强缓存与协商缓存，并分析它们在长连接场景下的取舍"
        self.assertEqual(decide(q, 0.01).path, "strong")

    def test_budget_downgrade(self):
        q = "请比较强缓存与协商缓存，并分析它们在长连接场景下的取舍"
        self.assertEqual(decide(q, 0.001).path, "cheap")


class TestPipeline(unittest.TestCase):
    def test_end_to_end(self):
        rag = RAG(Settings(top_k=2, embed_dim=64, chunk_size=80))
        rag.ingest({"a.md": "Redis 是内存数据库。它支持持久化。"})
        out = rag.query("Redis 是什么？")
        self.assertIn("answer", out)
        self.assertGreaterEqual(out["trace"]["context_tokens"], 1)
        self.assertIn(out["trace"]["path"], ("cheap", "strong"))


if __name__ == "__main__":
    unittest.main()
