# Saudi Mario Bros

A NES ROM hack of *Super Mario Bros* with a Saudi/Najdi theme, built from [doppelganger's 6502 disassembly](https://gist.github.com/1wErt3r/4048722).

Inspired by the 8-bit Saudi Mario graffiti at **Roshn Front / Riyadh Front** (by [@asadalghareeb](https://twitter.com/asadalghareeb)) — featuring Mario in a thobe and red/white shemagh jumping past a Najdi castle with the Saudi flag, palm trees, sand-colored bricks, a camel, a smiley cloud, and "TIME 2030" (a nod to Vision 2030).

## Screenshots

*(Coming soon)*

## What's Changed

- **Saudi Mario** — Mario wears a thobe (white robe), shemagh (headscarf), and iqal (black cord). Custom sprite art for all animation frames.
- **Desert palette** — Sand-colored bricks, tan ground, warm dune tones replace the original Mushroom Kingdom colors.
- **Najdi castle** — End-of-world castle retiled with crenellated fortress walls inspired by Masmak Fort architecture.
- **Mushroom power-up** — Redrawn sprite (qahwa cup planned).
- **Dark underground** — Dark brown background for underground/castle/transition areas.

## Theme Vision

The full retheme plan (pending implementation):

| Original | Saudi Version |
|----------|--------------|
| Mario | Saudi Mario — thobe + shemagh + iqal + sandals |
| Goomba | Date Goomba — angry date cluster |
| Koopa | Camel Troopa — camel with saddle |
| Piranha Plant | Cactus in pipe |
| Bowser | Sheikh Boss — bisht + ghutrah |
| Mushroom | Qahwa cup |
| Fire Flower | Oud bottle |
| Coin | Dinar |
| Bricks | Sand/mud bricks |
| Castle | Najdi fortress (Masmak-style) |
| Flag | Saudi flag |
| ? Block | Arabic ? block |

See [CLAUDE.md](CLAUDE.md) for the complete retheme table with Arabic names.

## Building

### Prerequisites

- **Docker** — builds the ROM inside a Debian container with the asm6f assembler
- **Docker compose** (optional) — easier then a run command.
- **FCEUX** (optional) — NES emulator for testing, placed in `fceux/`

### Build & Run

```bash
# Import all sprites/tiles, assemble ROM, launch emulator
./bake.sh
```

This runs the full pipeline:
1. Imports Mario sprites from `mario_sprites.txt`
2. Imports background tiles (castle, mushroom, question block, title) from their ASCII files
3. Assembles the PRG-ROM from `SMBDIS.ASM`
4. Stitches the iNES header + PRG + CHR into `output/saudi-mario-bros.nes`
5. Launches FCEUX with the built ROM

### Output

The built ROM is written to `output/saudi-mario-bros.nes`.

## Editing Graphics

All graphics are edited as ASCII art in plain text files — no hex editor needed.

### Mario Sprites (`mario_sprites.txt`)

Each of Mario's animation frames (standing, walking, jumping, etc.) is laid out as ASCII pixel art:

```
. = transparent
# = color 1 (black / iqal)
@ = color 2 (skin)
O = color 3 (white / thobe)
```

Mark edited frames with `[x]` in the header so the importer knows which tiles take priority when frames share tiles.

### Castle Tiles (`castle_tiles.txt`)

Eight castle background tiles (walls, crenellations, entrance arches) editable as 8x8 grids. The file also documents the metatile layout and full castle formation for reference.

### Mushroom Sprite (`mushroom.txt`)

A single 16x16 grid for the mushroom power-up (4 tiles in Pattern Table 0).

### Regenerating the Sprite Sheet

To regenerate `mario_sprites.txt` from the current `chr.bin`:

```bash
docker run --rm -v "$(pwd):/build" smb-build python3 sprite_tools.py export
```

## Project Structure

```
saudi-mario-bros/
├── SMBDIS.ASM            # PRG-ROM source — all game code (6502 ASM)
├── chr-rom/chr.bin        # CHR-ROM tile graphics (8 KB)
├── mario_sprites.txt      # Editable Mario sprite sheet (ASCII art)
├── castle_tiles.txt       # Editable castle background tiles
├── mushroom.txt           # Editable mushroom power-up sprite
├── sprite_tools.py        # Mario sprite export/import tool
├── import_bg_tiles.py     # Background tile importer (castle, mushroom, etc.)
├── bake.sh                # Full build + launch pipeline
├── build.sh               # PRG-ROM assembler wrapper
├── build_rom.py           # iNES ROM stitcher
├── extract_chr.py         # One-time CHR extractor from original ROM
├── Dockerfile             # Build environment (Debian + asm6f)
└── output/
    └── saudi-mario-bros.nes
```

## How NES Graphics Work

The NES has two **pattern tables** of 256 tiles each (8x8 pixels, 2-bit color):

- **Pattern Table 0** (sprites) — Mario, enemies, items, power-ups
- **Pattern Table 1** (backgrounds) — bricks, pipes, scenery, text, title screen

Each tile gets 4 colors from a **palette** (one color is always transparent). The NES supports 4 background palettes and 4 sprite palettes, assigned to screen regions via the **attribute table** in 16x16 pixel blocks.

Mario's colors are controlled by `PlayerColors` in `SMBDIS.ASM` — currently set to black (iqal), skin tone, and white (thobe).

## Credits

- **Original disassembly**: [doppelganger](https://gist.github.com/1wErt3r/4048722) — complete 6502 disassembly of Super Mario Bros
- **Graffiti inspiration**: [@asadalghareeb](https://twitter.com/asadalghareeb) — 8-bit Saudi Mario at Roshn Front, Riyadh
- **Assembler**: [asm6f](https://github.com/freem/asm6f) — 6502 assembler
- **Emulator**: [FCEUX](https://fceux.com/) — NES emulator used for testing

## License

This is a fan project / ROM hack for educational and cultural purposes. Super Mario Bros is property of Nintendo. The original game ROM is not included in this repository.
