"""查看缓存状态：命中率、条目数、占用。

python scripts/cache_stats.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from budget_rag.cache import DiskCache, EmbedCache   # noqa: E402


def main() -> int:
    rows = []
    for c in (DiskCache(), EmbedCache()):
        s = c.stats()
        rows.append(s)

    print(f"{'类型':<10}{'条目':>8}{'文件KB':>10}{'启用':>6}")
    for s in rows:
        print(f"{s['kind']:<10}{s['entries']:>8}{s['size_kb']:>10.1f}{str(s['enabled']):>6}")

    total_kb = sum(s["size_kb"] for s in rows)
    print(f"\n合计 {total_kb:.1f} KB")
    print("\n提示：`RAG_CACHE=0` 关答案缓存，`RAG_EMBED_CACHE=0` 关向量缓存。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
