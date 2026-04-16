#!/usr/bin/env python3
"""
Sprite tools for Saudi Mario Bros CHR-ROM editing.
Usage:
  python3 sprite_tools.py export   - Export all Mario frames as ASCII art to mario_sprites.txt
  python3 sprite_tools.py thobe    - Fill transparent pixels between legs with thobe color
  python3 sprite_tools.py import   - Import mario_sprites.txt back into chr-rom/chr.bin
"""
import argparse, re
from pathlib import Path
from collections import defaultdict


# Color symbols: . = transparent, # = color1, @ = color2, O = color3
SYM = ['.', '#', '@', 'O']

SPRITE_TABLE = 0  # SMB uses pattern table 0 for sprites (PPU_CTRL bit3=0, bit4=1)
EMPTY_CODE=0xfc
# Frames that have right-sprite-flipped on specific rows (from ChkForPlayerAttrib)
# Format: frame_name -> set of row indices (0-based) where right tile is h-flipped
# ChkForPlayerAttrib flips row 3 right sprite for: crouch($50), stand($b8), grow-mid($c0,$c8)
# It flips rows 2+3 right sprite for: killed($0b game engine routine)
# Additionally, when same tile ID appears for left and right, the right is always flipped.

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

HEADER = (
    "# Mario Sprite Frames - Saudi Mario Bros\n"
    "# Legend: . = transparent  # = color1 (black/iqal)  @ = color2 (skin)  O = color3 (white/thobe)\n"
    "# Edit pixels below, then run: python3 sprite_tools.py import\n"
    "# H-flip is applied where the game mirrors tiles (e.g. symmetric legs in standing pose).\n"
    "# Palette: color1=$0f(black)  color2=$27(skin)  color3=$30(white)\n\n"
)

def read_chr(b):
    with b.open("rb") as f:
        return bytearray(f.read())

def write_chr(data, b):
    with b.open("wb") as f:
        f.write(data)

def get_tile(data, tile_num, size, table):
    """Read 8x8 tile as 2D array of color indices (0-3)."""
    offset = table * 4096 + tile_num * 16
    for y in range(size[1]):
        row = []
        p0 = data[offset + y]
        p1 = data[offset + y + size[1]]
        for bit in range(size[0]-1,-1,-1):
            color = ((p0 >> bit) & 1) | (((p1 >> bit) & 1) << 1)
            row.append(color)
        yield row

def set_tile(data, tile_num, pixels, size, table):
    """Write 8x8 tile from 2D array of color indices back to CHR data."""
    offset = table * 4096 + tile_num * 16
    for y in range(size[0]):
        p0 = 0
        p1 = 0
        for x in range(size[1]):
            bit = size[1]-1 - x
            color = pixels[y][x]
            p0 |= ((color & 1) << bit)
            p1 |= (((color >> 1) & 1) << bit)
        data[offset + y] = p0
        data[offset + y + size[1]] = p1

def compose_frame(data, tile_ids, size=[8,8], empty_code=EMPTY_CODE, cols=2, sprite_table=SPRITE_TABLE):
    """Compose multiple tiles into a frame, applying h-flip where needed."""
    rows_of_tiles = [tile_ids[i:i+cols] for i in range(0, len(tile_ids), cols)]
    frame = []
    for tile_row in rows_of_tiles:
        if tile_row[0]==empty_code:
            frame.extend([[0]*size[1]*2]*size[0])
        tile1 = get_tile(data, tile_row[0], size, sprite_table)
        if tile_row[0]!=empty_code and tile_row[0]==tile_row[1]:
            frame.extend([row + row[::-1] for row in tile1])
        else:
            tile2 = get_tile(data, tile_row[1], size, sprite_table)
            frame.extend([row_a + row_b for row_a, row_b in zip(tile1, tile2)])
    return frame

def decompose_frame(frame, tile_ids, cols=2, empty_code=EMPTY_CODE):
    """Decompose a frame back into individual tile pixel arrays.
    Returns dict {tile_id: pixels}."""
    tiles = {}
    rows_of_tiles = [tile_ids[i:i+cols] for i in range(0, len(tile_ids), cols)]
    for row_idx, tile_row in enumerate(rows_of_tiles):
        if tile_row[0] == empty_code:
            continue
        pixels1 = []
        for y in range(8):
            frame_y = row_idx * 8 + y
            frame_x = 0
            pixels1.append(frame[frame_y][frame_x:frame_x+8])
        if tile_row[0] not in tiles:
            tiles[tile_row[0]] = pixels1
        # Un-flip right tile if it was flipped during export
        if tile_row[0]!=tile_row[1]:
            pixels2 = []
            for y in range(8):
                frame_y = row_idx * 8 + y
                frame_x = 8
                pixels2.append(frame[frame_y][frame_x:frame_x+8])
            if tile_row[1] not in tiles:
                tiles[tile_row[1]] = pixels2
    return tiles

def frame_to_ascii(frame, ascii_colors=SYM):
    lines = []
    for row in frame:
        lines.append("".join(ascii_colors[c] for c in row)+"\n")
    return lines

