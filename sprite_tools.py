#!/usr/bin/env python3
"""
Sprite tools for Saudi Mario Bros CHR-ROM editing.
Usage:
  python3 sprite_tools.py export   - Export all Mario frames as ASCII art to mario_sprites.txt
  python3 sprite_tools.py thobe    - Fill transparent pixels between legs with thobe color
  python3 sprite_tools.py import   - Import mario_sprites.txt back into chr-rom/chr.bin
"""
import sys, os, copy

CHR_PATH = "chr-rom/chr.bin"
EXPORT_PATH = "mario_sprites.txt"

# Color symbols: . = transparent, # = color1, @ = color2, O = color3
SYM = ['.', '#', '@', 'O']
SYM_TO_COLOR = {'.': 0, '#': 1, '@': 2, 'O': 3}

SPRITE_TABLE = 0  # SMB uses pattern table 0 for sprites (PPU_CTRL bit3=0, bit4=1)

def read_chr():
    with open(CHR_PATH, "rb") as f:
        return bytearray(f.read())

def write_chr(data):
    with open(CHR_PATH, "wb") as f:
        f.write(data)

def get_tile(data, table, tile_num):
    """Read 8x8 tile as 2D array of color indices (0-3)."""
    offset = table * 4096 + tile_num * 16
    pixels = []
    for y in range(8):
        row = []
        p0 = data[offset + y]
        p1 = data[offset + y + 8]
        for x in range(8):
            bit = 7 - x
            color = ((p0 >> bit) & 1) | (((p1 >> bit) & 1) << 1)
            row.append(color)
        pixels.append(row)
    return pixels

def set_tile(data, table, tile_num, pixels):
    """Write 8x8 tile from 2D array of color indices back to CHR data."""
    offset = table * 4096 + tile_num * 16
    for y in range(8):
        p0 = 0
        p1 = 0
        for x in range(8):
            bit = 7 - x
            color = pixels[y][x]
            p0 |= ((color & 1) << bit)
            p1 |= (((color >> 1) & 1) << bit)
        data[offset + y] = p0
        data[offset + y + 8] = p1

def hflip_tile(tile):
    """Horizontally flip an 8x8 tile."""
    return [row[::-1] for row in tile]

# Frames that have right-sprite-flipped on specific rows (from ChkForPlayerAttrib)
# Format: frame_name -> set of row indices (0-based) where right tile is h-flipped
# ChkForPlayerAttrib flips row 3 right sprite for: crouch($50), stand($b8), grow-mid($c0,$c8)
# It flips rows 2+3 right sprite for: killed($0b game engine routine)
# Additionally, when same tile ID appears for left and right, the right is always flipped.
HFLIP_RIGHT = {
    "BIG_STAND":   {2, 3},    # $4a,$4a and $4b,$4b
    "BIG_CROUCH":  {3},       # $5a,$5a
    "SMALL_STAND": {1},       # $4f,$4f
    "SMALL_DEAD":  {0, 1},    # $9e,$9e and $9f,$9f
    "GROW_MID":    {3},       # $4e,$4e
}

