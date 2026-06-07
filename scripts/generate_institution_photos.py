# -*- coding: utf-8 -*-
"""
Generate deterministic raster cover images for every institution.

The images are intentionally synthetic campus-style covers, not real photos of
specific buildings. Each asset is tied to the exact institution slug/name.
"""
import hashlib
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data"))

import institutions as D


OUT_DIR = os.path.join(ROOT, "img", "inst")
W, H = 1200, 750
FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"

PALETTES = {
    "blue": ((36, 100, 196), (86, 157, 222), (238, 244, 250)),
    "green": ((42, 133, 92), (104, 184, 139), (237, 246, 239)),
    "purple": ((109, 82, 185), (159, 132, 222), (242, 237, 250)),
    "amber": ((198, 105, 39), (226, 157, 82), (250, 241, 230)),
}
COLOR_CYCLE = ["blue", "green", "purple", "amber"]


def load_font(path, size):
    return ImageFont.truetype(path, size)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lighten(c, amount):
    return mix(c, (255, 255, 255), amount)


def darken(c, amount):
    return mix(c, (0, 0, 0), amount)


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw, text, font, max_width, max_lines=2):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test = word if not line else f"{line} {word}"
        if text_size(draw, test, font)[0] <= max_width:
            line = test
            continue
        if line:
            lines.append(line)
        line = word
        if len(lines) >= max_lines:
            break
    if line and len(lines) < max_lines:
        lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if words and " ".join(lines).strip() != text.strip() and lines:
        while lines[-1] and text_size(draw, lines[-1] + "…", font)[0] > max_width:
            lines[-1] = lines[-1][:-1].rstrip()
        lines[-1] += "…"
    return lines


def fit_font(draw, text, max_width, start_size, min_size=28, bold=True):
    path = FONT_BOLD if bold else FONT_REG
    for size in range(start_size, min_size - 1, -2):
        font = load_font(path, size)
        if text_size(draw, text, font)[0] <= max_width:
            return font
    return load_font(path, min_size)


def seed_for(item, section):
    raw = f"{section}:{item['slug']}:{item['name']}".encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:16], 16)


def theme_for(item, kind):
    s = (item.get("dirs", "") + " " + item.get("name", "") + " " + item.get("full", "")).lower()
    if any(x in s for x in ("меди", "фарма", "стомат", "ветерин")):
        return "medical"
    if any(x in s for x in ("it", "програм", "кибер", "информ", "технолог", "связь", "сети")):
        return "tech"
    if any(x in s for x in ("транспорт", "дорог", "авиа", "авто", "логист", "желез")):
        return "transport"
    if any(x in s for x in ("архит", "строит", "дизайн", "рестав")):
        return "architecture"
    if any(x in s for x in ("эконом", "финанс", "банк", "бизнес", "предприним", "управ")):
        return "business"
    if any(x in s for x in ("музык", "театр", "кино", "искус", "культур", "режисс", "акт")):
        return "arts"
    if any(x in s for x in ("спорт", "физической культур")):
        return "sport"
    if any(x in s for x in ("туризм", "гостеп", "сервис", "ресторан")):
        return "hospitality"
    if any(x in s for x in ("хим", "био", "нефт", "геолог", "материал")):
        return "science"
    return "college" if kind == "college" else "classic"


def draw_gradient(draw, top, bottom):
    for y in range(H):
        t = y / (H - 1)
        draw.line([(0, y), (W, y)], fill=mix(top, bottom, t))


