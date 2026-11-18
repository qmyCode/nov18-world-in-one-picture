#!/usr/bin/env python3
"""Draw the 18 Nov entry poster v2: 'Wednesday 18 November 2026'.

Format v2 (after crawling the dev board's top 10): 36 verified stories --
3 large illustrated mains, 9 medium mains (icon + headline + deck) and 24
one-liners with bold region lead-ins in a larger, airier ALSO tier. Navy
masthead with a gold rule, a slim Day-in-Numbers strip (six figures), a
quote-of-the-day line, and a dot-matrix world map with a numbered pin for
each of the 12 mains. No region tally (dropped from v1: meta-info, not
news). Deterministic: pure Pillow drawing, no randomness, no clock.

Tooling only -- the shipped main.py just copies the committed entry.png.
Run:  python3 draw.py   (writes entry.png next to this file)
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
PAPER = (248, 244, 233)
INK = (18, 18, 20)
GREY = (96, 96, 100)
ACCENT = (146, 30, 30)
RULE = (216, 208, 192)
NAVY = (19, 35, 68)
GOLD = (198, 152, 40)
CREAM = (224, 214, 188)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF = FD + "DejaVuSerif.ttf"
SERIFB = FD + "DejaVuSerif-Bold.ttf"
SANS = FD + "DejaVuSans.ttf"
SANSB = FD + "DejaVuSans-Bold.ttf"

REGIONS = {
    "EUROPE": (31, 78, 120),
    "MIDEAST": (146, 96, 16),
    "ASIA": (46, 107, 52),
    "AFRICA": (176, 84, 18),
    "AMERICAS": (110, 52, 148),
    "OCEANIA": (0, 121, 107),
    "GLOBAL": (84, 84, 84),
}
REGION_LABEL = {"MIDEAST": "MIDDLE EAST"}


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, xy, lines, font, fill, lh):
    x, y = xy
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def centered(draw, y, text, font, fill):
    draw.text(((W - draw.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)


def tracked(draw, x, y, text, font, fill, spacing=6):
    for c in text:
        draw.text((x, y), c, font=font, fill=fill)
        x += draw.textlength(c, font=font) + spacing
    return x


def tracked_right(draw, right, y, text, font, fill, spacing=6):
    total = sum(draw.textlength(c, font=font) for c in text) + spacing * (len(text) - 1)
    return tracked(draw, right - total, y, text, font, fill, spacing)


def fit_font(draw, text, path, size, max_w, min_size=8):
    while size > min_size and draw.textlength(text, font=F(path, size)) > max_w:
        size -= 1
    return F(path, size)


def badge(draw, cx, cy, num, colour, r=9):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    t = str(num)
    f = F(SANSB, 10 if num < 10 else 9)
    draw.text((cx - draw.textlength(t, font=f) / 2, cy - 6), t, font=f, fill=(255, 255, 255))


def kicker(draw, x, y, num, region, topic, big=False):
    r = 10 if big else 8
    badge(draw, x + r, y + r - 2, num, REGIONS[region], r=r)
    label = REGION_LABEL.get(region, region) + " · " + topic
    f = F(SANSB, 11 if big else 10)
    draw.text((x + 2 * r + 6, y), label, font=f, fill=REGIONS[region])


# ---------------------------------------------------------------- icons
def icon_ballot(d, x, y, s):
    d.rectangle([x + 8, y + s - 22, x + s - 8, y + s - 6], outline=(90, 60, 130), width=3)
    d.rectangle([x + 18, y + 6, x + s - 18, y + 26], outline=(90, 60, 130), width=2)
    d.line([x + 23, y + 12, x + s - 23, y + 12], fill=(90, 60, 130), width=2)
    d.line([x + 23, y + 18, x + s - 28, y + 18], fill=(90, 60, 130), width=2)
    d.line([x + 16, y + s - 24, x + s - 16, y + s - 24], fill=(200, 40, 40), width=3)


def icon_chip(d, x, y, s):
    d.rounded_rectangle([x + 12, y + 12, x + s - 12, y + s - 12], radius=4,
                        outline=(30, 110, 60), width=3)
    for i in range(4):
        px = x + 16 + i * (s - 36) / 3
        d.line([px, y + 4, px, y + 12], fill=(30, 110, 60), width=2)
        d.line([px, y + s - 12, px, y + s - 4], fill=(30, 110, 60), width=2)
    d.rectangle([x + s // 2 - 7, y + s // 2 - 7, x + s // 2 + 7, y + s // 2 + 7],
                fill=(30, 110, 60))
    d.text((x + s // 2 - 8, y + s // 2 - 19), "AI", font=F(SANSB, 11), fill=(30, 110, 60))


def icon_chart(d, x, y, s):
    d.line([x + 10, y + 8, x + 10, y + s - 10], fill=(52, 52, 56), width=2)
    d.line([x + 10, y + s - 10, x + s - 6, y + s - 10], fill=(52, 52, 56), width=2)
    for i, bh in enumerate((14, 22, 30)):
        bx = x + 16 + i * 13
        d.rectangle([bx, y + s - 10 - bh, bx + 9, y + s - 10], fill=(46, 107, 52))
    d.line([x + 14, y + s - 26, x + 30, y + s - 36, x + s - 12, y + 12],
           fill=(200, 40, 40), width=3)
    d.polygon([(x + s - 12, y + 8), (x + s - 20, y + 12), (x + s - 11, y + 17)],
              fill=(200, 40, 40))


def icon_ban(d, x, y, s):
    d.polygon([(x + 14, y + 30), (x + 14, y + 18), (x + s // 2, y + 10),
               (x + s - 14, y + 18), (x + s - 14, y + 30)], outline=(120, 84, 30), width=3)
    d.rectangle([x + s // 2 - 4, y + 22, x + s // 2 + 4, y + 30], fill=(120, 84, 30))
    d.ellipse([x + 8, y + 4, x + s - 8, y + s - 4], outline=(200, 40, 40), width=4)
    d.line([x + 14, y + s - 11, x + s - 14, y + 11], fill=(200, 40, 40), width=4)


def icon_euro(d, x, y, s):
    cx, cy, r = x + s // 2, y + s // 2, s * 0.38
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
    f = F(SERIFB, 26)
    d.text((cx - d.textlength("€", font=f) / 2, cy - 17), "€", font=f, fill=NAVY)


def icon_cyclone(d, x, y, s):
    cx, cy = x + s // 2, y + s // 2
    col = (0, 110, 140)
    d.arc([cx - 17, cy - 17, cx + 17, cy + 17], 300, 130, fill=col, width=4)
    d.arc([cx - 11, cy - 11, cx + 11, cy + 11], 120, 310, fill=col, width=4)
    d.arc([cx - 5, cy - 5, cx + 5, cy + 5], 200, 60, fill=col, width=3)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=col)
    for dx, dy in ((-14, 14), (16, -12)):
        d.line([cx + dx - 4, cy + dy, cx + dx + 4, cy + dy], fill=(90, 150, 180), width=2)


def icon_ship(d, x, y, s):
    d.polygon([(x + 4, y + s - 16), (x + s - 4, y + s - 16), (x + s - 10, y + s - 6),
               (x + 10, y + s - 6)], fill=(52, 60, 74))
    for i, col in enumerate(((190, 60, 40), (40, 90, 160), (46, 130, 70))):
        bx = x + 10 + i * 11
        d.rectangle([bx, y + s - 26, bx + 9, y + s - 17], fill=col)
    d.rectangle([x + 12, y + 12, x + 20, y + s - 27], fill=(120, 124, 132))
    d.line([x + 6, y + s - 3, x + 22, y + s - 3], fill=(90, 140, 180), width=2)
    d.line([x + 26, y + s - 3, x + s - 6, y + s - 3], fill=(90, 140, 180), width=2)


def icon_phone(d, x, y, s):
    d.rounded_rectangle([x + 13, y + 4, x + s - 13, y + s - 4], radius=5,
                        fill=(30, 32, 38))
    d.rectangle([x + 17, y + 10, x + s - 17, y + s - 12], fill=(214, 226, 236))
    d.line([x + 20, y + 26, x + 27, y + 33, x + s - 20, y + 16],
           fill=(30, 140, 70), width=3)


def icon_sun(d, x, y, s):
    cx, cy = x + s // 2, y + 15
    for dx, dy in ((0, -11), (0, 11), (-11, 0), (11, 0), (-8, -8), (8, -8),
                   (-8, 8), (8, 8)):
        d.line([cx, cy, cx + dx, cy + dy], fill=(216, 150, 30), width=2)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(240, 180, 50))
    d.polygon([(x + 8, y + s - 4), (x + 14, y + s - 16), (x + s - 14, y + s - 16),
               (x + s - 8, y + s - 4)], fill=(40, 80, 140))
    for i in range(1, 4):
        lx = x + 14 + i * (s - 28) / 4
        d.line([lx, y + s - 16, lx - 2, y + s - 4], fill=(140, 180, 220), width=1)
    d.line([x + 12, y + s - 10, x + s - 12, y + s - 10], fill=(140, 180, 220), width=1)


# ------------------------------------------------------------- big art
def bridge_art(d, x0, y0, x1, y1):
    """Kerch Bridge scene: strait, towers, collapsed span (from v1)."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y0 + h * 0.52], fill=(206, 224, 236))
    d.rectangle([x0, y0 + h * 0.52, x1, y1], fill=(88, 138, 178))
    for i in range(6):
        yy = y0 + h * (0.60 + i * 0.07)
        d.line([x0 + (i % 3) * 46, yy, x0 + (i % 3) * 46 + 74, yy],
               fill=(140, 180, 205), width=2)
    deck = y0 + h * 0.50
    for fx in (0.16, 0.84):
        tx = x0 + w * fx
        d.rectangle([tx - 5, y0 + h * 0.10, tx + 5, deck], fill=(70, 74, 82))
        d.polygon([(tx - 34, deck), (tx, y0 + h * 0.10), (tx + 34, deck)],
                  outline=(70, 74, 82), width=2)
    d.rectangle([x0, deck - 4, x0 + w * 0.40, deck + 3], fill=(52, 56, 64))
    d.rectangle([x0 + w * 0.60, deck - 4, x1, deck + 3], fill=(52, 56, 64))
    d.polygon([(x0 + w * 0.40, deck - 3), (x0 + w * 0.52, deck + h * 0.20),
               (x0 + w * 0.60, deck - 3)], fill=(40, 44, 50))
    for fx, col in ((0.10, (200, 60, 40)), (0.24, (240, 244, 248)), (0.72, (60, 110, 200))):
        cx = x0 + w * fx
        d.rectangle([cx - 11, deck - 13, cx + 11, deck - 4], fill=col)
        d.rectangle([cx - 6, deck - 19, cx + 3, deck - 13], fill=(230, 232, 236))
    gx, gy = x0 + w * 0.50, y0 + h * 0.16
    for r, col in ((17, (120, 120, 124)), (12, (168, 96, 40)), (7, (226, 178, 60))):
        d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=col)
    for dx, dy, r in ((-24, 8, 8), (22, 12, 9), (-6, -16, 7), (14, -12, 6)):
        d.ellipse([gx + dx - r, gy + dy - r, gx + dx + r, gy + dy + r], fill=(110, 110, 114))
    gx2, gy2 = x0 + w * 0.78, y0 + h * 0.30
    for r, col in ((10, (130, 130, 134)), (6, (226, 178, 60))):
        d.ellipse([gx2 - r, gy2 - r, gx2 + r, gy2 + r], fill=col)


