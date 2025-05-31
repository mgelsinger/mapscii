# Procedural Map Generator

A noise‑driven overworld map generator that can render to **plain ASCII** for quick
debugging _or_ assemble a full‑color PNG using any 16 × 16 (or 32 × 32 …) sprite‑sheet.

---

## ✨ Features

* **Noise‑based terrain** &mdash; dual Perlin layers (height + moisture)  
* **Plug‑in renderers** &mdash; swap `AsciiRenderer` for `SpriteRenderer` without touching
  generation logic  
* **Sprite‑sheet ready** &mdash; just point to a PNG laid out on a uniform grid  
* **Fully deterministic** &mdash; pass `--seed` for reproducible worlds  
* Minimal dependencies: `noise`, `numpy`, `Pillow` (and `reportlab` if you want PDFs)

---

## 📦 Requirements

```bash
python ≥ 3.9
pip install noise numpy pillow
```

*(add `reportlab` if you intend to export printable PDFs)*

---

## 🚀 Quick start

### 1. ASCII preview

```bash
python procedural_map.py --size 100x40 --seed 42
```

### 2. Sprite render (16&nbsp;×&nbsp;16 tiles)

```bash
python procedural_map.py --size 120x60 --seed 42 ^
    --renderer sprite ^
    --tiles tileset_16.png ^
    --tile-size 16 ^
    --out map.png
```

> **PowerShell tip**  
> Use the back‑tick **\`** for line continuations (shown above).  
> In Bash/Unix, you can use a back‑slash `\`.

---

## 🎨 Sprite‑sheet layout

| Row | Col | Terrain ID      |
|-----|-----|-----------------|
| 0   | 0   | `water_deep`    |
| 0   | 1   | `water_shallow` |
| 1   | 0   | `sand`          |
| 1   | 1   | `plains`        |
| 2   | 0   | `forest`        |
| 2   | 1   | `mountain`      |

Make sure each tile is the same size (16 × 16, 32 × 32, …).  
Update the `(row, col)` tuples in **`TILESET`** if your art uses a different grid.

---

## ⚙️ Command‑line options

| Flag | Default | Description |
|------|---------|-------------|
| `--size WxH`   | `100x60` | Map size in tiles |
| `--seed N`     | `0`      | Random seed for deterministic maps |
| `--renderer ascii|sprite` | `ascii` | Output format |
| `--tiles FILE` | *(req. for sprite)* | PNG sprite‑sheet |
| `--tile-size N`| `16`     | Tile pixel dimension |
| `--out FILE`   | `map.png`| Output when using sprite renderer |

---

## 🛠 How it works

1. **`TerrainGenerator`** builds two Perlin noise arrays  
2. Each `(height, moisture)` pair is mapped to a **logical terrain ID**  
3. A renderer (ASCII _or_ sprite) turns that ID grid into an image or text block

Because the generator never sees pixel data, you can plug in:

* A **PixiJS/WebGL** renderer for interactive panning  
* An SDL renderer for game‑engine integration  
* A PDF renderer for printable tabletop maps

---

## 🗺️ Extending

* Add new biomes by appending to `TILESET` and tweaking the threshold logic  
* Swap in hex noise or Voronoi regions for a different look  
* Overlay rivers/roads by running a second algorithm over the same height‑map  
* Animate water by cycling through multiple deep/shallow water frames in the sprite renderer

---

## 📚 Credits

* Kenney “Roguelike / RPG” tileset (CC0)  
* Puny World tileset (CC0)  
* Dawnlike Universal tileset (CC‑BY‑SA 3.0)  

*(replace or remove according to the art you actually ship)*

---

## 📝 License

MIT License &mdash; see `LICENSE` for details.
