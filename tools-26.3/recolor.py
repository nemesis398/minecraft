"""Recolor the GUI textures the Catppuccin pack lacks on 26.3, and draw a review sheet.

Exact learned rules first; any other opaque color goes to the target of the
nearest *anchor* (a rule backed by >= ANCHOR_PX pixels), with its own alpha
kept. Fully transparent pixels stay untouched.
"""
import io, json, sys, zipfile, math
from PIL import Image, ImageDraw
from learn_map import learn, PREFIX

ANCHOR_PX = 100
SKIP_PREFIX = ('signs/', 'hanging_signs/', 'realms/', 'title/', 'advancements/backgrounds/', 'presets/')
SKIP_NAME = ('locator_bar_dot',)
PICTURES = {  # item-like pictures and artwork: Mika chose to leave these vanilla (2026-11-06)
    'sprites/statistics/block_mined.png', 'sprites/statistics/item_broken.png',
    'sprites/statistics/item_crafted.png', 'sprites/statistics/item_dropped.png',
    'sprites/statistics/item_picked_up.png', 'sprites/statistics/item_used.png',
    'sprites/toast/tree.png', 'sprites/toast/wooden_planks.png',
    'sprites/friends/illustrations_00.png',
    'sprites/friends/friends.png', 'sprites/spectator/teleport_to_player.png',
    'sprites/icon/new_realm.png',
}
# Backgrounds behind every menu: a dark noise texture in vanilla. Mapped by
# brightness rank onto Crust, Mantle and Base, alpha kept, so the noise stays
# but sits in Mocha's darkest colors instead of the mid greys the rules give.
BACKGROUNDS = {
    'menu_background.png', 'menu_list_background.png',
    'inworld_menu_background.png', 'inworld_menu_list_background.png',
    'tab_header_background.png',
}
DARKS = [(0x11, 0x11, 0x1b), (0x18, 0x18, 0x25), (0x1e, 0x1e, 0x2e)]  # Crust, Mantle, Base

def todo(jar, pack):
    v = {n for n in jar.namelist() if n.startswith(PREFIX) and n.endswith('.png')}
    p = set(pack.namelist())
    out = []
    for n in sorted(v - p):
        rel = n[len(PREFIX):]
        if rel.startswith(SKIP_PREFIX) or any(s in rel for s in SKIP_NAME) or rel in PICTURES:
            continue
        out.append(n)
    return out

def build_mapper(rules, votes):
    anchors = [(s, d) for s, d in rules.items() if sum(votes[s].values()) >= ANCHOR_PX]
    cache = {}
    def m(rgb):
        if rgb in rules:
            return rules[rgb]
        hi, lo = max(rgb), min(rgb)
        if hi and (hi - lo) / hi > 0.15:   # a real color with no rule: keep vanilla
            return rgb
        if rgb not in cache:
            cache[rgb] = min(anchors, key=lambda sd: sum((a - b) ** 2 for a, b in zip(sd[0], rgb)))[1]
        return cache[rgb]
    return m, len(anchors)

def background(img):
    img = img.convert('RGBA')
    px = list(img.getdata())
    lum = sorted({r + g + b for r, g, b, a in px if a})
    def pick(r, g, b):
        i = lum.index(r + g + b) * len(DARKS) // max(len(lum), 1)
        return DARKS[min(i, len(DARKS) - 1)]
    img.putdata([(0, 0, 0, 0) if a == 0 else pick(r, g, b) + (a,) for r, g, b, a in px])
    return img

def recolor(img, m):
    img = img.convert('RGBA')
    img.putdata([(0, 0, 0, 0) if a == 0 else m((r, g, b)) + (a,) for r, g, b, a in img.getdata()])
    return img

if __name__ == '__main__':
    jar_p, pack_p, out_dir, sheet_p = sys.argv[1:5]
    jar, pack = zipfile.ZipFile(jar_p), zipfile.ZipFile(pack_p)
    rules, votes, _ = learn(jar_p, pack_p)
    m, na = build_mapper(rules, votes)
    names = todo(jar, pack)
    print(f'{len(names)} textures, {len(rules)} rules, {na} anchors')
    import os
    pairs = []
    for n in names:
        src = Image.open(io.BytesIO(jar.read(n)))
        dst = background(src) if n[len(PREFIX):] in BACKGROUNDS else recolor(src, m)
        path = os.path.join(out_dir, n)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        dst.save(path)
        pairs.append((n[len(PREFIX):], src.convert('RGBA'), dst))
    # review sheet: before | after, scaled to fit 96 px tall cells, on a checkerboard
    cell_w, cell_h, cols = 300, 110, 4
    rows = math.ceil(len(pairs) / cols)
    sheet = Image.new('RGBA', (cols * cell_w, rows * cell_h), (40, 40, 40, 255))
    d = ImageDraw.Draw(sheet)
    for i, (rel, a, b) in enumerate(pairs):
        x0, y0 = (i % cols) * cell_w, (i // cols) * cell_h
        s = min(1, 90 / max(a.height, 1), 140 / max(a.width, 1))
        sz = (max(1, int(a.width * s)), max(1, int(a.height * s)))
        if s >= 1:
            k = int(min(90 / a.height, 140 / a.width)) or 1
            sz = (a.width * k, a.height * k)
        for j, im in enumerate((a, b)):
            bg = Image.new('RGBA', sz, (90, 90, 90, 255))
            bg.alpha_composite(im.resize(sz, Image.NEAREST))
            sheet.paste(bg, (x0 + 4 + j * (sz[0] + 4), y0 + 4))
        d.text((x0 + 4, y0 + 96), rel[-46:], fill=(230, 230, 230, 255))
    sheet.save(sheet_p)
    print('sheet', sheet.size)