def gulf_art(d, x0, y0, x1, y1):
    """Gulf trade-fire scene: Bahrain shore + radar, drones, Qeshm island."""
    w, h = x1 - x0, y1 - y0
    sea = y0 + h * 0.60
    d.rectangle([x0, y0, x1, sea], fill=(203, 222, 235))
    d.rectangle([x0, sea, x1, y1], fill=(88, 138, 178))
    for i in range(4):
        yy = sea + 8 + i * 9
        d.line([x0 + (i % 3) * 52, yy, x0 + (i % 3) * 52 + 66, yy],
               fill=(140, 180, 205), width=2)
    # Bahrain shore (left) with a radar station
    d.polygon([(x0, sea + 4), (x0 + w * 0.30, sea + 2), (x0 + w * 0.34, y1),
               (x0, y1)], fill=(198, 180, 134))
    rx = x0 + w * 0.15
    d.line([rx, sea + 2, rx, sea - 34], fill=(60, 64, 72), width=3)
    d.arc([rx - 16, sea - 52, rx + 16, sea - 20], 200, 340, fill=(60, 64, 72), width=3)
    d.line([rx, sea - 34, rx + 13, sea - 44], fill=(60, 64, 72), width=2)
    d.rectangle([rx - 20, sea - 2, rx + 8, sea + 6], fill=(90, 94, 102))
    # Attack drones crossing the sky
    for fx, fy in ((0.44, 0.26), (0.55, 0.14), (0.63, 0.32)):
        cx, cy = x0 + w * fx, y0 + h * fy
        d.rectangle([cx - 4, cy - 3, cx + 4, cy + 3], fill=(40, 44, 52))
        for dx, dy in ((-8, -6), (8, -6), (-8, 6), (8, 6)):
            d.line([cx, cy, cx + dx, cy + dy], fill=(40, 44, 52), width=2)
            d.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2],
                      fill=(40, 44, 52))
        d.line([cx + 12, cy, cx + 26, cy], fill=(150, 160, 170), width=1)
    # Qeshm island (right) with a missile site and a strike burst
    d.polygon([(x0 + w * 0.68, sea + 3), (x0 + w * 0.76, sea - 12),
               (x0 + w * 0.88, sea - 6), (x1, sea + 3), (x1, y1),
               (x0 + w * 0.68, y1)], fill=(66, 72, 82))
    lx = x0 + w * 0.80
    d.polygon([(lx, sea - 10), (lx + 16, sea - 26), (lx + 20, sea - 22),
               (lx + 5, sea - 6)], fill=(30, 32, 38))
    bx, by = x0 + w * 0.90, sea - 20
    for r, col in ((13, (226, 120, 40)), (8, (240, 178, 60)), (4, (250, 240, 200))):
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=col)
    for dx, dy, r in ((-14, -10, 6), (10, -14, 7), (2, -20, 5)):
        d.ellipse([bx + dx - r, by + dy - r, bx + dx + r, by + dy + r],
                  fill=(110, 110, 114))
    # A jet high on the right
    jx, jy = x0 + w * 0.86, y0 + h * 0.14
    d.polygon([(jx - 20, jy), (jx + 8, jy - 6), (jx + 22, jy), (jx + 6, jy + 4),
               (jx - 12, jy + 4)], fill=(70, 78, 92))
    d.polygon([(jx - 4, jy + 2), (jx + 4, jy - 10), (jx + 10, jy + 2)], fill=(56, 64, 78))