# All Mario frames with their tile IDs
FRAMES = {
    "BIG_WALK1":    [0x00,0x01, 0x02,0x03, 0x04,0x05, 0x06,0x07],
    "BIG_WALK2":    [0x08,0x09, 0x0a,0x0b, 0x0c,0x0d, 0x0e,0x0f],
    "BIG_WALK3":    [0x10,0x11, 0x12,0x13, 0x14,0x15, 0x16,0x17],
    "BIG_SKID":     [0x18,0x19, 0x1a,0x1b, 0x1c,0x1d, 0x1e,0x1f],
    "BIG_JUMP":     [0x20,0x21, 0x22,0x23, 0x24,0x25, 0x26,0x27],
    "BIG_SWIM1":    [0x08,0x09, 0x28,0x29, 0x2a,0x2b, 0x2c,0x2d],
    "BIG_SWIM2":    [0x08,0x09, 0x0a,0x0b, 0x0c,0x30, 0x2c,0x2d],
    "BIG_SWIM3":    [0x08,0x09, 0x0a,0x0b, 0x2e,0x2f, 0x2c,0x2d],
    "BIG_CLIMB1":   [0x08,0x09, 0x28,0x29, 0x2a,0x2b, 0x5c,0x5d],
    "BIG_CLIMB2":   [0x08,0x09, 0x0a,0x0b, 0x0c,0x0d, 0x5e,0x5f],
    "BIG_CROUCH":   [0xfc,0xfc, 0x08,0x09, 0x58,0x59, 0x5a,0x5a],
    "BIG_THROW":    [0x08,0x09, 0x28,0x29, 0x2a,0x2b, 0x0e,0x0f],
    "BIG_STAND":    [0x00,0x01, 0x4c,0x4d, 0x4a,0x4a, 0x4b,0x4b],
    "SMALL_WALK1":  [0xfc,0xfc, 0xfc,0xfc, 0x32,0x33, 0x34,0x35],
    "SMALL_WALK2":  [0xfc,0xfc, 0xfc,0xfc, 0x36,0x37, 0x38,0x39],
    "SMALL_WALK3":  [0xfc,0xfc, 0xfc,0xfc, 0x3a,0x37, 0x3b,0x3c],
    "SMALL_SKID":   [0xfc,0xfc, 0xfc,0xfc, 0x3d,0x3e, 0x3f,0x40],
    "SMALL_JUMP":   [0xfc,0xfc, 0xfc,0xfc, 0x32,0x41, 0x42,0x43],
    "SMALL_SWIM1":  [0xfc,0xfc, 0xfc,0xfc, 0x32,0x33, 0x44,0x45],
    "SMALL_SWIM2":  [0xfc,0xfc, 0xfc,0xfc, 0x32,0x33, 0x44,0x47],
    "SMALL_SWIM3":  [0xfc,0xfc, 0xfc,0xfc, 0x32,0x33, 0x48,0x49],
    "SMALL_CLIMB1": [0xfc,0xfc, 0xfc,0xfc, 0x32,0x33, 0x90,0x91],
    "SMALL_CLIMB2": [0xfc,0xfc, 0xfc,0xfc, 0x3a,0x37, 0x92,0x93],
    "SMALL_DEAD":   [0xfc,0xfc, 0xfc,0xfc, 0x9e,0x9e, 0x9f,0x9f],
    "SMALL_STAND":  [0xfc,0xfc, 0xfc,0xfc, 0x3a,0x37, 0x4f,0x4f],
    "GROW_MID":     [0xfc,0xfc, 0x00,0x01, 0x4c,0x4d, 0x4e,0x4e],
}

def get_flip_rows(name, tile_ids):
    """Determine which rows have the right tile h-flipped.
    Uses explicit HFLIP_RIGHT table, plus auto-detects when same tile ID
    appears for both left and right in a row."""
    cols = 2
    rows_of_tiles = [tile_ids[i:i+cols] for i in range(0, len(tile_ids), cols)]
    flip_rows = set()

    # Explicit flips from ChkForPlayerAttrib
    if name in HFLIP_RIGHT:
        # Convert to absolute row index (accounting for leading $fc rows)
        first_real = 0
        for i, row in enumerate(rows_of_tiles):
            if row[0] != 0xfc or row[1] != 0xfc:
                first_real = i
                break
        for rel_row in HFLIP_RIGHT[name]:
            flip_rows.add(first_real + rel_row)

    # Auto-detect: same tile used for left and right (always flipped)
    for i, row in enumerate(rows_of_tiles):
        if row[0] == row[1] and row[0] != 0xfc:
            flip_rows.add(i)

    return flip_rows

def compose_frame(data, tile_ids, name="", cols=2):
    """Compose multiple tiles into a frame, applying h-flip where needed."""
    rows_of_tiles = [tile_ids[i:i+cols] for i in range(0, len(tile_ids), cols)]
    flip_rows = get_flip_rows(name, tile_ids)
    frame = []
    for row_idx, tile_row in enumerate(rows_of_tiles):
        for y in range(8):
            row = []
            for col_idx, tid in enumerate(tile_row):
                if tid == 0xfc:
                    row.extend([0]*8)
                else:
                    tile = get_tile(data, SPRITE_TABLE, tid)
                    # Flip right tile if this row is flagged
                    if col_idx == 1 and row_idx in flip_rows:
                        tile = hflip_tile(tile)
                    row.extend(tile[y])
            frame.append(row)
    return frame

