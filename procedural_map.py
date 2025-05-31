#!/usr/bin/env python3
"""
procedural_map.py  – noise-driven world generator

Usage examples
--------------

# ASCII, on stdout (exactly what you have already)
python procedural_map.py --size 120x60 --seed 123

# Sprite render instead, saved to map.png
python procedural_map.py --size 120x60 --seed 123 \
                         --renderer sprite \
                         --tiles tiles.png --tile-size 16 --out map.png
"""
import sys, argparse, random, pathlib, io
from dataclasses import dataclass
from typing import List
import numpy as np
from noise import pnoise2
from PIL import Image, ImageDraw                  # ── NEW: Pillow

# ──────────────────────────────────────────────
# 1.  Tileset meta-model
# ──────────────────────────────────────────────
@dataclass(frozen=True)
class Tile:
    id: str
    glyph: str
    passable: bool
    rc: tuple  # (row, col) on the sprite-sheet

TILESET: List[Tile] = [
    Tile("water_deep",     "~", False, (0, 0)),
    Tile("water_shallow",  ",", False, (0, 1)),
    Tile("sand",           ".", True,  (1, 0)),
    Tile("plains",         "\"",True,  (1, 1)),
    Tile("forest",         "♣", True,  (2, 0)),
    Tile("mountain",       "^", False, (2, 1)),
]

ID2TILE   = {t.id: t for t in TILESET}
ID2GLYPH  = {t.id: t.glyph for t in TILESET}

# ──────────────────────────────────────────────
# 2.  Terrain generator (unchanged)
# ──────────────────────────────────────────────
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

        height_map   = (height_map   + 0.5)
        moisture_map = (moisture_map + 0.5)

        terrain = [["" for _ in range(self.w)] for _ in range(self.h)]
        for y in range(self.h):
            for x in range(self.w):
                h, m = height_map[y,x], moisture_map[y,x]
                if h < 0.35:   terrain[y][x] = "water_deep"
                elif h < 0.42: terrain[y][x] = "water_shallow"
                elif h < 0.45: terrain[y][x] = "sand"
                elif h < 0.70: terrain[y][x] = "plains" if m < 0.5 else "forest"
                else:          terrain[y][x] = "mountain"
        return terrain

# ──────────────────────────────────────────────
# 3.  Renderers
# ──────────────────────────────────────────────
class AsciiRenderer:
    def __init__(self, terrain): self.terrain = terrain
    def render(self):            # returns str
        return "\n".join(
            "".join(ID2GLYPH[id_] for id_ in row)
            for row in self.terrain
        )

class SpriteRenderer:
    """
    Renders terrain[][] → PNG file using a sprite-sheet laid out in
    a uniform grid.  The TILESET list provides (row,col) coordinates.
    """
    def __init__(self, terrain, sheet_path, tile_size):
        self.terrain    = terrain
        self.tile_size  = tile_size
        self.sheet_img  = Image.open(sheet_path).convert("RGBA")
        self.id2sprite  = self._slice_sheet()

    def _slice_sheet(self):
        """
        Build {terrain_id: Image} by cropping the sheet once.
        """
        tile_w = tile_h = self.tile_size
        sprites = {}
        for tile in TILESET:
            r, c = tile.rc
            x0, y0 = c * tile_w, r * tile_h
            sprites[tile.id] = self.sheet_img.crop(
                (x0, y0, x0 + tile_w, y0 + tile_h)
            )
        return sprites

    def render(self, out_path):
        h, w = len(self.terrain), len(self.terrain[0])
        canvas = Image.new("RGBA", (w * self.tile_size,
                                    h * self.tile_size))
        for y, row in enumerate(self.terrain):
            for x, id_ in enumerate(row):
                canvas.paste(self.id2sprite[id_],
                             (x * self.tile_size, y * self.tile_size))
        canvas.save(out_path)
        return out_path

# ──────────────────────────────────────────────
# 4.  (Optional) dummy sheet generator
# ──────────────────────────────────────────────
def make_placeholder_sheet(path: pathlib.Path, tile_size: int = 16):
    """
    Creates a tiny 3×2 grid of colored squares so you can try the
    SpriteRenderer immediately.  Delete once you have real art.
    """
    colors = {
        "water_deep":    (30,  60,160),
        "water_shallow": (60, 120,200),
        "sand":          (210,180, 80),
        "plains":        ( 60,180, 60),
        "forest":        ( 20,120, 20),
        "mountain":      (120,120,120),
    }
    cols = max(t.rc[1] for t in TILESET)+1
    rows = max(t.rc[0] for t in TILESET)+1
    sheet = Image.new("RGBA", (cols*tile_size, rows*tile_size))
    draw  = ImageDraw.Draw(sheet)
    for tile in TILESET:
        r,c = tile.rc
        x0,y0 = c*tile_size, r*tile_size
        draw.rectangle([x0,y0,x0+tile_size,y0+tile_size],
                       fill=colors[tile.id])
    sheet.save(path)

# ──────────────────────────────────────────────
# 5.  CLI
# ──────────────────────────────────────────────
def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--size", default="100x60")
    p.add_argument("--seed", type=int, default=0)

    # renderer options
    p.add_argument("--renderer", choices=("ascii","sprite"),
                   default="ascii")
    p.add_argument("--tiles", help="sprite sheet PNG")
    p.add_argument("--tile-size", type=int, default=16)
    p.add_argument("--out", default="map.png",
                   help="output PNG when using sprite renderer")

    args = p.parse_args(argv)

    w,h = map(int, args.size.lower().split("x"))
    terrain = TerrainGenerator(w, h, args.seed).generate()

    if args.renderer == "ascii":
        print(AsciiRenderer(terrain).render())
    else:
        # generate a dummy sheet if none supplied (for first-time test)
        tiles_path = pathlib.Path(args.tiles or "dummy_tiles.png")
        if not tiles_path.exists():
            make_placeholder_sheet(tiles_path, args.tile_size)
            print(f"[info] No sheet supplied; wrote placeholder {tiles_path}")

        sprite_out = SpriteRenderer(
            terrain, tiles_path, args.tile_size
        ).render(args.out)
        print(f"[✓] Sprite map saved → {sprite_out}")

if __name__ == "__main__":
    main(sys.argv[1:])
