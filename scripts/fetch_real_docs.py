"""抓取 Docker / Redis / Kubernetes 官方文档作为真实检索语料。

只取 content 下的正文页（跳过导航、模板、partials），清洗成纯文本，
保留标题层级，输出到 data/real_docs/<project>/<slug>.md。

python scripts/fetch_real_docs.py --per-repo 15
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TREES = ROOT / "data" / "_trees"
OUT = ROOT / "data" / "real_docs"

REPOS = {
    "docker": {
        "repo": "docker/docs",
        "prefixes": ("content/manuals/", "content/get-started/", "content/build/"),
        "skip": ("index.md", "_index.md", "partials/", "includes/", "faq.md"),
    },
    "redis": {
        "repo": "redis/docs",
        "prefixes": ("content/develop/data-types/", "content/develop/use-cases/", "content/develop/clients/"),
        "skip": ("index.md", "_index.md", "partials/", "includes/"),
    },
    "kubernetes": {
        "repo": "kubernetes/website",
        "prefixes": ("content/en/docs/concepts/",),
        "skip": ("index.md", "_index.md", "partials/", "includes/", "tools/reference"),
    },
}

MIN_BYTES = 3500
MAX_BYTES = 16000


def fetch_raw(repo: str, path: str) -> str | None:
    url = f"https://raw.githubusercontent.com/{repo}/main/{path}"
    try:
        out = subprocess.run(
            ["curl.exe", "-sS", "--ssl-no-revoke", "--max-time", "25", url],
            capture_output=True, check=False,
        )
    except FileNotFoundError:
        out = subprocess.run(
            ["curl", "-sS", "--max-time", "25", url], capture_output=True, check=False,
        )
    if out.returncode != 0 or not out.stdout:
        return None
    try:
        return out.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def clean_markdown(text: str) -> str:
    # YAML front matter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    # Hugo/MDX shortcodes
    text = re.sub(r"\{\{[<%].*?[>%]\}\}", "", text, flags=re.S)
    text = re.sub(r"^import .*$", "", text, flags=re.M)
    text = re.sub(r"^export .*$", "", text, flags=re.M)
    # HTML 块与注释
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    # 代码块压成一行占位（保留可执行信息但不占大量 token）
    text = re.sub(r"```.*?```", "[code example]", text, flags=re.S)
    # 图片与链接保留文字
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    # 表格分隔行
    text = re.sub(r"^\|[-:\s|]+\|$", "", text, flags=re.M)
    # 折叠多余空行
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-repo", type=int, default=15)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []

    for project, cfg in REPOS.items():
        tree_file = TREES / (cfg["repo"].replace("/", "_") + ".json")
        tree = json.loads(tree_file.read_text(encoding="utf-8-sig"))
        blobs = [
            t for t in tree.get("tree", [])
            if t.get("type") == "blob"
            and t["path"].endswith(".md")
            and any(t["path"].startswith(p) for p in cfg["prefixes"])
            and not any(s in t["path"] for s in cfg["skip"])
            and MIN_BYTES <= t.get("size", 0) <= MAX_BYTES
        ]
        blobs.sort(key=lambda t: (-t.get("size", 0), t["path"]))
        picked: list[dict] = []
        seen_slug: set[str] = set()
        for b in blobs:
            if len(picked) >= args.per_repo:
                break
            slug = re.sub(r"[^a-z0-9]+", "-", b["path"].rsplit("/", 1)[-1][:-3].lower()).strip("-")
            if slug in seen_slug:
                continue
            raw = fetch_raw(cfg["repo"], b["path"])
            if not raw:
                continue
            body = clean_markdown(raw)
            if len(body) < 1200:
                continue
            seen_slug.add(slug)
            dest = OUT / f"{project}-{slug}.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(body, encoding="utf-8")
            picked.append({"project": project, "path": b["path"], "slug": slug,
                           "bytes_src": b["size"], "bytes_clean": len(body.encode("utf-8")),
                           "chars": len(body)})
            print(f"  {project}/{slug:<40} {len(body):>6} 字符  ← {b['path']}")
        manifest.extend(picked)
        print(f"--- {project}: 取 {len(picked)} 篇")

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    total_chars = sum(m["chars"] for m in manifest)
    print(f"\n合计 {len(manifest)} 篇，{total_chars:,} 字符（≈{total_chars // 4:,} token 量级）")
    print(f"清单: {OUT / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
