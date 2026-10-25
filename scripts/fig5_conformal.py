"""图 5：保形校准的覆盖率诊断（名义 vs 经验，含 5% 分位与预算标注）。"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"
SCALE = 2


def font(size: int):
    for name in ("msyh.ttc", "simhei.ttf", "arial.ttf"):
        f = Path("C:/Windows/Fonts") / name
        if f.exists():
            try:
                return ImageFont.truetype(str(f), size * SCALE)
            except Exception:
                continue
    return ImageFont.load_default()


def main() -> int:
    rows = json.loads((ROOT / "results" / "conformal_sweep_hybrid.json").read_text(encoding="utf-8"))
    rows = [r for r in rows if r.get("coverage")]

    W, H = 760 * SCALE, 520 * SCALE
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    ml, mr, mt, mb = 140 * SCALE, 70 * SCALE, 60 * SCALE, 70 * SCALE
    x0, y0 = ml, mt
    w, h = W - ml - mr, H - mt - mb

    xmin, xmax = 0.45, 1.0
    ymin, ymax = 0.30, 1.0

    def sx(v):
        return x0 + (v - xmin) / (xmax - xmin) * w

    def sy(v):
        return y0 + h - (v - ymin) / (ymax - ymin) * h

    f_tick, f_lab, f_note = font(10), font(12), font(9)

    for r in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        d.line([(x0, sy(r)), (x0 + w, sy(r))], fill=(236, 239, 241), width=SCALE)
        d.text((x0 - 8 * SCALE, sy(r)), f"{r:.1f}", font=f_tick, fill=(96, 125, 139), anchor="rm")
    for v in (0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95):
        d.text((sx(v), y0 + h + 18 * SCALE), f"{v:.2f}", font=f_tick, fill=(96, 125, 139), anchor="mm")

    # 对角线
    d.line([(sx(0.5), sy(0.5)), (sx(0.95), sy(0.95))], fill=(150, 150, 150), width=SCALE)
    d.text((sx(0.64), sy(0.665)), "nominal = empirical", font=f_note, fill=(120, 120, 120), anchor="lm")

    # 数据点与区间
    for i, r in enumerate(rows):
        x, y = sx(r["nominal"]), sy(r["coverage"])
        lo = sy(min(r.get("coverage_p05", r["coverage"]), r["coverage"]))
        d.line([(x, sy(r["coverage"])), (x, lo)], fill=(180, 180, 180), width=SCALE)
        rad = 4 * SCALE
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(43, 108, 176))
        d.text((x + 8 * SCALE, y - (14 if i % 2 else 4) * SCALE), f"{r['budget']:.0f}tok",
               font=f_note, fill=(60, 90, 130), anchor="lm")
        if r.get("refusal_rate", 0) > 0:
            d.text((x + 7 * SCALE, y + 6 * SCALE), f"refuse {r['refusal_rate']*100:.0f}%",
                   font=f_note, fill=(176, 58, 58), anchor="lm")

    d.line([(x0, y0), (x0, y0 + h), (x0 + w, y0 + h)], fill=(55, 71, 79), width=SCALE)
    d.text((x0 + w / 2, y0 + h + 46 * SCALE), "nominal coverage (1 - alpha)",
           font=f_lab, fill=(55, 71, 79), anchor="mm")
    d.text((12 * SCALE, y0 + h / 2), "empirical coverage",
           font=f_lab, fill=(55, 71, 79), anchor="lm")
    d.text((x0, 24 * SCALE), "Conformal calibration, hybrid retriever, 143 questions",
           font=f_lab, fill=(30, 30, 30), anchor="lm")

    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / "fig5-conformal.png")
    print("生成", OUT / "fig5-conformal.png", img.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
