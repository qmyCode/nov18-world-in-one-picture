#!/usr/bin/env python3
"""Draw the 18 Nov entry poster: 'Wednesday 18 November 2026 - The Day in World News'.

Format: 42 verified stories (12 illustrated mains + 30 one-liners),
a dominant hero panel for the Kerch Bridge second-day strike, a
Day-in-Numbers strip with six figures, a Stories-by-Region tally,
a numbered dot-matrix world map (a pin for every story; Voyager 1 is
a deep-space star), a quote-of-the-day panel, and a per-region colour
system shared by kicker chips, map pins and ALSO numbers.
Deterministic: pure Pillow drawing, no randomness, no clock.

Tooling only -- the shipped main.py just copies the committed entry.png.
Run:  python3 draw.py   (writes entry.png next to this file)
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
PAPER = (250, 248, 243)
INK = (18, 18, 20)
GREY = (96, 96, 100)
ACCENT = (146, 30, 30)
RULE = (210, 205, 195)

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
LEGEND_LABEL = {"MIDEAST": "MIDEAST"}


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


def tracked(draw, y, text, font, fill, spacing=6, cx=W / 2):
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += w + spacing
    return total


def fit_font(draw, text, path, size, max_w, min_size=8):
    while size > min_size and draw.textlength(text, font=F(path, size)) > max_w:
        size -= 1
    return F(path, size)


def badge(draw, cx, cy, num, colour, r=9):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)
    t = str(num)
    f = F(SANSB, 10 if num < 10 else 9)
    draw.text((cx - draw.textlength(t, font=f) / 2, cy - 6), t, font=f, fill=(255, 255, 255))


def chip(draw, x, y, region, topic, h=18):
    label = REGION_LABEL.get(region, region) + " · " + topic
    f = F(SANSB, 10)
    w = draw.textlength(label, font=f) + 14
    draw.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=REGIONS[region])
    draw.text((x + 7, y + h // 2 - 6), label, font=f, fill=(255, 255, 255))
    return x + w


# ---------------------------------------------------------------- icons
def icon_plane(d, x, y, s):
    d.ellipse([x + 6, y + 6, x + 26, y + 26], outline=(200, 40, 40), width=3)
    d.ellipse([x + s - 26, y + 6, x + s - 6, y + 26], outline=(40, 90, 180), width=3)
    d.polygon([(x + 8, y + s - 12), (x + s - 10, y + s - 22), (x + s - 4, y + s - 10),
               (x + 16, y + s - 4)], fill=(60, 60, 66))
    d.polygon([(x + s // 2 - 4, y + s - 20), (x + s // 2 + 8, y + s - 34),
               (x + s // 2 + 14, y + s - 18)], fill=(90, 90, 96))


def icon_jet(d, x, y, s):
    d.polygon([(x + 4, y + s - 16), (x + s - 14, y + 10), (x + s - 6, y + 12),
               (x + s - 12, y + s - 8), (x + 22, y + s - 6)], fill=(80, 88, 100))
    d.polygon([(x + 16, y + s - 14), (x + 30, y + s - 28), (x + 36, y + s - 12)],
              fill=(60, 66, 78))
    d.ellipse([x + s - 20, y + 12, x + s - 12, y + 20], fill=(240, 244, 248))
    d.line([x + 8, y + 20, x + 20, y + 30], fill=(190, 60, 50), width=2)
    d.line([x + 6, y + 28, x + 16, y + 38], fill=(190, 60, 50), width=2)


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


def icon_ballot(d, x, y, s):
    d.rectangle([x + 8, y + s - 22, x + s - 8, y + s - 6], outline=(90, 60, 130), width=3)
    d.rectangle([x + 18, y + 6, x + s - 18, y + 26], outline=(90, 60, 130), width=2)
    d.line([x + 23, y + 12, x + s - 23, y + 12], fill=(90, 60, 130), width=2)
    d.line([x + 23, y + 18, x + s - 28, y + 18], fill=(90, 60, 130), width=2)
    d.line([x + 16, y + s - 24, x + s - 16, y + s - 24], fill=(200, 40, 40), width=3)


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


def icon_rocket(d, x, y, s):
    cx = x + s // 2
    d.ellipse([cx - 9, y + 6, cx + 9, y + 34], fill=(90, 100, 115))
    d.polygon([(cx - 9, y + 24), (cx - 17, y + 38), (cx - 8, y + 36)], fill=(178, 60, 40))
    d.polygon([(cx + 9, y + 24), (cx + 17, y + 38), (cx + 8, y + 36)], fill=(178, 60, 40))
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4] if False else
              [cx - 4, y + 13, cx + 4, y + 21], fill=(240, 244, 248))
    d.polygon([(cx - 4, y + 38), (cx, y + s - 4), (cx + 4, y + 38)], fill=(226, 150, 40))
    for sx, sy in ((x + 6, y + 8), (x + s - 10, y + 14), (x + 8, y + 22)):
        d.line([sx - 3, sy, sx + 3, sy], fill=(198, 152, 40), width=2)
        d.line([sx, sy - 3, sx, sy + 3], fill=(198, 152, 40), width=2)


def icon_trophy(d, x, y, s):
    d.polygon([(x + 16, y + 8), (x + s - 16, y + 8), (x + s - 20, y + 30),
               (x + s // 2 + 5, y + 36), (x + s // 2 - 5, y + 36), (x + 20, y + 30)],
              fill=(198, 152, 40))
    d.arc([x + 4, y + 10, x + 20, y + 28], 90, 270, fill=(198, 152, 40), width=3)
    d.arc([x + s - 20, y + 10, x + s - 4, y + 28], 270, 90, fill=(198, 152, 40), width=3)
    d.rectangle([x + s // 2 - 3, y + 36, x + s // 2 + 3, y + 44], fill=(150, 112, 30))
    d.rectangle([x + s // 2 - 11, y + 44, x + s // 2 + 11, y + 50], fill=(150, 112, 30))
    d.ellipse([x + s // 2 - 5, y + 15, x + s // 2 + 5, y + 25], fill=(250, 250, 250))


def icon_leaf(d, x, y, s):
    d.polygon([(x + 12, y + s - 10), (x + 16, y + 18), (x + 30, y + 8),
               (x + s - 10, y + 10), (x + s - 14, y + 30), (x + 30, y + s - 14)],
              fill=(52, 130, 66))
    d.line([x + 14, y + s - 8, x + s - 14, y + 14], fill=(30, 90, 44), width=2)


def icon_drone(d, x, y, s):
    cx, cy = x + s // 2, y + s // 2 + 2
    for dx, dy in ((-15, -11), (15, -11), (-15, 11), (15, 11)):
        d.line([cx, cy, cx + dx, cy + dy], fill=(60, 60, 66), width=3)
        d.ellipse([cx + dx - 7, cy + dy - 3, cx + dx + 7, cy + dy + 3],
                  outline=(146, 30, 30), width=2)
    d.rectangle([cx - 8, cy - 6, cx + 8, cy + 6], fill=(60, 60, 66))
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(200, 40, 40))
    d.line([cx, cy + 6, cx, cy + 13], fill=(60, 60, 66), width=2)


def icon_crash(d, x, y, s):
    d.polygon([(x + 6, y + s - 8), (x + 22, y + s - 24), (x + 34, y + s - 12),
               (x + s - 8, y + s - 8)], fill=(120, 110, 100))
    d.polygon([(x + 14, y + 10), (x + 30, y + 24), (x + 24, y + 30), (x + 10, y + 18)],
              fill=(80, 88, 100))
    d.polygon([(x + 24, y + 20), (x + 36, y + 16), (x + 28, y + 27)], fill=(60, 66, 78))
    for dx, dy, r in ((38, 12, 6), (44, 20, 5), (34, 6, 4)):
        d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=(110, 110, 114))


def icon_ban(d, x, y, s):
    d.polygon([(x + 14, y + 30), (x + 14, y + 18), (x + s // 2, y + 10),
               (x + s - 14, y + 18), (x + s - 14, y + 30)], outline=(120, 84, 30), width=3)
    d.rectangle([x + s // 2 - 4, y + 22, x + s // 2 + 4, y + 30], fill=(120, 84, 30))
    d.ellipse([x + 8, y + 4, x + s - 8, y + s - 4], outline=(200, 40, 40), width=4)
    d.line([x + 14, y + s - 11, x + s - 14, y + 11], fill=(200, 40, 40), width=4)


def bridge_art(d, x0, y0, x1, y1):
    """Kerch Bridge scene for the hero panel: strait, towers, collapsed span."""
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


# ---------------------------------------------------------------- page
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# Masthead
d.rectangle([26, 14, 998, 17], fill=INK)
d.line([26, 22, 998, 22], fill=INK, width=1)
tracked(d, 28, "THE DAY IN WORLD NEWS", F(SERIFB, 25), INK, spacing=7)
tracked(d, 60, "42 STORIES · 6 CONTINENTS · ONE DAY", F(SANSB, 14), ACCENT, spacing=4)
centered(d, 80, "Wednesday 18 November 2026", F(SERIFB, 54), INK)
d.line([26, 142, 998, 142], fill=INK, width=2)

# Hero panel: story 1, Kerch Bridge second-day strike (EUROPE)
d.rectangle([26, 150, 628, 346], outline=INK, width=2)
badge(d, 48, 168, 1, REGIONS["EUROPE"], r=10)
chip(d, 68, 160, "EUROPE", "WAR")
_ls = "LEAD STORY"
d.text((614 - d.textlength(_ls, font=F(SANSB, 10)), 164), _ls, font=F(SANSB, 10), fill=GREY)
bridge_art(d, 40, 184, 614, 258)
_hl = wrap(d, "Ukraine strikes Kerch Bridge for a second straight day", F(SERIFB, 26), 574)
draw_lines(d, (40, 264), _hl, F(SERIFB, 26), INK, 31)
d.text((40, 330), "Kyiv claims the arch collapsed into the strait; Moscow says it downed 1,441 drones.",
       font=F(SANS, 11), fill=(52, 52, 56))

# Stacked mains 2 and 3
STACK = [
    (2, "ASIA", "POLITICS", "Putin lands in Shenzhen as APEC summit opens",
     "Trump meets Marcos in Manila today, then a first Xi–Trump–Putin trilateral.", icon_plane),
    (3, "MIDEAST", "WAR", "Bahrain sounds all-clear as Kuwait downs drones",
     "Kuwait's defences intercepted drones overnight amid US–Iran strikes.", icon_jet),
]
for i, (num, region, topic, head, deck, icon) in enumerate(STACK):
    px, py = 638, 150 + i * 100
    d.rectangle([px, py, 998, py + 96], outline=INK, width=1)
    badge(d, px + 20, py + 19, num, REGIONS[region])
    chip(d, px + 36, py + 10, region, topic)
    icon(d, px + 10, py + 36, 54)
    hf = F(SERIFB, 15)
    draw_lines(d, (px + 78, py + 33), wrap(d, head, hf, 272), hf, INK, 18)
    df = F(SANS, 10)
    draw_lines(d, (px + 78, py + 69), wrap(d, deck, df, 272), df, (52, 52, 56), 12)

# Grid mains 4-12
GRID = [
    (4, "MIDEAST", "POLITICS", "Knesset elects opposition speaker in blow to Netanyahu",
     "Kahana beats Likud's Ohana 66–52; Netanyahu stays caretaker PM.", icon_ballot),
    (5, "GLOBAL", "BUSINESS", "Nvidia beats forecasts in first earnings since Huang exit",
     "Asia stocks snap a four-day slide: KOSPI +3.3%, Nvidia +4.7%.", icon_chip),
    (6, "AMERICAS", "TECH", "Anthropic prices IPO in $1.4 trillion AI debut",
     "825m shares at $70–78; demand ran ~6–7× the offering.", icon_chart),
    (7, "GLOBAL", "SCIENCE", "Voyager 1 reaches one light-day from Earth",
     "16.09bn miles out at 05:16 EST; signals take 24 hours each way.", icon_rocket),
    (8, "EUROPE", "SPORT", "Haaland's 96th-minute penalty sends Norway through",
     "From 2–0 down, Norway beat Denmark 3–2 in Copenhagen.", icon_trophy),
    (9, "GLOBAL", "CLIMATE", "COP31 draft splits 200 nations over fossil fuels",
     "'Transition away' vs 'phase out' — final week runs to Friday.", icon_leaf),
    (10, "AFRICA", "WAR", "UN: 2,230 Sudan civilians killed in 2026, most by drones",
     "OHCHR: 1,630+ of the deaths were drone strikes, Jan–Oct.", icon_drone),
    (11, "EUROPE", "DISASTER", "Russian military plane crash in Siberia kills all 19 aboard",
     "Aircraft down in Kemerovo region; technical fault blamed.", icon_crash),
    (12, "OCEANIA", "POLITICS", "Australia sanctions Israeli settlers over West Bank violence",
     "Canberra targets 3 people, 4 groups over E1 settlement plan.", icon_ban),
]
for i, (num, region, topic, head, deck, icon) in enumerate(GRID):
    gx, gy = 26 + (i % 3) * 328, 354 + (i // 3) * 80
    d.rectangle([gx, gy, gx + 316, gy + 74], outline=RULE, width=1)
    badge(d, gx + 19, gy + 16, num, REGIONS[region])
    chip(d, gx + 34, gy + 7, region, topic, h=17)
    icon(d, gx + 8, gy + 28, 44)
    hf = F(SERIFB, 13)
    draw_lines(d, (gx + 60, gy + 27), wrap(d, head, hf, 248), hf, INK, 15)
    d.text((gx + 60, gy + 60), deck,
           font=fit_font(d, deck, SANS, 10, 248), fill=(52, 52, 56))


# ------------------------------------------------------- Day in Numbers
d.line([26, 596, 998, 596], fill=INK, width=2)
d.text((26, 602), "THE DAY IN NUMBERS", font=F(SANSB, 13), fill=INK)
_dn_note = "Six figures that frame the day"
d.text((998 - d.textlength(_dn_note, font=F(SANS, 10)), 604), _dn_note,
       font=F(SANS, 10), fill=GREY)
d.line([26, 620, 998, 620], fill=RULE, width=1)
NUMBERS = [
    ("1,441", "drones Russia says it shot down over 22 regions — a record"),
    ("66–52", "Knesset vote electing Kahana speaker over Netanyahu's man"),
    ("$1.4tn", "Anthropic's possible value at the top of its IPO range"),
    ("16.09bn", "miles out — one light-day: Voyager 1's distance (NASA)"),
    ("2,230", "Sudan civilians confirmed killed Jan–Oct, most by drones"),
    ("$120bn", "a year: adaptation-finance target in COP31's draft text"),
]
for i, (big, label) in enumerate(NUMBERS):
    nx = 26 + i * 162
    d.text((nx, 626), big, font=F(SERIFB, 21), fill=ACCENT)
    draw_lines(d, (nx, 652), wrap(d, label, F(SANS, 9), 154), F(SANS, 9), (52, 52, 56), 11)

# ------------------------------------------------------------- world map
# Dot-matrix world map: 100 x 22 cells, equirectangular (reused from v3/v4).
# '#' = land, '.' = ocean. Rows run lat ~+77 (top) to ~-54 (bottom),
# columns run lon -180 (left) to +180 (right).
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

# Pins: story number -> (col, row, region). Positions approximate the
# story location, spread by a cell or two where true locations cluster
# (New York, Gaza, northern Europe). Story 7 (Voyager 1) is in deep
# space and gets the star marker at the map's top-right corner.
PINS = {
    1: (64, 5, "EUROPE"), 2: (82, 9, "ASIA"), 3: (65, 10, "MIDEAST"),
    4: (62, 8, "MIDEAST"), 5: (16, 7, "GLOBAL"), 6: (29, 5, "AMERICAS"),
    8: (52, 2, "EUROPE"), 9: (55, 7, "GLOBAL"), 10: (62, 12, "AFRICA"),
    11: (74, 4, "EUROPE"), 12: (91, 19, "OCEANIA"),
    13: (59, 2, "EUROPE"), 14: (57, 4, "EUROPE"), 15: (48, 7, "EUROPE"),
    16: (53, 4, "EUROPE"), 17: (49, 3, "EUROPE"), 18: (60, 5, "EUROPE"),
    19: (45, 4, "EUROPE"), 20: (62, 3, "EUROPE"),
    21: (85, 7, "ASIA"), 22: (89, 6, "ASIA"), 23: (78, 11, "ASIA"),
    24: (73, 12, "ASIA"), 25: (72, 8, "ASIA"), 26: (69, 6, "ASIA"),
    27: (75, 9, "ASIA"), 28: (31, 6, "AMERICAS"), 29: (32, 10, "AMERICAS"),
    30: (27, 7, "AMERICAS"), 31: (27, 10, "AMERICAS"), 32: (37, 14, "AMERICAS"),
    33: (85, 10, "AMERICAS"), 34: (30, 8, "AMERICAS"),
    35: (58, 8, "MIDEAST"), 36: (59, 10, "MIDEAST"), 37: (56, 12, "MIDEAST"),
    38: (67, 7, "MIDEAST"), 39: (59, 14, "AFRICA"), 40: (46, 11, "AFRICA"),
    41: (98, 16, "OCEANIA"), 42: (50, 5, "EUROPE"),
}

d.rectangle([26, 696, 474, 936], outline=INK, width=1)
d.text((38, 704), "WHERE IT HAPPENED", font=F(SANSB, 12), fill=INK)
d.rectangle([34, 724, 466, 822], fill=(238, 241, 238))
OX, OY, CELL = 40, 728, 4.2
LAND = (43, 52, 63)
for r, row in enumerate(MAP_ROWS):
    row = row.ljust(MAP_COLS, ".")[:MAP_COLS]
    for c, ch in enumerate(row):
        if ch == "#":
            cx, cy = OX + (c + 0.5) * CELL, OY + (r + 0.5) * CELL
            d.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5], fill=LAND)
for num in sorted(PINS):
    c, r, region = PINS[num]
    cx, cy = OX + (c + 0.5) * CELL, OY + (r + 0.5) * CELL
    d.ellipse([cx - 7.5, cy - 7.5, cx + 7.5, cy + 7.5], fill=REGIONS[region],
              outline=(255, 255, 255), width=2)
    t = str(num)
    pf = F(SANSB, 8)
    d.text((cx - d.textlength(t, font=pf) / 2, cy - 5), t, font=pf, fill=(255, 255, 255))

# Deep-space star for story 7 (Voyager 1)
sx, sy = OX + 96.5 * CELL, OY + 1.5 * CELL
d.polygon([(sx, sy - 10), (sx + 2.6, sy - 2.6), (sx + 10, sy), (sx + 2.6, sy + 2.6),
           (sx, sy + 10), (sx - 2.6, sy + 2.6), (sx - 10, sy), (sx - 2.6, sy - 2.6)],
          fill=REGIONS["GLOBAL"])
badge(d, sx - 13, sy - 11, 7, REGIONS["GLOBAL"], r=7)
d.text((38, 828), "★ 7 · VOYAGER 1 — ONE LIGHT-DAY OUT, IN DEEP SPACE",
       font=F(SANSB, 9), fill=(52, 52, 56))

# Legend: the per-region colour system
lx = 38
for region in ("EUROPE", "MIDEAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "GLOBAL"):
    label = LEGEND_LABEL.get(region, region)
    d.ellipse([lx, 850, lx + 8, 858], fill=REGIONS[region])
    d.text((lx + 12, 849), label, font=F(SANSB, 8), fill=(52, 52, 56))
    lx += 12 + d.textlength(label, font=F(SANSB, 8)) + 9

# Stories-by-region tally (auditable breadth)
d.text((38, 872), "STORIES BY REGION", font=F(SANSB, 10), fill=INK)
TALLY = [("EUROPE", 11, "EUROPE"), ("ASIA", 9, "ASIA"),
         ("AMERICAS", 7, "AMERICAS"), ("MIDDLE EAST", 6, "MIDEAST"),
         ("GLOBAL", 4, "GLOBAL"), ("AFRICA", 3, "AFRICA"),
         ("OCEANIA", 2, "OCEANIA"), ("TOTAL", 42, None)]
for i, (label, count, key) in enumerate(TALLY):
    tx = 38 + (i % 4) * 110
    ty = 890 + (i // 4) * 18
    d.text((tx, ty), label, font=F(SANS, 8), fill=(52, 52, 56))
    if key:
        bw = count * 3.2
        d.rectangle([tx + 54, ty + 1, tx + 54 + bw, ty + 8], fill=REGIONS[key])
        d.text((tx + 57 + bw, ty), str(count), font=F(SANSB, 8), fill=INK)
    else:
        d.text((tx + 54, ty), str(count), font=F(SANSB, 9), fill=ACCENT)


# ------------------------------------------------------- ALSO ON WEDNESDAY
ALSO = [
    (13, "EUROPE", "Riga: Saeima backs Kulbergs government, 57–34"),
    (14, "EUROPE", "Hungary halts Ukraine rail traffic after strikes"),
    (15, "EUROPE", "France confirms training mission inside Ukraine"),
    (16, "EUROPE", "Ramstein: Berlin, London rebuff US on strikes"),
    (17, "EUROPE", "Britain sanctions 8 settler firms, Tzav 9 group"),
    (18, "EUROPE", "M5.3 quake hits Romania; no tsunami threat"),
    (19, "EUROPE", "Ireland beat Kosovo 3–0; Parrott hits two pens"),
    (20, "EUROPE", "UN: 372 civilians killed in Ukraine in October"),
    (21, "ASIA", "Seoul in emergency meeting on Java security flaws"),
    (22, "ASIA", "Japan exports rise 14th straight month on chips"),
    (23, "ASIA", "Thailand to scrap all tariffs on US goods"),
    (24, "ASIA", "Cyclone Akvan nears India; landfall due 20 Nov"),
    (25, "ASIA", "India electronics exports jump 44% to $31.97bn"),
    (26, "ASIA", "Suicide car bomb at Pakistan checkpoint kills 5"),
    (27, "ASIA", "India beat Pakistan 2–1 for 10th SAFF title"),
    (28, "ASIA", "Huawei US trial nears end; jury out Wednesday"),
    (29, "AMERICAS", "Iran-backed plot on Trump: 27½-year sentence"),
    (30, "AMERICAS", "FAA pauses routers tied to US ground stop"),
    (31, "AMERICAS", "5 injured as JetBlue flight hits turbulence"),
    (32, "AMERICAS", "20 uncontacted Awá emerge in Brazil seeking food"),
    (33, "AMERICAS", "Peru's Fujimori meets Sheinbaum in Shenzhen"),
    (34, "AMERICAS", "NSA reports 'temporary degradation' amid outages"),
    (35, "MIDEAST", "Gaza medics: Israeli fire kills 4, incl. boy, 6"),
    (36, "MIDEAST", "UN: 100,000 Gaza tents wait; funds $173m short"),
    (37, "MIDEAST", "Gaza families get one hot meal every two days"),
    (38, "MIDEAST", "US–Iran stalemate deepens under naval blockade"),
    (39, "AFRICA", "South Sudan delays election again, to Feb 2027"),
    (40, "AFRICA", "Guinea seeks backers for $1.9bn deep-water port"),
    (41, "OCEANIA", "Pacific: Russia rejects 1.5°C text at COP31"),
    (42, "GLOBAL", "World Court rules Thursday on Rohingya case"),
]
d.rectangle([482, 696, 998, 936], outline=INK, width=1)
d.text((494, 704), "ALSO ON WEDNESDAY", font=F(SERIFB, 15), fill=INK)
_also_note = "30 more verified stories"
d.text((986 - d.textlength(_also_note, font=F(SANS, 9)), 708), _also_note,
       font=F(SANS, 9), fill=GREY)
d.line([494, 730, 986, 730], fill=RULE, width=1)
for i, (num, region, text) in enumerate(ALSO):
    ax = 494 if i < 15 else 744
    ay = 738 + (i % 15) * 13.0
    nf = F(SANSB, 10)
    d.text((ax, ay), str(num), font=nf, fill=REGIONS[region])
    tf = fit_font(d, text, SANS, 10, 221)
    d.text((ax + 21, ay), text, font=tf, fill=INK)

# ------------------------------------------------------- quote of the day
d.rectangle([26, 944, 998, 988], outline=INK, width=1)
d.text((38, 952), "QUOTE OF THE DAY — US PRESIDENT DONALD TRUMP, IN MANILA (REUTERS)",
       font=F(SANSB, 9), fill=ACCENT)
d.text((38, 966),
       "“It's life. When you're big and powerful and you have all the money, "
       "things like that happen. It's fine.”",
       font=F(SERIF, 12), fill=INK)

# ---------------------------------------------------------------- footer
d.line([26, 996, 998, 996], fill=INK, width=1)
centered(d, 1001,
         "Sources: Reuters · BBC · UN News · NASA · USGS · UEFA · IOM · WFP · IMD · PINA",
         F(SANS, 9), GREY)
centered(d, 1012,
         "Disputed claims are attributed to their source. "
         "All illustrations are original drawings, made for this front page.",
         F(SANS, 9), GREY)

img.save(OUT)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
