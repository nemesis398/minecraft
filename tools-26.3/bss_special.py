"""Theme Better Statistics Screen and its library TCDCommons (2026-11-06).

Takes the learned-map output of recolor_mods.py for both jars (WORK_DIR) into
the pack, then repairs what the map gets wrong, mostly the way JEI went:

1. Grey icons (close, settings, filters, trash, dropdown arrows, grey folder)
   are light on light vanilla buttons; the map made them dark, so they vanished
   on dark Catppuccin. They are recolored from the original onto Crust..Text by
   luminance, so light stays light.
2. TCDCommons' toggle buttons are vanilla stone noise, which the map turns into
   speckles. They are cut from the pack's own widget/button sprites (left and
   right 10 px of the 200x20 button make the 20x20 toggle, whose nine-slice
   border of 3 the mod's mcmeta keeps). The toggled states get a Mauve tint.
3. The selected tab's underline is vanilla blue; it becomes Mauve.
4. popup/shadow is drawn tinted by code, so it stays vanilla.

    bss_special.py MODS_DIR PACK_DIR WORK_DIR
"""
import glob
import io
import os
import shutil
import sys
import zipfile

from PIL import Image

CRUST = (0x11, 0x11, 0x1B)
TEXT = (0xCD, 0xD6, 0xF4)
MAUVE = (0xCB, 0xA6, 0xF7)
BASE = (0x1E, 0x1E, 0x2E)
MANTLE = (0x18, 0x18, 0x25)
SURFACE1 = (0x45, 0x47, 0x5A)
VANILLA_BLUE = (74, 136, 199)

BSS = "assets/betterstats/textures/gui/sprites/"
TCDC = "assets/tcdcommons/textures/gui/sprites/"
GREY_ICONS = [BSS + f"icon/{n}.png" for n in (
    "close", "filter_group", "filter_sort", "filter_unit_dist", "filter_unit_time",
    "settings", "trash")] + [TCDC + f"widget/{n}.png" for n in (
    "dropdown_collapsed", "dropdown_expanded")] + [TCDC + "icon/fs_folder_gray.png"]


def onto_crust_text(img):
    """Luminance onto Crust..Text, stretched so the brightest pixel is Text:
    vanilla draws these icons mid grey, which read dull on Catppuccin."""
    out = img.copy()
    px = out.load()
    lum = lambda r, g, b: 0.299 * r + 0.587 * g + 0.114 * b
    top = max((lum(*px[x, y][:3]) for y in range(out.height) for x in range(out.width)
               if px[x, y][3]), default=255) or 255
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            t = lum(r, g, b) / top
            px[x, y] = tuple(round(c0 + (c1 - c0) * t) for c0, c1 in zip(CRUST, TEXT)) + (a,)
    return out


def toggle_from(button, tint):
    """20x20 toggle from a 200x20 nine-slice button: its outer 10 px each side."""
    out = Image.new("RGBA", (20, 20))
    out.paste(button.crop((0, 0, 10, 20)), (0, 0))
    out.paste(button.crop((190, 0, 200, 20)), (10, 0))
    if tint:
        px = out.load()
        for y in range(3, 17):
            for x in range(3, 17):
                r, g, b, a = px[x, y]
                px[x, y] = tuple(round(c + (m - c) * 0.45) for c, m in zip((r, g, b), MAUVE)) + (a,)
    return out


def main(mods, pack, work):
    jars = {}
    for pattern in ("betterstats-*.jar", "tcdcommons-*.jar"):
        z = zipfile.ZipFile(sorted(glob.glob(os.path.join(mods, pattern)))[-1])
        jars.update({n: z for n in z.namelist()})

    # Learned-map output, with the mods' own .mcmeta, into the pack.
    for root, _, files in os.walk(os.path.join(work, "assets")):
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.join(pack, os.path.relpath(src, work))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)

    def original(name):
        return Image.open(io.BytesIO(jars[name].read(name))).convert("RGBA")

    def put(name, img):
        img.save(os.path.join(pack, name))
        print("fixed", name.split("sprites/")[1])

    for n in GREY_ICONS:
        put(n, onto_crust_text(original(n)))

    widgets = os.path.join(pack, "assets/minecraft/textures/gui/sprites/widget/")
    plain = Image.open(widgets + "button.png").convert("RGBA")
    hover = Image.open(widgets + "button_highlighted.png").convert("RGBA")
    off = Image.open(widgets + "button_disabled.png").convert("RGBA")
    for suffix, base, tint in (("", plain, False), ("_highlighted", hover, False),
                               ("_disabled", off, False), ("_toggled", plain, True),
                               ("_toggled_highlighted", hover, True),
                               ("_toggled_disabled", off, True)):
        put(TCDC + f"widget/togglebtn{suffix}.png", toggle_from(base, tint))

    name = BSS + "editor/tab_strip/entry_selected.png"
    img = Image.open(os.path.join(pack, name)).convert("RGBA")  # recolored; the map kept the blue
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y][:3] == VANILLA_BLUE:
                px[x, y] = MAUVE + (px[x, y][3],)
    put(name, img)

    put(TCDC + "popup/shadow.png", original(TCDC + "popup/shadow.png"))

    # 5. The editor's panels are 1x1 translucent black (alpha 80, 40 or 0), so
    #    the blurred world showed through and the stat rows, which the mod
    #    fills in code with translucent white, read as light grey bars (Mika's
    #    screenshots, 2026-11-06). Opaque Catppuccin instead; the rows then sit
    #    on Base. The search field (black), the group header (yellow) and the
    #    rows are drawn in code and stay as the mod draws them.
    for rel, color in (("editor/menubar/background.png", MANTLE),
                       ("editor/tab_strip/background.png", CRUST),
                       ("editor/tab/background.png", BASE),
                       ("editor/tab/stats_file/filters_background.png", MANTLE),
                       ("editor/tab/stats_file/stats_background.png", None)):
        put(BSS + rel, Image.new("RGBA", (1, 1), (color + (255,)) if color else (0, 0, 0, 0)))
    for rel in ("editor/menubar/foreground.png", "editor/tab/foreground.png"):
        img = original(BSS + rel)
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                if px[x, y][3]:
                    px[x, y] = CRUST + (px[x, y][3],)
        put(BSS + rel, img)

    # 6. Dropdown and context menus: neutral grey in vanilla and after the map.
    for suffix, edge in (("", SURFACE1), ("_highlighted", MAUVE)):
        img = original(TCDC + f"popup/ctxmenu{suffix}.png")
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = px[x, y]
                if a:
                    px[x, y] = (MANTLE if r < 60 else edge) + (a,)
        put(TCDC + f"popup/ctxmenu{suffix}.png", img)


if __name__ == "__main__":
    main(*sys.argv[1:4])
