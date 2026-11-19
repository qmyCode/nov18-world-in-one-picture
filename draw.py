"""Renderer for 'The World on Wednesday' — news-image-20261118 final entry.

Draws a one-page newspaper front page (1024x1024 PNG) summing up the news of
Wednesday 18 November 2026: 3 large mains, 11 medium mains and 34 one-liners,
48 stories across six continents, plus a Day in Numbers strip and a pin map.
All artwork is drawn from scratch with PIL primitives.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

PAPER = (247, 242, 231)
PAPER_DARK = (238, 230, 214)
INK = (22, 26, 34)
INK_SOFT = (58, 62, 70)
NAVY = (13, 32, 56)
NAVY_LIGHT = (24, 52, 84)
GOLD = (198, 158, 44)
GOLD_SOFT = (226, 199, 120)
RED = (158, 28, 36)
TEAL = (16, 92, 96)
WHITE = (252, 250, 244)

REGION_COLORS = {
    "EUROPE": (38, 84, 150),
    "ASIA": (178, 92, 26),
    "AMERICAS": (24, 110, 74),
    "MIDDLE EAST": (158, 28, 36),
    "AFRICA": (146, 104, 18),
    "OCEANIA": (88, 62, 150),
    "GLOBAL": (70, 74, 84),
    "BUSINESS": (16, 92, 96),
    "SCIENCE": (52, 96, 140),
    "SPORT": (30, 128, 60),
}

_FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = _FONT_DIR + "/liberation/LiberationSerif-Bold.ttf"
SERIF_R = _FONT_DIR + "/liberation/LiberationSerif-Regular.ttf"
SERIF_I = _FONT_DIR + "/liberation/LiberationSerif-Italic.ttf"
SANS_B = _FONT_DIR + "/liberation/LiberationSans-Bold.ttf"
SANS_R = _FONT_DIR + "/liberation/LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# --------------------------------------------------------------------------
# Story data — every item verified against reputable reporting of the
# 18 November 2026 news cycle (see the build report for sources).
# --------------------------------------------------------------------------

BIG = [
    {
        "region": "MIDDLE EAST", "tag": "WAR",
        "headline": "US and Iran trade fire over Bahrain",
        "deck": "Iran says its drones struck a US radar at Sheikh Isa air base; "
                "CENTCOM says all were intercepted. US jets then hit an IRGC "
                "missile site on Qeshm Island.",
        "art": "gulf",
    },
    {
        "region": "AMERICAS", "tag": "MARKETS",
        "headline": "Anthropic prices IPO at $83 in record debut",
        "deck": "Above its $70-78 range, the upsized sale of 980m shares raises "
                "about $81bn - the largest IPO ever - and values the Claude "
                "maker near $1.5 trillion.",
        "art": "ipo",
    },
    {
        "region": "EUROPE", "tag": "WAR",
        "headline": "Ukraine strikes Kerch Bridge for second day",
        "deck": "Kyiv says the road arch fell into the strait; Moscow says it "
                "downed a record 1,441 drones over 22 regions as its strikes "
                "pounded Kyiv's bridges.",
        "art": "bridge",
    },
]

MEDIUM = [
    {"n": 4, "region": "ASIA", "icon": "summit",
     "headline": "Xi greets Trump in Shenzhen as APEC opens",
     "deck": "Putin took a two-hour bilateral with Xi; Thursday brings a "
             "Xi-Trump summit and a first-ever trilateral."},
    {"n": 5, "region": "AMERICAS", "icon": "flag",
     "headline": "US restores military ties with Venezuela",
     "deck": "Hegseth signs a training-to-intelligence deal in Caracas, 10 "
             "months after US forces seized Maduro."},
    {"n": 6, "region": "BUSINESS", "icon": "chip",
     "headline": "Nvidia revenue leaps 103% to $115.8bn",
     "deck": "Guidance of $130bn beats forecasts - yet the shares fade 2.9% "
             "as the Huang succession weighs."},
    {"n": 7, "region": "AMERICAS", "icon": "chartdown",
     "headline": "Dow falls 561 in third straight big drop",
     "deck": "The S&P slips a fifth straight day on hawkish Fed minutes; "
             "the Nasdaq edges up 0.4%."},
    {"n": 8, "region": "EUROPE", "icon": "euro",
     "headline": "EU to propose a \u20ac45bn loan for Ukraine",
     "deck": "Budget-backed loans for 2027 would cover two-thirds of Kyiv's "
             "\u20ac70bn shortfall, repaid from reparations."},
    {"n": 9, "region": "MIDDLE EAST", "icon": "ballot",
     "headline": "Knesset elects opposition speaker, 66-52",
     "deck": "Eisenkot ally Matan Kahana ousts Netanyahu's pick; the PM "
             "stays on as caretaker after deadlock."},
    {"n": 10, "region": "GLOBAL", "icon": "leaf",
     "headline": "COP31 draft splits 200 nations on fossils",
     "deck": "Rival 'transition away' and 'phase out' texts, a $120bn "
             "adaptation goal and a Friday deadline."},
    {"n": 11, "region": "SCIENCE", "icon": "dish",
     "headline": "Voyager 1 reaches one light-day out",
     "deck": "At 05:16 EST the 1977 probe hit 16.09bn miles; its signals "
             "now take a full 24 hours to reach Earth."},
    {"n": 12, "region": "AFRICA", "icon": "warn",
     "headline": "UN: 2,230 Sudan civilians killed in 2026",
     "deck": "OHCHR counts the dead from January to October - over 1,630 "
             "of them killed by drone strikes."},
    {"n": 13, "region": "SPORT", "icon": "ball",
     "headline": "Haaland's 96th-minute penalty saves Norway",
     "deck": "Norway rally from 2-0 down to beat Denmark 3-2 in Copenhagen "
             "and reach the Nations League last eight."},
    {"n": 14, "region": "ASIA", "icon": "cyclone",
     "headline": "Cyclone Akvan bears down on India's coast",
     "deck": "IMD forecasts landfall near Nellore-Tuni around noon on "
             "20 Nov, gusting to 145 km/h."},
]

QUOTE = {
    "text": "\u201cIt's life. When you're big and powerful and you have all "
            "the money, things like that happen. It's fine.\u201d",
    "who": "Donald Trump, on the wave of US tech and banking outages (Reuters)",
}

NUMBERS = [
    ("$83", "Anthropic IPO price, above range"),
    ("$115.8bn", "Nvidia revenue, +103% YoY"),
    ("1,441", "drones Russia says it downed"),
    ("66-52", "Knesset speaker vote"),
    ("2,230", "Sudan civilians killed in 2026"),
    ("24 hrs", "Voyager 1's signal time home"),
]

ALSO = [
    ("EUROPE", "Latvia's Saeima backs PM Kulbergs' new government 57-34"),
    ("EUROPE", "Hungary halts Ukraine rail traffic as drones hit near Mukachevo"),
    ("EUROPE", "France confirms a small training and support mission inside Ukraine"),
    ("EUROPE", "Germany and Britain reject US criticism of Kyiv's deep strikes"),
    ("EUROPE", "Britain sanctions eight settlement firms and the Tzav 9 group"),
    ("EUROPE", "Magnitude 5.3 quake strikes Romania, 131 km deep; no tsunami threat"),
    ("EUROPE", "Ireland beat Kosovo 3-0, Parrott scoring two penalties"),
    ("ASIA", "Japan's exports rise a 14th straight month on chip shipments"),
    ("ASIA", "Thailand to scrap tariffs on US goods, buy $2.6bn more farm produce"),
    ("ASIA", "India's electronics exports jump 44% to nearly $32bn"),
    ("ASIA", "Suicide car bombing at a Pakistan checkpoint kills 5, injures 13"),
    ("ASIA", "India beat Pakistan 2-1 to win a record 10th SAFF title"),
    ("ASIA", "China gives Canada tariff relief on C$400m of exports"),
    ("ASIA", "ICRA estimates India's GDP grew 7.5% in July-September"),
    ("ASIA", "Amazon to invest $7bn in India renewables by 2030"),
    ("AMERICAS", "Merchant gets 330 months for the Iran-backed plot to kill Trump"),
    ("AMERICAS", "FAA pauses router installs tied to Friday's nationwide ground stop"),
    ("AMERICAS", "Five hurt as a JetBlue flight hits severe turbulence"),
    ("AMERICAS", "Uncontacted Awa emerge in Brazil's Maranhao asking for food"),
    ("AMERICAS", "Sheinbaum: Mexico-US trade talks are 'very far along'"),
    ("AMERICAS", "Alaska is called for Peltola; Democrats take the Senate 56-44"),
    ("AMERICAS", "House Democrats elect Clark, Aguilar, Neguse and Lieu to lead"),
    ("AMERICAS", "US debt limit is forecast to reach $41.1 trillion in Feb-March"),
    ("AMERICAS", "Apple restores all services after a three-hour outage"),
    ("MIDDLE EAST", "Israeli fire kills four in Gaza, incl. a 6-year-old, medics say"),
    ("MIDDLE EAST", "IOM: 100,000 tents await entry to Gaza; shelter fund $173m short"),
    ("MIDDLE EAST", "Displaced Gaza families get one WFP hot meal every two days"),
    ("MIDDLE EAST", "US blockade squeezes Iran as mediators work on a deal"),
    ("AFRICA", "South Sudan delays its election again, now to 11 Feb 2027"),
    ("AFRICA", "Guinea seeks backers for a planned $1.9bn deep-water port"),
    ("OCEANIA", "Australia sanctions Israeli settlers over E1 expansion"),
    ("OCEANIA", "Pacific negotiators say Russia blocked 1.5C text at COP31"),
    ("GLOBAL", "World Court rules Thursday on Myanmar's Rohingya genocide case"),
    ("GLOBAL", "Robert Pattinson is confirmed as the seventh James Bond"),
]

# Pins for the map: (story number, lon, lat). Story 11 (Voyager) is in deep
# space and gets no pin.
PINS = [
    (1, 50.6, 26.2), (2, -74.0, 40.7), (3, 36.6, 45.3), (4, 114.1, 22.5),
    (5, -66.9, 10.5), (6, -122.0, 37.4), (7, -71.5, 41.8), (8, 4.4, 50.8),
    (9, 35.2, 31.8), (10, 30.7, 36.9), (12, 32.5, 15.6), (13, 12.6, 55.7),
    (14, 84.0, 15.0),
]

# Coarse dot world map, 100 cols x 22 rows (3.6 deg lon x ~6.5 deg lat per
# cell). '#' is land.
WORLD = [
    "                                                                                                    ",
    "        #########                                                                                   ",
    "     ##############        ##   #####################################################  #########    ",
    "    ################      ########################################################## #############  ",
    "     ##############        ######################################################   ##########    ",
    "      ##########            #################  #################################      ########    ",
    "       ########              ################ ##################################        ####      ",
    "        ######                ##############   #################################                  ",
    "         ####                  ##########       ##############################                    ",
    "          ##                    ########         ##################  #######                      ",
    "           #                     ######           ################    #####        ##  ##         ",
    "                                #######            ##############      ###       ########         ",
    "                                ########            ############                  #########       ",
    "                                #########            ##########                    ########       ",
    "                                 ########             ########                      ######        ",
    "                                 #######               ######                        ####         ",
    "                                  #####                 ####                                        ",
    "                                  ####                  ###                       ##########      ",
    "                                  ###                    ##                      ############     ",
    "                                  ##                                               ########       ",
    "                                  #                                                 ######        ",
    "                                                                                                    ",
]


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap(draw, s, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, s, path, size, max_w, min_size=8):
    """Shrink a single-line string until it fits max_w."""
    while size > min_size:
        fnt = font(path, size)
        if text_w(draw, s, fnt) <= max_w:
            return fnt
        size -= 1
    return font(path, min_size)


def draw_wrapped(draw, xy, s, fnt, fill, max_w, line_h, max_lines=None):
    x, y = xy
    lines = wrap(draw, s, fnt, max_w)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += line_h
    return y


# --------------------------------------------------------------------------
# Artwork for the three large mains — flat geometric scenes.
# --------------------------------------------------------------------------

def art_gulf(d, x, y, w, h):
    """Night Gulf: radar headland, drones, dashed tracks, a jet streak."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 38, 62))
    for i in range(4):  # sky bands
        yy = y + 6 + i * 8
        d.line([x + 10, yy, x + w - 10, yy], fill=(28, 58, 92), width=2)
    # sea
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(13, 74, 84))
    for i in range(2):
        yy = y + h - 14 + i * 6
        d.line([x + 8, yy, x + w - 8, yy], fill=(30, 110, 118), width=2)
    # headland + radar
    d.polygon([(x, y + h - 20), (x + 92, y + h - 20), (x + 68, y + h - 42),
               (x + 16, y + h - 42)], fill=(8, 22, 38))
    d.line([x + 42, y + h - 42, x + 42, y + h - 58], fill=GOLD_SOFT, width=3)
    d.arc([x + 22, y + h - 76, x + 62, y + h - 38], start=200, end=340,
          fill=GOLD_SOFT, width=3)
    d.ellipse([x + 38, y + h - 60, x + 46, y + h - 52], fill=GOLD)
    # drones (small x-quads)
    drones = [(x + w - 88, y + 16), (x + w - 52, y + 30)]
    for cx, cy in drones:
        d.line([cx - 8, cy - 5, cx + 8, cy + 5], fill=(230, 120, 90), width=2)
        d.line([cx - 8, cy + 5, cx + 8, cy - 5], fill=(230, 120, 90), width=2)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(240, 150, 110))
    # dashed tracks from the drones toward the radar
    for cx, cy in drones:
        for t in (0.25, 0.45, 0.65, 0.85):
            px = cx + (x + 46 - cx) * t
            py = cy + (y + h - 56 - cy) * t
            d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6],
                      fill=(240, 210, 120))
    # jet streak low over the sea
    jy = y + h - 30
    d.polygon([(x + w - 128, jy + 4), (x + w - 106, jy - 2),
               (x + w - 128, jy - 6)], fill=(220, 226, 235))
    d.line([x + w - 106, jy - 2, x + w - 34, jy - 2],
           fill=(220, 226, 235), width=2)


