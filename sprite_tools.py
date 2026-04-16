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

import config

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

def compose_frame(data, tile_ids, size=[8,8], empty_code=config.EMPTY_CODE, cols=2, sprite_table=config.SPRITE_TABLE):
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

def decompose_frame(frame, tile_ids, cols=2, empty_code=config.EMPTY_CODE):
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

def frame_to_ascii(frame, ascii_colors=config.SYM):
    lines = []
    for row in frame:
        lines.append("".join(ascii_colors[c] for c in row)+"\n")
    return lines

def ascii_to_frame(lines, ascii_colors=config.SYM):
    frame = []
    for line in lines:
        row = [ascii_colors.index(c) for c in line.strip()]
        frame.append(row)
    return frame

def get_shared_frames(empty_code=config.EMPTY_CODE):
    """Build map: for each frame, which other frames share tiles with it."""
    tile_to_frames = defaultdict(set)

    for name, tiles in config.FRAMES.items():
        for tid in tiles:
            if tid != empty_code: # Skip empty/transparent tiles
                tile_to_frames[tid].add(name)

    shared = {}
    for name, tiles in config.FRAMES.items():
        others = set()
        for tid in tiles:
            if tid != empty_code:
                # Union the sets of frames sharing this tile, then remove self
                others.update(tile_to_frames[tid])

        others.discard(name)
        shared[name] = sorted(others)

    return shared

def cmd_export(args, frames=config.FRAMES, header=config.HEADER, tile_size=[8,8], empty_code=config.EMPTY_CODE):
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

def cmd_import(args, frames=config.FRAMES, frame_size=[16,32], tile_size=[8,8], ascii_colors=config.SYM, sprite_table=config.SPRITE_TABLE):
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
