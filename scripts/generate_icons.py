#!/usr/bin/env python3
"""
Generate placeholder 32x32 item icons for The Long Haul mod.
Uses only Python stdlib — no PIL or other dependencies required.

Run from project root:
    python3 scripts/generate_icons.py

Icons are written to:
    Contents/mods/TheLongHaul/42/media/textures/Item_*.png

Replace these with proper art when ready. The designs here are functional
placeholders — simple enough to be recognizable at 32x32.
"""

import struct
import zlib
import math
import os

# ---------------------------------------------------------------------------
# PNG writer (stdlib only)
# ---------------------------------------------------------------------------

def write_png(path, pixels, width=32, height=32):
    """Write an RGBA pixel array to a PNG file. pixels is a flat list of
    (R, G, B, A) tuples in row-major order."""
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    raw = b""
    for y in range(height):
        raw += b"\x00"
        for x in range(width):
            raw += bytes(pixels[y * width + x])

    png  = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(png)

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

T  = (  0,   0,   0,   0)   # transparent
OB = ( 50,  28,   8, 255)   # outline/shadow brown
DB = ( 90,  55,  18, 255)   # dark brown
MB = (140,  90,  40, 255)   # medium brown (main wood)
LB = (190, 145,  80, 255)   # light brown (highlight wood)
RO = (155, 122,  48, 255)   # rope / twine
CA = (190, 165, 112, 255)   # canvas / cloth
OG = ( 55,  55,  55, 255)   # outline gray (metal)
DG = ( 80,  80,  85, 255)   # dark gray (metal shadow)
MG = (135, 135, 140, 255)   # medium gray (metal / stone)
LG = (190, 190, 195, 255)   # light gray (highlight)
ST = (112, 105,  98, 255)   # stone mid
LST= (148, 140, 130, 255)   # stone highlight
DST= ( 78,  72,  66, 255)   # stone shadow

# ---------------------------------------------------------------------------
# Drawing primitives — all operate on a flat pixel list
# ---------------------------------------------------------------------------

def canvas():
    return [T] * (32 * 32)

def px(c, x, y, color):
    if 0 <= x < 32 and 0 <= y < 32:
        c[y * 32 + x] = color