def ascii_to_frame(lines, ascii_colors=SYM):
    frame = []
    for line in lines:
        row = [ascii_colors.index(c) for c in line.strip()]
        frame.append(row)
    return frame

def get_shared_frames(empty_code=EMPTY_CODE):
    """Build map: for each frame, which other frames share tiles with it."""
    tile_to_frames = defaultdict(set)

    for name, tiles in FRAMES.items():
        for tid in tiles:
            if tid != empty_code: # Skip empty/transparent tiles
                tile_to_frames[tid].add(name)

    shared = {}
    for name, tiles in FRAMES.items():
        others = set()
        for tid in tiles:
            if tid != empty_code:
                # Union the sets of frames sharing this tile, then remove self
                others.update(tile_to_frames[tid])

        others.discard(name)
        shared[name] = sorted(others)

    return shared

def cmd_export(args, frames=FRAMES, header=HEADER, tile_size=[8,8], empty_code=EMPTY_CODE):
    data = read_chr(args.b)
    shared = get_shared_frames()
    output_lines = [header]
    for name, tiles in frames.items():
        frame = compose_frame(data, tiles)
        ascii_lines = frame_to_ascii(frame)
        height = tile_size[0]*(len(tiles)//2-2) if tiles[0] == empty_code and tiles[2] == empty_code else tile_size[0]*(len(tiles)//2)
        updates = shared.get(name, [])
        update_info = f" [ ] updates: {', '.join(updates)}" if updates else ""
        output_lines.append(f"=== {name} ({height}px){update_info} ===\n")
        output_lines.extend(ascii_lines)
        output_lines.append("\n")
    with args.f.open("w") as f:
        f.write("".join(output_lines))
    print(f"Exported {len(frames)} frames to {str(args.f)}")

def cmd_import(args, frames=FRAMES, frame_size=[16,32], tile_size=[8,8], ascii_colors=SYM, sprite_table=SPRITE_TABLE):
    data = read_chr(args.b)
    with args.f.open() as f:
        content = f.read()

    # Parse frames from the file
    header_re = re.compile(r'^=== (\w+) \((\d+)px\)(.*) ===$')
    frames_data = {}
    priority_frames = set()  # frames marked [x] take precedence
    current_name = None
    current_lines = []
    for line in content.split("\n"):
        m = header_re.match(line)
        if m:
            if current_name and len(current_lines)==frame_size[1]:
                frames_data[current_name] = ascii_to_frame(current_lines)
            elif current_name:
                print(f"WARNING: {current_name} has {len(current_lines)} lines, expected {frame_size[1]} — skipping")
            current_name = m.group(1)
            rest = m.group(3)
            if "[x]" in rest.lower():
                priority_frames.add(current_name)
            current_lines = []
        elif current_name and line:
            stripped = line.strip()
            if len(stripped) == frame_size[0] and all(c in ascii_colors for c in stripped):
                current_lines.append(line)
    if current_name and len(current_lines)==frame_size[1]:
        frames_data[current_name] = ascii_to_frame(current_lines)
    elif current_name:
        print(f"WARNING: {current_name} has {len(current_lines)} lines, expected {frame_size[1]} — skipping")

    if not priority_frames and not args.a:
        print("No frames marked with [x] — skipping import.")
        return
    print(f"Priority frames: {sorted(priority_frames)}")

    # Only import frames marked with [x]
    written_tiles = set()
    for name, tiles in frames.items():
        if name not in frames_data or name not in priority_frames and not args.a:
            continue
        tile_pixels = decompose_frame(frames_data[name], tiles)
        for tid, pixels in tile_pixels.items():
            set_tile(data, tid, pixels, tile_size, sprite_table)
            written_tiles.add(tid)

    write_chr(data, args.b)
    print(f"Imported {len(written_tiles)} unique tiles from {str(args.f)}")


def isfile(file):
    path = Path(file)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"'{str(file)}' Does not exist.")
    return path

def main():
    parser = argparse.ArgumentParser(
         prog='sprit',
         description='Sprite tools for Saudi Mario Bros CHR-ROM editing.',
    )
    actionParser = parser.add_subparsers(
         required=True,
         title='SubCommand',
         description='Export, Import or thobe Mario sprite.',
    )

    pexport= actionParser.add_parser(
         'export',
         help='Export all Mario frames as ASCII art to a file from the SBM binary',
    )
    pexport.add_argument('-f', type=Path, required=True, help='sprite file path.')
    pexport.add_argument('-b', type=isfile, required=True , help='Mario binary path.')
    pexport.set_defaults(func=cmd_export)

    pimport = actionParser.add_parser(
         'import',
         help='Import mario sprite frames back into the binary',
    )
    pimport.add_argument('-f', type=isfile, required=True, help='sprite file path.')
    pimport.add_argument('-b', type=isfile, required=True , help='Mario binary path.')
    pimport.add_argument('-a', action='store_true', help='import all frames. (by deafault import only x marked priority frames)')
    pimport.set_defaults(func=cmd_import)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