def add_grain(img, rnd, amount=8):
    px = img.load()
    for _ in range(W * H // 14):
        x = rnd.randrange(W)
        y = rnd.randrange(H)
        r, g, b = px[x, y]
        delta = rnd.randint(-amount, amount)
        px[x, y] = (max(0, min(255, r + delta)), max(0, min(255, g + delta)), max(0, min(255, b + delta)))


def draw_windows(draw, x, y, w, h, rows, cols, rnd, tint):
    gap_x = max(7, w // (cols * 7))
    gap_y = max(7, h // (rows * 7))
    win_w = max(12, (w - gap_x * (cols + 1)) // cols)
    win_h = max(12, (h - gap_y * (rows + 1)) // rows)
    for row in range(rows):
        for col in range(cols):
            if rnd.random() < 0.09:
                continue
            wx = x + gap_x + col * (win_w + gap_x)
            wy = y + gap_y + row * (win_h + gap_y)
            color = lighten(tint, rnd.uniform(0.38, 0.68))
            draw.rounded_rectangle((wx, wy, wx + win_w, wy + win_h), radius=3, fill=color)
            if rnd.random() < 0.18:
                draw.line((wx + 3, wy + 3, wx + win_w - 3, wy + win_h - 3), fill=lighten(color, 0.3), width=1)


def draw_campus(draw, rnd, palette, theme):
    base, accent, paper = palette
    ground_y = rnd.randint(538, 568)
    draw.rectangle((0, ground_y, W, H), fill=mix(darken(paper, 0.08), base, 0.18))
    draw.polygon([(0, ground_y + 42), (W, ground_y - 12), (W, H), (0, H)], fill=mix(paper, base, 0.24))
    draw.line((0, ground_y, W, ground_y - 22), fill=lighten(base, 0.5), width=4)

    # Soft distant skyline.
    for i in range(11):
        x = i * 118 + rnd.randint(-34, 24)
        bw = rnd.randint(64, 132)
        bh = rnd.randint(70, 168)
        y = ground_y - bh - rnd.randint(0, 24)
        color = mix(paper, base, 0.12 + rnd.random() * 0.1)
        draw.rectangle((x, y, x + bw, ground_y + 8), fill=color)

    main_w = rnd.randint(520, 680)
    main_h = rnd.randint(265, 352)
    main_x = rnd.randint(280, 390)
    main_y = ground_y - main_h
    facade = lighten(base, 0.55)
    side = lighten(base, 0.44)
    shadow = darken(base, 0.25)
    roof = darken(base, 0.12)

    if theme in ("classic", "business", "arts"):
        draw.rectangle((main_x, main_y + 24, main_x + main_w, ground_y), fill=facade)
        draw.polygon([(main_x, main_y + 24), (main_x + main_w // 2, main_y - 38), (main_x + main_w, main_y + 24)], fill=roof)
        col_count = rnd.choice([6, 7, 8])
        col_gap = main_w // (col_count + 1)
        for c in range(col_count):
            cx = main_x + col_gap * (c + 1)
            draw.rounded_rectangle((cx - 14, main_y + 72, cx + 14, ground_y - 34), radius=7, fill=lighten(paper, 0.35))
            draw.rectangle((cx - 21, ground_y - 38, cx + 21, ground_y - 24), fill=lighten(paper, 0.15))
        draw_windows(draw, main_x + 30, main_y + 64, main_w - 60, 160, 3, 8, rnd, accent)
    elif theme in ("tech", "science"):
        skew = rnd.randint(44, 78)
        draw.polygon([(main_x + skew, main_y), (main_x + main_w, main_y + 42), (main_x + main_w - skew, ground_y), (main_x, ground_y - 34)], fill=facade)
        for i in range(9):
            xx = main_x + 42 + i * (main_w - 110) // 8
            draw.line((xx, main_y + 22, xx - skew // 2, ground_y - 36), fill=lighten(accent, 0.33), width=3)
        for i in range(7):
            yy = main_y + 50 + i * 36
            draw.line((main_x + 28, yy, main_x + main_w - 44, yy + 20), fill=lighten(accent, 0.48), width=2)
    elif theme in ("medical", "college"):
        draw.rounded_rectangle((main_x, main_y, main_x + main_w, ground_y), radius=18, fill=facade)
        wing_w = main_w // 4
        draw.rounded_rectangle((main_x - wing_w + 18, main_y + 72, main_x + 30, ground_y), radius=18, fill=side)
        draw.rounded_rectangle((main_x + main_w - 30, main_y + 64, main_x + main_w + wing_w - 18, ground_y), radius=18, fill=side)
        draw_windows(draw, main_x + 52, main_y + 54, main_w - 104, 210, 4, 7, rnd, accent)
    else:
        draw.rounded_rectangle((main_x, main_y + 30, main_x + main_w, ground_y), radius=16, fill=facade)
        draw.polygon([(main_x, main_y + 86), (main_x + main_w, main_y + 28), (main_x + main_w, main_y + 76), (main_x, main_y + 134)], fill=lighten(accent, 0.14))
        draw_windows(draw, main_x + 46, main_y + 112, main_w - 92, 170, 3, 8, rnd, accent)

    # Entrance and foreground details.
    door_w = rnd.randint(76, 112)
    door_x = main_x + main_w // 2 - door_w // 2
    draw.rounded_rectangle((door_x, ground_y - 108, door_x + door_w, ground_y), radius=12, fill=shadow)
    draw.rectangle((door_x + 10, ground_y - 96, door_x + door_w - 10, ground_y - 8), fill=lighten(accent, 0.48))
    draw.line((door_x + door_w // 2, ground_y - 96, door_x + door_w // 2, ground_y - 8), fill=lighten(shadow, 0.25), width=3)

    for tx in (rnd.randint(72, 160), rnd.randint(1010, 1110), rnd.randint(170, 245)):
        ty = ground_y + rnd.randint(-16, 20)
        trunk = darken((118, 86, 53), 0.05)
        draw.rectangle((tx - 7, ty - 70, tx + 7, ty + 8), fill=trunk)
        for _ in range(5):
            ox, oy = rnd.randint(-32, 32), rnd.randint(-96, -44)
            draw.ellipse((tx + ox - 34, ty + oy - 28, tx + ox + 34, ty + oy + 28), fill=mix((54, 132, 86), accent, 0.16))

    if theme == "transport":
        draw.line((0, H - 72, W, H - 124), fill=darken(base, 0.12), width=58)
        for x in range(-80, W, 180):
            draw.line((x, H - 94, x + 72, H - 100), fill=(255, 235, 160), width=6)
    elif theme == "medical":
        cx, cy = main_x + main_w - 92, main_y + 92
        draw.rectangle((cx - 10, cy - 38, cx + 10, cy + 38), fill=(214, 69, 68))
        draw.rectangle((cx - 38, cy - 10, cx + 38, cy + 10), fill=(214, 69, 68))
    elif theme == "arts":
        for x in range(main_x + 80, main_x + main_w - 80, 70):
            draw.ellipse((x, ground_y - 116, x + 26, ground_y - 90), outline=lighten(accent, 0.14), width=5)
            draw.line((x + 25, ground_y - 104, x + 25, ground_y - 148), fill=lighten(accent, 0.14), width=5)
    elif theme == "architecture":
        for x in range(60, 250, 34):
            draw.line((x, H - 44, x + 210, H - 142), fill=(255, 255, 255), width=2)
        draw.arc((72, H - 184, 268, H + 12), 205, 342, fill=(255, 255, 255), width=3)


def draw_copy(img, item, section, kind, theme, palette):
    draw = ImageDraw.Draw(img, "RGBA")
    base, accent, _ = palette
    name = item["name"]
    abbr = item["abbr"]
    dirs = item.get("dirs", "")
    city = item.get("city", "Москва")

    # Readable lower glass panel.
    panel_y = 552
    draw.rounded_rectangle((54, panel_y, W - 54, H - 52), radius=26, fill=(15, 19, 28, 158))
    draw.rounded_rectangle((74, panel_y + 22, 214, panel_y + 58), radius=18, fill=(*accent, 232))
    kind_label = "ВУЗ" if kind == "vuz" else "КОЛЛЕДЖ"
    draw.text((94, panel_y + 29), kind_label, font=load_font(FONT_BOLD, 19), fill=(255, 255, 255, 255))

    abbr_font = fit_font(draw, abbr, 420, 82, 42)
    draw.text((74, panel_y + 76), abbr, font=abbr_font, fill=(255, 255, 255, 255))

    name_font = fit_font(draw, name, 720, 42, 26)
    lines = wrap_text(draw, name, name_font, 720, 2)
    y = panel_y + 73
    for line in lines:
        draw.text((440, y), line, font=name_font, fill=(255, 255, 255, 248))
        y += text_size(draw, line, name_font)[1] + 8
    meta = f"{city} · {dirs}"
    meta_font = load_font(FONT_REG, 25)
    meta_lines = wrap_text(draw, meta, meta_font, 710, 1)
    draw.text((440, H - 92), meta_lines[0] if meta_lines else city, font=meta_font, fill=(231, 235, 242, 236))

    # Building sign.
    sign_w = min(520, max(190, text_size(draw, abbr, load_font(FONT_BOLD, 31))[0] + 76))
    sign_x = W // 2 - sign_w // 2
    draw.rounded_rectangle((sign_x, 100, sign_x + sign_w, 160), radius=15, fill=(255, 255, 255, 218))
    draw.text((sign_x + 38, 114), abbr, font=load_font(FONT_BOLD, 31), fill=(*darken(base, 0.08), 255))


def add_vignette(img):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(120):
        alpha = int(80 * (i / 120) ** 2)
        draw.rectangle((i, i, W - i, H - i), outline=(0, 0, 0, alpha), width=2)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def generate(item, section, kind, index):
    rnd = random.Random(seed_for(item, section))
    color = COLOR_CYCLE[index % len(COLOR_CYCLE)]
    palette = PALETTES[color]
    theme = theme_for(item, kind)

    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    base, accent, paper = palette
    sky_top = lighten(accent, 0.74)
    sky_bottom = lighten(paper, 0.1)
    draw_gradient(draw, sky_top, sky_bottom)

    # Soft sun glow.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gx, gy = rnd.randint(80, 320), rnd.randint(46, 130)
    for radius in range(230, 20, -16):
        a = int(54 * (1 - radius / 230))
        gd.ellipse((gx - radius, gy - radius, gx + radius, gy + radius), fill=(255, 245, 220, a))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)

    draw_campus(draw, rnd, palette, theme)
    add_grain(img, rnd)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=105, threshold=3))
    img = add_vignette(img)
    draw_copy(img, item, section, kind, theme, palette)
    return img.convert("RGB")


def iter_items():
    sets = [
        ("vuzy-moskvy", "vuz", D.VUZY_MSK),
        ("vuzy-moskovskoy-oblasti", "vuz", D.VUZY_MO),
        ("kolledzhi-moskvy", "college", D.KOLLEDZHI_MSK),
        ("kolledzhi-pri-vuze", "college", D.KOLLEDZHI_PRI_VUZE),
    ]
    for section, kind, items in sets:
        for i, item in enumerate(items):
            yield section, kind, i, item


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    written = []
    for section, kind, i, item in iter_items():
        img = generate(item, section, kind, i)
        path = os.path.join(OUT_DIR, f"{item['slug']}.jpg")
        img.save(path, "JPEG", quality=88, optimize=True, progressive=True)
        written.append(path)
    print(f"Generated {len(written)} institution photos into {OUT_DIR}")


if __name__ == "__main__":
    main()
