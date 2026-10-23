"""生成论文图 2（预算-召回曲线）与图 3（消融柱状图）。

零依赖，直接输出 SVG。
python scripts/make_paper_figures.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 报告 4.5 / 4.13 的实测值
BUDGET_CURVE = {
    "sentence": [(80, 0.850), (200, 0.892), (300, 0.912), (500, 0.928), (800, 0.938)],
    "fixed": [(80, 0.800), (200, 0.836), (300, 0.894), (500, 0.918), (800, 0.954)],
}

ABLATION = [
    ("完整系统", 0.960, "#2b6cb0"),
    ("去掉门控", 0.924, "#e07b39"),
    ("混合权重 0.5", 0.943, "#e07b39"),
    ("预算 300→100", 0.899, "#e07b39"),
    ("去掉混合", 0.892, "#e07b39"),
]


def line_chart(series: dict[str, list[tuple[int, float]]], path: Path) -> None:
    w, h, ml, mr, mt, mb = 680, 420, 78, 130, 34, 62
    xs = [p[0] for pts in series.values() for p in pts]
    ys = [p[1] for pts in series.values() for p in pts]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys) - 0.04, max(ys) + 0.03

    def sx(v: float) -> float:
        return ml + (v - x0) / (x1 - x0) * (w - ml - mr)

    def sy(v: float) -> float:
        return h - mb - (v - y0) / (y1 - y0) * (h - mt - mb)

    colors = {"sentence": "#2b6cb0", "fixed": "#c53030"}
    labels = {"sentence": "句级索引", "fixed": "固定块索引"}

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'font-family="system-ui,-apple-system,sans-serif">',
        f'<rect width="{w}" height="{h}" fill="white"/>',
    ]
    for i in range(5):
        v = y0 + (y1 - y0) * i / 4
        y = sy(v)
        parts.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{w - mr}" y2="{y:.1f}" stroke="#eceff1"/>')
        parts.append(f'<text x="{ml - 10}" y="{y + 4:.1f}" font-size="11" fill="#607d8b" '
                     f'text-anchor="end">{v:.2f}</text>')
    for v in (100, 200, 300, 500, 800):
        x = sx(v)
        parts.append(f'<text x="{x:.1f}" y="{h - mb + 20}" font-size="11" fill="#607d8b" '
                     f'text-anchor="middle">{v}</text>')
    parts.append(f'<line x1="{ml}" y1="{h - mb}" x2="{w - mr}" y2="{h - mb}" stroke="#37474f"/>')
    parts.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{h - mb}" stroke="#37474f"/>')

    for name, pts in series.items():
        c = colors[name]
        d = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in pts)
        parts.append(f'<polyline points="{d}" fill="none" stroke="{c}" stroke-width="2.5"/>')
        for x, y in pts:
            parts.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" fill="{c}"/>')
            parts.append(f'<text x="{sx(x):.1f}" y="{sy(y) - 11:.1f}" font-size="10" '
                         f'fill="{c}" text-anchor="middle">{y:.3f}</text>')

    # 图例
    for i, name in enumerate(series):
        ly = mt + 14 + i * 22
        parts.append(f'<line x1="{w - mr + 18}" y1="{ly}" x2="{w - mr + 44}" y2="{ly}" '
                     f'stroke="{colors[name]}" stroke-width="2.5"/>')
        parts.append(f'<text x="{w - mr + 50}" y="{ly + 4}" font-size="11" fill="#37474f">'
                     f'{labels[name]}</text>')

    parts.append(f'<text x="{(ml + w - mr) / 2}" y="{h - 16}" font-size="12" fill="#37474f" '
                 f'text-anchor="middle">上下文预算（token）</text>')
    parts.append(f'<text x="24" y="{(mt + h - mb) / 2}" font-size="12" fill="#37474f" '
                 f'transform="rotate(-90 24 {(mt + h - mb) / 2})" text-anchor="middle">'
                 f'答案片段召回率</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def bar_chart(rows: list[tuple[str, float, str]], path: Path) -> None:
    w, h = 680, 340
    ml, mr, mt, mb = 150, 90, 40, 50
    base = 0.85
    top = 0.97

    def sx(v: float) -> float:
        return ml + (v - base) / (top - base) * (w - ml - mr)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'font-family="system-ui,-apple-system,sans-serif">',
        f'<rect width="{w}" height="{h}" fill="white"/>',
    ]
    for v in (0.86, 0.88, 0.90, 0.92, 0.94, 0.96):
        x = sx(v)
        parts.append(f'<line x1="{x:.1f}" y1="{mt - 10}" x2="{x:.1f}" y2="{h - mb}" stroke="#eceff1"/>')
        parts.append(f'<text x="{x:.1f}" y="{h - mb + 18}" font-size="11" fill="#607d8b" '
                     f'text-anchor="middle">{v:.2f}</text>')
    parts.append(f'<line x1="{ml}" y1="{h - mb}" x2="{w - mr}" y2="{h - mb}" stroke="#37474f"/>')

    bar_h = 34
    gap = 14
    for i, (label, value, color) in enumerate(rows):
        y = mt + i * (bar_h + gap)
        x_end = sx(value)
        parts.append(f'<rect x="{ml}" y="{y}" width="{max(1.5, x_end - ml):.1f}" height="{bar_h}" '
                     f'fill="{color}" opacity="0.88" rx="3"/>')
        parts.append(f'<text x="{ml - 12}" y="{y + bar_h / 2 + 4}" font-size="12" fill="#37474f" '
                     f'text-anchor="end">{label}</text>')
        delta = (value - 0.960) * 100
        tag = f"{value:.3f}" if abs(delta) < 0.01 else f"{value:.3f}（{delta:+.1f} pt）"
        parts.append(f'<text x="{x_end + 8:.1f}" y="{y + bar_h / 2 + 4}" font-size="11" '
                     f'fill="#37474f">{tag}</text>')

    parts.append(f'<text x="{(ml + w - mr) / 2}" y="{h - 12}" font-size="12" fill="#37474f" '
                 f'text-anchor="middle">答案片段召回率</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


# ---------- PNG（Word 需要位图，SVG 插不进去）----------

def _font(size: int):
    from PIL import ImageFont

    for name in ("msyh.ttc", "simhei.ttf", "arial.ttf"):
        f = Path("C:/Windows/Fonts") / name
        if f.exists():
            try:
                return ImageFont.truetype(str(f), size)
            except Exception:
                continue
    return ImageFont.load_default()


def _draw_vertical(d, text: str, xy, font, fill, scale: int = 2):
    """把文字画到临时图再旋转 90°，避免 PIL 不支持文字旋转。"""
    from PIL import Image

    tmp = Image.new("RGBA", (int(font.size * (len(text) + 1)), int(font.size * 2)), (255, 255, 255, 0))
    from PIL import ImageDraw

    ImageDraw.Draw(tmp).text((2, 2), text, font=font, fill=fill)
    rot = tmp.rotate(90, expand=True)
    d._image.paste(rot, (int(xy[0]), int(xy[1])), rot)


def png_line_chart(series, path: Path, scale: int = 2) -> None:
    from PIL import Image, ImageDraw

    w, h, ml, mr, mt, mb = 680 * scale, 420 * scale, 78 * scale, 130 * scale, 34 * scale, 62 * scale
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    d._image = img
    xs = [p[0] for pts in series.values() for p in pts]
    ys = [p[1] for pts in series.values() for p in pts]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys) - 0.04, max(ys) + 0.03
    sx = lambda v: ml + (v - x0) / (x1 - x0) * (w - ml - mr)
    sy = lambda v: h - mb - (v - y0) / (y1 - y0) * (h - mt - mb)
    fs, fs2 = _font(11 * scale), _font(12 * scale)

    for i in range(5):
        v = y0 + (y1 - y0) * i / 4
        y = sy(v)
        d.line([(ml, y), (w - mr, y)], fill=(236, 239, 241), width=scale)
        d.text((ml - 10 * scale, y), f"{v:.2f}", font=fs, fill=(96, 125, 139), anchor="rm")
    for v in (100, 200, 300, 500, 800):
        d.text((sx(v), h - mb + 20 * scale), str(v), font=fs, fill=(96, 125, 139), anchor="mm")
    d.line([(ml, h - mb), (w - mr, h - mb)], fill=(55, 71, 79), width=scale)
    d.line([(ml, mt), (ml, h - mb)], fill=(55, 71, 79), width=scale)

    colors = {"sentence": (43, 108, 176), "fixed": (197, 48, 48)}
    labels = {"sentence": "句级索引", "fixed": "固定块索引"}
    for name, pts in series.items():
        c = colors[name]
        d.line([(sx(x), sy(y)) for x, y in pts], fill=c, width=3 * scale, joint="curve")
        for x, y in pts:
            r = 4 * scale
            d.ellipse([sx(x) - r, sy(y) - r, sx(x) + r, sy(y) + r], fill=c)
            d.text((sx(x), sy(y) - 11 * scale), f"{y:.3f}", font=_font(10 * scale), fill=c, anchor="mb")
    for i, name in enumerate(series):
        ly = mt + 14 * scale + i * 22 * scale
        d.line([(w - mr + 18 * scale, ly), (w - mr + 44 * scale, ly)], fill=colors[name], width=3 * scale)
        d.text((w - mr + 50 * scale, ly), labels[name], font=fs, fill=(55, 71, 79), anchor="lm")
    d.text(((ml + w - mr) / 2, h - 16 * scale), "上下文预算（token）", font=fs2, fill=(55, 71, 79), anchor="mm")
    _draw_vertical(d, "召回率", (10 * scale, (mt + h - mb) / 2 - 40 * scale), fs2, (55, 71, 79), scale)
    img.save(path)


def png_bar_chart(rows, path: Path, scale: int = 2) -> None:
    from PIL import Image, ImageDraw

    w, h = 680 * scale, 340 * scale
    ml, mr, mt, mb = 150 * scale, 90 * scale, 40 * scale, 50 * scale
    base, top = 0.85, 0.97
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    sx = lambda v: ml + (v - base) / (top - base) * (w - ml - mr)
    fs, fs2, fs3 = _font(11 * scale), _font(12 * scale), _font(13 * scale)

    for v in (0.86, 0.88, 0.90, 0.92, 0.94, 0.96):
        x = sx(v)
        d.line([(x, mt - 10 * scale), (x, h - mb)], fill=(236, 239, 241), width=scale)
        d.text((x, h - mb + 18 * scale), f"{v:.2f}", font=fs, fill=(96, 125, 139), anchor="mm")
    d.line([(ml, h - mb), (w - mr, h - mb)], fill=(55, 71, 79), width=scale)

    bar_h, gap = 34 * scale, 14 * scale
    for i, (label, value, color) in enumerate(rows):
        y = mt + i * (bar_h + gap)
        rgb = {"#2b6cb0": (43, 108, 176), "#e07b39": (224, 123, 57)}.get(color, (120, 120, 120))
        d.rounded_rectangle([ml, y, max(ml + 2 * scale, sx(value)), y + bar_h], radius=3 * scale, fill=rgb)
        d.text((ml - 12 * scale, y + bar_h / 2), label, font=fs3, fill=(55, 71, 79), anchor="rm")
        delta = (value - 0.960) * 100
        tag = f"{value:.3f}" if abs(delta) < 0.01 else f"{value:.3f}（{delta:+.1f} pt）"
        d.text((sx(value) + 8 * scale, y + bar_h / 2), tag, font=fs, fill=(55, 71, 79), anchor="lm")
    d.text(((ml + w - mr) / 2, h - 12 * scale), "召回率", font=fs2, fill=(55, 71, 79), anchor="mm")
    img.save(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/figures")
    args = ap.parse_args()
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)

    line_chart(BUDGET_CURVE, out / "fig2-budget-recall.svg")
    bar_chart(ABLATION, out / "fig3-ablation.svg")
    try:
        png_line_chart(BUDGET_CURVE, out / "fig2-budget-recall.png")
        png_bar_chart(ABLATION, out / "fig3-ablation.png")
    except ImportError:
        print("提示：当前解释器没有 Pillow，跳过 PNG（Word 插图需要它）")
    for name in ("fig2-budget-recall.svg", "fig2-budget-recall.png",
                 "fig3-ablation.svg", "fig3-ablation.png"):
        print(f"生成: {out / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
