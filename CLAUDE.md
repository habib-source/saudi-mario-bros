# Saudi Mario Bros

NES ROM hack of Super Mario Bros with a Saudi/Najdi theme. Built from doppelganger's 6502 disassembly.

Inspired by the 8-bit Saudi Mario graffiti at Roshn Front / Riyadh Front (by @asadalghareeb) — features Mario in thobe + red/white shemagh, Najdi castle with Saudi flag, palm trees, sand bricks, a camel, smiley cloud, and "TIME 2030" (Vision 2030 nod).

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

## Theme Vision

### Reference
Roshn Front graffiti (Riyadh, by @asadalghareeb): 8-bit Saudi Mario in thobe + red/white shemagh jumping past a Najdi castle with Saudi flag, palm tree, sand-colored bricks, camel in foreground, smiley cloud, HUD reads "TIME 2030".

### Character Rethemes

| Original | Saudi Version | Notes |
|----------|--------------|-------|
| Mario | **Saudi Mario** | Thobe + shemagh (red/white keffiyeh) + iqal + sandals. Classic jump pose. Same for Luigi (player 2) |
| Goomba | **Date Goomba** (تمر) | Angry date cluster with feet, same grumpy walk cycle |
| Green/Red Koopa | **Camel Troopa** (جمل) | Camel with saddle bags + hump. Shell variant: retreats under the saddle |
| Buzzy Beetle | **Scorpion** (عقرب) | Desert scorpion, same shell/flip mechanic |
| Cheep-Cheep (flying fish) | **Falcon** (صقر) | Hunting falcon — falconry is iconic in KSA |
| Blooper (squid) | **Sand Snake** (ثعبان) | Desert snake, replaces underwater squid |
| Piranha Plant | **Cactus** (صبّار) | Spiky cactus poking out of the pipe |
| Lakitu | **Carpet Rider** | On a flying carpet instead of cloud, throws scorpions/spiny |
| Bowser | **Sheikh Boss** (الشيخ) | Big boss in bisht + ghutrah, gold-trimmed. Crown energy |
| Toad / Retainer | **Najdi Villager** | In traditional Najdi dress |
| Hammer Bro | **Sword Dancer** (عرضة) | Saudi sword dance warrior, throws curved swords |

### Power-up Rethemes

| Original | Saudi Version | Notes |
|----------|--------------|-------|
| Mushroom | **Qahwa cup** (قهوة) | Cardamom coffee — grow big after caffeine hit |
| Fire Flower | **Oud bottle** (عود) | Shoots smoke/incense clouds instead of fireballs |
| Super Star | **Camel milk carton** (حليب إبل) | Invincibility item |
| Coin | **Dinar coin** (ريال) | Gold coin with Arabic Riyal symbol |
| 1-Up Mushroom | **Dates basket** | Extra life |

### Environment Rethemes

| Original | Saudi Version | Notes |
|----------|--------------|-------|
| Green warp pipes | **Oil derrick pipes** | Black/dark steel, oil dripping |
| Bricks | **Sand/mud bricks** | Najdi architectural style, warm tan/brown |
| ? Block | **؟ Block** | Arabic question mark |
| Green hills | **Sand dunes** | Rolling desert dunes |
| Bushes | **Palm trees** (نخلة) | With dates hanging from them |
| Clouds | **Smiley clouds** | Keep the friendly face from the graffiti |
| Mountains | **Rock formations** | AlUla/Madain Saleh style |
| Castle (end of level) | **Najdi fortress** | Masmak-style pointed battlements (شُرُفات), arched windows, Saudi flag on top |
| Flagpole flag | **Saudi flag** | Green with shahada + sword |
| Underground | **Oasis cave** | Underground water → oasis pool theme |

### World Themes (ideas, not final)

| World | Theme | Vibe |
|-------|-------|------|
| World 1 | **Najdi Desert** | Sand dunes, palm trees, mud-brick villages — the graffiti style |
| World 2 | **Nabataean Ruins** | AlUla / Madain Saleh carved rock facades |
| World 3 | **Red Sea / Jeddah Corniche** | Underwater coral, Jeddah waterfront |
| World 4 | **Modern Riyadh** | NEOM-futuristic, Kingdom Tower silhouettes |
| World 5–8 | TBD | Mix and escalate difficulty |

### Palette Direction

Desert warmth: swap the blue sky ($22) for amber/sunset tones in later worlds. Sand ($38 cream, $28 yellow, $07 brown) replaces green ($1a, $29). Keep sky blue for World 1 (matches the graffiti), go orange/sunset for World 4+.

### Music Direction (ideas)

Arabic/Middle-Eastern scales using the existing NES APU channels. Oud-like melodies on Square channels, darbuka rhythms on Noise channel. The frequency table (line 16301) can be modified for quarter-tone approximations.

### Sprite Sheet Concepts (8-bit, NES constraints)

All sprites must fit NES limits: 8x8 or 8x16 pixel tiles, max 4 colors per sprite palette (including transparent). Each character below maps to existing tile slots in CHR-ROM.

