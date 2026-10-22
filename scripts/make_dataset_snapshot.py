"""生成长文档基准的小样本快照（入库用），避免依赖外部镜像。

python scripts/make_dataset_snapshot.py --per-file 15
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "longbench"
DST = ROOT / "data" / "longbench_sample"
KEEP = ("input", "context", "answers", "dataset", "language", "_id")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-file", type=int, default=15)
    ap.add_argument("--subsets", nargs="+",
                    default=["passage_retrieval_zh", "passage_retrieval_en",
                             "hotpotqa", "2wikimqa", "musique", "triviaqa"])
    args = ap.parse_args()

    DST.mkdir(parents=True, exist_ok=True)
    total = 0
    for name in args.subsets:
        src = SRC / f"{name}.jsonl"
        if not src.exists():
            print(f"跳过（未下载）: {name}")
            continue
        rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
        sample = [{k: r[k] for k in KEEP if k in r} for r in rows[: args.per_file]]
        out = DST / f"{name}_{args.per_file}.jsonl"
        out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in sample) + "\n",
                       encoding="utf-8")
        kb = out.stat().st_size / 1024
        total += kb
        print(f"{name}: {len(sample)} 条 -> {out.name} ({kb:.0f} KB)")

    print(f"\n快照合计 {total/1024:.1f} MB，位于 {DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
