"""Hand fixes for the 26.3 friends screen that the learned color map gets wrong.

1. friends/button, button_highlighted, button_disabled are vanilla's stone-noise
   button. The map recolors each noise grey on its own and leaves red and mauve
   speckles (the "Friends / Requests" tab headers, 2026-11-06). They get the
   pack's own themed widget/button sprites with their .mcmeta instead: same
   200x20 size, the fix JEI's buttons got in mods_special.py.
2. friends/background: vanilla's interior grey (55,55,55) is a shadow elsewhere
   in the GUI, so the map turned the list area light Lavender. It becomes
   Mantle #181825; the frame colors already match the pack.

Run after assemble.py and fix_mcmeta.py.

    friends_special.py PACK_DIR
"""
import os
import shutil
import sys

from PIL import Image

MANTLE = (24, 24, 37, 255)
WRONG_INTERIOR = (196, 205, 231, 255)  # what the map made of vanilla (55,55,55)


def main(pack):
    sprites = os.path.join(pack, "assets/minecraft/textures/gui/sprites")
    for state in ("", "_highlighted", "_disabled"):
        src = os.path.join(sprites, f"widget/button{state}.png")
        dst = os.path.join(sprites, f"friends/button{state}.png")
        shutil.copyfile(src, dst)
        # The metadata travels with the PNG: vanilla's friends/button_disabled
        # has a 1 px border, the themed widget/button_disabled needs 3.
        shutil.copyfile(src + ".mcmeta", dst + ".mcmeta")
        print("copied", f"widget/button{state}.png (+ .mcmeta) -> friends/button{state}.png")

    path = os.path.join(sprites, "friends/background.png")
    im = Image.open(path).convert("RGBA")
    px = im.load()
    n = 0
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y] == WRONG_INTERIOR:
                px[x, y] = MANTLE
                n += 1
    im.save(path)
    print(f"friends/background.png: {n} interior pixels -> Mantle")


if __name__ == "__main__":
    main(sys.argv[1])
