"""核对参考文献是否真实存在（防 LLM 编造）。

方法：
  1. 有 arXiv 编号 → 请求 arxiv.org/abs/<id>，HTTP 200 且标题能取到 → 通过
  2. 期刊/会议论文 → Crossref 按标题检索，返回条目 → 通过
  3. ACL 系列 → ACL Anthology 按标题扫描 P##-#### 编号

用法：
    python scripts/verify_refs.py            # 检查 docs/paper-en.md
    python scripts/verify_refs.py --src docs/paper-draft.md
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def curl(url: str, timeout: int = 25) -> tuple[str, str]:
    """返回 (状态码, 正文)。"""
    p = subprocess.run(
        ["curl.exe", "-sSL", "-w", "\n%{http_code}", "--ssl-no-revoke",
         "--max-time", str(timeout), url],
        capture_output=True,
    )
    out = p.stdout.decode("utf-8", "ignore")
    body, _, code = out.rpartition("\n")
    return code.strip(), body


def arxiv_ok(aid: str) -> tuple[bool, str]:
    code, body = curl(f"https://export.arxiv.org/api/query?id_list={aid}")
    if code != "200":
        return False, f"HTTP {code}"
    m = re.search(r"<entry>.*?<title>(.*?)</title>", body, re.S)
    if not m:
        return False, "无条目（编号不存在）"
    return True, re.sub(r"\s+", " ", m.group(1)).strip()[:90]


def crossref_ok(title: str) -> tuple[bool, str]:
    q = urllib.parse.quote(title[:110])
    code, body = curl(f"https://api.crossref.org/works?rows=1&query.bibliographic={q}")
    if code != "200":
        return False, f"HTTP {code}"
    try:
        items = json.loads(body)["message"]["items"]
    except Exception:
        return False, "返回不是 JSON"
    if not items:
        return False, "Crossref 无结果"
    it = items[0]
    got = (it.get("title") or ["?"])[0]
    year = it.get("issued", {}).get("date-parts", [["?"]])[0][0]
    return True, f"{got[:80]} ({year})"


def anthology_scan(title: str) -> tuple[bool, str]:
    """在 ACL Anthology 的 P11 系列里扫标题（2011 年论文够用）。"""
    key = re.sub(r"[^a-z ]", "", title.lower())[:30].strip()
    for n in range(1000, 1120):
        code, body = curl(f"https://aclanthology.org/P11-{n}/", timeout=10)
        if code != "200":
            continue
        m = re.search(r"<title>(.*?)</title>", body, re.S)
        if m and key[:18] in re.sub(r"\s+", " ", m.group(1)).lower():
            return True, f"ACL Anthology P11-{n}: {m.group(1).strip()[:70]}"
    return False, "Anthology 未找到"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="docs/paper-en.md")
    args = ap.parse_args()

    text = (ROOT / args.src).read_text(encoding="utf-8")
    if "## References" not in text:
        print("找不到 References 段")
        return 1
    sec = text[text.index("## References"):]
    lines = [ln for ln in sec.splitlines() if re.match(r"^\d+\.\s", ln)]

    bad = 0
    print(f"共 {len(lines)} 条\n")
    for ln in lines:
        num = ln.split(".")[0]
        plain = re.sub(r"\*\*", "", ln)
        plain = re.sub(r"^\d+\.\s*", "", plain)
        m_arx = re.search(r"arXiv:(\d{4}\.\d{4,5})", plain)
        if m_arx:
            ok, info = arxiv_ok(m_arx.group(1))
            tag = "arXiv " + m_arx.group(1)
        else:
            title = re.sub(r"^[^.]*\.\s*", "", plain)[:110] or plain[:110]
            ok, info = crossref_ok(title)
            tag = "Crossref"
            if not ok and ("ACL-HLT" in plain or "EMNLP" in plain or "ACL 20" in plain):
                ok, info = anthology_scan(title)
                tag = "ACL"
        mark = "✅" if ok else "❌"
        print(f"{mark} [{num:>2}] {tag:<12} {info}")
        if not ok:
            bad += 1
        time.sleep(0.5)

    print(f"\n结论：{'全部可查证' if bad == 0 else f'{bad} 条需人工核对'}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