def decompose_frame(frame, tile_ids, name="", cols=2):
    """Decompose a frame back into individual tile pixel arrays.
    Un-flips right tiles that were flipped during export.
    Returns dict {tile_id: pixels}."""
    tiles = {}
    rows_of_tiles = [tile_ids[i:i+cols] for i in range(0, len(tile_ids), cols)]
    flip_rows = get_flip_rows(name, tile_ids)
    tile_row_idx = 0
    for row_idx, tile_row in enumerate(rows_of_tiles):
        for col_idx, tid in enumerate(tile_row):
            if tid == 0xfc:
                continue
            pixels = []
            for y in range(8):
                frame_y = row_idx * 8 + y
                frame_x = col_idx * 8
                pixels.append(frame[frame_y][frame_x:frame_x+8])
            # Un-flip right tile if it was flipped during export
            if col_idx == 1 and row_idx in flip_rows:
                pixels = hflip_tile(pixels)
            # For duplicate tiles (same left+right), only store once (left version)
            if tid not in tiles:
                tiles[tid] = pixels
        tile_row_idx += 1
    return tiles

def frame_to_ascii(frame):
    lines = []
    for row in frame:
        lines.append("".join(SYM[c] for c in row))
    return lines

def ascii_to_frame(lines):
    frame = []
    for line in lines:
        row = [SYM_TO_COLOR.get(c, 0) for c in line.strip()]
        frame.append(row)
    return frame

def get_shared_frames():
    """Build map: for each frame, which other frames share tiles with it."""
    # tile_id -> list of frame names that use it
    tile_to_frames = {}
    for name, tiles in FRAMES.items():
        for tid in tiles:
            if tid == 0xfc:
                continue
            if tid not in tile_to_frames:
                tile_to_frames[tid] = []
            if name not in tile_to_frames[tid]:
                tile_to_frames[tid].append(name)

    # frame -> set of other frames that share tiles
    shared = {}
    for name, tiles in FRAMES.items():
        others = set()
        for tid in tiles:
            if tid == 0xfc:
                continue
            for other in tile_to_frames[tid]:
                if other != name:
                    others.add(other)
        shared[name] = sorted(others)
    return shared

def cmd_export():
    data = read_chr()
    shared = get_shared_frames()
    with open(EXPORT_PATH, "w") as f:
        f.write("# Mario Sprite Frames - Saudi Mario Bros\n")
        f.write("# Legend: . = transparent  # = color1 (black/iqal)  @ = color2 (skin)  O = color3 (white/thobe)\n")
        f.write("# Edit pixels below, then run: python3 sprite_tools.py import\n")
        f.write("# H-flip is applied where the game mirrors tiles (e.g. symmetric legs in standing pose).\n")
        f.write(f"# Palette: color1=$0f(black)  color2=$27(skin)  color3=$30(white)\n")
        f.write("\n")
        for name, tiles in FRAMES.items():
            frame = compose_frame(data, tiles, name)
            ascii_lines = frame_to_ascii(frame)
            height = "32" if tiles[0] != 0xfc or tiles[2] != 0xfc else "16"
            updates = shared.get(name, [])
            if updates:
                update_str = ", ".join(updates)
                f.write(f"=== {name} ({height}px) [ ] updates: {update_str} ===\n")
            else:
                f.write(f"=== {name} ({height}px) ===\n")
            for line in ascii_lines:
                f.write(line + "\n")
            f.write("\n")
    print(f"Exported {len(FRAMES)} frames to {EXPORT_PATH}")

