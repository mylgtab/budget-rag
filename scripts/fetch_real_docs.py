"""抓取多项目官方文档，构建约 500 篇的真实检索语料（含同域干扰）。

python scripts/fetch_real_docs.py --target 500
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "real_docs"
TREES = ROOT / "data" / "_trees"
TREES2 = ROOT / "data" / "_trees2"

# (项目, 仓库, 树文件, 前缀白名单, 目标篇数)
CONFIG = [
    ("docker", "docker/docs", TREES / "docker_docs.json",
     ("content/manuals/", "content/get-started/", "content/build/", "content/reference/"), 120),
    ("redis", "redis/docs", TREES / "redis_docs.json",
     ("content/commands/", "content/develop/", "content/operate/"), 100),
    ("kubernetes", "kubernetes/website", TREES / "kubernetes_website.json",
     ("content/en/docs/concepts/", "content/en/docs/tasks/", "content/en/docs/reference/"), 150),
    ("grafana", "grafana/grafana", TREES2 / "grafana.json",
     ("docs/sources/",), 100),
    ("prometheus", "prometheus/prometheus", TREES2 / "prometheus.json",
     ("docs/",), 30),
]

SKIP = ("index.md", "_index.md", "partials/", "includes/", "release-notes", "changelog",
        "/_", "templates/", "snippets/", "menu", "nav")
MIN_BYTES, MAX_BYTES = 3000, 20000


def fetch_raw(repo: str, path: str) -> str | None:
    url = f"https://raw.githubusercontent.com/{repo}/main/{path}"
    r = subprocess.run(["curl.exe", "-sS", "--ssl-no-revoke", "--max-time", "25", url],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    try:
        return r.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def clean_markdown(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    text = re.sub(r"\{\{[<%].*?[>%]\}\}", "", text, flags=re.S)
    text = re.sub(r"^import .*$|^export .*$", "", text, flags=re.M)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"```.*?```", "[code example]", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\|[-:\s|]+\|$", "", text, flags=re.M)
    text = text.replace("**", " ").replace("`", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=500)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    existing = {p.name for p in OUT.glob("*.md")}
    manifest = []
    total = len(existing)
    print(f"已有 {total} 篇\n")

    for project, repo, tree_file, prefixes, quota in CONFIG:
        if not tree_file.exists():
            print(f"跳过 {project}: 缺 {tree_file.name}")
            continue
        tree = json.loads(tree_file.read_text(encoding="utf-8-sig"))
        blobs = [
            t for t in tree.get("tree", [])
            if t.get("type") == "blob" and t["path"].endswith(".md")
            and any(t["path"].startswith(p) for p in prefixes)
            and not any(s in t["path"] for s in SKIP)
            and MIN_BYTES <= t.get("size", 0) <= MAX_BYTES
        ]
        blobs.sort(key=lambda t: (t["path"].count("/"), t["path"]))
        got = 0
        for b in blobs:
            if got >= quota or total >= args.target:
                break
            slug = re.sub(r"[^a-z0-9]+", "-", b["path"].rsplit("/", 1)[-1][:-3].lower()).strip("-")
            name = f"{project}-{slug}.md"
            if name in existing:
                continue
            raw = fetch_raw(repo, b["path"])
            if not raw:
                continue
            body = clean_markdown(raw)
            if len(body) < 1500:
                continue
            (OUT / name).write_text(body, encoding="utf-8")
            existing.add(name)
            manifest.append({"project": project, "file": name, "path": b["path"], "chars": len(body)})
            got += 1
            total += 1
        print(f"{project:<12} 新增 {got:>3}（累计 {total}）")

    mf = OUT / "manifest.json"
    old = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else []
    mf.write_text(json.dumps(old + manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    chars = sum(p.stat().st_size for p in OUT.glob("*.md"))
    print(f"\n总计 {total} 篇，约 {chars/1024/1024:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
