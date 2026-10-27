# -*- coding: utf-8 -*-
"""根据 JSON 规格绘制 Orange Canvas 风格的工作流示意图。

用法：
    python orange_style_diagram.py spec.json out.png

这不是 Orange 截图，只是按 Orange 控件/连线风格绘制的示意图。
"""
import json
import math
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
BOLD_CANDIDATES = [
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
]

DEFAULT_COLORS = {
    "file": "#4c8bf5",
    "cols": "#7b61ff",
    "sliders": "#f2a900",
    "box": "#16a085",
    "curve": "#e74c3c",
    "table": "#607d8b",
    "scatter": "#8e44ad",
    "tree": "#2e7d32",
    "cluster": "#d35400",
    "gear": "#7f8c8d",
    "text": "#455a64",
    "confusion": "#c0392b",
}


def pick_font(candidates, size):
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


class Canvas:
    def __init__(self, spec):
        self.spec = spec
        self.widgets = spec.get("widgets", [])
        if not self.widgets:
            raise ValueError("spec 至少需要一个 widget")
        self.W = int(spec.get("width") or 0)
        self.H = int(spec.get("height") or 0)
        if not self.W or not self.H:
            max_x = max(w["x"] + w.get("w", 180) for w in self.widgets)
            max_y = max(w["y"] + w.get("h", 100) for w in self.widgets)
            note = spec.get("note") or {}
            if note:
                max_x = max(max_x, note.get("x", 0) + note.get("w", 0))
                max_y = max(max_y, note.get("y", 0) + note.get("h", 0))
            self.W = self.W or max(1200, max_x + 260)
            self.H = self.H or max(650, max_y + 170)
        self.img = Image.new("RGB", (self.W, self.H), "#f7f7f7")
        self.d = ImageDraw.Draw(self.img)
        self.fonts = {}
        self.pads = {}

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = pick_font(BOLD_CANDIDATES if bold else FONT_CANDIDATES, size)
        return self.fonts[key]

    def text_w(self, text, size, bold=False):
        return self.d.textlength(text, font=self.font(size, bold))

    def fit_size(self, text, max_w, base, bold=False, minimum=10):
        size = base
        while size > minimum and self.text_w(text, size, bold) > max_w:
            size -= 1
        return size

    def top_bar(self):
        d = self.d
        d.rectangle((0, 0, self.W, 58), fill="white")
        d.line((0, 58, self.W, 58), fill="#d0d0d0", width=2)
        d.ellipse((22, 14, 52, 44), fill="#f57c00")
        d.text((37, 29), "O", font=self.font(22, True), fill="white", anchor="mm")
        d.text((64, 29), "Orange", font=self.font(26, True), fill="#333333", anchor="lm")
        subtitle = self.spec.get("subtitle", "")
        if subtitle:
            d.text((180, 31), subtitle, font=self.font(16), fill="#888888", anchor="lm")
        for i, menu in enumerate(["File", "Edit", "View", "Widget", "Options", "Help"]):
            d.text((self.W - 520 + i * 82, 30), menu, font=self.font(16), fill="#666666", anchor="lm")

    def dot_grid(self):
        for y in range(70, self.H, 32):
            for x in range(0, self.W, 32):
                self.d.ellipse((x, y, x + 2, y + 2), fill="#dedede")

    def widget(self, w):
        d = self.d
        x, y = int(w["x"]), int(w["y"])
        ww, hh = int(w.get("w", 180)), int(w.get("h", 100))
        title = w.get("title", "Widget")
        sub = w.get("sub", "")
        glyph = w.get("glyph", "gear")
        color = w.get("color") or DEFAULT_COLORS.get(glyph, "#7f8c8d")
        selected = bool(w.get("selected"))

        d.rounded_rectangle((x + 5, y + 6, x + ww + 5, y + hh + 6), radius=14, fill="#e2e2e2")
        d.rounded_rectangle(
            (x, y, x + ww, y + hh), radius=14, fill="white",
            outline="#f57c00" if selected else "#b9b9b9",
            width=4 if selected else 2,
        )

        ix, iy = x + 16, y + 16
        d.rounded_rectangle((ix, iy, ix + 38, iy + 38), radius=8, fill=color)
        self.glyph(glyph, ix + 19, iy + 19)

        title_size = self.fit_size(title, ww - 74, 21, True)
        d.text((x + 64, y + 25), title, font=self.font(title_size, True), fill="#2f2f2f", anchor="lm")
        if sub:
            sub_size = self.fit_size(sub, ww - 28, 14)
            d.text((x + 16, y + 72), sub, font=self.font(sub_size), fill="#808080", anchor="lm")

        in_pt = out_pt = None
        if w.get("inputs", True):
            in_pt = (x - 2, y + hh // 2)
            d.ellipse((x - 7, y + hh // 2 - 7, x + 7, y + hh // 2 + 7),
                      fill="#a8a8a8", outline="white", width=2)
        if w.get("outputs", True):
            out_pt = (x + ww + 2, y + hh // 2)
            d.ellipse((x + ww - 7, y + hh // 2 - 7, x + ww + 7, y + hh // 2 + 7),
                      fill=color, outline="white", width=2)
        self.pads[w["id"]] = {"in": in_pt, "out": out_pt, "color": color}

    def glyph(self, kind, gx, gy):
        d = self.d
        if kind == "file":
            d.rectangle((gx - 9, gy - 12, gx + 9, gy + 12), outline="white", width=2)
            for k in range(3):
                d.line((gx - 6, gy - 6 + k * 6, gx + 6, gy - 6 + k * 6), fill="white", width=2)
        elif kind == "cols":
            for k in range(3):
                d.rectangle((gx - 13 + k * 9, gy - 10, gx - 8 + k * 9, gy + 10), fill="white")
        elif kind == "sliders":
            for k, yy in enumerate((-8, 0, 8)):
                d.line((gx - 12, gy + yy, gx + 12, gy + yy), fill="white", width=2)
                d.ellipse((gx - 4 + k * 5, gy + yy - 4, gx + 4 + k * 5, gy + yy + 4), fill="white")
        elif kind == "box":
            d.rectangle((gx - 13, gy - 7, gx + 3, gy + 7), outline="white", width=2)
            d.line((gx - 13, gy, gx - 18, gy), fill="white", width=3)
            d.line((gx + 3, gy, gx + 9, gy), fill="white", width=3)
            d.line((gx - 18, gy - 5, gx - 18, gy + 5), fill="white", width=2)
            d.line((gx + 9, gy - 5, gx + 9, gy + 5), fill="white", width=2)
        elif kind == "curve":
            pts = []
            for i in range(30):
                xx = -13 + i * 26 / 29
                yy = 13 * math.exp(-(xx ** 2) / 70)
                pts.append((gx + xx, gy + 10 - yy))
            d.line(pts, fill="white", width=3)
            d.line((gx - 15, gy + 11, gx + 15, gy + 11), fill="white", width=2)
        elif kind == "table":
            d.rectangle((gx - 12, gy - 10, gx + 12, gy + 10), outline="white", width=2)
            d.line((gx - 12, gy - 2, gx + 12, gy - 2), fill="white", width=2)
            d.line((gx - 2, gy - 10, gx - 2, gy + 10), fill="white", width=2)
        elif kind == "scatter":
            for dx, dy in [(-8, 6), (-2, -5), (5, 3), (9, -7), (0, 0)]:
                d.ellipse((gx + dx - 3, gy + dy - 3, gx + dx + 3, gy + dy + 3), fill="white")
        elif kind == "tree":
            d.line((gx, gy - 12, gx - 10, gy + 8), fill="white", width=2)
            d.line((gx, gy - 12, gx + 10, gy + 8), fill="white", width=2)
            d.ellipse((gx - 4, gy - 16, gx + 4, gy - 8), fill="white")
            d.ellipse((gx - 14, gy + 4, gx - 6, gy + 12), fill="white")
            d.ellipse((gx + 6, gy + 4, gx + 14, gy + 12), fill="white")
        elif kind == "cluster":
            for dx, dy, r in [(-8, -5, 5), (7, -6, 4), (0, 8, 6)]:
                d.ellipse((gx + dx - r, gy + dy - r, gx + dx + r, gy + dy + r), fill="white")
        elif kind == "confusion":
            for i in range(3):
                for j in range(3):
                    if (i + j) % 2 == 0:
                        d.rectangle((gx - 12 + i * 8, gy - 12 + j * 8,
                                     gx - 6 + i * 8, gy - 6 + j * 8), fill="white")
        elif kind == "text":
            d.text((gx, gy), "T", font=self.font(22, True), fill="white", anchor="mm")
        else:
            d.ellipse((gx - 10, gy - 10, gx + 10, gy + 10), outline="white", width=3)

    def link(self, src_id, dst_id, dashed=False, color="#9e9e9e"):
        src = self.pads.get(src_id)
        dst = self.pads.get(dst_id)
        if not src or not dst or not src["out"] or not dst["in"]:
            print(f"skip link {src_id}->{dst_id}: missing pad", file=sys.stderr)
            return
        x0, y0 = src["out"]
        x1, y1 = dst["in"]
        dx = max(60, abs(x1 - x0) * 0.45)
        pts = []
        for i in range(41):
            t = i / 40
            p = (
                (1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * (x0 + dx)
                + 3 * (1 - t) * t ** 2 * (x1 - dx) + t ** 3 * x1,
                (1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * y0
                + 3 * (1 - t) * t ** 2 * y1 + t ** 3 * y1,
            )
            pts.append(p)
        if dashed:
            for i in range(0, len(pts) - 1, 2):
                self.d.line([pts[i], pts[i + 1]], fill=color, width=3)
        else:
            self.d.line(pts, fill=color, width=3, joint="curve")
        ang = math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])
        tip = pts[-1]
        L, wd = 13, 6
        self.d.polygon([
            tip,
            (tip[0] - L * math.cos(ang) + wd * math.sin(ang),
             tip[1] - L * math.sin(ang) - wd * math.cos(ang)),
            (tip[0] - L * math.cos(ang) - wd * math.sin(ang),
             tip[1] - L * math.sin(ang) + wd * math.cos(ang)),
        ], fill=color)

    def note(self):
        note = self.spec.get("note")
        if not note:
            return
        x, y = int(note.get("x", 60)), int(note.get("y", self.H - 180))
        w, h = int(note.get("w", 460)), int(note.get("h", 130))
        self.d.rounded_rectangle((x, y, x + w, y + h), radius=12,
                                 fill="#fff8e6", outline="#f0c36d", width=2)
        self.d.text((x + 24, y + 25), note.get("title", "说明"),
                    font=self.font(19, True), fill="#8a5a00", anchor="lm")
        for i, line in enumerate(note.get("lines", [])):
            size = self.fit_size(line, w - 48, 16)
            self.d.text((x + 24, y + 58 + i * 30), line,
                        font=self.font(size), fill="#6b4a00", anchor="lm")

    def footer(self):
        text = self.spec.get("footer", "")
        if not text:
            return
        size = self.fit_size(text, self.W - 120, 15)
        self.d.text((60, self.H - 32), text, font=self.font(size), fill="#888888", anchor="lm")

    def render(self):
        self.dot_grid()
        self.top_bar()
        for w in self.widgets:
            self.widget(w)
        for link in self.spec.get("links", []):
            if isinstance(link, dict):
                self.link(link["from"], link["to"], link.get("dashed", False))
            else:
                self.link(link[0], link[1])
        self.note()
        self.footer()
        return self.img


def main():
    if len(sys.argv) < 3:
        print("usage: python orange_style_diagram.py spec.json out.png")
        raise SystemExit(2)
    spec_path = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2]).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    img = Canvas(spec).render()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, dpi=(300, 300))
    print(f"saved: {out_path} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()

