# Saudi Mario Bros

NES ROM hack of Super Mario Bros with a Saudi Arabian theme. Built from doppelganger's 6502 disassembly.

**No theme changes without explicit user approval.**

---

## Quick Start

```bash
# 1. One-time: extract graphics from original ROM
python extract_chr.py original-rom.nes

# 2. Build
docker build -t smb-build .
docker run --rm -v "C:\Users\a\Desktop\dev\saudi-mario-bros\output:/output" smb-build

# 3. Play
./fceux/fceux64.exe output/saudi-mario-bros.nes
```

---

## Project Layout

```
saudi-mario-bros/
├── SMBDIS.ASM          # Source of truth — all game code (16,351 lines, 6502 ASM)
├── Dockerfile           # Build env: Debian + asm6f assembler
├── build.sh             # Strips x816 directives, assembles PRG-ROM
├── build_rom.py         # Stitches iNES header + PRG + CHR into .nes
├── extract_chr.py       # Extracts 8 KB CHR-ROM from an original .nes
├── original-rom.nes     # Original SMB ROM (gitignored)
├── chr-rom/chr.bin      # Extracted tile graphics (gitignored, 8 KB)
├── fceux/               # FCEUX 2.6.6 emulator (gitignored)
│   └── fceux64.exe
└── output/
    └── saudi-mario-bros.nes  # Built ROM (gitignored)
```

---

## How NES ROMs Work

A NES ROM = **PRG-ROM** (program) + **CHR-ROM** (graphics). They are separate.

### PRG-ROM — `SMBDIS.ASM` (what we edit)
32 KB of 6502 assembly. Contains all game logic, level layouts, text strings, color palettes, music data, and physics. Tells the NES *which* tile to place *where* and *what color*, but has **zero pixel data**.

### CHR-ROM — `chr-rom/chr.bin` (binary, edit with tile editor)
8 KB of raw pixels. Every 8x8 tile: Mario, Goombas, bricks, pipes, letters, title screen logo. The CPU never touches this directly — the PPU (graphics chip) reads it:
```asm
OutputTScr: lda PPU_DATA  ;get title screen from chr-rom  (line 1599)
```

### What to edit where

| Want to change... | Edit |
|-------------------|------|
| Colors / palettes | `SMBDIS.ASM` palette tables (line 2238) |
| Text / messages | `SMBDIS.ASM` game text (line 1636, 2306) |
| Level layouts | `SMBDIS.ASM` level data (line 4457) |
| Music / SFX | `SMBDIS.ASM` sound engine (line 14994) |
| Physics / gameplay | `SMBDIS.ASM` various sections |
| Sprite art (Mario, enemies, items) | `chr-rom/chr.bin` with tile editor (YY-CHR, NES Screen Tool) |
| Background art (bricks, pipes, scenery) | `chr-rom/chr.bin` with tile editor |
| Title screen logo | `chr-rom/chr.bin` at offset $1EC0 |

---

## Build System

### Assembler
Original targets **x816** (65816 assembler). We use **asm6f** in Docker. `build.sh` strips the two incompatible directives (`.index 8`, `.mem 8`) automatically.

### iNES ROM Format
```
16 bytes    iNES header (mapper 0/NROM, vertical mirroring)
32,768 bytes PRG-ROM (2 × 16 KB banks) — from SMBDIS.ASM
8,192 bytes  CHR-ROM (1 × 8 KB bank) — from chr-rom/chr.bin
= 40,976 bytes total
```

### Build commands
```bash
# Full rebuild
docker build -t smb-build .
docker run --rm -v "C:\Users\a\Desktop\dev\saudi-mario-bros\output:/output" smb-build

# Test
./fceux/fceux64.exe output/saudi-mario-bros.nes
```

Note: `$(pwd)` volume mounts don't work on Windows. Use the full path.

---

## SMBDIS.ASM Section Map

All code starts at `.org $8000` (CPU address $8000–$FFFF).