def line(c, x0, y0, x1, y1, color):
    """Bresenham line."""
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        px(c, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy; x0 += sx
        if e2 < dx:
            err += dx; y0 += sy

def thick_line(c, x0, y0, x1, y1, color, w=2):
    """Draw a line with pixel width w by offsetting perpendicular."""
    for t in range(-(w // 2), w - (w // 2)):
        dx = x1 - x0; dy = y1 - y0
        length = math.hypot(dx, dy) or 1
        nx = -dy / length; ny = dx / length
        line(c, round(x0 + nx*t), round(y0 + ny*t),
                round(x1 + nx*t), round(y1 + ny*t), color)

def rect(c, x, y, w, h, color):
    """Filled rectangle."""
    for ry in range(y, y + h):
        for rx in range(x, x + w):
            px(c, rx, ry, color)

def rect_outline(c, x, y, w, h, color):
    line(c, x, y, x+w-1, y, color)
    line(c, x, y+h-1, x+w-1, y+h-1, color)
    line(c, x, y, x, y+h-1, color)
    line(c, x+w-1, y, x+w-1, y+h-1, color)

def circle_fill(c, cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx)**2 + (y - cy)**2 <= r*r:
                px(c, x, y, color)

def circle_outline(c, cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = math.sqrt((x-cx)**2 + (y-cy)**2)
            if r - 1 < d <= r + 0.5:
                px(c, x, y, color)

# ---------------------------------------------------------------------------
# Icon definitions
# ---------------------------------------------------------------------------

def icon_stick_travois():
    """Two poles in a V shape with a rope crosspiece."""
    c = canvas()
    # Left pole: bottom-center to top-left
    thick_line(c, 16, 29,  3,  3, MB, 2)
    thick_line(c, 16, 29,  3,  3, OB, 1)
    # Right pole: bottom-center to top-right
    thick_line(c, 16, 29, 29,  3, MB, 2)
    thick_line(c, 16, 29, 29,  3, OB, 1)
    # Rope crosspiece at about 1/3 from top
    line(c,  7, 12, 25, 12, RO)
    line(c,  7, 13, 25, 13, RO)
    # Binding knots
    rect(c,  6, 11, 3, 4, RO)
    rect(c, 23, 11, 3, 4, RO)
    return c

def icon_lashed_travois():
    """Travois with a canvas platform lashed between the poles."""
    c = canvas()
    # Canvas platform (trapezoid approximated as rect)
    for y in range(12, 26):
        spread = int((y - 12) * 0.55)
        x0 = max(4,  8 - spread)
        x1 = min(28, 24 + spread)
        for x in range(x0, x1):
            px(c, x, y, CA)
    # Canvas outline / rope lashing
    for y in range(12, 26):
        spread = int((y - 12) * 0.55)
        x0 = max(4,  8 - spread)
        x1 = min(28, 24 + spread)
        px(c, x0, y, RO)
        px(c, x1-1, y, RO)
    line(c, 8, 12, 24, 12, RO)
    line(c, 8, 13, 24, 13, RO)
    # Poles on top of canvas
    thick_line(c, 16, 29,  3,  3, MB, 2)
    thick_line(c, 16, 29, 29,  3, MB, 2)
    return c

def icon_drag_sledge():
    """Side view: flat plank platform on two runners."""
    c = canvas()
    # Runners (two horizontal skid lines at bottom)
    rect(c,  3, 24, 27, 2, OB)
    rect(c,  3, 23, 27, 2, DB)
    # Platform planks
    rect(c,  3, 17, 27, 6, MB)
    # Plank lines (vertical dividers)
    for x in range(8, 28, 5):
        line(c, x, 17, x, 22, DB)
    # Platform top edge highlight
    line(c,  3, 17, 29, 17, LB)
    # Platform outline
    rect_outline(c, 3, 17, 27, 6, OB)
    # Front rope lashing
    for y in range(17, 23):
        px(c,  3, y, RO)
    return c

def icon_shoulder_yoke():
    """Horizontal bar with hooks at each end."""
    c = canvas()
    # Main bar
    rect(c, 3, 13, 26, 6, MB)
    rect_outline(c, 3, 13, 26, 6, OB)
    # Top highlight
    line(c, 4, 14, 27, 14, LB)
    # Left hook (notch/peg pointing down)
    rect(c, 3, 19, 5, 5, DB)
    rect_outline(c, 3, 19, 5, 5, OB)
    # Right hook
    rect(c, 24, 19, 5, 5, DB)
    rect_outline(c, 24, 19, 5, 5, OB)
    # Notch indicators on top of bar
    line(c,  5, 13, 5, 13, OB)
    line(c, 26, 13, 26, 13, OB)
    return c

def icon_padded_yoke():
    """Shoulder yoke with rag padding on top."""
    c = icon_shoulder_yoke()
    # Padding (bumpy rag texture on top edge of bar)
    for x in range(5, 27, 3):
        rect(c, x, 11, 2, 3, CA)
        rect_outline(c, x, 11, 2, 3, RO)
    return c

def icon_carved_wood_wheel():
    """Solid wooden disc wheel."""
    c = canvas()
    # Fill
    circle_fill(c, 16, 16, 13, MB)
    # Grain rings
    circle_outline(c, 16, 16, 9, DB)
    circle_outline(c, 16, 16, 5, DB)
    # Outer outline
    circle_outline(c, 16, 16, 13, OB)
    # Hub
    circle_fill(c, 16, 16, 2, DB)
    return c

def icon_assembled_wood_wheel():
    """Spoked wheel: outer ring, 6 spokes, hub."""
    c = canvas()
    # Outer ring
    circle_fill(c, 16, 16, 13, MB)
    circle_fill(c, 16, 16, 10, T)    # hollow center
    circle_outline(c, 16, 16, 13, OB)
    circle_outline(c, 16, 16, 10, OB)
    # 6 spokes
    for i in range(6):
        angle = math.radians(i * 60)
        x1 = round(16 + 3 * math.cos(angle))
        y1 = round(16 + 3 * math.sin(angle))
        x2 = round(16 + 10 * math.cos(angle))
        y2 = round(16 + 10 * math.sin(angle))
        line(c, x1, y1, x2, y2, DB)
    # Hub
    circle_fill(c, 16, 16, 3, DB)
    circle_outline(c, 16, 16, 3, OB)
    return c

def _wheelbarrow_base(c, wheel_color, wheel_outline, tray_color, tray_outline, handle_color):
    """Shared wheelbarrow silhouette (side view, wheel left, handles right)."""
    # Wheel
    circle_fill(c, 9, 22, 7, wheel_color)
    circle_fill(c, 9, 22, 4, T)
    circle_outline(c, 9, 22, 7, wheel_outline)
    circle_outline(c, 9, 22, 4, wheel_outline)
    # Spoke cross
    line(c, 9, 18, 9, 26, wheel_outline)
    line(c, 5, 22, 13, 22, wheel_outline)
    # Axle stub
    circle_fill(c, 9, 22, 2, wheel_outline)
    # Tray (trapezoid: wider at top, narrower toward wheel)
    for y in range(10, 22):
        spread = int((21 - y) * 0.25)
        x0 = 13 + spread
        x1 = 29
        for x in range(x0, x1 + 1):
            px(c, x, y, tray_color)
    # Tray outline
    line(c, 13, 21, 29, 21, tray_outline)   # bottom
    line(c, 16, 10, 29, 10, tray_outline)   # top
    line(c, 29, 10, 29, 21, tray_outline)   # right
    line(c, 16, 10, 13, 21, tray_outline)   # left diagonal
    # Handles (two lines extending right from tray base)
    line(c, 13, 19, 3, 26, handle_color)
    line(c, 13, 21, 3, 28, handle_color)
    # Handle grip
    line(c,  3, 26,  3, 28, handle_color)

def icon_stone_wheelbarrow():
    c = canvas()
    _wheelbarrow_base(c, ST, DST, ST, DST, DB)
    # Stone texture dots
    for pos in [(18,13),(22,15),(25,12),(20,17),(27,17),(17,19)]:
        px(c, pos[0], pos[1], LST)
    return c

def icon_metal_axled_stone_wheelbarrow():
    c = canvas()
    _wheelbarrow_base(c, ST, DST, ST, DST, DG)
    # Metal axle (bright line through wheel center)
    line(c, 3, 22, 16, 22, LG)
    line(c, 3, 22, 16, 22, MG)
    # Metal reinforcement strips on tray
    line(c, 16, 10, 29, 10, MG)
    line(c, 13, 21, 29, 21, MG)
    line(c, 29, 10, 29, 21, LG)
    # Stone texture
    for pos in [(18,13),(22,15),(25,12),(20,17),(27,17)]:
        px(c, pos[0], pos[1], LST)
    return c

def icon_wooden_wheelbarrow():
    c = canvas()
    _wheelbarrow_base(c, MB, OB, LB, OB, DB)
    # Wood grain lines on tray
    line(c, 17, 11, 28, 11, DB)
    line(c, 16, 14, 28, 14, DB)
    line(c, 15, 17, 28, 17, DB)
    line(c, 14, 20, 28, 20, DB)
    return c

def icon_reinforced_wheelbarrow():
    c = canvas()
    _wheelbarrow_base(c, MB, OB, LB, OB, DG)
    # Wood grain
    line(c, 17, 11, 28, 11, DB)
    line(c, 15, 17, 28, 17, DB)
    # Metal reinforcement strips
    line(c, 16, 10, 29, 10, MG)   # top edge
    line(c, 13, 21, 29, 21, MG)   # bottom edge
    line(c, 29, 10, 29, 21, LG)   # right edge
    # Metal axle
    line(c,  3, 22, 16, 22, MG)
    circle_fill(c, 9, 22, 2, LG)
    return c

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

ICONS = {
    "Item_StickTravois":               icon_stick_travois,
    "Item_LashedTravois":              icon_lashed_travois,
    "Item_DragSledge":                 icon_drag_sledge,
    "Item_ShoulderYoke":               icon_shoulder_yoke,
    "Item_PaddedYoke":                 icon_padded_yoke,
    "Item_CarvedWoodWheel":            icon_carved_wood_wheel,
    "Item_AssembledWoodWheel":         icon_assembled_wood_wheel,
    "Item_StoneWheelbarrow":           icon_stone_wheelbarrow,
    "Item_MetalAxledStoneWheelbarrow": icon_metal_axled_stone_wheelbarrow,
    "Item_WoodenWheelbarrow":          icon_wooden_wheelbarrow,
    "Item_ReinforcedWheelbarrow":      icon_reinforced_wheelbarrow,
}

if __name__ == "__main__":
    out_dir = os.path.join(
        os.path.dirname(__file__),
        "..", "Contents", "mods", "TheLongHaul", "42", "media", "textures"
    )
    os.makedirs(out_dir, exist_ok=True)

    for name, fn in ICONS.items():
        path = os.path.join(out_dir, f"{name}.png")
        write_png(path, fn())
        print(f"  wrote {name}.png")

    print(f"\nAll {len(ICONS)} icons written to {os.path.realpath(out_dir)}")
