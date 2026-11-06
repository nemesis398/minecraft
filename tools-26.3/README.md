# Catppuccin Mocha Mauve for Minecraft 26.3 (local build)

Upstream `create_flavors.py` stops at 1.21.6. These scripts extend its Mocha
Mauve output to 26.3 for Mika's Prism instance `Minecraft 26.3` (2026-11-06).
Run them with the venv in `resource-packs/Catppuccin UI/.venv` (`catppuccin`,
`pillow`) and `PYTHONDONTWRITEBYTECODE=1`.

| Step | Script | What it does |
|---|---|---|
| 1 | `create_flavors.py -f mocha -a mauve`, template `1.20.2` | upstream Mocha Mauve zip in `output/1.20.2/` |
| 2 | `recolor.py JAR GEN_ZIP WORK/new WORK/sheet.png` | learns the vanilla → Catppuccin color map from the 418 textures upstream covers, recolors the 75 GUI textures 26.3 adds; skips signs, Realms, title art, advancement backgrounds, presets, locator dots and item-like pictures |
| 3 | `recolor_mods.py JAR GEN_ZIP WORK/mods WORK/mods-sheet.png MODS/jei-*.jar MODS/Jade-*.jar MODS/xaerominimap-*.jar` | the same map over JEI, Jade and Xaero GUI sprites |
| 4 | `mods_special.py MODS PACK_DIR WORK/mods` | what the map cannot do: Xaero's tinted white/black textures painted Crust→Mauve, Jade's dark tooltip = the pack's vanilla tooltip, JEI buttons = the pack's vanilla buttons, JEI icons inverted onto Crust→Text, JEI panel border thinned to one Mauve pixel. `PACK_DIR` must already hold an assembled pack (run step 7 once first) |
| 5 | `font_tint.py JAR WORK/font` | bitmap font sheets multiplied by Text `#cdd6f4` (only shows where the TTF lacks a glyph) |
| 6 | `ttf_font.py ~/.local/share/fonts/JetBrainsMonoNerd/JetBrainsMonoNerdFont-Regular.ttf WORK/ttf 8` | JetBrains Mono Nerd Font as the game font, size 8, vanilla fonts as fallback |
| 7 | `assemble.py GEN_ZIP WORK/new JAR OUT_DIR WORK/mods WORK/font WORK/ttf` | folder pack with a transparent pumpkin overlay and `pack.mcmeta` widened to format 97 |
| 8 | `fix_mcmeta.py JAR OUT_DIR` | copies vanilla `.png.mcmeta` next to every GUI sprite that has none, if the sizes match. Without it the game stretches instead of nine-slicing: 27 sprites lacked it, among them the tabs and the friends screen (2026-11-06) |
| 9 | `friends_special.py OUT_DIR` | friends screen: its noisy buttons replaced by the pack's `widget/button` sprites, the list interior painted Mantle |
| 10 | `recolor_mods.py JAR GEN_ZIP WORK/bss WORK/bss-sheet.png MODS/betterstats-*.jar MODS/tcdcommons-*.jar`, then `bss_special.py MODS OUT_DIR WORK/bss` | Better Statistics Screen and TCDCommons: the map's output into the pack, grey icons light again (Crust→Text), toggle buttons cut from the pack's `widget/button` sprites with a Mauve tint when toggled, the selected tab's blue line Mauve, the popup shadow vanilla, the editor's translucent panels opaque (Mantle, Crust, Base), dropdown menus Mantle with a Surface1 or Mauve edge. The search field, the yellow group header and the stat rows are drawn in code and stay |

`JAR` is `~/.local/share/PrismLauncher/libraries/com/mojang/minecraft/26.3/minecraft-26.3-client.jar`,
`MODS` the instance's `mods/`, `OUT_DIR` the instance's
`resourcepacks/Catppuccin Mocha Mauve 26.3`. A folder pack reloads in game with
F3+T.

Settings outside the pack that belong to the look:

- `config/jei/client/default/jei-client.ini`: `drawBackground = BACKGROUND`
- `config/jade/jade.json`: overlay `alpha` 0.9, mod name color `#CBA6F7`
- `config/xaero/minimap/profiles/default.cfg`: `minimap_frame_color = 15` (white, so no tint)
- `config/enhancedoverlay.json`: subtitle, chat input and tab list background
  Base `#1e1e2e` (alpha 220, 200, 200); every other option at its vanilla value

After a Minecraft or mod update, rerun steps 2 to 10 and check the sheets.