| Lines | Section | What's Here |
|-------|---------|-------------|
| 1–665 | **RAM defines** | PPU/APU/joypad registers, game state vars, object buffers, timers |
| 666–670 | **Directives** | `.org $8000` |
| 671–882 | **Boot & NMI** | `Start:` cold/warm boot, `NonMaskableInterrupt:` VBlank, timers, pause |
| 883–930 | **Sprite shuffler** | OAM cycling to prevent flicker |
| 931–1063 | **Game modes** | Title screen / game / victory / game over dispatch, demo playback |
| 1064–1480 | **Screen routines** | Status bar, intermediate screens, palette loading |
| 1481–1633 | **Title screen** | Column rendering, title screen draw from CHR-ROM |
| 1636–1692 | **Game text** | HUD: "MARIO", "WORLD", "TIME", "GAME OVER", "WARP ZONE", "LUIGI" |
| 1694–1790 | **Text engine** | `WriteGameText` routine |
| 1791–2117 | **Player graphics** | Sprite rendering, animation frames |
| 2118–2234 | **Metatile graphics** | Block/tile definition tables |
| 2238–2304 | **Palette data** | Color palettes for all area types |
| 2306–2362 | **Story messages** | Victory/defeat messages |
| 2365–2530 | **Status bar** | Score, coins, lives display |
| 2531–3530 | **Scenery rendering** | Clouds, mountains, bushes, terrain, pipes, staircases |
| 3531–4456 | **Area parser** | Decodes compressed level data into metatile columns |
| 4457–5280 | **Level data** | All 32 level layouts |
| 5281–5375 | **Enemy data** | Enemy placement per area |
| 5376–6010 | **Scrolling** | Screen scroll, movement |
| 6011–6270 | **Player physics** | Jump forces, friction, acceleration, max speed |
| 6271–6623 | **Fireball & items** | Fireball state machine, power-ups |
| 6624–7440 | **Misc objects** | Coins, hammers, floatey numbers |
| 7441–7760 | **Power-ups** | Mushroom / fire flower / star / 1-up |
| 7761–9002 | **Enemy init** | Goomba, Koopa, Hammer Bro, Lakitu, Bowser, etc. |
| 9003–11000 | **Enemy AI** | Movement, Bowser AI, bridge collapse |
| 11001–11543 | **Sprite collision** | Fireball/player vs enemy, stomps |
| 11544–12723 | **Block collision** | Brick breaking, pipe entry, coin collect |
| 12724–13090 | **Injury & death** | Damage, shrink, death animation |
| 13092–14086 | **Sprite drawing** | Vine, enemy, block, debris rendering |
| 14087–14993 | **Flagpole & victory** | End-of-level sequence, fireworks |
| 14994–16346 | **Sound engine** | APU driver, all SFX, all music tracks |
| 16347–16352 | **Vectors** | NMI, Reset, IRQ |

---

## Theming Targets

All changes require user approval.

### 1. Palettes — colors (lines 2238–2304)

Format: 3-byte PPU address header + groups of 4 NES color indices. The NES has a fixed 64-color hardware palette.

| Label | Line | Area |
|-------|------|------|
| `WaterPaletteData` | 2238 | Water/swimming |
| `GroundPaletteData` | 2250 | Overworld (most levels) |
| `UndergroundPaletteData` | 2262 | Underground bonus |
| `CastlePaletteData` | 2274 | Castle/fortress |
| `DaySnowPaletteData` | 2286 | Snow (day) |
| `NightSnowPaletteData` | 2291 | Snow (night) |
| `MushroomPaletteData` | 2296 | Toad rooms |
| `BowserPaletteData` | 2301 | Bowser sprite |

**NES color cheat sheet:**
```
$0f=black    $00=dark gray  $10=light gray  $30=white
$05=dark red $06=dark red2  $16=red         $27=orange
$07=brown    $08=dark org   $17=brown       $28=yellow
$09=dk green $0a=dk green2  $1a=green       $29=lime
$01=dk blue  $02=dk blue2   $12=blue        $22=sky blue
$38=cream    $36=peach      $37=tan
```

### 2. Text — messages (lines 1636–1692, 2306–2362)

Custom character encoding (NOT ASCII):
```
$0a=A  $0b=B  $0c=C  $0d=D  $0e=E  $0f=F  $10=G  $11=H  $12=I
$13=J  $14=K  $15=L  $16=M  $17=N  $18=O  $19=P  $1a=Q  $1b=R
$1c=S  $1d=T  $1e=U  $1f=V  $20=W  $21=X  $22=Y  $23=Z
$24=space  $28=-  $29=x(multiply)  $2b=!  $af=.
```