def cmd_import():
    data = read_chr()
    with open(EXPORT_PATH, "r") as f:
        content = f.read()

    # Parse frames from the file
    import re
    header_re = re.compile(r'^=== (\w+) \((\d+)px\)(.*) ===$')
    frames_data = {}
    priority_frames = set()  # frames marked [x] take precedence
    current_name = None
    current_lines = []
    for line in content.split("\n"):
        m = header_re.match(line)
        if m:
            if current_name and current_lines:
                frames_data[current_name] = current_lines
            current_name = m.group(1)
            rest = m.group(3)
            if "[x]" in rest.lower():
                priority_frames.add(current_name)
            current_lines = []
        elif current_name and line and not line.startswith("#"):
            stripped = line.strip()
            if len(stripped) == 16 and all(c in '.#@O' for c in stripped):
                current_lines.append(line)
    if current_name and current_lines:
        frames_data[current_name] = current_lines

    # Two passes: first non-priority, then priority (so [x] frames overwrite)
    written_tiles = set()
    for do_priority in [False, True]:
        for name, tiles in FRAMES.items():
            if name not in frames_data:
                continue
            is_priority = name in priority_frames
            if do_priority != is_priority:
                continue
            expected_rows = len(tiles) // 2 * 8
            if len(frames_data[name]) != expected_rows:
                print(f"WARNING: {name} has {len(frames_data[name])} lines, expected {expected_rows} — skipping")
                continue
            frame = ascii_to_frame(frames_data[name])
            tile_pixels = decompose_frame(frame, tiles, name)
            for tid, pixels in tile_pixels.items():
                if tid not in written_tiles or is_priority:
                    set_tile(data, SPRITE_TABLE, tid, pixels)
                    written_tiles.add(tid)

    print(f"Priority frames: {sorted(priority_frames) if priority_frames else 'none'}")

    write_chr(data)
    print(f"Imported {len(written_tiles)} unique tiles from {EXPORT_PATH}")

def cmd_thobe():
    """Fill transparent pixels between Mario's legs with thobe color (color 3 = white)."""
    data = read_chr()
    THOBE_COLOR = 3  # color 3 = white

    leg_tile_pairs = [
        (0x06, 0x07),  (0x0e, 0x0f),  (0x16, 0x17),
        (0x1e, 0x1f),  (0x26, 0x27),  (0x4b, 0x4b),
        (0x04, 0x05),  (0x0c, 0x0d),  (0x14, 0x15),
        (0x1c, 0x1d),  (0x24, 0x25),  (0x4a, 0x4a),
        (0x34, 0x35),  (0x38, 0x39),  (0x3b, 0x3c),
        (0x3f, 0x40),  (0x42, 0x43),  (0x4f, 0x4f),
    ]

    modified_tiles = set()
    for left_tid, right_tid in leg_tile_pairs:
        left = get_tile(data, SPRITE_TABLE, left_tid)
        right = get_tile(data, SPRITE_TABLE, right_tid)
        # If same tile, flip right for correct spatial layout
        if left_tid == right_tid:
            right = hflip_tile(copy.deepcopy(right))

        changed = False
        for y in range(8):
            full_row = left[y] + right[y]
            non_transparent = [x for x in range(16) if full_row[x] != 0]
            if len(non_transparent) < 2:
                continue
            leftmost = non_transparent[0]
            rightmost = non_transparent[-1]
            for x in range(leftmost, rightmost + 1):
                if full_row[x] == 0:
                    full_row[x] = THOBE_COLOR
                    changed = True
            left[y] = full_row[:8]
            right[y] = full_row[8:]

        if changed:
            set_tile(data, SPRITE_TABLE, left_tid, left)
            if left_tid == right_tid:
                # Un-flip before writing back
                right = hflip_tile(right)
            set_tile(data, SPRITE_TABLE, right_tid, right)
            modified_tiles.add(left_tid)
            modified_tiles.add(right_tid)

    write_chr(data)
    print(f"Thobe applied: modified {len(modified_tiles)} tiles")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 sprite_tools.py [export|import|thobe]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "export":
        cmd_export()
    elif cmd == "import":
        cmd_import()
    elif cmd == "thobe":
        cmd_thobe()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
