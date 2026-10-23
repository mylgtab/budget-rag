"""API 鉴权与限流测试（没装 fastapi 时自动跳过）。"""

from __future__ import annotations

import importlib
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    from fastapi.testclient import TestClient  # noqa: F401

    HAS_FASTAPI = True
except Exception:
    HAS_FASTAPI = False


@unittest.skipUnless(HAS_FASTAPI, "需要 fastapi + httpx")
class TestApi(unittest.TestCase):
    def _client(self, token: str = "", rate: int = 60, burst: int = 10):
        os.environ["RAG_API_TOKEN"] = token
        os.environ["RAG_RATE_LIMIT"] = str(rate)
        os.environ["RAG_RATE_BURST"] = str(burst)
        import budget_rag.api as api

        importlib.reload(api)
        return TestClient(api.app)

    def tearDown(self):
        os.environ.pop("RAG_API_TOKEN", None)
        os.environ.pop("RAG_RATE_LIMIT", None)
        os.environ.pop("RAG_RATE_BURST", None)

    def test_health_open(self):
        c = self._client(token="secret")
        self.assertEqual(c.get("/health").status_code, 200)

    def test_query_requires_token(self):
        c = self._client(token="secret")
        self.assertEqual(c.post("/query", json={"question": "x"}).status_code, 401)

    def test_query_rejects_bad_token(self):
        c = self._client(token="secret")
        r = c.post("/query", json={"question": "x"}, headers={"Authorization": "Bearer wrong"})
        self.assertEqual(r.status_code, 401)

    def test_query_accepts_good_token(self):
        c = self._client(token="secret")
        r = c.post("/query", json={"question": "x"}, headers={"Authorization": "Bearer secret"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("answer", r.json())

    def test_v1_paths(self):
        c = self._client(token="secret")
        h = c.get("/v1/health")
        self.assertEqual(h.status_code, 200)
        self.assertIn("version", h.json())
        r = c.post("/v1/query", json={"question": "x"},
                   headers={"Authorization": "Bearer secret"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("answer", r.json())
        self.assertIn("trace", r.json())

    def test_legacy_alias_still_works(self):
        c = self._client(token="")
        self.assertEqual(c.get("/health").status_code, 200)
        self.assertEqual(c.post("/query", json={"question": "x"}).status_code, 200)

    def test_openapi_only_documents_v1(self):
        c = self._client(token="")
        spec = c.get("/openapi.json").json()
        self.assertIn("/v1/query", spec["paths"])
        self.assertIn("/v1/health", spec["paths"])
        self.assertNotIn("/query", spec["paths"])

    def test_question_validation(self):
        c = self._client(token="")
        self.assertEqual(c.post("/v1/query", json={"question": ""}).status_code, 422)
        self.assertEqual(c.post("/v1/query", json={"question": "x" * 3000}).status_code, 422)

    def test_rate_limit(self):
        c = self._client(token="", rate=1, burst=2)
        codes = [c.post("/query", json={"question": "x"}).status_code for _ in range(4)]
        self.assertIn(429, codes)
        self.assertEqual(codes[0], 200)


if __name__ == "__main__":
    unittest.main()