**Saudi Mario (small — 16x16, 4 tiles)**
```
    ░█░░
    █RW█      R = red shemagh pattern
    ░█W█      W = white thobe
    █░░█      Black iqal band on head
    ░██░      Sandals (dark)
```

**Saudi Mario (big — 16x32, 8 tiles)**
```
    ░██░░
    █RWR█     Red/white keffiyeh pattern
    ░████     Iqal (black band)
    ░█SS█     S = skin (face)
    █WWWW█    White thobe body
    █WWWW█    
    █W██W█    Thobe skirt
    ░█░░█░    Sandals
```

**Date Goomba (16x16, 4 tiles)**
```
    ░████░
    █BBBB█    B = brown date color
    █>BB<█    Angry eyes (> <)
    ░████░
    ░█░░█░    Little feet
```

**Camel Troopa (16x24, 6 tiles)**
```
    █░░░░░
    ██░░░░    Head + neck
    ░████░    Hump + saddle bags
    █BBBB█    B = brown body
    █░██░█    
    █░░░░█    Four legs
```

**Qahwa Cup (16x16, power-up)**
```
    ░░██░░
    ░░~~░░    Steam wisps
    ░█CC█░    C = coffee brown
    ░█CC█░    Dallah shape
    ░░██░░
    ░████░    Base
```

**Dinar Coin (8x8, single tile)**
```
    ░████░
    █YYYY█    Y = yellow/gold
    █ ﷼  █    Riyal symbol (simplified)
    █YYYY█
    ░████░
```

**Najdi Castle (end-level, background tiles)**
```
    █░█░█░█    Pointed battlements (شرفات)
    ████████   
    █░████░█   Arched windows
    ████████   
    ██▓▓▓▓██   Door (wooden, dark)
    ████████   Mud-brick tan color
    [Saudi flag on top flagpole]
```

**Oil Pipe (replaces warp pipe, background tiles)**
```
    ████████    Dark steel/black
    █░░░░░█    
    █░░░░░█    Pipe interior
    █░░░░░█    
    ████████    
    ░░█~~█░    Oil drip (~)
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

## Implementation Mapping — Theme to Code

How each theme idea maps to actual edits:

### PRG-ROM changes (SMBDIS.ASM)

| Theme Change | What to Edit | Lines | Complexity |
|-------------|-------------|-------|------------|
| Sand/desert palette | `GroundPaletteData` | 2250 | Easy — swap color bytes |
| Sunset sky for later worlds | `DaySnowPaletteData` or new palette | 2286 | Easy |
| Oasis underground | `UndergroundPaletteData` | 2262 | Easy |
| Najdi castle colors | `CastlePaletteData` | 2274 | Easy |
| "MARIO" → "SAUDI" in HUD | `TopStatusBarLine` | 1637 | Easy — re-encode text |
| "LUIGI" → "KHALID" etc. | `LuigiName` | 1679 | Easy |
| Story messages (princess → ??) | Lines 2306–2362 | 2306 | Easy — re-encode, update length bytes |
| "TIME 2030" easter egg | `TopStatusBarLine` | 1637 | Fun |
| Arabic ؟ on mystery block | Metatile table | 2118 | Medium — need CHR tile too |
| Level layouts (desert feel) | Level data | 4457 | Hard — compressed format |
| Arabic music scales | Music data + freq table | 14994, 16301 | Hard |

### CHR-ROM changes (chr-rom/chr.bin, tile editor)

| Theme Change | CHR-ROM Region | Tile Slots |
|-------------|---------------|------------|
| Saudi Mario (small) | Pattern Table 1 | $00–$1F |
| Saudi Mario (big) | Pattern Table 1 | $20–$5F |
| Date Goomba | Pattern Table 1 | $60–$6F |
| Camel Troopa | Pattern Table 1 | $70–$7F |
| Scorpion (Buzzy Beetle) | Pattern Table 1 | same slot as beetle |
| Falcon (Cheep-Cheep) | Pattern Table 1 | same slot as cheep |
| Sand Snake (Blooper) | Pattern Table 1 | $80–$8F |
| Sheikh Boss (Bowser) | Pattern Table 1 | $C0–$DF |
| Qahwa cup (mushroom) | Pattern Table 1 | $A0–$A7 |
| Oud bottle (fire flower) | Pattern Table 1 | $A8–$AF |
| Dinar coin | Pattern Table 0 | coin tile slot |
| Sand bricks | Pattern Table 0 | $10–$1F |
| Oil pipes | Pattern Table 0 | pipe tile slots |
| Palm trees | Pattern Table 0 | $50–$5F |
| Sand dunes | Pattern Table 0 | hill tile slots |
| Najdi castle | Pattern Table 0 | $80–$BF |
| ؟ block | Pattern Table 0 | ? block tile |
| Title screen "SAUDI MARIO BROS" | Pattern Table 0 | $C0–$FF + $1EC0 nametable |
| Saudi flag (flagpole) | Pattern Table 1 | $E0–$E7 |

---

## Theming Reference Details

### Palettes (lines 2238–2304)

Format: 3-byte PPU address header + groups of 4 NES color indices.

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

### Text (lines 1636–1692, 2306–2362)

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

### Enemy IDs

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