| Label | Line | Current Text |
|-------|------|-------------|
| `TopStatusBarLine` | 1637 | "MARIO" / "WORLD" / "TIME" |
| `TwoPlayerTimeUp` | 1655 | "MARIO" |
| `OnePlayerTimeUp` | 1657 | "TIME UP" |
| `TwoPlayerGameOver` | 1661 | "MARIO" |
| `OnePlayerGameOver` | 1663 | "GAME OVER" |
| `WarpZoneWelcome` | 1668 | "WELCOME TO WARP ZONE!" |
| `LuigiName` | 1679 | "LUIGI" |
| `MarioThanksMessage` | 2306 | "THANK YOU MARIO!" |
| `LuigiThanksMessage` | 2314 | "THANK YOU LUIGI!" |
| `MushroomRetainerSaved` | 2322 | "BUT OUR PRINCESS IS IN ANOTHER CASTLE!" |
| `PrincessSaved1` | 2333 | "YOUR QUEST IS OVER." |
| `PrincessSaved2` | 2341 | "WE PRESENT YOU A NEW QUEST." |
| `WorldSelectMessage1` | 2350 | "PUSH BUTTON B" |
| `WorldSelectMessage2` | 2357 | "TO SELECT A WORLD" |

**CRITICAL**: Messages start with 3-byte VRAM header: `high_addr, low_addr, length`. The length byte MUST match the data that follows. Change text length → update this byte.

### 3. CHR-ROM — pixel art (external binary)

Edit `chr-rom/chr.bin` with YY-CHR or NES Screen Tool.

**Pattern Table 1 — sprites ($1000–$1FFF):**

| Tiles | Content |
|-------|---------|
| $00–$1F | Mario (small) — walk, jump, swim |
| $20–$3F | Mario (big) — upper body |
| $40–$5F | Mario (big) — lower body |
| $60–$7F | Goomba, Koopa, Buzzy Beetle |
| $80–$9F | Hammer Bro, Lakitu, Spiny, Blooper |
| $A0–$BF | Mushroom, fire flower, star, fireball |
| $C0–$DF | Bowser, Cheep Cheep, Bullet Bill |
| $E0–$FF | Flagpole, fireworks, misc |

**Pattern Table 0 — backgrounds ($0000–$0FFF):**

| Tiles | Content |
|-------|---------|
| $00–$0F | Font (numbers, letters, punctuation) |
| $10–$4F | Bricks, blocks, ground, pipes |
| $50–$7F | Clouds, bushes, mountains, trees, fences |
| $80–$BF | Castle, underwater, misc |
| $C0–$FF | Title screen elements |

### 4. Level Data (lines 4457–5280)

Compressed format: 2-byte area header + object commands. 32 areas total:
- `L_GroundArea1`–`22` — overworld
- `L_UndergroundArea1`–`3` — underground
- `L_WaterArea1`–`3` — swimming
- `L_CastleArea1`–`6` — castles
- Cloud areas and warp zones

### 5. Music (lines 14994–16346)

| Label | Track |
|-------|-------|
| `GroundM_P1Data`–`P4CData` | Overworld (4-part) |
| `CastleMusData` | Castle |
| `UndergroundMusData` | Underground |
| `WaterMusData` | Water |
| `Star_CloudMData` | Star power |
| `VictoryMusData` | Level complete |
| `GameOverMusData` | Game over |
| `DeathMusHdr` | Death jingle |
| `FreqRegLookupTbl` (line 16301) | Note frequency table |

### 6. Enemy IDs

```
$00=Green Koopa  $01=Red Koopa     $02=Buzzy Beetle  $03=Red Koopa(fly)
$05=Hammer Bro   $06=Goomba        $09=Blooper       $0a=Bullet Bill
$0c=Podoboo      $0d=Spiny         $0e=Fly Cheep     $11=Lakitu
$12=Spiny(egg)   $14=Red Piranha   $15=Firebar
$1b-$24=Platforms $2d=Bowser        $2e=Bowser Flame  $35=Toad/Retainer
```

---

## Development Rules

1. **No theme changes without user approval** — propose, wait for go-ahead
2. Build with Docker: `docker build` then `docker run`
3. Test in FCEUX after every change: `./fceux/fceux64.exe output/saudi-mario-bros.nes`
4. `SMBDIS.ASM` is the single source of truth for PRG-ROM
5. When editing text, always recalculate the VRAM header length byte
6. CHR-ROM edits are binary — document tile changes in commit messages
7. PRG-ROM must be exactly 32,768 bytes
8. Use full Windows path for Docker volume mount, not `$(pwd)`
