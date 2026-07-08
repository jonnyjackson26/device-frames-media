#!/usr/bin/env python3
"""Generate the cover image (docs/cover.png) showing every device frame in a grid.

Reads device-frames-output/index.json, picks one representative color variant
per device model, and composites them into a categorized grid with a gradient
fill in each screen (via each device's mask.png).

Usage
-----
    python generate_cover.py
"""
import colorsys
import json
import os
import urllib.parse

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(REPO_ROOT, "device-frames-output")
INDEX = os.path.join(ROOT, "index.json")
OUT_PATH = os.path.join(REPO_ROOT, "docs", "cover.png")

with open(INDEX, "r", encoding="utf-8") as f:
    data = json.load(f)


def local_path_from_url(url):
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(parsed.path)
    marker = "device-frames-output/"
    idx = path.index(marker) + len(marker)
    rel = path[idx:]
    return os.path.join(ROOT, *rel.split("/"))


def pick_color(colors):
    keys = list(colors.keys())

    def bad(k):
        kl = k.lower()
        return "landscape" in kl or "shadow" in kl or kl.endswith("-2") or (kl.endswith("2") and "titanium" not in kl)

    good = [k for k in keys if not bad(k)]
    pool = good if good else keys
    preference_order = ["natural-titanium", "silver", "space-grey", "space-gray", "space-black",
                         "black", "starlight", "white", "portrait-silver", "portrait-space-black",
                         "portrait-space-grey", "hazel", "obsidian"]
    for pref in preference_order:
        for k in pool:
            if k.lower() == pref:
                return k
    return sorted(pool)[0]


SECTIONS = [
    ("Apple iPhone", ["apple-iphone"]),
    ("Apple iPad", ["apple-ipad"]),
    ("Android", ["android-phone", "android-tablet"]),
]


def load_section_items(cat_keys):
    items = []
    for cat in cat_keys:
        devices = data[cat]
        for dev_key, colors in devices.items():
            color_key = pick_color(colors)
            entry = colors[color_key]
            path = local_path_from_url(entry["frame"])
            mask_path = os.path.join(os.path.dirname(path), "mask.png")
            if not os.path.exists(path):
                print("MISSING FILE:", path)
                continue
            items.append({"path": path, "mask_path": mask_path if os.path.exists(mask_path) else None})
    return items


sections_data = [(label, load_section_items(cats)) for label, cats in SECTIONS]
total_items = sum(len(items) for _, items in sections_data)

# ---- layout config ----
TILE = 360
GAP = 12
COLS = 8
MARGIN_X = 90
MARGIN_TOP = 100
MARGIN_BOTTOM = 90
HEADER_H = 78
SECTION_GAP = 46
INNER_PAD = 0.09

BG_TOP = (250, 250, 252)
BG_BOTTOM = (232, 234, 239)
HEADER_COLOR = (35, 37, 45)
HEADER_RULE = (210, 212, 219)
TITLE_COLOR = (20, 21, 26)
SUBTITLE_COLOR = (110, 114, 126)

FONT_DIR = r"C:\Windows\Fonts" if os.name == "nt" else "/usr/share/fonts/truetype/dejavu"
FONT_BOLD = "segoeuib.ttf" if os.name == "nt" else "DejaVuSans-Bold.ttf"
FONT_REGULAR = "segoeui.ttf" if os.name == "nt" else "DejaVuSans.ttf"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


title_font = font(FONT_BOLD, 80)
subtitle_font = font(FONT_REGULAR, 46)
header_font = font(FONT_BOLD, 40)

content_w = MARGIN_X * 2 + COLS * TILE + (COLS - 1) * GAP

