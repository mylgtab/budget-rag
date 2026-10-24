"""自适应检索深度的单元测试（不需要网络）。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.pipeline import adaptive_depth  # noqa: E402


class _Chunk:
    def __init__(self, name: str) -> None:
        self.name = name


class _StubStore:
    """按给定分数返回固定数量的块。"""

    def __init__(self, scores: list[float]) -> None:
        self._ranked = [(_Chunk(f"c{i}"), s) for i, s in enumerate(scores)]

    def search_hybrid(self, query: str, k: int):
        return self._ranked[:k]

    def search_bm25(self, query: str, k: int):
        return self._ranked[:k]


class TestAdaptiveDepth(unittest.TestCase):
    def test_high_confidence_takes_few(self):
        store = _StubStore([1.0, 0.95, 0.9, 0.85] + [0.5] * 6)   # 间隔 0.05 < tau 0.25 → 多取
        got = adaptive_depth(store, "q", tau=0.02, k_easy=2, k_hard=8)
        self.assertEqual(len(got), 2)

    def test_low_confidence_takes_many(self):
        store = _StubStore([1.0, 0.5] + [0.4] * 8)                # 间隔 0.5 > tau → 少取
        got = adaptive_depth(store, "q", tau=0.25, k_easy=2, k_hard=8)
        self.assertEqual(len(got), 8)

    def test_short_pool_falls_back_to_easy(self):
        store = _StubStore([1.0])
        got = adaptive_depth(store, "q", k_easy=3, k_hard=10)
        self.assertLessEqual(len(got), 3)

    def test_pool_size_respected(self):
        store = _StubStore([1.0, 0.2] + [0.1] * 30)
        got = adaptive_depth(store, "q", tau=0.05, k_easy=4, k_hard=10)
        self.assertLessEqual(len(got), 10)


if __name__ == "__main__":
    unittest.main()
