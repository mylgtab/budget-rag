"""生成 README 用的终端演示 GIF（纯 Pillow 渲染，不录屏）。

python scripts/make_demo_gif.py
产出 docs/figures/demo.gif
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 860, 520
BG = (24, 26, 32)
FG = (220, 223, 228)
GREEN = (126, 217, 138)
BLUE = (130, 170, 255)
GREY = (130, 135, 145)
YELLOW = (240, 200, 120)

SCENES = [
    ("$ python scripts/eval.py --set data/eval_500.jsonl --llm", BLUE, 22),
    ("", FG, 6),
    ("  [1/500] retrieve → generate → score", GREY, 10),
    ("  [120/500] ...", GREY, 10),
    ("  [340/500] ...", GREY, 10),
    ("  [500/500] done in 3.5 min", GREY, 14),
    ("", FG, 8),
    ('{', FG, 2),
    ('  "n": 500,', FG, 4),
    ('  "recall@3": 0.946,', FG, 4),
    ('  "em": 0.614,', FG, 4),
    ('  "contain": 0.920,', GREEN, 4),
    ('  "cost_rmb": 0.002034,', YELLOW, 4),
    ('  "billed_pct": 1.0', YELLOW, 4),
    ('}', FG, 14),
    ("", FG, 8),
    ("$ python scripts/rewrite_gate.py --tokens 300", BLUE, 22),
    ("  off     recall 0.912   rewrite   0%", GREY, 12),
    ("  always  recall 0.966   rewrite 100%", GREY, 12),
    ("  auto    recall 0.948   rewrite  38%   ← 38% 的钱，67% 的收益", GREEN, 26),
]


def font(size: int):
    for name in ("msyh.ttc", "msyhbd.ttc", "consola.ttf"):
        p = Path("C:/Windows/Fonts") / name
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()


def render(lines: list[tuple[str, tuple, int]], title: str = "budget-rag") -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # 顶栏
    d.rectangle([0, 0, W, 34], fill=(38, 41, 49))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([14 + i * 22, 11, 26 + i * 22, 23], fill=c)
    d.text((W // 2 - 40, 8), title, font=font(15), fill=GREY)

    f = font(17)
    y = 52
    for text, color, pad in lines:
        if text:
            d.text((22, y), text, font=f, fill=color)
            y += 24
        y += pad
        if y > H - 30:
            break
    return img


def main() -> int:
    frames: list[Image.Image] = []
    visible: list[tuple[str, tuple, int]] = []

    # 逐行出现
    for line in SCENES:
        visible.append(line)
        frames.append(render(visible))
        frames.append(render(visible))   # 每行停两帧

    # 结尾多停一会儿（用最后一行闪烁光标感）
    for _ in range(6):
        frames.append(render(visible))

    out = Path("docs/figures/demo.gif")
    out.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=180, loop=0)
    print(f"GIF: {out}  帧数={len(frames)}  大小={out.stat().st_size/1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
