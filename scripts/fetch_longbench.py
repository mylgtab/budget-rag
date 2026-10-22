"""下载 LongBench 子集并解压到 data/longbench/。

镜像默认 hf-mirror，可用 HF_ENDPOINT 覆盖。

python scripts/fetch_longbench.py --subsets passage_retrieval_zh dureader
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "longbench"
URL = "{base}/datasets/THUDM/LongBench/resolve/main/data.zip"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subsets", nargs="+", default=["passage_retrieval_zh"])
    ap.add_argument("--cache", default=str(Path(os.getenv("TEMP", "/tmp")) / "longbench_data.zip"))
    args = ap.parse_args()

    base = os.getenv("HF_ENDPOINT", "https://hf-mirror.com").rstrip("/")
    zip_path = Path(args.cache)
    if not zip_path.exists() or zip_path.stat().st_size < 100_000_000:
        print(f"下载 {URL.format(base=base)}  ->  {zip_path}")
        cmd = ["curl", "-sS", "-L", "--ssl-no-revoke", "-C", "-", "-o", str(zip_path),
               "--max-time", "3600", URL.format(base=base)]
        subprocess.run(cmd, check=False)

    if not zip_path.exists():
        print("下载失败")
        return 1
    try:
        zf = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile:
        print("压缩包不完整，删掉重试")
        return 1

    DEST.mkdir(parents=True, exist_ok=True)
    names = {e.filename for e in zf.infolist()}
    for sub in args.subsets:
        member = f"data/{sub}.jsonl"
        if member not in names:
            print(f"跳过（包里没有）: {member}")
            continue
        target = DEST / f"{sub}.jsonl"
        target.write_bytes(zf.read(member))
        print(f"解压 {member} -> {target} ({target.stat().st_size/1024:.0f} KB)")
    zf.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
