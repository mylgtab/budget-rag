"""缓存层：LLM 结果（JSON）+ 向量（SQLite BLOB）。

为什么向量单独用 SQLite：一条 1024 维向量用 JSON 存约 8KB，几千条就几十 MB；
用 float32 的 BLOB 只要 4KB，而且能按 key 精确取、不用整文件读进内存。
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import struct
from pathlib import Path


class DiskCache:
    """键值缓存，值是字符串（答案、改写结果）。"""

    def __init__(self, path: str | Path = ".cache/llm.json", enabled: bool | None = None,
                 max_entries: int = 20000) -> None:
        self.enabled = (os.getenv("RAG_CACHE", "1") != "0") if enabled is None else enabled
        self.path = Path(path)
        self.max_entries = max_entries
        self._data: dict[str, str] = {}
        self._loaded = False
        self._dirty = 0
        self.hits = 0
        self.misses = 0

    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}

    @staticmethod
    def key(*parts: str) -> str:
        return hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()[:32]

    def get(self, key: str) -> str | None:
        if not self.enabled:
            return None
        self._load()
        v = self._data.get(key)
        self.hits += int(v is not None)
        self.misses += int(v is None)
        return v

    def put(self, key: str, value: str) -> None:
        if not self.enabled or not value:
            return
        self._load()
        self._data[key] = value
        self._dirty += 1
        if self._dirty >= 5:
            self.flush()

    def flush(self) -> None:
        if not self.enabled or not self._dirty:
            return
        if len(self._data) > self.max_entries:          # 简单裁剪：丢掉最早写入的
            drop = len(self._data) - self.max_entries
            for k in list(self._data)[:drop]:
                del self._data[k]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, ensure_ascii=False), encoding="utf-8")
        self._dirty = 0

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "kind": "llm",
            "enabled": self.enabled,
            "entries": len(self._data),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total, 3) if total else 0.0,
            "file": str(self.path),
            "size_kb": round(self.path.stat().st_size / 1024, 1) if self.path.exists() else 0.0,
        }


class EmbedCache:
    """向量缓存：key = 模型名 + 文本，value = float32 BLOB。"""

    def __init__(self, path: str | Path = ".cache/embed.db", enabled: bool | None = None) -> None:
        self.enabled = (os.getenv("RAG_EMBED_CACHE", "1") != "0") if enabled is None else enabled
        self.path = Path(path)
        self.hits = 0
        self.misses = 0
        self._conn: sqlite3.Connection | None = None

    def _db(self) -> sqlite3.Connection:
        if self._conn is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.path))
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS vectors (key TEXT PRIMARY KEY, dim INTEGER, vec BLOB)"
            )
            self._conn.commit()
        return self._conn

    @staticmethod
    def key(model: str, text: str) -> str:
        return hashlib.sha256((model + "\x00" + text).encode("utf-8")).hexdigest()

    def get_many(self, model: str, texts: list[str]) -> list[list[float] | None]:
        if not self.enabled or not texts:
            return [None] * len(texts)
        db = self._db()
        keys = [self.key(model, t) for t in texts]
        out: list[list[float] | None] = [None] * len(texts)
        for start in range(0, len(keys), 500):                 # 分批查，避免变量太多
            chunk = keys[start:start + 500]
            q = f"SELECT key, dim, vec FROM vectors WHERE key IN ({','.join('?' * len(chunk))})"
            for k, dim, blob in db.execute(q, chunk):
                idx = keys.index(k)
                out[idx] = list(struct.unpack(f"<{dim}f", blob))
        self.hits += sum(1 for v in out if v is not None)
        self.misses += sum(1 for v in out if v is None)
        return out

    def put_many(self, model: str, texts: list[str], vecs: list[list[float]]) -> None:
        if not self.enabled or not texts:
            return
        db = self._db()
        rows = [
            (self.key(model, t), len(v), struct.pack(f"<{len(v)}f", *v))
            for t, v in zip(texts, vecs)
        ]
        db.executemany("INSERT OR REPLACE INTO vectors (key, dim, vec) VALUES (?, ?, ?)", rows)
        db.commit()

    def close(self) -> None:
        """Windows 上不关连接会锁住文件，测试和脚本退出前要调。"""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def stats(self) -> dict:
        total = self.hits + self.misses
        entries = 0
        if self.path.exists():
            try:
                entries = self._db().execute("SELECT COUNT(*) FROM vectors").fetchone()[0]
            except Exception:
                entries = -1
        return {
            "kind": "embedding",
            "enabled": self.enabled,
            "entries": entries,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total, 3) if total else 0.0,
            "file": str(self.path),
            "size_kb": round(self.path.stat().st_size / 1024, 1) if self.path.exists() else 0.0,
        }
