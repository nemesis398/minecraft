"""Copy vanilla .png.mcmeta files next to pack sprites that lack them.

Why: Minecraft reads a texture's metadata only from the pack that supplies the
PNG. A recolored sprite without its .mcmeta therefore loses nine-slice scaling
and animation: the 26.3 friends screen stretched its 236x34 panel over the
whole window, and the tab headers smeared (2026-11-06). recolor.py and the
upstream pack write PNGs only, so this runs last, after assemble.py and
mods_special.py.

A vanilla .mcmeta is copied only when the pack's PNG has the vanilla pixel
size; otherwise its nine-slice borders or animation frames would not line up,
and the sprite is reported instead.

    fix_mcmeta.py JAR PACK_DIR
"""
import io
import os
import sys
import zipfile

from PIL import Image


def main(jar, pack):
    z = zipfile.ZipFile(jar)
    copied, skipped = [], []
    for name in z.namelist():
        if not (name.startswith("assets/minecraft/textures/gui/") and name.endswith(".png.mcmeta")):
            continue
        png = name[: -len(".mcmeta")]
        dst_png = os.path.join(pack, png)
        dst_meta = os.path.join(pack, name)
        if not os.path.exists(dst_png) or os.path.exists(dst_meta):
            continue
        vanilla = Image.open(io.BytesIO(z.read(png))).size
        ours = Image.open(dst_png).size
        if vanilla != ours:
            skipped.append(f"{png}: vanilla {vanilla}, pack {ours}")
            continue
        with open(dst_meta, "wb") as out:
            out.write(z.read(name))
        copied.append(png)
    for p in copied:
        print("copied", p.split("textures/gui/")[1] + ".mcmeta")
    for s in skipped:
        print("SKIPPED (size differs)", s)
    print(f"{len(copied)} copied, {len(skipped)} skipped")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
