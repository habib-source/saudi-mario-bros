# Saudi Mario Bros

NES ROM hack of Super Mario Bros with a Saudi/Najdi theme. Built from doppelganger's 6502 disassembly.

Inspired by the 8-bit Saudi Mario graffiti at Roshn Front / Riyadh Front (by @asadalghareeb) — features Mario in thobe + red/white shemagh, Najdi castle with Saudi flag, palm trees, sand bricks, a camel, smiley cloud, and "TIME 2030" (Vision 2030 nod).

**No theme changes without explicit user approval.**

---

## Quick Start

```bash
# One-time setup
python extract_chr.py original-rom.nes       # extract CHR graphics (once)
docker build -t smb-build .                   # build toolchain image (once)

# Bake & run (after any edit)
./bake.sh

# Screenshots are saved to fceux/snaps/.
# ALWAYS delete all files in fceux/snaps/ before viewing, so you only see current screenshots.
# It's a temp folder — safe to delete from freely.
```

---

## Project Layout

```
saudi-mario-bros/
├── SMBDIS.ASM          # PRG-ROM source — all game code (16,351 lines, 6502 ASM)
├── chr-rom/chr.bin      # CHR-ROM — tile graphics (8 KB, checked into git)
├── mario_sprites.txt    # ASCII sprite sheet — edit Mario frames here
├── sprite_tools.py      # Export/import sprites between chr.bin <-> ASCII
├── bake.sh              # Import sprites + build ROM + launch emulator
├── build.sh             # Assembles PRG-ROM (called by bake.sh)
├── build_rom.py         # Stitches iNES header + PRG + CHR into .nes
├── extract_chr.py       # One-time CHR-ROM extraction from original .nes
├── Dockerfile           # Build env: Debian + asm6f assembler
├── original-rom.nes     # Original SMB ROM (gitignored)
├── fceux/               # FCEUX 2.6.6 emulator (gitignored)
│   ├── fceux64.exe
│   └── snaps/           # Screenshots (temp, safe to delete)
├── tools/               # YY-CHR tile editor etc. (gitignored)
└── output/
    └── saudi-mario-bros.nes  # Built ROM (gitignored)
```

---

## Sprite Editing Workflow

Edit `mario_sprites.txt` to change Mario's pixel art. Legend:
- `.` = transparent
- `#` = color 1 (black / iqal)
- `@` = color 2 (skin)
- `O` = color 3 (white / thobe)

Each frame header shows which other frames share tiles:
```
=== SMALL_STAND (16px) [ ] updates: SMALL_CLIMB2, SMALL_WALK2, SMALL_WALK3 ===
```
Mark `[x]` on frames you edited — those tiles take priority during import.

```bash
# Full workflow:
# 1. Edit mario_sprites.txt
# 2. Mark edited frames with [x]
# 3. Run: ./bake.sh

# Regenerate sprite sheet from current chr.bin:
docker run --rm -v "C:\Users\a\Desktop\dev\saudi-mario-bros:/build" smb-build python3 sprite_tools.py export

# Reset chr.bin to original:
docker run --rm -v "C:\Users\a\Desktop\dev\saudi-mario-bros:/build" smb-build python3 extract_chr.py original-rom.nes
```

H-flip is applied where the game mirrors tiles (standing pose legs, etc). Shared tiles only need editing in one frame — import writes each tile once (first-come, or `[x]` priority).

---

## NES Graphics Architecture

### Pattern Tables (in chr-rom/chr.bin)
- **Pattern Table 0** ($0000–$0FFF, bytes 0–4095): **Sprites** — Mario, enemies, items, power-ups
- **Pattern Table 1** ($1000–$1FFF, bytes 4096–8191): **Backgrounds** — bricks, pipes, scenery, text, title screen

PPU_CTRL bit 3=0 (sprites from PT0), bit 4=1 (backgrounds from PT1), bit 5=0 (8x8 sprites).

### Palettes
Each sprite/background gets 4 colors (including transparent). NES has 4 BG palettes + 4 sprite palettes.

**Mario's colors** are set in TWO places:
1. `PlayerColors` (line 1431) — **this is what actually controls Mario's in-game colors**. `GetPlayerColors` writes these directly to VRAM, overriding the palette table.
2. `GroundPaletteData` sprite palette 0 (line 2256) — initial palette, gets overwritten by PlayerColors.

Current Mario palette: `$22`(bg), `$0f`(black), `$27`(skin), `$30`(white)

**Background colors** (underground/castle/transitions): `BackgroundColors` (line 1427). Currently dark brown (`$07`) instead of black.

### Attribute Table Constraint
Background palettes are assigned per 16x16 area via the attribute table. Objects sharing the same screen region share a palette. Example: pipes and bushes both use BG palette 0 — changing one affects the other.

---

## Current Theme Status

### Applied
- Desert ground palette (sand bricks, tan ground, warm dunes)
- Mario palette: black + skin + white (thobe look)
- Dark brown background for underground/castle/transitions
- Sprite editing tools (ASCII export/import with flip support)

### Not Yet Applied (needs approval)
- Text changes (HUD, story messages)
- CHR-ROM sprite rethemes (enemies, items, environment)
- Level layout changes
- Music changes
- Other palette areas (water, castle, underground)

---

## Theme Vision

