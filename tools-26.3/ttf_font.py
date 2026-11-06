"""Use JetBrains Mono Nerd Font as the game font (Mika's trial, 2026-11-06).

The TTF goes first in minecraft:default; the vanilla bitmap fonts and unifont
stay behind it as fallback. Usage: ttf_font.py TTF OUT_DIR [SIZE] [OVERSAMPLE]
"""
import json, os, shutil, sys

ttf, out = sys.argv[1], sys.argv[2]
size = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
over = float(sys.argv[4]) if len(sys.argv) > 4 else 4.0
fdir = os.path.join(out, 'assets/minecraft/font')
os.makedirs(fdir, exist_ok=True)
shutil.copy2(ttf, os.path.join(fdir, 'jetbrainsmono.ttf'))
json.dump({'providers': [
    {'type': 'reference', 'id': 'minecraft:include/space'},
    {'type': 'ttf', 'file': 'minecraft:jetbrainsmono.ttf', 'size': size, 'oversample': over, 'shift': [0, 0.5], 'skip': ''},
    {'type': 'reference', 'id': 'minecraft:include/default', 'filter': {'uniform': False}},
    {'type': 'reference', 'id': 'minecraft:include/unifont'},
]}, open(os.path.join(fdir, 'default.json'), 'w'), indent=2)
print('ttf font at size', size, 'oversample', over)