def apec_art(d, x0, y0, x1, y1):
    """Shenzhen summit scene: skyline and the Russian, Chinese, US flags."""
    w, h = x1 - x0, y1 - y0
    d.rectangle([x0, y0, x1, y1], fill=(210, 226, 240))
    d.ellipse([x0 + w * 0.84, y0 + 8, x0 + w * 0.84 + 22, y0 + 30], fill=(244, 214, 130))
    base = y1
    heights = (0.44, 0.62, 0.36, 0.54, 0.30, 0.58, 0.40, 0.50, 0.34, 0.46)
    bw = w / len(heights)
    for i, fh in enumerate(heights):
        bx = x0 + i * bw
        d.rectangle([bx + 1, base - h * fh, bx + bw - 1, base], fill=(74, 88, 110))
    d.rectangle([x0, base - 4, x1, base], fill=(52, 62, 78))
    # Three flags on poles in front of the skyline
    for fx, kind in ((0.22, "ru"), (0.50, "cn"), (0.78, "us")):
        px = x0 + w * fx
        top = y0 + h * 0.14
        d.line([px, top, px, base - 6], fill=(30, 32, 38), width=2)
        fw, fh = 40, 24
        fx0, fy0 = px + 2, top
        if kind == "ru":
            d.rectangle([fx0, fy0, fx0 + fw, fy0 + fh], fill=(240, 240, 240))
            d.rectangle([fx0, fy0 + fh / 3, fx0 + fw, fy0 + 2 * fh / 3], fill=(60, 90, 170))
            d.rectangle([fx0, fy0 + 2 * fh / 3, fx0 + fw, fy0 + fh], fill=(200, 50, 50))
        elif kind == "cn":
            d.rectangle([fx0, fy0, fx0 + fw, fy0 + fh], fill=(206, 44, 40))
            d.ellipse([fx0 + 4, fy0 + 4, fx0 + 11, fy0 + 11], fill=(246, 205, 60))
            for dx, dy in ((14, 3), (16, 8), (16, 13), (13, 17)):
                d.ellipse([fx0 + dx, fy0 + dy, fx0 + dx + 3, fy0 + dy + 3],
                          fill=(246, 205, 60))
        else:
            for i in range(6):
                col = (196, 52, 52) if i % 2 == 0 else (244, 244, 244)
                d.rectangle([fx0, fy0 + i * fh / 6, fx0 + fw, fy0 + (i + 1) * fh / 6],
                            fill=col)
            d.rectangle([fx0, fy0, fx0 + 17, fy0 + fh / 2], fill=(52, 62, 140))
            for r_ in range(3):
                for c_ in range(4):
                    d.point((fx0 + 3 + c_ * 4, fy0 + 3 + r_ * 4), fill=(255, 255, 255))


