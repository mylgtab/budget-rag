"""极简磁盘缓存：同一问题/同一上下文重复调用时不再花钱。

默认开启，`RAG_CACHE=0` 关闭；缓存文件在 `.cache/llm.json`。
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


class DiskCache:
    def __init__(self, path: str | Path = ".cache/llm.json", enabled: bool | None = None) -> None:
        self.enabled = (os.getenv("RAG_CACHE", "1") != "0") if enabled is None else enabled
        self.path = Path(path)
        self._data: dict[str, str] = {}
        self._loaded = False
        self._dirty = 0

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
        h = hashlib.sha256("\x00".join(parts).encode("utf-8"))
        return h.hexdigest()[:32]

    def get(self, key: str) -> str | None:
        if not self.enabled:
            return None
        self._load()
        return self._data.get(key)

    def put(self, key: str, value: str) -> None:
        if not self.enabled or not value:
            return
        self._load()
        self._data[key] = value
        self._dirty += 1
        if self._dirty >= 5:          # 攒几次再落盘，减少 IO
            self.flush()

    def flush(self) -> None:
        if not self.enabled or not self._dirty:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, ensure_ascii=False), encoding="utf-8")
        self._dirty = 0
