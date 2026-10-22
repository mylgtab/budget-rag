"""核心模块单元测试：用 mock 覆盖 LLM / embedding / store 的网络路径。"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.cache import DiskCache, EmbedCache       # noqa: E402
from budget_rag.config import Settings                   # noqa: E402
from budget_rag.embedding import (                       # noqa: E402
    CachedEmbedder, HashEmbedder, OpenAIEmbedder, cosine,
)
from budget_rag.llm import LLMAnswerer, OfflineAnswerer  # noqa: E402
from budget_rag.store import Store                        # noqa: E402
from budget_rag import tokens as tokens_mod               # noqa: E402


class FakeResp:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def chat_payload(content: str, prompt: int = 100, completion: int = 10) -> dict:
    return {
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
    }


class TestLLMAnswerer(unittest.TestCase):
    def setUp(self):
        self.env = mock.patch.dict(os.environ, {"RAG_CACHE": "0"})
        self.env.start()
        self.s = Settings(api_key="test-key", llm_model="m", llm_base="http://x/v1")

    def tearDown(self):
        self.env.stop()

    def test_answer_with_usage(self):
        a = LLMAnswerer(self.s)
        with mock.patch("budget_rag.llm.urllib.request.urlopen",
                        return_value=FakeResp(chat_payload("答案：缓存命中率。"))):
            text, usage = a.answer_with_usage("q", ["缓存命中率决定收益。"])
        self.assertIn("缓存命中率", text)
        self.assertEqual(usage["prompt_tokens"], 100)

    def test_answer_uses_usage(self):
        a = LLMAnswerer(self.s)
        with mock.patch("budget_rag.llm.urllib.request.urlopen",
                        return_value=FakeResp(chat_payload("答"))) as m:
            out = a.answer("q", ["ctx"])
        self.assertEqual(out, "答")
        self.assertEqual(m.call_count, 1)

    def test_retry_then_success(self):
        a = LLMAnswerer(self.s)
        seq = [RuntimeError("boom"), FakeResp(chat_payload("重试后成功"))]
        with mock.patch("budget_rag.llm.urllib.request.urlopen",
                        side_effect=seq), \
             mock.patch("budget_rag.llm.time.sleep", return_value=None):
            ans, _ = a.answer_with_usage("q", ["ctx"])
        self.assertIn("重试后成功", ans)

    def test_all_fail_raises(self):
        a = LLMAnswerer(self.s)
        with mock.patch("budget_rag.llm.urllib.request.urlopen",
                        side_effect=RuntimeError("down")), \
             mock.patch("budget_rag.llm.time.sleep", return_value=None):
            with self.assertRaises(RuntimeError):
                a.answer_with_usage("q", ["缓存命中率决定收益"])

    def test_rewrite_query(self):
        a = LLMAnswerer(self.s)
        with mock.patch("budget_rag.llm.urllib.request.urlopen",
                        return_value=FakeResp(chat_payload("缓存 命中率 收益"))):
            out = a.rewrite_query("缓存能带来什么好处？")
        self.assertIn("缓存", out)
        self.assertIsNotNone(a.last_rewrite_usage)

    def test_offline_answerer(self):
        o = OfflineAnswerer()
        out = o.answer("缓存收益", ["缓存命中率决定缓存的实际收益。"])
        self.assertIn("缓存", out)


class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = Store(HashEmbedder(32), 80, 10, "sentence")
        self.store.add_documents({
            "a": "缓存命中率决定缓存收益。索引能加速查询。",
            "b": "TCP 是字节流，没有消息边界。",
        })

    def test_vector_search(self):
        hits = self.store.search_vector("缓存收益", 2)
        self.assertGreaterEqual(len(hits), 1)

    def test_hybrid_search(self):
        hits = self.store.search_hybrid("缓存收益", 2)
        self.assertGreaterEqual(len(hits), 1)

    def test_hybrid_precomputed(self):
        qv = HashEmbedder(32).embed(["缓存"])[0]
        hits = self.store.search_hybrid_precomputed("缓存", qv, 2)
        self.assertGreaterEqual(len(hits), 1)

    def test_prf_search(self):
        hits = self.store.search_bm25_prf("缓存收益", 2)
        self.assertGreaterEqual(len(hits), 1)

    def test_budget_search_hybrid(self):
        hits = self.store.search_to_budget("缓存收益", 200, hybrid=True)
        self.assertGreaterEqual(len(hits), 1)

    def test_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "idx.json"
            self.store.save(path)
            self.assertTrue(path.exists())
            fresh = Store(HashEmbedder(32), 80, 10, "sentence")
            fresh.load(path)
            self.assertEqual(len(fresh.chunks), len(self.store.chunks))


class TestEmbedding(unittest.TestCase):
    def test_openai_embedder(self):
        payload = {"data": [{"embedding": [0.1, 0.2, 0.3]},
                            {"embedding": [0.4, 0.5, 0.6]}],
                   "usage": {"prompt_tokens": 7}}
        emb = OpenAIEmbedder("http://x/v1", "m", "k")
        with mock.patch("urllib.request.urlopen",
                        return_value=FakeResp(payload)):
            vecs = emb.embed(["a", "b"])
        self.assertEqual(len(vecs), 2)
        self.assertEqual(emb.dim, 3)
        self.assertAlmostEqual(cosine(vecs[0], vecs[0]), 1.0)

    def test_openai_retry_then_fail(self):
        emb = OpenAIEmbedder("http://x/v1", "m", "k")
        with mock.patch("urllib.request.urlopen",
                        side_effect=RuntimeError("down")), \
             mock.patch("time.sleep", return_value=None):
            with self.assertRaises(Exception):
                emb.embed(["a"])


class TestTokens(unittest.TestCase):
    def test_factor_applied(self):
        base = tokens_mod.count_tokens("一段用于测试的中文文本，重复几次看看效果。" * 3)
        with mock.patch.dict(os.environ, {"RAG_TOKEN_FACTOR": "0.5"}):
            tokens_mod._CACHE.clear()
            half = tokens_mod.count_tokens("一段用于测试的中文文本，重复几次看看效果。" * 3)
        tokens_mod._CACHE.clear()
        self.assertGreater(base, 0)
        self.assertLessEqual(half, base)


class TestCacheLimits(unittest.TestCase):
    def test_max_entries_pruned_on_flush(self):
        with tempfile.TemporaryDirectory() as td:
            c = DiskCache(path=Path(td) / "c.json", enabled=True, max_entries=3)
            for i in range(6):
                c.put(f"k{i}", str(i))
            c.flush()
            self.assertLessEqual(len(c._data), 3)

    def test_stats_shape(self):
        with tempfile.TemporaryDirectory() as td:
            c = DiskCache(path=Path(td) / "c.json", enabled=True)
            c.put("a", "1")
            c.get("a")
            s = c.stats()
            for key in ("kind", "entries", "hits", "misses", "hit_rate"):
                self.assertIn(key, s)


if __name__ == "__main__":
    unittest.main()