section_rows = [-(-len(items) // COLS) for _, items in sections_data]

TOP_TITLE_H = 200

total_h = TOP_TITLE_H + MARGIN_TOP
for rows, (label, items) in zip(section_rows, sections_data):
    total_h += HEADER_H
    total_h += rows * TILE + (rows - 1) * GAP
    total_h += SECTION_GAP
total_h += MARGIN_BOTTOM - SECTION_GAP

canvas = Image.new("RGB", (content_w, total_h), BG_TOP)
grad = Image.new("RGB", (1, total_h), BG_TOP)
for y in range(total_h):
    t = y / max(1, total_h - 1)
    r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
    g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
    b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
    grad.putpixel((0, y), (r, g, b))
canvas.paste(grad.resize((content_w, total_h)), (0, 0))
canvas = canvas.convert("RGBA")

draw = ImageDraw.Draw(canvas)

title_text = "Device Frames"
subtitle_text = "A curated collection of high-fidelity device mockup frames"
tb = draw.textbbox((0, 0), title_text, font=title_font)
tw = tb[2] - tb[0]
draw.text(((content_w - tw) / 2, 40), title_text, font=title_font, fill=TITLE_COLOR)
sb = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
sw = sb[2] - sb[0]
draw.text(((content_w - sw) / 2, 144), subtitle_text, font=subtitle_font, fill=SUBTITLE_COLOR)


def hue_gradient_fill(size, hue1, hue2, sat=0.62, light1=0.58, light2=0.42):
    w, h = size
    c1 = np.array([c * 255 for c in colorsys.hls_to_rgb(hue1, light1, sat)])
    c2 = np.array([c * 255 for c in colorsys.hls_to_rgb(hue2, light2, sat)])
    xs = np.linspace(0, 1, w)
    ys = np.linspace(0, 1, h)
    t = (xs[None, :] + ys[:, None]) / 2.0
    t = t[:, :, None]
    arr = (c1[None, None, :] * (1 - t) + c2[None, None, :] * t).astype(np.uint8)
    return Image.fromarray(arr, mode="RGB")


def build_filled_device(frame_path, mask_path, hue1, hue2):
    frame = Image.open(frame_path).convert("RGBA")
    w, h = frame.size
    if mask_path:
        mask = Image.open(mask_path).convert("L")
        screen_fill = hue_gradient_fill((w, h), hue1, hue2)
        base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        base.paste(screen_fill, (0, 0), mask)
        base.alpha_composite(frame)
        return base
    return frame


def paste_with_shadow(canvas, frame_img, cx, cy, max_w, max_h):
    fw, fh = frame_img.size
    scale = min(max_w / fw, max_h / fh)
    nw, nh = max(1, int(fw * scale)), max(1, int(fh * scale))
    resized = frame_img.resize((nw, nh), Image.LANCZOS)

    alpha = resized.split()[3]
    pad = 60
    shadow = Image.new("RGBA", (nw + pad * 2, nh + pad * 2), (0, 0, 0, 0))
    shadow_alpha = Image.new("L", (nw + pad * 2, nh + pad * 2), 0)
    shadow_alpha.paste(alpha, (pad, pad + 10))
    shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(16))
    shadow_black = Image.new("RGBA", shadow.size, (25, 28, 36, 60))
    shadow.paste(shadow_black, (0, 0), shadow_alpha)

    sx = int(cx - shadow.width / 2)
    sy = int(cy - shadow.height / 2)
    canvas.alpha_composite(shadow, (sx, sy))

    px = int(cx - nw / 2)
    py = int(cy - nh / 2)
    canvas.alpha_composite(resized, (px, py))


y_cursor = TOP_TITLE_H + MARGIN_TOP
global_idx = 0

for (label, items), rows in zip(sections_data, section_rows):
    header_y = y_cursor
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN_X, header_y + 16), label, font=header_font, fill=HEADER_COLOR)
    draw.line(
        [(MARGIN_X + 250, header_y + HEADER_H / 2 + 6), (content_w - MARGIN_X, header_y + HEADER_H / 2 + 6)],
        fill=HEADER_RULE, width=2,
    )
    grid_top = header_y + HEADER_H

    for idx, item in enumerate(items):
        row = idx // COLS
        col = idx % COLS
        cx = MARGIN_X + col * (TILE + GAP) + TILE / 2
        cy = grid_top + row * (TILE + GAP) + TILE / 2

        t = global_idx / max(1, total_items - 1)
        hue1 = 0.60 - 0.22 * t
        hue2 = hue1 + 0.06
        img = build_filled_device(item["path"], item["mask_path"], hue1, hue2)
        max_dim = TILE * (1 - INNER_PAD * 2)
        paste_with_shadow(canvas, img, cx, cy, max_dim, max_dim)
        global_idx += 1

    y_cursor = grid_top + rows * TILE + (rows - 1) * GAP + SECTION_GAP

canvas = canvas.convert("RGB")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
canvas.save(OUT_PATH, "PNG")
print("Saved to", OUT_PATH, canvas.size)