# ---------------------------------------------------------------- page
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ------------------------------------------------------------- masthead
d.rectangle([0, 0, W, 112], fill=NAVY)
tracked(d, 26, 13, "THE DAY IN WORLD NEWS", F(SANSB, 12), GOLD, spacing=5)
tracked_right(d, 998, 13, "36 STORIES · 6 CONTINENTS · ONE DAY", F(SANSB, 12),
              GOLD, spacing=4)
d.text((26, 34), "Wednesday 18 November 2026", font=F(SERIFB, 50), fill=(250, 250, 248))
d.text((26, 92), "Every story below happened, or was first reported, on this day.",
       font=F(SERIF, 13), fill=CREAM)
d.rectangle([0, 112, W, 115], fill=GOLD)

# ------------------------------------------------- 3 large illustrated mains
BIG = [
    (1, "MIDEAST", "WAR", "US and Iran trade fire over Bahrain",
     "Iranian drones target a US radar at Sheikh Isa; US jets answer on Qeshm Island.",
     gulf_art),
    (2, "EUROPE", "WAR", "Ukraine hits the Kerch Bridge again",
     "A road span collapses into the strait on day two; Russia answers at Kyiv's bridges.",
     bridge_art),
    (3, "ASIA", "POLITICS", "Putin lands in Shenzhen as APEC opens",
     "Trump meets Marcos in Manila today, then a first Xi–Trump–Putin trilateral.",
     apec_art),
]
for i, (num, region, topic, head, deck, art) in enumerate(BIG):
    px = 26 + i * 330
    d.rectangle([px, 124, px + 312, 338], outline=RULE, width=1)
    art(d, px + 1, 125, px + 311, 225)
    kicker(d, px + 2, 236, num, region, topic, big=True)
    hf = F(SERIFB, 20)
    draw_lines(d, (px + 2, 254), wrap(d, head, hf, 306), hf, INK, 24)
    df = F(SANS, 10)
    draw_lines(d, (px + 2, 306), wrap(d, deck, df, 306), df, (52, 52, 56), 13)