### Reference
Roshn Front graffiti (Riyadh, by @asadalghareeb): 8-bit Saudi Mario in thobe + red/white shemagh jumping past a Najdi castle with Saudi flag, palm tree, sand-colored bricks, camel in foreground, smiley cloud, HUD reads "TIME 2030".

### Character Rethemes

| Original | Saudi Version | Notes |
|----------|--------------|-------|
| Mario | **Saudi Mario** | Thobe + shemagh + iqal + sandals |
| Goomba | **Date Goomba** (تمر) | Angry date cluster with feet |
| Green/Red Koopa | **Camel Troopa** (جمل) | Camel with saddle bags + hump |
| Buzzy Beetle | **Scorpion** (عقرب) | Desert scorpion |
| Cheep-Cheep | **Falcon** (صقر) | Hunting falcon |
| Blooper | **Sand Snake** (ثعبان) | Desert snake |
| Piranha Plant | **Cactus** (صبّار) | Spiky cactus in pipe |
| Lakitu | **Carpet Rider** | Flying carpet, throws scorpions |
| Bowser | **Sheikh Boss** (الشيخ) | Bisht + ghutrah, gold-trimmed |
| Toad | **Najdi Villager** | Traditional Najdi dress |
| Hammer Bro | **Sword Dancer** (عرضة) | Throws curved swords |

### Power-ups / Items

| Original | Saudi Version |
|----------|--------------|
| Mushroom | **Qahwa cup** (قهوة) |
| Fire Flower | **Oud bottle** (عود) |
| Super Star | **Camel milk** (حليب إبل) |
| Coin | **Dinar** (ريال) |
| 1-Up | **Dates basket** |

### Environment

| Original | Saudi Version |
|----------|--------------|
| Warp pipes | **Oil derrick pipes** |
| Bricks | **Sand/mud bricks** |
| ? Block | **؟ Block** |
| Hills | **Sand dunes** |
| Bushes | **Palm trees** (نخلة) |
| Castle | **Najdi fortress** (Masmak-style) |
| Flag | **Saudi flag** |
| Underground | **Oasis cave** |

---

## SMBDIS.ASM Section Map

| Lines | Section |
|-------|---------|
| 1–665 | RAM defines, PPU/APU registers |
| 666–882 | Boot, NMI, VBlank |
| 883–1063 | Sprite shuffler, game modes |
| 1064–1633 | Screen routines, title screen |
| 1636–1692 | **Game text** (HUD messages) |
| 1694–1790 | Text engine |
| 1791–2117 | Player graphics rendering |
| 2118–2234 | Metatile graphics |
| 2238–2304 | **Palette data** |
| 2306–2362 | **Story messages** |
| 2365–2530 | Status bar |
| 2531–3530 | Scenery rendering |
| 3531–4456 | Area parser |
| 4457–5280 | **Level data** (32 levels) |
| 5281–5375 | Enemy placement |
| 5376–6270 | Scrolling, player physics |
| 6271–7760 | Items, power-ups |
| 7761–11000 | Enemy init + AI |
| 11001–12723 | Collision (sprite + block) |
| 12724–13090 | Injury & death |
| 13092–14086 | Sprite drawing |
| 14087–14993 | Flagpole & victory |
| 14994–16346 | **Sound engine** |
| 16347–16352 | Vectors (NMI, Reset, IRQ) |

Key locations:
- `PlayerColors` (line 1431): Mario's actual in-game colors
- `BackgroundColors` (line 1427): BG color per area type
- `PlayerGraphicsTable` (line 14399): Tile IDs for all Mario animation frames
- `GroundPaletteData` (line 2250): Desert palette (currently modified)

---

## Text Encoding

Custom encoding (NOT ASCII):
```
$0a=A  $0b=B  $0c=C  $0d=D  $0e=E  $0f=F  $10=G  $11=H  $12=I
$13=J  $14=K  $15=L  $16=M  $17=N  $18=O  $19=P  $1a=Q  $1b=R
$1c=S  $1d=T  $1e=U  $1f=V  $20=W  $21=X  $22=Y  $23=Z
$24=space  $28=-  $29=x(multiply)  $2b=!  $af=.
```

Messages have 3-byte VRAM header: `high_addr, low_addr, length`. Length byte MUST match data.

---

## NES Color Cheat Sheet

```
$0f=black    $00=dark gray  $10=light gray  $30=white
$05=dark red $06=dark red2  $16=red         $27=orange
$07=brown    $08=dark org   $17=brown       $28=yellow
$09=dk green $0a=dk green2  $1a=green       $29=lime
$01=dk blue  $02=dk blue2   $12=blue        $22=sky blue
$38=cream    $36=peach      $37=tan
```

---

## Development Rules

1. **No theme changes without user approval** — propose, wait for go-ahead
2. `./bake.sh` is the standard build+test cycle
3. `SMBDIS.ASM` is the single source of truth for PRG-ROM
4. `mario_sprites.txt` is the editable sprite sheet — mark `[x]` on edited frames
5. When editing text, always recalculate the VRAM header length byte
6. PRG-ROM must be exactly 32,768 bytes
7. Use full Windows path for Docker volume mount, not `$(pwd)`
8. Always `rm -rf __pycache__` before running sprite import (stale bytecode)
