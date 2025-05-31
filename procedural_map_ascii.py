#!/usr/bin/env python3
"""
procedural_map.py  – ASCII map generator with a plug-in renderer

Swap  AsciiRenderer → SpriteRenderer later (same terrain[][] array).
"""

import sys, argparse, random
from dataclasses import dataclass
from typing import List
import numpy as np
from noise import pnoise2

# ───────────────────────────────────────────
# 1.  Tileset meta-model
# ───────────────────────────────────────────
@dataclass(frozen=True)
class Tile:
    id: str           # logical ID ("water_deep")
    glyph: str        # ASCII fallback ('~')
    passable: bool    # walkable?
    rc: tuple = None  # (row,col) in a future sprite-sheet (optional)

# Ordered list ⇒ determins default glyph priority in legend
TILESET: List[Tile] = [
    Tile("water_deep",     "~", False, (0,0)),
    Tile("water_shallow",  ",", False, (0,1)),
    Tile("sand",           ".", True,  (1,0)),
    Tile("plains",         "\"",True,  (1,1)),
    Tile("forest",         "♣", True,  (2,0)),
    Tile("mountain",       "^", False, (2,1)),
]

ID2TILE   = {t.id: t for t in TILESET}
ID2GLYPH  = {t.id: t.glyph for t in TILESET}

# ───────────────────────────────────────────
# 2.  Noise-based terrain generator
# ───────────────────────────────────────────
class TerrainGenerator:
    def __init__(self, width, height, seed, octaves=4):
        self.w, self.h, self.seed, self.oct = width, height, seed, octaves
        random.seed(seed)

    def _noise(self, x, y, scale, offset=0):
        return pnoise2((x+offset)/scale, (y+offset)/scale,
                       octaves=self.oct, repeatx=1024, repeaty=1024,
                       base=self.seed)

    def generate(self):
        height_map   = np.zeros((self.h, self.w))
        moisture_map = np.zeros((self.h, self.w))

        for y in range(self.h):
            for x in range(self.w):
                height_map[y,x]   = self._noise(x,y,  60)
                moisture_map[y,x] = self._noise(x,y, 120, offset=999)

        # Normalise to 0..1
        height_map   = (height_map   + 0.5)
        moisture_map = (moisture_map + 0.5)

        # Biome lookup: simple thresholds now, tweak later
        terrain = [["" for _ in range(self.w)] for _ in range(self.h)]
        for y in range(self.h):
            for x in range(self.w):
                h, m = height_map[y,x], moisture_map[y,x]
                if h < 0.35:
                    terrain[y][x] = "water_deep"
                elif h < 0.42:
                    terrain[y][x] = "water_shallow"
                elif h < 0.45:
                    terrain[y][x] = "sand"
                elif h < 0.70:
                    terrain[y][x] = "plains"  if m < 0.5 else "forest"
                else:
                    terrain[y][x] = "mountain"
        return terrain

# ───────────────────────────────────────────
# 3.  Pluggable renderer(s)
# ───────────────────────────────────────────
class AsciiRenderer:
    def __init__(self, terrain):
        self.terrain = terrain

    def render(self):
        return "\n".join(
            "".join(ID2GLYPH[id_] for id_ in row)
            for row in self.terrain
        )

# Future replacement -------------------------------------------------
# class SpriteRenderer:
#     def __init__(self, terrain, sheet_png, tile_size, lookup_json):
#         ...
# --------------------------------------------------------------------

# ───────────────────────────────────────────
# 4.  CLI entry point
# ───────────────────────────────────────────
def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--size", default="120x60",
                   help="widthxheight, e.g. 200x100")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args(argv)

    w,h = map(int, args.size.lower().split("x"))
    gen = TerrainGenerator(w, h, seed=args.seed)
    terrain = gen.generate()

    out = AsciiRenderer(terrain).render()
    print(out)

if __name__ == "__main__":
    main(sys.argv[1:])
