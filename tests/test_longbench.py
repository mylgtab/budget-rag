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