# ------------------------------------------------------------- section bar
d.rectangle([26, 348, 998, 372], fill=NAVY)
d.text((38, 354), "MORE OF THE DAY — STORIES 4–12", font=F(SANSB, 12),
       fill=(250, 250, 248))

# ------------------------------------------------------------- medium mains
MEDIUM = [
    (4, "EUROPE", "UKRAINE AID", "EU to propose a €45bn loan for Ukraine",
     "Covers two-thirds of Kyiv's €70bn 2027 gap; repaid only if Russia pays reparations.",
     icon_euro),
    (5, "ASIA", "WEATHER", "Cyclone Akvan bears down on India",
     "Heavy rain for Andhra Pradesh and Odisha; landfall due Friday, gusting 145 km/h.",
     icon_cyclone),
    (6, "MIDEAST", "POLITICS", "Knesset elects Kahana, a blow to Netanyahu",
     "Eisenkot's ally wins the speakership 66–52, replacing Likud's Ohana.",
     icon_ballot),
    (7, "EUROPE", "SANCTIONS", "Britain sanctions settlement builders",
     "Eight Israeli firms and the group Tzav 9 face asset freezes.",
     icon_ban),
    (8, "ASIA", "TRADE", "China cuts tariffs as Xi meets Carney",
     "C$400m relief on pork and seafood; Canada extends steel relief.",
     icon_ship),
    (9, "AMERICAS", "TECHNOLOGY", "Apple restores services after outage",
     "App Store, iCloud and Apple Pay return after a three-hour failure blamed on an update.",
     icon_phone),
    (10, "GLOBAL", "BUSINESS", "Nvidia beats forecasts since Huang exit",
     "Asia stocks snap a four-day slide: KOSPI +3.3%, Nvidia +4.7% after hours.",
     icon_chip),
    (11, "ASIA", "ECONOMY", "India's GDP grew an estimated 7.5%",
     "ICRA puts July–September growth at 7.5%, down from 7.8% in April–June.",
     icon_chart),
    (12, "ASIA", "BUSINESS", "Amazon to invest $7bn in India renewables",
     "Solar and wind for its Indian operations, atop $4bn already contracted.",
     icon_sun),
]
for i, (num, region, topic, head, deck, icon) in enumerate(MEDIUM):
    gx, gy = 26 + (i % 3) * 330, 382 + (i // 3) * 92
    if i % 3 == 0 and i > 0:
        d.line([26, gy - 6, 998, gy - 6], fill=RULE, width=1)
    icon(d, gx, gy + 24, 44)
    tx = gx + 58
    kicker(d, tx, gy + 2, num, region, topic)
    hf = F(SERIFB, 15)
    draw_lines(d, (tx, gy + 18), wrap(d, head, hf, 252), hf, INK, 18)
    df = F(SANS, 10)
    draw_lines(d, (tx, gy + 56), wrap(d, deck, df, 252), df, (52, 52, 56), 12)

# ------------------------------------------------------- Day in Numbers
d.line([26, 662, 998, 662], fill=INK, width=2)
d.text((26, 676), "THE DAY IN", font=F(SANSB, 11), fill=INK)
d.text((26, 690), "NUMBERS", font=F(SANSB, 11), fill=INK)
NUMBERS = [
    ("1,441", "drones Russia says it shot down — a record"),
    ("66–52", "Knesset vote that elected speaker Kahana"),
    ("$1.4tn", "Anthropic's value at the top of its IPO range"),
    ("16.09bn", "miles out: Voyager 1's one light-day (NASA)"),
    ("2,230", "Sudan civilians killed Jan–Oct, most by drones"),
    ("$120bn", "a year: COP31 adaptation-finance target"),
]
for i, (big, label) in enumerate(NUMBERS):
    nx = 150 + i * 141
    d.text((nx, 668), big, font=F(SERIFB, 17), fill=ACCENT)
    draw_lines(d, (nx, 690), wrap(d, label, F(SANS, 8), 133), F(SANS, 8),
               (52, 52, 56), 10)

# ------------------------------------------------------------- world map
MAP_COLS = 100
MAP_ROWS = [
    "......####" "#####....." ".........." ".........." ".........." ".........." "##########" "##########" "##########" "######....",
    "....######" "###.######" "#########." "........##" "####......" "..########" "##########" "##########" "##########" "########..",
    "...#######" "###.######" "##########" "####......" "####......" "..########" "##########" "##########" "##########" "######....",
    ".........." "##########" "##########" "##..######" "#......###" "##########" "##########" "##########" "##########" "######....",
    ".........#" "##########" "##########" "#........." ".......###" "##########" "##########" "##########" "##########" "#####.....",
    ".........." ".#########" "##########" "##........" ".......###" "##########" "##########" "##########" "#####....#" "#.........",
    ".........." "##########" "##########" "###......." "......####" "##########" "##########" "##########" "#######.##" "..........",
    ".........." ".#########" "##########" "#........." "....######" "##########" "##########" "##########" "########.#" "..........",
    ".........." "...#######" "##########" ".........." "....######" "##########" "#######..#" "##########" "######...." "..........",
    ".........." "....######" "#######..." ".........." "....######" "##########" "#######..#" "####..####" "#...##...." "..........",
    ".........." ".........." ".......###" "##........" "....######" "##########" "#........#" "###...####" "#.#####..." "..........",
    ".........." ".........." ".......###" "##########" "......####" "#########." ".........." "...##..##." ".##..##..." "..........",
    ".........." ".........." "........##" "##########" "#.....####" "########.." ".........." "....##..##" "...##..##." "..........",
    ".........." ".........." ".........#" "##########" "......####" "#######..." ".........." ".........." "##########" "#.........",
    ".........." ".........." ".........#" "########.." ".......###" "######...." ".........." ".........." "##########" "##........",
    ".........." ".........." "........##" "#######..." "......####" "#####....." ".........." ".........." "##########" "##........",
    ".........." ".........." ".........#" "#######..." "......####" "####......" ".........." ".........." "##########" "#.........",
    ".........." ".........." ".........." "#######..." "......####" "###......." ".........." ".........." ".#########" "..........",
    ".........." ".........." ".........." "######...." ".........." ".........." ".........." ".........." ".#########" ".....##...",
    ".........." ".........." ".........." "####......" ".........." ".........." ".........." ".........." ".........." "....##....",
    ".........." ".........." ".........." "##........" ".........." ".........." ".........." ".........." ".........." "..........",
    ".........." ".........." ".........." "#........." ".........." ".........." ".........." ".........." ".........." "..........",
]

# Pins for the 12 mains only: story -> (col, row, region).
PINS = {
    1: (65, 10, "MIDEAST"), 2: (63, 4, "EUROPE"), 3: (82, 9, "ASIA"),
    4: (51, 3, "EUROPE"), 5: (73, 11, "ASIA"), 6: (61, 8, "MIDEAST"),
    7: (49, 2, "EUROPE"), 8: (79, 6, "ASIA"), 9: (12, 6, "AMERICAS"),
    10: (15, 9, "AMERICAS"), 11: (70, 8, "ASIA"), 12: (69, 14, "ASIA"),
}

d.rectangle([26, 720, 400, 960], outline=RULE, width=1)
d.text((38, 730), "WHERE IT HAPPENED", font=F(SANSB, 11), fill=INK)
d.rectangle([34, 748, 392, 840], fill=(233, 238, 240))
OX, OY, CELL = 38, 754, 3.5
LAND = (43, 52, 63)
for r, row in enumerate(MAP_ROWS):
    row = row.ljust(MAP_COLS, ".")[:MAP_COLS]
    for c, ch in enumerate(row):
        if ch == "#":
            cx, cy = OX + (c + 0.5) * CELL, OY + (r + 0.5) * CELL
            d.ellipse([cx - 1.4, cy - 1.4, cx + 1.4, cy + 1.4], fill=LAND)
for num in sorted(PINS):
    c, r, region = PINS[num]
    cx, cy = OX + (c + 0.5) * CELL, OY + (r + 0.5) * CELL
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=REGIONS[region],
              outline=(255, 255, 255), width=2)
    t = str(num)
    pf = F(SANSB, 8 if num < 10 else 7)
    d.text((cx - d.textlength(t, font=pf) / 2, cy - 5), t, font=pf, fill=(255, 255, 255))