def art_ipo(d, x, y, w, h):
    """Nasdaq debut: rising gold steps, a big price, an ANT ticker chip."""
    d.rectangle([x, y, x + w, y + h], fill=(10, 26, 20))
    base = y + h - 12
    heights = [16, 28, 40, 54]
    for i, bh in enumerate(heights):
        bx = x + 18 + i * 52
        d.rectangle([bx, base - bh, bx + 38, base], fill=(30, 122, 78)
                    if i < 3 else GOLD)
    pts = [(x + 30, base - 20), (x + 82, base - 32), (x + 134, base - 44),
           (x + 186, base - 58)]
    d.line(pts, fill=(240, 220, 150), width=3)
    ax, ay = pts[-1]
    d.polygon([(ax, ay), (ax - 14, ay + 2), (ax - 4, ay + 12)],
              fill=(240, 220, 150))
    big = font(SERIF_B, 44)
    d.text((x + w - 118, y + 12), "$83", font=big, fill=WHITE)
    chip_f = font(SANS_B, 13)
    d.rounded_rectangle([x + w - 108, y + 66, x + w - 18, y + 90], radius=5,
                        fill=GOLD)
    d.text((x + w - 92, y + 70), "ANT", font=chip_f, fill=(20, 20, 20))
    d.text((x + w - 62, y + 70), "IPO", font=chip_f, fill=(20, 20, 20))


