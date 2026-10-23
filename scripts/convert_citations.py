"""把英文稿的作者-年引用转成 MDPI 数字引用，并重排参考文献表。

做法：先按出现位置统一编号（叙述式「作者 [年]」与方括号「[作者, 年]」一起扫），
再从后往前替换，保证编号与出现顺序一致。

python scripts/convert_citations.py --src docs/paper-en.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CITE_TO_KEY = {
    "Lewis et al., 2020": "Lewis",
    "Robertson and Zaragoza, 2009": "Robertson",
    "Karpukhin et al., 2020": "Karpukhin",
    "Liu et al., 2024": "Liu",
    "Jiang Z. et al., 2023": "Jiang Z",
    "Jiang H. et al., 2023": "Jiang H 2023",
    "Jiang H. et al., 2024": "Jiang H 2024",
    "Asai et al., 2024": "Asai",
    "Wang et al., 2023": "Wang",
    "Jeong et al., 2024": "Jeong",
    "Press et al., 2023": "Press",
    "Trivedi et al., 2023": "Trivedi",
    "Yan et al., 2024": "Yan",
    "Wu et al., 2026": "Wu",
    "Xu et al., 2024": "Xu",
    "Nogueira et al., 2020": "Nogueira",
    "Sun et al., 2023": "Sun",
    "Gao et al., 2023": "Gao",
    "Ma et al., 2023": "Ma",
    "Carbonell and Goldstein, 1998": "Carbonell",
    "Nemhauser et al., 1978": "Nemhauser",
    "Khuller et al., 1999": "Khuller",
    "Wald, 1947": "Wald",
    "Chen et al., 2023": "Chen",
    "Lin and Bilmes, 2011": "Lin",
    # 表格里的无逗号写法
    "Jiang Z. 2023": "Jiang Z",
    "Asai 2024": "Asai",
    "Jeong 2024": "Jeong",
    "Press 2023": "Press",
    "Trivedi 2023": "Trivedi",
    "Yan 2024": "Yan",
    "Wu 2026": "Wu",
    "Xu 2024": "Xu",
    "Nogueira 2020": "Nogueira",
    "Sun 2023": "Sun",
    "Carbonell and Goldstein 1998": "Carbonell",
    "Nemhauser 1978": "Nemhauser",
    "Khuller 1999": "Khuller",
    "Wald 1947": "Wald",
    "Chen 2023": "Chen",
    "Lin and Bilmes 2011": "Lin",
}

KEY_TO_REF = {
    "Asai": "**Asai, A.",
    "Carbonell": "**Carbonell, J.",
    "Chen": "**Chen, L.",
    "Gao": "**Gao, L.",
    "Jeong": "**Jeong, S.",
    "Jiang H 2023": "**Jiang, H.; Wu, Q.; Lin, C.-Y.",
    "Jiang H 2024": "**Jiang, H.; Wu, Q.; Luo, X.",
    "Jiang Z": "**Jiang, Z.; Xu, F. F.",
    "Karpukhin": "**Karpukhin, V.",
    "Khuller": "**Khuller, S.",
    "Lewis": "**Lewis, P.",
    "Lin": "**Lin, H.",
    "Liu": "**Liu, N. F.",
    "Ma": "**Ma, X.",
    "Nemhauser": "**Nemhauser, G. L.",
    "Nogueira": "**Nogueira, R.",
    "Press": "**Press, O.",
    "Robertson": "**Robertson, S.",
    "Sun": "**Sun, W.",
    "Trivedi": "**Trivedi, H.",
    "Wald": "**Wald, A.",
    "Wang": "**Wang, Y.",
    "Wu": "**Wu, M.",
    "Xu": "**Xu, F.",
    "Yan": "**Yan, S.-Q.",
}

NARRATIVE = re.compile(r"([A-Z][A-Za-z\-]+(?: (?:et al\.|and [A-Z][A-Za-z\-]+))?) \[(\d{4})\]")
BRACKET = re.compile(r"\[([^\]\[]*\b(?:19|20)\d\d[^\]]*)\]")
COMBINED = "Jiang H. 2023/2024"


def resolve(part: str) -> str | None:
    return CITE_TO_KEY.get(part.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="docs/paper-en.md")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    src = ROOT / args.src
    out = ROOT / (args.out or args.src)
    text = src.read_text(encoding="utf-8")

    m = re.search(r"^## References\s*$", text, flags=re.M)
    if not m:
        raise SystemExit("找不到 References 段")
    body, tail = text[: m.start()], text[m.start():]

    events: list[tuple[int, str, str]] = []
    for mm in NARRATIVE.finditer(body):
        events.append((mm.start(), "narr", f"{mm.group(1)}, {mm.group(2)}"))
    for mm in BRACKET.finditer(body):
        events.append((mm.start(), "bracket", mm.group(1)))
    events.sort()

    order: dict[str, int] = {}
    missing: set[str] = set()

    def num_of(key: str) -> int:
        if key not in order:
            order[key] = len(order) + 1
        return order[key]

    for _, kind, payload in events:
        if kind == "narr":
            key = resolve(payload)
            if key is None:
                missing.add(payload)
            else:
                num_of(key)
        else:
            for part in payload.split(";"):
                if part.strip() == COMBINED:
                    num_of("Jiang H 2023")
                    num_of("Jiang H 2024")
                    continue
                key = resolve(part)
                if key is None:
                    missing.add(part.strip())
                else:
                    num_of(key)

    def narr_repl(mm: re.Match) -> str:
        key = resolve(f"{mm.group(1)}, {mm.group(2)}")
        return f"{mm.group(1)} [{num_of(key)}]" if key else mm.group(0)

    def bracket_repl(mm: re.Match) -> str:
        nums: list[str] = []
        for part in mm.group(1).split(";"):
            if part.strip() == COMBINED:
                nums += [str(order["Jiang H 2023"]), str(order["Jiang H 2024"])]
                continue
            key = resolve(part)
            nums.append(str(order[key]) if key else "?")
        return "[" + ",".join(nums) + "]"

    for mm in reversed(list(NARRATIVE.finditer(body))):
        body = body[: mm.start()] + narr_repl(mm) + body[mm.end():]
    for mm in reversed(list(BRACKET.finditer(body))):
        body = body[: mm.start()] + bracket_repl(mm) + body[mm.end():]

    ref_block: dict[str, str] = {}
    for ln in tail.splitlines():
        if not ln.startswith("- **"):
            continue
        for key, sig in KEY_TO_REF.items():
            if ln.startswith("- " + sig):
                ref_block[key] = ln[2:]

    lacking = [k for k in order if k not in ref_block]
    if lacking:
        raise SystemExit(f"这些引用找不到文献条目: {lacking}")

    used = [ref_block[k] for k in order]
    unused = [v for k, v in ref_block.items() if k not in order]

    decl_start = tail.find("## Declarations")
    declarations = tail[decl_start:] if decl_start > 0 else ""

    new_tail = "## References\n\n" + "\n".join(f"{i}. {ln}" for i, ln in enumerate(used, 1)) + "\n\n"
    if unused:
        new_tail += "## References (not cited in text)\n\n" + "\n".join(f"- {ln}" for ln in unused) + "\n\n"

    out.write_text(body.rstrip() + "\n\n" + new_tail + declarations, encoding="utf-8")

    print(f"引用编号 {len(order)} 条；未引用文献 {len(unused)} 条")
    if missing:
        print("未匹配（需人工）:", sorted(missing))
    print("编号顺序：")
    for k, n in order.items():
        print(f"  [{n}] {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
