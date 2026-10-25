"""画图 4：预算-召回曲线 + 安全边际对达标率的影响（Pillow，无 matplotlib）。"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"
SCALE = 2

CURVES = ["BM25", "Dense (bge-large)", "Dense (bge-m3)", "Hybrid (bge-m3)"]
COLORS = {
    "BM25": (120, 120, 120),
    "Dense (bge-large)": (197, 148, 48),
    "Dense (bge-m3)": (43, 108, 176),
    "Hybrid (bge-m3)": (176, 58, 58),
}
TARGETS = [(0.80, (140, 170, 140)), (0.85, (170, 150, 110)), (0.90, (150, 140, 170))]
MARGINS = [0.0, 0.03, 0.05, 0.10]
REACH = {  # 来自 results/calibration_hybrid.json
    0.80: [0.83, 0.90, 0.93, 0.97],
    0.85: [0.63, 0.77, 0.83, 0.95],
    0.90: [0.59, 0.71, 0.76, 1.00],
}


def font(size: int):
    for name in ("msyh.ttc", "simhei.ttf", "arial.ttf"):
        f = Path("C:/Windows/Fonts") / name
        if f.exists():
            try:
                return ImageFont.truetype(str(f), size * SCALE)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_panel_a(d, x0, y0, w, h, data):
    budgets = data["budgets"]
    curves = data["curves"]
    f_tick, f_lab, f_leg = font(10), font(12), font(10)

    xmin, xmax = 30, 1500
    ymin, ymax = 0.0, 1.0

    def sx(v):
        # 对数横轴：预算跨两个数量级
        import math
        a, b = math.log10(xmin), math.log10(xmax)
        return x0 + (math.log10(max(v, xmin)) - a) / (b - a) * w

    def sy(v):
        return y0 + h - (v - ymin) / (ymax - ymin) * h

    # 网格
    for r in (0.2, 0.4, 0.6, 0.8, 1.0):
        d.line([(x0, sy(r)), (x0 + w, sy(r))], fill=(236, 239, 241), width=SCALE)
        d.text((x0 - 8 * SCALE, sy(r)), f"{r:.1f}", font=f_tick, fill=(96, 125, 139), anchor="rm")
    for b in (50, 100, 200, 500, 1000):
        d.text((sx(b), y0 + h + 16 * SCALE), str(b), font=f_tick, fill=(96, 125, 139), anchor="mm")

    # 目标线
    for t, c in TARGETS:
        y = sy(t)
        for i in range(0, int(w), 14 * SCALE):
            d.line([(x0 + i, y), (x0 + min(i + 7 * SCALE, w), y)], fill=c, width=SCALE)
        d.text((x0 + w + 4 * SCALE, y), f"{t:.2f}", font=f_tick, fill=c, anchor="lm")

    # 曲线
    for name in CURVES:
        pts = [(sx(b), sy(v)) for b, v in zip(budgets, curves[name])]
        d.line(pts, fill=COLORS[name], width=2 * SCALE, joint="curve")
        for p in pts:
            r = 3 * SCALE
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=COLORS[name])

    # 图例
    for i, name in enumerate(CURVES):
        lx = x0 + w - 210 * SCALE + (i % 2) * 100 * SCALE
        ly = y0 + h - 52 * SCALE + (i // 2) * 18 * SCALE
        d.line([(lx, ly), (lx + 18 * SCALE, ly)], fill=COLORS[name], width=2 * SCALE)
        d.text((lx + 24 * SCALE, ly), name, font=f_leg, fill=(55, 71, 79), anchor="lm")

    d.line([(x0, y0), (x0, y0 + h), (x0 + w, y0 + h)], fill=(55, 71, 79), width=SCALE)
    d.text((x0 + w / 2, y0 + h + 40 * SCALE), "context budget (tokens, log scale)",
           font=f_lab, fill=(55, 71, 79), anchor="mm")
    d.text((14 * SCALE, y0 + h / 2), "recall", font=f_lab, fill=(55, 71, 79), anchor="mm")


def draw_panel_b(d, x0, y0, w, h):
    f_tick, f_lab, f_leg = font(10), font(12), font(10)
    xs = MARGINS

    def sx(v):
        return x0 + (v / max(xs)) * w

    def sy(v):
        return y0 + h - v * h

    for r in (0.0, 0.25, 0.5, 0.75, 1.0):
        d.line([(x0, sy(r)), (x0 + w, sy(r))], fill=(236, 239, 241), width=SCALE)
        d.text((x0 - 8 * SCALE, sy(r)), f"{r:.2f}", font=f_tick, fill=(96, 125, 139), anchor="rm")
    for v in xs:
        d.text((sx(v), y0 + h + 16 * SCALE), f"{v:.2f}", font=f_tick, fill=(96, 125, 139), anchor="mm")

    for t in (0.80, 0.90):
        c = (43, 108, 176) if t == 0.80 else (176, 58, 58)
        pts = [(sx(x), sy(y)) for x, y in zip(xs, REACH[t])]
        d.line(pts, fill=c, width=2 * SCALE, joint="curve")
        for p in pts:
            r = 3 * SCALE
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=c)
        dy = -12 * SCALE if t >= 0.90 else 12 * SCALE
        d.text((sx(xs[-1]) - 20 * SCALE, sy(REACH[t][-1]) + dy), f"target {t:.2f}",
               font=f_leg, fill=c, anchor="rm")

    d.line([(x0, y0), (x0, y0 + h), (x0 + w, y0 + h)], fill=(55, 71, 79), width=SCALE)
    d.text((x0 + w / 2, y0 + h + 40 * SCALE), "safety margin delta",
           font=f_lab, fill=(55, 71, 79), anchor="mm")
    d.text((x0 - 74 * SCALE, y0 + h / 2), "reach rate", font=f_lab, fill=(55, 71, 79), anchor="mm")


def main() -> int:
    data = json.loads((ROOT / "results" / "calibration_curves.json").read_text(encoding="utf-8"))
    W, H = 1180 * SCALE, 420 * SCALE
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    panel_w, panel_h = 470 * SCALE, 300 * SCALE
    draw_panel_a(d, 60 * SCALE, 40 * SCALE, panel_w, panel_h, data)
    draw_panel_b(d, 660 * SCALE, 40 * SCALE, 380 * SCALE, panel_h)

    d.text((110 * SCALE, 10 * SCALE), "A  budget-recall curves (143 questions, 312 docs)",
           font=font(12), fill=(30, 30, 30))
    d.text((730 * SCALE, 10 * SCALE), "B  reach rate vs safety margin (hybrid)",
           font=font(12), fill=(30, 30, 30))

    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / "fig4-calibration.png")
    print("生成", OUT / "fig4-calibration.png", f"{img.size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