def art_bridge(d, x, y, w, h):
    """A long bridge over a strait, one span down, smoke rising."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 74, 96))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(24, 66, 92))
    for i in range(2):
        yy = y + h - 15 + i * 6
        d.line([x + 8, yy, x + w - 8, yy], fill=(44, 96, 122), width=2)
    deck = y + h - 36
    for px in (x + 26, x + 108, x + 252, x + w - 30):
        d.rectangle([px, deck, px + 6, y + h - 22], fill=(16, 24, 34))
    d.rectangle([x + 6, deck - 5, x + 168, deck], fill=(16, 24, 34))
    d.rectangle([x + 196, deck - 5, x + w - 6, deck], fill=(16, 24, 34))
    # fallen span, tilted into the water
    d.polygon([(x + 168, deck), (x + 198, deck + 16), (x + 193, deck + 21),
               (x + 164, deck + 5)], fill=(16, 24, 34))
    # smoke plume, kept inside the frame
    for cx, cy, r in [(x + 180, deck - 13, 7), (x + 189, deck - 22, 9),
                      (x + 200, deck - 30, 11)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 126, 134))
    # drone dots overhead
    for cx, cy in [(x + 60, y + 16), (x + 96, y + 10), (x + 250, y + 18)]:
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(240, 170, 90))


ART = {"gulf": art_gulf, "ipo": art_ipo, "bridge": art_bridge}


# --------------------------------------------------------------------------
# Small icons for medium mains (drawn in a 30x30 box at x, y).
# --------------------------------------------------------------------------

def icon(d, kind, x, y, color):
    d.rounded_rectangle([x, y, x + 30, y + 30], radius=6, fill=color)
    cx, cy = x + 15, y + 15
    wht = (250, 248, 240)
    if kind == "summit":  # three overlapping circles = trilateral
        d.ellipse([cx - 10, cy - 9, cx + 2, cy + 3], outline=wht, width=2)
        d.ellipse([cx - 2, cy - 9, cx + 10, cy + 3], outline=wht, width=2)
        d.ellipse([cx - 6, cy - 2, cx + 6, cy + 10], outline=wht, width=2)
    elif kind == "flag":
        d.line([cx - 8, cy - 9, cx - 8, cy + 10], fill=wht, width=2)
        d.polygon([(cx - 8, cy - 9), (cx + 9, cy - 5), (cx - 8, cy - 1)],
                  fill=wht)
        d.line([cx - 8, cy + 4, cx + 7, cy + 4], fill=wht, width=2)
        d.line([cx - 8, cy + 8, cx + 5, cy + 8], fill=wht, width=2)
    elif kind == "chip":
        d.rectangle([cx - 7, cy - 7, cx + 7, cy + 7], outline=wht, width=2)
        for off in (-4, 0, 4):
            d.line([cx + off, cy - 11, cx + off, cy - 7], fill=wht, width=2)
            d.line([cx + off, cy + 7, cx + off, cy + 11], fill=wht, width=2)
            d.line([cx - 11, cy + off, cx - 7, cy + off], fill=wht, width=2)
            d.line([cx + 7, cy + off, cx + 11, cy + off], fill=wht, width=2)
    elif kind == "chartdown":
        for i, bh in enumerate((10, 6, 2)):
            bx = cx - 11 + i * 9
            d.rectangle([bx, cy + 8 - bh, bx + 6, cy + 8], fill=wht)
        d.line([cx - 11, cy - 8, cx + 10, cy + 3], fill=(255, 170, 150),
               width=2)
    elif kind == "euro":
        f = font(SANS_B, 19)
        d.text((cx - 7, cy - 11), "\u20ac", font=f, fill=wht)
    elif kind == "ballot":
        d.rectangle([cx - 10, cy - 2, cx + 10, cy + 10], outline=wht, width=2)
        d.rectangle([cx - 5, cy - 11, cx + 5, cy - 3], fill=wht)
        d.line([cx - 5, cy + 4, cx + 5, cy + 4], fill=wht, width=2)
    elif kind == "leaf":
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=wht, width=2)
        d.line([cx - 6, cy + 7, cx + 7, cy - 7], fill=wht, width=2)
    elif kind == "dish":
        d.arc([cx - 11, cy - 11, cx + 7, cy + 7], start=300, end=120,
              fill=wht, width=2)
        d.line([cx - 2, cy - 2, cx + 9, cy + 9], fill=wht, width=2)
        for r in (5, 9):
            d.arc([cx + 3 - r, cy - 12 - r, cx + 3 + r, cy - 12 + r],
                  start=20, end=110, fill=wht, width=2)
    elif kind == "warn":
        d.polygon([(cx, cy - 11), (cx + 11, cy + 9), (cx - 11, cy + 9)],
                  outline=wht, width=2)
        d.line([cx, cy - 4, cx, cy + 3], fill=wht, width=2)
        d.ellipse([cx - 1, cy + 5, cx + 1, cy + 7], fill=wht)
    elif kind == "ball":
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=wht, width=2)
        d.polygon([(cx, cy - 4), (cx + 4, cy - 1), (cx + 2, cy + 4),
                   (cx - 2, cy + 4), (cx - 4, cy - 1)], fill=wht)
    elif kind == "cyclone":
        for start in (0, 120, 240):
            d.arc([cx - 10, cy - 10, cx + 10, cy + 10], start=start,
                  end=start + 80, fill=wht, width=2)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=wht)
    else:
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=wht)


# --------------------------------------------------------------------------
# Page layout
# --------------------------------------------------------------------------

def section_label(d, y, text, note=""):
    f = font(SANS_B, 11)
    d.text((14, y), text, font=f, fill=NAVY)
    tw = text_w(d, text, f)
    d.line([14 + tw + 10, y + 6, 1010, y + 6], fill=GOLD, width=2)
    if note:
        fn = font(SANS_R, 9)
        nw = text_w(d, note, fn)
        d.text((1010 - nw, y + 1), note, font=fn, fill=INK_SOFT)


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    d.rectangle([0, 0, W, 86], fill=NAVY)
    d.rectangle([0, 86, W, 90], fill=GOLD)
    d.text((14, 10), "T H E   D A Y   I N   O N E   P I C T U R E",
           font=font(SANS_B, 11), fill=GOLD_SOFT)
    d.text((14, 26), "THE WORLD ON WEDNESDAY", font=font(SERIF_B, 36),
           fill=WHITE)
    d.text((14, 66),
           "Wednesday 18 November 2026  ·  the whole day, from Asia-Pacific "
           "through Europe to the Americas",
           font=font(SANS_R, 11), fill=(196, 208, 224))
    d.rounded_rectangle([838, 12, 1010, 74], radius=6, outline=GOLD, width=2)
    d.text((856, 16), "48", font=font(SERIF_B, 30), fill=GOLD_SOFT)
    d.text((908, 22), "STORIES", font=font(SANS_B, 13), fill=WHITE)
    d.text((908, 42), "SIX CONTINENTS", font=font(SANS_B, 10),
           fill=(196, 208, 224))
    d.text((856, 52), "one front page", font=font(SERIF_I, 10),
           fill=(196, 208, 224))

    # ---- Day in Numbers --------------------------------------------------
    d.text((14, 93), "THE DAY IN NUMBERS", font=font(SANS_B, 8), fill=RED)
    ny = 102
    cell_w = (1024 - 28) / 6.0
    for i, (big, cap) in enumerate(NUMBERS):
        cx = 14 + i * cell_w
        if i:
            d.line([cx - 5, ny + 2, cx - 5, ny + 32], fill=(206, 196, 168),
                   width=1)
        fb = fit_font(d, big, SERIF_B, 19, cell_w - 12)
        d.text((cx, ny), big, font=fb, fill=NAVY)
        cf = fit_font(d, cap, SANS_R, 8, cell_w - 12)
        d.text((cx, ny + 23), cap, font=cf, fill=INK_SOFT)

    # ---- The Big Three ---------------------------------------------------
    section_label(d, 140, "THE BIG THREE", "stories 1-3")
    py, ph = 156, 202
    pw = (1024 - 28 - 20) / 3.0
    for i, story in enumerate(BIG):
        px = 14 + i * (pw + 10)
        d.rectangle([px, py, px + pw, py + ph], fill=(255, 253, 246),
                    outline=(208, 198, 168), width=1)
        ART[story["art"]](d, px + 8, py + 8, pw - 16, 78)
        color = REGION_COLORS[story["region"]]
        chip = story["region"] + " · " + story["tag"]
        cf = font(SANS_B, 9)
        cw = text_w(d, chip, cf) + 12
        d.rectangle([px + 10, py + 92, px + 10 + cw, py + 106], fill=color)
        d.text((px + 16, py + 94), chip, font=cf, fill=WHITE)
        num_f = font(SERIF_B, 15)
        d.text((px + pw - 26, py + 90), str(i + 1), font=num_f, fill=GOLD)
        draw_wrapped(d, (px + 10, py + 110), story["headline"],
                     font(SERIF_B, 17), INK, pw - 20, 20, max_lines=2)
        draw_wrapped(d, (px + 10, py + 152), story["deck"],
                     font(SANS_R, 10), INK_SOFT, pw - 20, 13, max_lines=3)

    # ---- More of the Day -------------------------------------------------
    section_label(d, 366, "MORE OF THE DAY", "stories 4-14")
    gy, row_h = 382, 53
    col_w = (1024 - 28 - 20) / 3.0
    cells = list(MEDIUM) + [None]  # last cell carries the quote
    for idx, story in enumerate(cells):
        cx = 14 + (idx % 3) * (col_w + 10)
        cy = gy + (idx // 3) * row_h
        if story is None:
            d.rectangle([cx, cy + 2, cx + col_w, cy + row_h - 4],
                        fill=PAPER_DARK, outline=(208, 198, 168), width=1)
            qy = draw_wrapped(d, (cx + 8, cy + 5), QUOTE["text"],
                              font(SERIF_I, 10), INK, col_w - 16, 12,
                              max_lines=3)
            d.text((cx + 8, qy + 1), QUOTE["who"], font=font(SANS_R, 7),
                   fill=INK_SOFT)
            continue
        color = REGION_COLORS[story["region"]]
        icon(d, story["icon"], cx, cy + 4, color)
        nf = font(SERIF_B, 12)
        d.text((cx + 38, cy + 1), str(story["n"]), font=nf, fill=GOLD)
        hx = cx + 38 + text_w(d, str(story["n"]), nf) + 5
        hf = fit_font(d, story["headline"], SANS_B, 11, cx + col_w - hx - 2,
                      min_size=9)
        d.text((hx, cy + 3), story["headline"], font=hf, fill=INK)
        draw_wrapped(d, (cx + 38, cy + 19), story["deck"], font(SANS_R, 9),
                     INK_SOFT, col_w - 42, 11, max_lines=3)

    # ---- Map band ---------------------------------------------------------
    section_label(d, 600, "WHERE IT HAPPENED", "the 14 mains, pinned")
    map_x, map_y, pitch_x, pitch_y = 14, 622, 4.6, 4.05
    for r, row in enumerate(WORLD):
        for c, ch in enumerate(row):
            if ch == "#":
                cx = map_x + c * pitch_x
                cy = map_y + r * pitch_y
                d.ellipse([cx, cy, cx + 2.6, cy + 2.6], fill=(168, 156, 122))
    nudges = {13: (-5, -8), 8: (-10, -2), 3: (7, -7), 10: (-9, 3),
              9: (-3, 9), 1: (11, 5), 12: (4, 3)}
    pin_f = font(SANS_B, 8)
    for num, lon, lat in PINS:
        px = map_x + (lon + 180) / 3.6 * pitch_x
        py2 = map_y + (84 - lat) / 6.55 * pitch_y
        dx, dy = nudges.get(num, (0, 0))
        px, py2 = px + dx, py2 + dy
        d.ellipse([px - 8, py2 - 8, px + 8, py2 + 8], fill=RED,
                  outline=WHITE, width=2)
        label = str(num)
        lw = text_w(d, label, pin_f)
        d.text((px - lw / 2, py2 - 5), label, font=pin_f, fill=WHITE)
    tx = 512
    draw_wrapped(d, (tx, 624),
                 "Pins mark where the 14 main stories happened, from the "
                 "Kerch Strait to Caracas and the Bay of Bengal.",
                 font(SANS_R, 10), INK, 486, 13, max_lines=3)
    draw_wrapped(d, (tx, 668),
                 "Story 11 has no pin: Voyager 1 is 16.09 billion miles "
                 "from Earth, and its radio signals now take a full day "
                 "to get home.",
                 font(SANS_R, 10), INK_SOFT, 486, 13, max_lines=3)
    d.text((tx, 706), "Map: pins 1-10, 12-14 shown; 11 in deep space.",
           font=font(SANS_R, 8), fill=INK_SOFT)

    # ---- Also Today --------------------------------------------------------
    section_label(d, 724, "ALSO TODAY", "stories 15-48")
    ay = 742
    row_pitch = 14.3
    lead_f = font(SANS_B, 10)
    body_path = SANS_R
    half = (len(ALSO) + 1) // 2
    for j, (region, text) in enumerate(ALSO):
        col = 0 if j < half else 1
        row = j if col == 0 else j - half
        x = 14 if col == 0 else 518
        y = ay + row * row_pitch
        lead = region + " — "
        d.text((x, y), lead, font=lead_f, fill=REGION_COLORS[region])
        lw = text_w(d, lead, lead_f)
        bf = fit_font(d, text, body_path, 10, 492 - lw, min_size=8)
        d.text((x + lw, y), text, font=bf, fill=INK)

    # ---- Footer ------------------------------------------------------------
    d.line([14, 990, 1010, 990], fill=NAVY, width=2)
    d.line([14, 993, 1010, 993], fill=GOLD, width=1)
    foot = ("Every story above happened or was first reported on Wednesday "
            "18 November 2026 · Sources: Reuters, AP, BBC, NASA, UN OHCHR, "
            "USGS, IMD, UEFA · Date checked: 18.11.2026")
    ff = fit_font(d, foot, SANS_R, 9, 996, min_size=8)
    fw = text_w(d, foot, ff)
    d.text(((1024 - fw) / 2, 999), foot, font=ff, fill=INK_SOFT)

    img.save(path)
    return path


if __name__ == "__main__":
    render("entry.png")
