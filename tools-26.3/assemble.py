"""Assemble Catppuccin Mocha Mauve for Minecraft 26.3 as a folder pack.

generated zip (create_flavors.py -f mocha -a mauve, template 1.20.2)
  + the recolored textures from recolor.py (and recolor_mods.py)
  + a transparent carved-pumpkin overlay (Mika's choice, 2026-11-06)
  + pack.mcmeta extended to resource pack format 97 (26.3)
"""
import io, json, os, shutil, sys, zipfile
from PIL import Image

gen_zip, new_dir, jar_path, out, *extra_dirs = sys.argv[1:]
if os.path.isdir(out):
    shutil.rmtree(out)
zipfile.ZipFile(gen_zip).extractall(out)
for d in (new_dir, *extra_dirs):   # extra: recolor_mods.py output (JEI, Jade, Xaero's)
    shutil.copytree(d, out, dirs_exist_ok=True)
pb = 'assets/minecraft/textures/misc/pumpkinblur.png'
size = Image.open(io.BytesIO(zipfile.ZipFile(jar_path).read(pb))).size
os.makedirs(os.path.join(out, os.path.dirname(pb)), exist_ok=True)
Image.new('RGBA', size, (0, 0, 0, 0)).save(os.path.join(out, pb))
meta_p = os.path.join(out, 'pack.mcmeta')
meta = json.load(open(meta_p))
meta['pack']['supported_formats'] = [18, 97]
meta['pack']['min_format'] = 18
meta['pack']['max_format'] = [97, 1]
meta['pack']['description'] = 'Catppuccin UI Mocha Mauve, extended for 26.3 (local build)'
json.dump(meta, open(meta_p, 'w'), indent=2)
print('pack at', out)
