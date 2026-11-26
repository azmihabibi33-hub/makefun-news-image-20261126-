#!/usr/bin/env python3
"""make.fun news-image entry (Python 3.13, standard library only).

The program DRAWS the whole image at run time: a newspaper front page,
"THE WORLD TODAY", summing up Thursday 26 November 2026. No image data
is stored in the repository at all -- every pixel is produced by the code
below, from a hand-designed 5x7 bitmap font and plain rectangles, encoded
to PNG with a small writer built on zlib and struct. Two runs therefore
write byte-identical files.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- canvas
W = 1024
H = 1024

PAPER = (247, 243, 232)   # warm newsprint cream
INK = (26, 26, 26)        # near-black headline ink
DECK = (74, 74, 74)       # grey deck text
RULE = (120, 114, 100)    # thin rule grey
RED = (178, 34, 34)       # masthead red / TRADE / WAR tags
AMBER = (176, 96, 0)      # DISASTER tag
NAVY = (31, 56, 100)      # ASIA / SPACE tags, ticker bar
PURPLE = (123, 45, 107)   # MIDDLE EAST tag
CARD = (255, 255, 255)    # story card fill
CARD_EDGE = (205, 200, 185)
WHITE = (255, 255, 255)


def new_frame():
    """A fresh framebuffer, filled with newsprint cream."""
    buf = bytearray(W * H * 3)
    r, g, b = PAPER
    row = bytes((r, g, b)) * W
    for y in range(H):
        buf[y * W * 3:(y + 1) * W * 3] = row
    return buf


def rect(buf, x, y, w, h, color):
    """Fill an axis-aligned rectangle (clipped to the canvas)."""
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    r, g, b = color
    row = bytes((r, g, b)) * (x1 - x0)
    for yy in range(y0, y1):
        off = (yy * W + x0) * 3
        buf[off:off + len(row)] = row


def hline(buf, x, y, w, color, thick=1):
    rect(buf, x, y, w, thick, color)


def set_px(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        off = (y * W + x) * 3
        buf[off] = color[0]
        buf[off + 1] = color[1]
        buf[off + 2] = color[2]


# ------------------------------------------------------------- PNG writer
def _chunk(kind, data):
    body = kind + data
    return (struct.pack(">I", len(data)) + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))


def write_png(path, buf):
    """Encode the RGB framebuffer as a PNG (color type 2, 8 bit)."""
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * stride:(y + 1) * stride]
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# ------------------------------------------------- hand-designed 5x7 font
# Each glyph is 7 rows of 5 bits, written as "1"/"0" strings. I drew every
# glyph myself on a 5-wide by 7-tall grid; all text is rendered uppercase.
FONT = {
    "A": ("01110",
          "10001",
          "10001",
          "11111",
          "10001",
          "10001",
          "10001"),
    "B": ("11110",
          "10001",
          "10001",
          "11110",
          "10001",
          "10001",
          "11110"),
    "C": ("01110",
          "10001",
          "10000",
          "10000",
          "10000",
          "10001",
          "01110"),
    "D": ("11110",
          "10001",
          "10001",
          "10001",
          "10001",
          "10001",
          "11110"),
    "E": ("11111",
          "10000",
          "10000",
          "11110",
          "10000",
          "10000",
          "11111"),
    "F": ("11111",
          "10000",
          "10000",
          "11110",
          "10000",
          "10000",
          "10000"),
    "G": ("01110",
          "10001",
          "10000",
          "10111",
          "10001",
          "10001",
          "01111"),
    "H": ("10001",
          "10001",
          "10001",
          "11111",
          "10001",
          "10001",
          "10001"),
    "I": ("01110",
          "00100",
          "00100",
          "00100",
          "00100",
          "00100",
          "01110"),
    "J": ("00111",
          "00010",
          "00010",
          "00010",
          "00010",
          "10010",
          "01100"),
    "K": ("10001",
          "10010",
          "10100",
          "11000",
          "10100",
          "10010",
          "10001"),
    "L": ("10000",
          "10000",
          "10000",
          "10000",
          "10000",
          "10000",
          "11111"),
    "M": ("10001",
          "11011",
          "10101",
          "10101",
          "10001",
          "10001",
          "10001"),
    "N": ("10001",
          "11001",
          "10101",
          "10011",
          "10001",
          "10001",
          "10001"),
    "O": ("01110",
          "10001",
          "10001",
          "10001",
          "10001",
          "10001",
          "01110"),
    "P": ("11110",
          "10001",
          "10001",
          "11110",
          "10000",
          "10000",
          "10000"),
    "Q": ("01110",
          "10001",
          "10001",
          "10001",
          "10101",
          "10010",
          "01101"),
    "R": ("11110",
          "10001",
          "10001",
          "11110",
          "10100",
          "10010",
          "10001"),
    "S": ("01111",
          "10000",
          "10000",
          "01110",
          "00001",
          "00001",
          "11110"),
    "T": ("11111",
          "00100",
          "00100",
          "00100",
          "00100",
          "00100",
          "00100"),
    "U": ("10001",
          "10001",
          "10001",
          "10001",
          "10001",
          "10001",
          "01110"),
    "V": ("10001",
          "10001",
          "10001",
          "10001",
          "10001",
          "01010",
          "00100"),
    "W": ("10001",
          "10001",
          "10001",
          "10101",
          "10101",
          "11011",
          "10001"),
    "X": ("10001",
          "10001",
          "01010",
          "00100",
          "01010",
          "10001",
          "10001"),
    "Y": ("10001",
          "10001",
          "01010",
          "00100",
          "00100",
          "00100",
          "00100"),
    "Z": ("11111",
          "00001",
          "00010",
          "00100",
          "01000",
          "10000",
          "11111"),
}

FONT.update({
    "0": ("01110",
          "10001",
          "10011",
          "10101",
          "11001",
          "10001",
          "01110"),
    "1": ("00100",
          "01100",
          "00100",
          "00100",
          "00100",
          "00100",
          "01110"),
    "2": ("01110",
          "10001",
          "00001",
          "00110",
          "01000",
          "10000",
          "11111"),
    "3": ("11111",
          "00010",
          "00100",
          "00010",
          "00001",
          "10001",
          "01110"),
    "4": ("00010",
          "00110",
          "01010",
          "10010",
          "11111",
          "00010",
          "00010"),
    "5": ("11111",
          "10000",
          "11110",
          "00001",
          "00001",
          "10001",
          "01110"),
    "6": ("00110",
          "01000",
          "10000",
          "11110",
          "10001",
          "10001",
          "01110"),
    "7": ("11111",
          "00001",
          "00010",
          "00100",
          "01000",
          "01000",
          "01000"),
    "8": ("01110",
          "10001",
          "10001",
          "01110",
          "10001",
          "10001",
          "01110"),
    "9": ("01110",
          "10001",
          "10001",
          "01111",
          "00001",
          "00010",
          "01100"),
    " ": ("00000",
          "00000",
          "00000",
          "00000",
          "00000",
          "00000",
          "00000"),
    ",": ("00000",
          "00000",
          "00000",
          "00000",
          "00100",
          "00100",
          "01000"),
    ".": ("00000",
          "00000",
          "00000",
          "00000",
          "00000",
          "01100",
          "01100"),
    ";": ("00000",
          "00100",
          "00100",
          "00000",
          "00100",
          "00100",
          "01000"),
    ":": ("00000",
          "01100",
          "01100",
          "00000",
          "01100",
          "01100",
          "00000"),
    "'": ("00100",
          "00100",
          "01000",
          "00000",
          "00000",
          "00000",
          "00000"),
    "-": ("00000",
          "00000",
          "00000",
          "01110",
          "00000",
          "00000",
          "00000"),
    "$": ("00100",
          "01111",
          "10100",
          "01110",
          "00101",
          "11110",
          "00100"),
    "%": ("11001",
          "11010",
          "00010",
          "00100",
          "01000",
          "01011",
          "10011"),
    "/": ("00001",
          "00010",
          "00010",
          "00100",
          "01000",
          "01000",
          "10000"),
    "—": ("00000",  # em dash, used in the ticker
          "00000",
          "00000",
          "11111",
          "00000",
          "00000",
          "00000"),
    "•": ("00000",  # bullet, used in the ticker
          "00000",
          "01100",
          "01100",
          "01100",
          "00000",
          "00000"),
    "(": ("00010",
          "00100",
          "01000",
          "01000",
          "01000",
          "00100",
          "00010"),
    ")": ("01000",
          "00100",
          "00010",
          "00010",
          "00010",
          "00100",
          "01000"),
    "!": ("00100",
          "00100",
          "00100",
          "00100",
          "00100",
          "00000",
          "00100"),
    "?": ("01110",
          "10001",
          "00001",
          "00010",
          "00100",
          "00000",
          "00100"),
    "&": ("01100",
          "10010",
          "10100",
          "01000",
          "10101",
          "10010",
          "01101"),
    "+": ("00000",
          "00100",
          "00100",
          "11111",
          "00100",
          "00100",
          "00000"),
    "=": ("00000",
          "00000",
          "11111",
          "00000",
          "11111",
          "00000",
          "00000"),
})


# ------------------------------------------------------------ text drawing
CELL = 6  # a glyph is 5 px wide plus 1 px of tracking


def text_width(text, scale):
    """Pixel width of text at the given integer scale."""
    if not text:
        return 0
    return len(text) * CELL * scale - scale


def draw_glyph(buf, x, y, glyph, scale, color):
    for row in range(7):
        bits = glyph[row]
        for col in range(5):
            if bits[col] == "1":
                rect(buf, x + col * scale, y + row * scale,
                     scale, scale, color)


def draw_text(buf, x, y, text, scale, color, bold=False):
    """Draw uppercased text; bold fakes a heavier weight with a 1 px jog."""
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        draw_glyph(buf, cx, y, glyph, scale, color)
        if bold:
            draw_glyph(buf, cx + 1, y, glyph, scale, color)
        cx += CELL * scale
    return cx


def draw_centered(buf, y, text, scale, color, bold=False):
    draw_text(buf, (W - text_width(text, scale)) // 2, y,
              text, scale, color, bold)


def wrap(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.upper().split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(buf, x, y, lines, scale, color, pitch, bold=False):
    for line in lines:
        draw_text(buf, x, y, line, scale, color, bold)
        y += pitch
    return y


def draw_tag(buf, x, y, label, color):
    """A filled category tag with white text, returning its pixel width."""
    pad = 10
    tw = text_width(label, 2)
    w = tw + pad * 2
    h = 26
    rect(buf, x, y, w, h, color)
    draw_text(buf, x + pad, y + 6, label, 2, WHITE, bold=True)
    return w


# ------------------------------------------------------------------ layout
MX = 36            # side margin
CW = W - 2 * MX    # content width


def draw_card(buf, x, y, w, h, tag, tag_color, headline, deck):
    rect(buf, x, y, w, h, CARD)
    # 1 px border: four thin rects
    hline(buf, x, y, w, CARD_EDGE)
    hline(buf, x, y + h - 1, w, CARD_EDGE)
    rect(buf, x, y, 1, h, CARD_EDGE)
    rect(buf, x + w - 1, y, 1, h, CARD_EDGE)
    inner = x + 16
    iw = w - 32
    draw_tag(buf, inner, y + 14, tag, tag_color)
    hy = y + 52
    lines = wrap(headline, iw, 3)
    hy = draw_lines(buf, inner, hy, lines, 3, INK, 24, bold=True)
    dy = hy + 10
    dlines = wrap(deck, iw, 2)
    draw_lines(buf, inner, dy, dlines, 2, DECK, 20)


def draw_page():
    buf = new_frame()

    # Masthead
    draw_centered(buf, 28, "THE WORLD TODAY", 6, INK, bold=True)
    # Date line
    draw_centered(buf, 88, "THURSDAY, 26 NOVEMBER 2026", 3, RED, bold=True)
    # Double rule under the date
    hline(buf, MX, 124, CW, INK, 3)
    hline(buf, MX, 131, CW, INK, 1)

    # Lead story
    tag_w = draw_tag(buf, MX, 150, "TRADE", RED)
    draw_text(buf, MX + tag_w + 12, 156, "UNITED STATES", 2, DECK, bold=True)
    lead_head = wrap("US unveils new tariffs on 14 economies, up to 20%",
                     CW, 4)
    hy = draw_lines(buf, MX, 190, lead_head, 4, INK, 32, bold=True)
    lead_deck = wrap("China, the EU and India are among the targets. "
                     "A public hearing is set for 25 January.", CW, 2)
    draw_lines(buf, MX, hy + 12, lead_deck, 2, DECK, 20)
    hline(buf, MX, 312, CW, RULE, 1)

    # 2 x 2 story cards
    card_w = (CW - 24) // 2
    card_h = 172
    cards = [
        (MX, 330, "WAR", RED,
         "Ukraine hits Russian refineries; Moscow approves record budget",
         "Samara hit; $606bn budget for 2027-29."),
        (MX + card_w + 24, 330, "DISASTER", AMBER,
         "Fuel tanker fire kills 31 near Cairo",
         "Tanker crashed and exploded on the Ring Road; "
         "27 vehicles charred."),
        (MX, 522, "ASIA", NAVY,
         "Kim orders wider rollout of tactical nuclear weapons",
         "North Korea signals nuclear expansion."),
        (MX + card_w + 24, 522, "MIDDLE EAST", PURPLE,
         "Israeli strikes kill 9 in Gaza for a third night in a row",
         "Attacks continue despite a year-old ceasefire."),
    ]
    for (cx, cy, tag, color, head, deck) in cards:
        draw_card(buf, cx, cy, card_w, card_h, tag, color, head, deck)

    # Space story
    tag_w = draw_tag(buf, MX, 716, "SPACE", NAVY)
    draw_text(buf, MX + tag_w + 12, 722, "TECHNOLOGY", 2, DECK, bold=True)
    draw_text(buf, MX, 752, "SpaceX wins approval for one million satellites",
              3, INK, bold=True)
    draw_text(buf, MX, 786, "Musk's orbital data network cleared to expand.",
              2, DECK)

    # Ticker bar
    rect(buf, MX, 824, CW, 72, NAVY)
    draw_centered(buf, 838,
                  "BOGOR MINE FLOOD — 13 DEAD, 13 MISSING • "
                  "UK MIGRATION LOWEST SINCE 1997",
                  2, WHITE, bold=True)
    draw_centered(buf, 864,
                  "MACY'S PARADE DELAYED BY STORM • "
                  "TRUMP BIRTHRIGHT ORDER BLOCKED",
                  2, WHITE, bold=True)

    # Footer rule + note
    hline(buf, MX, 908, CW, RULE, 1)
    draw_centered(buf, 922,
                  "ALL EVENTS HAPPENED OR WERE FIRST REPORTED ON "
                  "THURSDAY, 26 NOVEMBER 2026.",
                  2, DECK)
    return buf


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    buf = draw_page()
    write_png(os.path.join(out_dir, "entry.png"), buf)


if __name__ == "__main__":
    main()
