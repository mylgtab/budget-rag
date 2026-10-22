"""LongBench 解析与预算取块测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from longbench_passage import parse_passages, take_budget  # noqa: E402
from budget_rag.embedding import HashEmbedder             # noqa: E402
from budget_rag.store import Store                        # noqa: E402

SAMPLE = "段落1：苹果是一种水果。\n\n段落2：香蕉是黄色的。\n\n段落12：樱桃是红色的。"


class TestParsePassages(unittest.TestCase):
    def test_split(self):
        p = parse_passages(SAMPLE)
        self.assertEqual(set(p), {"段落1", "段落2", "段落12"})
        self.assertIn("苹果", p["段落1"])
        self.assertIn("樱桃", p["段落12"])

    def test_no_marks(self):
        self.assertEqual(parse_passages("没有段落标记的文本"), {})

    def test_keeps_content_after_last(self):
        p = parse_passages("段落1：唯一内容")
        self.assertEqual(p["段落1"], "唯一内容")


class TestTakeBudget(unittest.TestCase):
    def setUp(self):
        self.store = Store(HashEmbedder(16), 100, 20, "sentence")
        self.store.add_document("a", "句子一。句子二。句子三。句子四。")

    def test_at_least_one(self):
        hits = self.store.search_bm25("句子", 10)
        self.assertEqual(len(take_budget(hits, 1)), 1)

    def test_respects_budget(self):
        hits = self.store.search_bm25("句子", 10)
        picked = take_budget(hits, 50)
        self.assertLessEqual(len(picked), len(hits))


if __name__ == "__main__":
    unittest.main()

class TestTakeBudgetScalesWithBudget(unittest.TestCase):
    """回归测试：取块上限不能先于预算卡死（曾导致 800 token 只用 500）。"""

    def setUp(self):
        from budget_rag.embedding import HashEmbedder
        from budget_rag.store import Store
        from longbench_qa import take_budget as qa_take

        self.qa_take = qa_take
        self.store = Store(HashEmbedder(16), 100, 20, "sentence")
        body = "".join(f"第{i}句讲的是主题{i}，内容足够长以便计数。" for i in range(120))
        self.store.add_document("doc", body)

    def test_large_budget_uses_large_context(self):
        from budget_rag.tokens import count_tokens

        hits = self.store.search_bm25("主题", len(self.store.chunks))
        for budget in (300, 800):
            ctx = self.qa_take(hits, budget)
            used = count_tokens(ctx)
            self.assertGreaterEqual(used, budget * 0.8,
                                    f"budget={budget} 实际只用了 {used} token，上限又卡死了")

    def test_small_budget_still_bounded(self):
        from budget_rag.tokens import count_tokens

        hits = self.store.search_bm25("主题", len(self.store.chunks))
        ctx = self.qa_take(hits, 60)
        self.assertLessEqual(count_tokens(ctx), 200)
