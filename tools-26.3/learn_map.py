"""Learn the vanilla -> Catppuccin color map from textures the pack already covers.

For every GUI texture present in both the vanilla client jar and the generated
pack, with the same size, count which pack color sits where each vanilla color
was. A vanilla color whose most common target holds a clear majority is a rule.
"""
import io, json, sys, zipfile, collections
from PIL import Image

PREFIX = 'assets/minecraft/textures/gui/'

def load(z, n):
    return Image.open(io.BytesIO(z.read(n))).convert('RGBA')

def learn(jar_path, pack_path, min_share=0.6, min_count=8):
    jar, pack = zipfile.ZipFile(jar_path), zipfile.ZipFile(pack_path)
    pn = set(pack.namelist())
    votes = collections.defaultdict(collections.Counter)
    for n in jar.namelist():
        if not (n.startswith(PREFIX) and n.endswith('.png') and n in pn):
            continue
        a, b = load(jar, n), load(pack, n)
        if a.size != b.size:
            continue
        for (r, g, bl, al), (r2, g2, b2, a2) in zip(a.getdata(), b.getdata()):
            if al and a2:
                votes[(r, g, bl)][(r2, g2, b2)] += 1
    rules, unsure = {}, 0
    for src, c in votes.items():
        (dst, k), total = c.most_common(1)[0], sum(c.values())
        if total >= min_count and k / total >= min_share:
            rules[src] = dst
        else:
            unsure += 1
    return rules, votes, unsure

if __name__ == '__main__':
    rules, votes, unsure = learn(sys.argv[1], sys.argv[2])
    greys = sorted((s, d) for s, d in rules.items() if max(s) - min(s) <= 6)
    print(f'colors seen {len(votes)}, rules {len(rules)}, unsure {unsure}, grey rules {len(greys)}')
    for s, d in greys[:: max(1, len(greys) // 25)]:
        print(f'  #{s[0]:02x}{s[1]:02x}{s[2]:02x} -> #{d[0]:02x}{d[1]:02x}{d[2]:02x}  ({sum(votes[s].values())} px)')
    json.dump({'%02x%02x%02x' % s: '%02x%02x%02x' % d for s, d in rules.items()}, open(sys.argv[3], 'w'), indent=0)
