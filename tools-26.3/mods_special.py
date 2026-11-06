"""Special cases the learned map cannot handle (2026-11-06).

Xaero's minimap frame and world-map icons are white and black and get tinted in
code, so they are painted directly: brightness blends Crust (black) to Mauve
(white), alpha kept. Use with minimap_frame_color = 15 (white = no tint).
Jade's dark tooltip reuses the pack's own vanilla tooltip sprites (Crust at
alpha 240, Mauve gradient frame), so both tooltips look the same.

Usage: mods_special.py MODS_DIR PACK_DIR OUT_DIR
"""
import glob, io, os, shutil, sys, zipfile
from PIL import Image

CRUST, MAUVE = (0x11, 0x11, 0x1b), (0xcb, 0xa6, 0xf7)

def blend(img):
    img = img.convert('RGBA')
    out = []
    for r, g, b, a in img.getdata():
        if a == 0:
            out.append((0, 0, 0, 0)); continue
        t = (r + g + b) / 765
        out.append(tuple(round(c0 + (c1 - c0) * t) for c0, c1 in zip(CRUST, MAUVE)) + (a,))
    img.putdata(out)
    return img

def save(img, out, name):
    p = os.path.join(out, name); os.makedirs(os.path.dirname(p), exist_ok=True); img.save(p)

mods, pack, out = sys.argv[1:4]
mm = zipfile.ZipFile(glob.glob(os.path.join(mods, 'xaerominimap-*.jar'))[0])
wm = zipfile.ZipFile(glob.glob(os.path.join(mods, 'xaeroworldmap-*.jar'))[0])
for z, n in ((mm, 'assets/xaerobetterpvp/gui/minimap_frame.png'), (mm, 'assets/xaerobetterpvp/gui/guis.png'),
             (wm, 'assets/xaeroworldmap/gui/gui.png')):
    save(blend(Image.open(io.BytesIO(z.read(n)))), out, n)
src = os.path.join(pack, 'assets/minecraft/textures/gui/sprites/tooltip')
dst = os.path.join(out, 'assets/jade/textures/gui/sprites/tooltip')
os.makedirs(dst, exist_ok=True)
for a, b in (('background', 'dark_background'), ('frame', 'dark_frame')):
    for ext in ('.png', '.png.mcmeta'):
        if os.path.exists(os.path.join(src, a + ext)):
            shutil.copy2(os.path.join(src, a + ext), os.path.join(dst, b + ext))
# JEI's own buttons are the old stone-noise style; the learned map turns that
# noise into speckles (Mika, 2026-11-06: "the buttons are broken"). Use the
# pack's hand-painted vanilla buttons instead, each with its own nine-slice mcmeta.
wsrc = os.path.join(pack, 'assets/minecraft/textures/gui/sprites/widget')
wdst = os.path.join(out, 'assets/jei/textures/gui/sprites')
os.makedirs(wdst, exist_ok=True)
for jei, van in (('button_enabled', 'button'), ('button_disabled', 'button_disabled'),
                 ('button_highlight', 'button_highlighted'), ('button_pressed', 'button_highlighted'),
                 ('button_pressed_highlighted', 'button_highlighted')):
    for ext in ('.png', '.png.mcmeta'):
        shutil.copy2(os.path.join(wsrc, van + ext), os.path.join(wdst, jei + ext))
# JEI's panel had a 1 px outline plus a 2 px light band, which read as thick
# (Mika, 2026-11-06). Keep one pixel of it, in Mauve like the tooltip frame.
bg = os.path.join(wdst, 'gui_background.png')
if os.path.exists(bg):
    im = Image.open(bg).convert('RGBA'); w, h = im.size; px = im.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][:3] == (0xcd, 0xd6, 0xf4):
                d = min(x, y, w - 1 - x, h - 1 - y)
                px[x, y] = (MAUVE if d == 1 else (0x1e, 0x1e, 0x2e)) + (px[x, y][3],)
    im.save(bg)
# JEI's icons are drawn dark for light vanilla buttons; on the dark Catppuccin
# buttons they vanished (Mika, 2026-11-06: "dark on dark"). A mostly dark icon
# is inverted onto Crust..Text, a light one is blended onto Crust..Text as is;
# coloured pixels (red wrench, blue info) keep their colour.
TEXT = (0xcd, 0xd6, 0xf4)
jz = zipfile.ZipFile(glob.glob(os.path.join(mods, 'jei-*.jar'))[0])
for n in jz.namelist():
    if not (n.startswith('assets/jei/textures/gui/sprites/icons/') and n.endswith('.png')):
        continue
    im = Image.open(io.BytesIO(jz.read(n))).convert('RGBA')
    px = list(im.getdata())
    grey = [(r + g + b) / 765 for r, g, b, a in px if a and max(r, g, b) - min(r, g, b) < 24]
    invert = bool(grey) and sum(grey) / len(grey) < 0.5
    out = []
    for r, g, b, a in px:
        if a == 0 or max(r, g, b) - min(r, g, b) >= 24:
            out.append((r, g, b, a)); continue
        t = (r + g + b) / 765
        t = 1 - t if invert else t
        out.append(tuple(round(c0 + (c1 - c0) * t) for c0, c1 in zip(CRUST, TEXT)) + (a,))
    im.putdata(out)
    save(im, sys.argv[3], n)
print('special cases written')