d.text((38, 850), "Numbered dots mark stories 1–12.", font=F(SANS, 9), fill=GREY)
for row_i, row_regions in enumerate((("EUROPE", "MIDEAST", "ASIA", "AFRICA"),
                                     ("AMERICAS", "OCEANIA", "GLOBAL"))):
    lx, ly = 38, 878 + row_i * 20
    for region in row_regions:
        label = REGION_LABEL.get(region, region)
        d.ellipse([lx, ly, lx + 8, ly + 8], fill=REGIONS[region])
        d.text((lx + 12, ly - 1), label, font=F(SANSB, 8), fill=(52, 52, 56))
        lx += 12 + d.textlength(label, font=F(SANSB, 8)) + 12

# ------------------------------------------------------- ALSO ON WEDNESDAY
ALSO = [
    ("EUROPE", "Riga backs Kulbergs govt, 57–34"),
    ("EUROPE", "Hungary halts Ukraine rail traffic"),
    ("EUROPE", "Berlin, London rebuff US at Ramstein"),
    ("EUROPE", "M5.3 quake hits Romania"),
    ("EUROPE", "372 civilians killed in Ukraine, Oct"),
    ("EUROPE", "Haaland penalty sends Norway through"),
    ("ASIA", "Japan exports up 14th straight month"),
    ("ASIA", "Thailand to scrap all US tariffs"),
    ("ASIA", "India electronics exports +44%"),
    ("ASIA", "Car bomb kills 5 at Pakistan post"),
    ("AMERICAS", "Trump plotter gets 27½ years"),
    ("AMERICAS", "FAA pauses routers after ground stop"),
    ("AMERICAS", "JetBlue turbulence injures five"),
    ("AMERICAS", "20 uncontacted Awá emerge, Brazil"),
    ("AMERICAS", "Anthropic prices $1.4tn IPO"),
    ("MIDEAST", "Gaza fire kills 4, incl. boy, 6"),
    ("MIDEAST", "100,000 Gaza tents await entry"),
    ("MIDEAST", "US–Iran stalemate deepens"),
    ("AFRICA", "UN: 2,230 Sudan civilians killed"),
    ("AFRICA", "South Sudan vote delayed to 2027"),
    ("GLOBAL", "Voyager 1 a light-day from Earth"),
    ("GLOBAL", "COP31 draft splits 200 nations"),
    ("GLOBAL", "Rohingya ruling due Thursday"),
    ("OCEANIA", "Canberra sanctions settlers"),
]
d.rectangle([412, 720, 998, 960], outline=RULE, width=1)
d.text((424, 728), "ALSO ON WEDNESDAY", font=F(SERIFB, 15), fill=INK)
_note = "24 more verified stories"
d.text((986 - d.textlength(_note, font=F(SANS, 9)), 732), _note,
       font=F(SANS, 9), fill=GREY)
