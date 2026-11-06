"""Recolor the GUI sprites of mods the Catppuccin pack does not cover (JEI, Jade,
Xaero's minimap frame), with the same learned map as recolor.py, and draw a sheet.

Usage: recolor_mods.py JAR_26.3 GENERATED_ZIP OUT_DIR SHEET MOD_JAR...
"""
import io, sys, zipfile, os, math
from PIL import Image, ImageDraw
from learn_map import learn
from recolor import build_mapper, recolor

def wanted(n):
    if not n.endswith('.png'):
        return False
    if n.startswith('assets/') and '/textures/gui/' in n:
        return True
    return n in ('assets/xaerobetterpvp/gui/minimap_frame.png', 'assets/xaerobetterpvp/gui/guis.png')

if __name__ == '__main__':
    jar_p, pack_p, out_dir, sheet_p, *mods = sys.argv[1:]
    rules, votes, _ = learn(jar_p, pack_p)
    m, _ = build_mapper(rules, votes)
    pairs = []
    for mj in mods:
        z = zipfile.ZipFile(mj)
        for n in sorted(x for x in z.namelist() if wanted(x)):
            src = Image.open(io.BytesIO(z.read(n))).convert('RGBA')
            dst = recolor(src, m)
            p = os.path.join(out_dir, n)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            dst.save(p)
            if n.endswith('.png.mcmeta'):
                continue
            pairs.append((n.split('/', 1)[1], src, dst))
        for n in z.namelist():   # nine-slice and animation metadata must travel with the sprite
            if n.endswith('.png.mcmeta') and wanted(n[:-len('.mcmeta')]):
                p = os.path.join(out_dir, n)
                open(p, 'wb').write(z.read(n))
    cell_w, cell_h, cols = 300, 110, 4
    rows = math.ceil(len(pairs) / cols)
    sheet = Image.new('RGBA', (cols * cell_w, rows * cell_h), (40, 40, 40, 255))
    d = ImageDraw.Draw(sheet)
    for i, (rel, a, b) in enumerate(pairs):
        x0, y0 = (i % cols) * cell_w, (i // cols) * cell_h
        k = max(1, int(min(90 / a.height, 140 / a.width)))
        s = min(1.0, 90 / a.height, 140 / a.width)
        sz = (a.width * k, a.height * k) if s >= 1 else (max(1, int(a.width * s)), max(1, int(a.height * s)))
        for j, im in enumerate((a, b)):
            bg = Image.new('RGBA', sz, (90, 90, 90, 255)); bg.alpha_composite(im.resize(sz, Image.NEAREST))
            sheet.paste(bg, (x0 + 4 + j * (sz[0] + 4), y0 + 4))
        d.text((x0 + 4, y0 + 96), rel[-46:], fill=(230, 230, 230, 255))
    sheet.save(sheet_p)
    print(len(pairs), 'sprites; sheet', sheet.size)
