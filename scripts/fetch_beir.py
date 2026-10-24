"""下载 BEIR 子集并解压到 data/beir/<dataset>/。

数据源（官方，无需 HF 登录）：
    https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/<name>.zip

用法：
    python scripts/fetch_beir.py --datasets scifact nfcorpus arguana
    python scripts/fetch_beir.py --datasets fiqa scidocs --dest data/beir

解压后目录结构：
    data/beir/<name>/corpus.jsonl
    data/beir/<name>/queries.jsonl
    data/beir/<name>/qrels/test.tsv
"""

from __future__ import annotations

import argparse
import os
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "beir"
URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{name}.zip"

# 官方 18 个数据集的规模（文档数，用来提示显存/内存需求）
SIZES = {
    "nfcorpus": 3_633,
    "scifact": 5_183,
    "arguana": 8_674,
    "scidocs": 25_657,
    "trec-covid": 171_332,
    "fiqa": 57_638,
    "cqadupstack": 457_000,
    "robust04": 528_155,
    "trec-news": 594_977,
    "signal1m": 1_000_000,
    "nq": 2_681_468,
    "hotpotqa": 5_233_329,
    "msmarco": 8_841_823,
}


def fetch(name: str, dest: Path, cache: Path) -> bool:
    zip_path = cache / f"{name}.zip"
    url = URL.format(name=name)
    if not zip_path.exists():
        print(f"下载 {url}")
        cmd = ["curl", "-sS", "-L", "--ssl-no-revoke", "-C", "-",
               "--max-time", "3600", "-o", str(zip_path), url]
        r = subprocess.run(cmd, check=False)
        if r.returncode != 0 or not zip_path.exists():
            print(f"  下载失败（curl {r.returncode}）")
            return False
    try:
        zf = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile:
        print("  压缩包不完整，删掉重试", zip_path)
        return False

    target = dest / name
    target.mkdir(parents=True, exist_ok=True)
    zf.extractall(target)
    zf.close()

    # 官方包里是 <name>/corpus.jsonl 这种嵌套一层，拍平
    nested = target / name
    if nested.is_dir():
        for item in nested.iterdir():
            item.rename(target / item.name)
        nested.rmdir()

    docs = SIZES.get(name)
    size_mb = sum(p.stat().st_size for p in target.rglob("*") if p.is_file()) / 1e6
    print(f"  -> {target}  ({size_mb:.1f} MB" + (f", 约 {docs:,} 篇" if docs else "") + ")")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="+", default=["scifact"])
    ap.add_argument("--dest", default=str(DEST))
    ap.add_argument("--cache", default=str(Path(os.getenv("TEMP", "/tmp")) / "beir_zip"))
    args = ap.parse_args()

    dest, cache = Path(args.dest), Path(args.cache)
    dest.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)

    ok = 0
    for name in args.datasets:
        name = name.strip().lower()
        if name not in SIZES:
            print(f"未知数据集 {name}，可用：{', '.join(sorted(SIZES))}")
            continue
        if fetch(name, dest, cache):
            ok += 1
    print(f"\n完成 {ok}/{len(args.datasets)}，数据在 {dest}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