d.line([424, 752, 986, 752], fill=RULE, width=1)
for i, (region, text) in enumerate(ALSO):
    ax, right = (424, 694) if i < 12 else (706, 986)
    ay = 764 + (i % 12) * 16.4
    lead = REGION_LABEL.get(region, region) + " — "
    lf = F(SANSB, 11)
    d.text((ax, ay), lead, font=lf, fill=REGIONS[region])
    tx = ax + d.textlength(lead, font=lf)
    tf = fit_font(d, text, SANS, 11, right - tx, min_size=10)
    d.text((tx, ay), text, font=tf, fill=INK)

# ------------------------------------------------------- quote of the day
_qlabel = "QUOTE OF THE DAY — TRUMP, IN MANILA (REUTERS)"
d.text((26, 970), _qlabel, font=F(SANSB, 9), fill=ACCENT)
_qx = 26 + d.textlength(_qlabel, font=F(SANSB, 9)) + 10
d.text((_qx, 968),
       "“It's life. When you're big and powerful and you have all the money, "
       "things like that happen. It's fine.”",
       font=F(SERIF, 12), fill=INK)

# ---------------------------------------------------------------- footer
d.line([26, 994, 998, 994], fill=INK, width=1)
centered(d, 1000,
         "Sources: Reuters · AP · AFP · BBC · Al Jazeera · UN News · NASA · USGS · UEFA · IOM · WFP · IMD · ICRA",
         F(SANS, 9), GREY)
centered(d, 1012,
         "Disputed claims are attributed to their source. "
         "All illustrations are original drawings, made for this front page.",
         F(SANS, 9), GREY)

img.save(OUT)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
