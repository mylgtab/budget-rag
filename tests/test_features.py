"""新增能力测试：tokenizer / 缓存 / 预算检索 / 路由 / 指标。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.cache import DiskCache                  # noqa: E402
from budget_rag.config import Settings                 # noqa: E402
from budget_rag.embedding import HashEmbedder          # noqa: E402
from budget_rag.metrics import cohen_kappa, contain, em, f1  # noqa: E402
from budget_rag.pipeline import RAG                    # noqa: E402
from budget_rag.router import decide                   # noqa: E402
from budget_rag.store import Store                     # noqa: E402
from budget_rag.tokens import backend, count_tokens    # noqa: E402


class TestTokenizer(unittest.TestCase):
    def test_positive_and_monotonic(self):
        self.assertGreater(count_tokens("你好"), 0)
        self.assertGreaterEqual(count_tokens("你好世界" * 10), count_tokens("你好"))

    def test_empty(self):
        self.assertEqual(count_tokens(""), 0)

    def test_backend_reported(self):
        self.assertIn(backend(), {"tiktoken/cl100k", "heuristic(chars/1.5)"})

    def test_mixed_text(self):
        n = count_tokens("Python 的字典在 3.7 之后保证插入顺序。")
        self.assertTrue(5 <= n <= 60)


class TestBudgetRetrieval(unittest.TestCase):
    def setUp(self):
        self.store = Store(HashEmbedder(32), 100, 20, "sentence")
        for i in range(6):
            self.store.add_document(f"d{i}.md", f"这是第{i}条事实句子，内容关于主题{i}。")

    def test_respects_budget(self):
        hits = self.store.search_to_budget("主题3", 40, hybrid=False)
        self.assertGreaterEqual(len(hits), 1)
        used = sum(count_tokens(c.text) for c, _ in hits)
        self.assertGreaterEqual(used, 40)

    def test_at_least_one_chunk(self):
        tiny = self.store.search_to_budget("主题1", 1)
        self.assertEqual(len(tiny), 1)

    def test_empty_store(self):
        empty = Store(HashEmbedder(32), 100, 20, "sentence")
        self.assertEqual(empty.search_to_budget("x", 100), [])


class TestRouterTiers(unittest.TestCase):
    def test_tight_budget_small_k(self):
        r = decide("ETag 是什么？", 0.0005)
        self.assertEqual(r.k, 1)
        self.assertFalse(r.hybrid)

    def test_wide_budget_hybrid(self):
        r = decide("ETag 是什么？", 0.05)
        self.assertTrue(r.hybrid)
        self.assertGreaterEqual(r.k, 5)

    def test_hard_question_gets_strong_path(self):
        q = "请比较强缓存与协商缓存在长连接场景下的取舍"
        self.assertEqual(decide(q, 0.05).path, "strong")


class TestAutoChunkMode(unittest.TestCase):
    def test_picks_sentence_for_small_budget(self):
        s = Settings(chunk_mode="auto", ctx_tokens=200)
        rag = RAG(s)
        rag.ingest({"a.md": "第一句话在这里。第二句话在这里。第三句话在这里。"})
        out = rag.query("第一句话是什么？", ctx_tokens=100)
        self.assertEqual(out["trace"]["store"], "sentence")

    def test_picks_fixed_for_large_budget(self):
        s = Settings(chunk_mode="auto", ctx_tokens=200)
        rag = RAG(s)
        rag.ingest({"a.md": "第一句话在这里。第二句话在这里。第三句话在这里。"})
        out = rag.query("第一句话是什么？", ctx_tokens=900)
        self.assertEqual(out["trace"]["store"], "fixed")


class TestCache(unittest.TestCase):
    def test_put_get(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "c.json"
            c = DiskCache(path=path, enabled=True)
            k = DiskCache.key("q", "ctx")
            self.assertIsNone(c.get(k))
            c.put(k, "答案")
            self.assertEqual(c.get(k), "答案")
            c.flush()
            self.assertTrue(path.exists())
            # 重新加载后仍在
            fresh = DiskCache(path=path, enabled=True)
            self.assertEqual(fresh.get(k), "答案")

    def test_disabled(self):
        c = DiskCache(path=Path("results/_test_cache2.json"), enabled=False)
        c.put("k", "v")
        self.assertIsNone(c.get("k"))


class TestMetrics(unittest.TestCase):
    def test_contain_and_em(self):
        self.assertEqual(contain("暂存区和版本库", "git diff --cached 对比暂存区和版本库"), 1.0)
        self.assertEqual(em("ABC", "abc"), 1.0)
        self.assertEqual(em("abc", "abd"), 0.0)

    def test_f1_partial(self):
        self.assertAlmostEqual(f1("a b c", "a b d"), 2 * (2 / 3) * (2 / 3) / (4 / 3), places=5)

    def test_kappa_perfect(self):
        pairs = [(3, 3), (2, 2), (1, 1)]
        self.assertAlmostEqual(cohen_kappa(pairs), 1.0, places=5)

    def test_kappa_unweighted_not_one_on_disagreement(self):
        pairs = [(3, 3)] * 7 + [(2, 3)] * 2 + [(1, 1)]
        k = cohen_kappa(pairs)
        self.assertLess(k, 1.0)
        self.assertGreater(k, 0.0)

    def test_kappa_weighted_higher_for_near_miss(self):
        pairs = [(3, 3)] * 7 + [(2, 3)] * 2 + [(1, 1)]
        self.assertGreater(cohen_kappa(pairs, weights=True), cohen_kappa(pairs))


if __name__ == "__main__":
    unittest.main()
