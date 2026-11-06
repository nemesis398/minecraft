"""Tint the bitmap font to Catppuccin Text (#cdd6f4), Mika's choice 2026-11-06.

Minecraft multiplies the text color with the glyph texture, so white text turns
into Catppuccin Text and colored text is softened slightly. Only the regular
fonts are tinted; the enchanting-table (sga) and illager fonts stay as they are.
Usage: font_tint.py CLIENT_JAR OUT_DIR
"""
import io, os, sys, zipfile
from PIL import Image

TEXT = (0xcd, 0xd6, 0xf4)
FONTS = ('ascii.png', 'accented.png', 'nonlatin_european.png')
jar, out = zipfile.ZipFile(sys.argv[1]), sys.argv[2]
for f in FONTS:
    n = 'assets/minecraft/textures/font/' + f
    im = Image.open(io.BytesIO(jar.read(n))).convert('RGBA')
    im.putdata([(r * TEXT[0] // 255, g * TEXT[1] // 255, b * TEXT[2] // 255, a) for r, g, b, a in im.getdata()])
    p = os.path.join(out, n); os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p)
print('tinted', len(FONTS), 'font sheets')
