"""numpy 向量化与二进制索引的回归测试。"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.store import Store  # noqa: E402

try:
    import numpy as _np
    HAS_NUMPY = True
except Exception:  # pragma: no cover
    HAS_NUMPY = False


class FakeEmbedder:
    """确定性向量：按词哈希，维度 64。"""

    dim = 64

    def embed(self, texts):
        out = []
        for t in texts:
            v = [0.0] * self.dim
            for w in t.lower().split():
                v[hash(w) % self.dim] += 1.0
            norm = sum(x * x for x in v) ** 0.5 or 1.0
            out.append([x / norm for x in v])
        return out


def make_store() -> Store:
    s = Store(FakeEmbedder(), size=120, overlap=20, mode="fixed")
    s.add_documents({
        "a.md": "docker volumes persist data. named volumes are managed by docker.",
        "b.md": "kubernetes pods are ephemeral. a daemonset keeps one pod per node.",
        "c.md": "redis sorted sets score members. zadd inserts a member with a score.",
    })
    return s


@unittest.skipUnless(HAS_NUMPY, "需要 numpy")
class TestVectorizedStore(unittest.TestCase):
    def test_vector_search_returns_best_first(self):
        s = make_store()
        hits = s.search_vector("daemonset pod per node", 3)
        self.assertTrue(hits)
        self.assertEqual(hits[0][0].doc, "b.md")
        self.assertGreaterEqual(hits[0][1], hits[-1][1])

    def test_hybrid_precomputed_matches_hybrid(self):
        s = make_store()
        qv = FakeEmbedder().embed(["redis sorted set score"])[0]
        a = s.search_hybrid_precomputed("redis sorted set score", qv, 3)
        b = s.search_hybrid("redis sorted set score", 3)
        self.assertEqual([c.doc for c, _ in a], [c.doc for c, _ in b])

    def test_npz_roundtrip_keeps_scores(self):
        s = make_store()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "index.json"
            s.save(path)
            self.assertTrue(path.with_suffix(".npz").exists())

            s2 = Store(FakeEmbedder(), mode="fixed")
            s2.load(path)
            self.assertEqual(len(s2.chunks), len(s.chunks))
            a = [c.text for c, _ in s.search_vector("docker volumes", 3)]
            b = [c.text for c, _ in s2.search_vector("docker volumes", 3)]
            self.assertEqual(a, b)

    def test_matrix_invalidates_after_add(self):
        s = make_store()
        n1 = s.matrix.shape[0]
        s.add_document("d.md", "grafana dashboards visualise metrics from prometheus.")
        n2 = s.matrix.shape[0]
        self.assertGreater(n2, n1)

    def test_empty_query_vector_is_safe(self):
        s = make_store()
        hits = s.search_vector_precomputed([], 3)
        self.assertEqual(len(hits), 3)

    def test_topk_matches_bruteforce(self):
        s = make_store()
        qv = FakeEmbedder().embed(["namespaces are immutable"])[0]
        fast = [c.text for c, _ in s.search_vector_precomputed(qv, 2)]
        scored = sorted(((c, sum(a * b for a, b in zip(qv, c.vec))) for c in s.chunks),
                        key=lambda x: x[1], reverse=True)
        slow = [c.text for c, _ in scored[:2]]
        self.assertEqual(fast, slow)


if __name__ == "__main__":
    unittest.main()
