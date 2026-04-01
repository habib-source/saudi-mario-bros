#!/usr/bin/env python3
"""Import background tile edits into chr-rom/chr.bin.

Imports:
  - question_block.txt -> tiles $53,$54,$55,$56 in Pattern Table 1
  - title_tilemap.txt  -> VRAM buffer at $1EC0 (SAUDI title letter IDs)
"""
import re, os

CHR_PATH = 'chr-rom/chr.bin'
PT1 = 4096
CHAR_TO_VAL = {'.': 0, '#': 1, '@': 2, 'O': 3}

with open(CHR_PATH, 'rb') as f:
    chrdata = bytearray(f.read())


def write_tile(tile_idx, pixels):
    offset = PT1 + tile_idx * 16
    for y in range(8):
        p0 = p1 = 0
        for x in range(8):
            v = pixels[y][7 - x]
            p0 |= (v & 1) << x
            p1 |= ((v >> 1) & 1) << x
        chrdata[offset + y] = p0
        chrdata[offset + y + 8] = p1


# --- Question block ---
if os.path.exists('question_block.txt'):
    with open('question_block.txt') as f:
        grid = [l.strip() for l in f if len(l.strip()) == 16 and all(c in '.#@O' for c in l.strip())]
    if len(grid) == 16:
        tile_map = {0x53: (0,0), 0x54: (0,8), 0x55: (8,0), 0x56: (8,8)}
        for tid, (ry, rx) in tile_map.items():
            pixels = [[CHAR_TO_VAL[grid[ry+y][rx+x]] for x in range(8)] for y in range(8)]
            write_tile(tid, pixels)
        print('Imported question_block.txt')


# --- Title tilemap (SAUDI) ---
if os.path.exists('title_tilemap.txt'):
    with open('title_tilemap.txt') as f:
        content = f.read()
    if '=== CURRENT TITLE: SAUDI ===' in content:
        section = content.split('=== CURRENT TITLE: SAUDI ===')[1]
        if '=== MARIO BROS' in section:
            section = section.split('=== MARIO BROS')[0]

        saudi_order = []
        current = None
        letter_tiles = {}
        for line in section.split('\n'):
            m = re.match(r'^# ([A-Z]\d?)$', line.strip())
            if m:
                current = m.group(1)
                saudi_order.append(current)
                letter_tiles[current] = []
            elif current and '[0x' in line:
                pairs = re.findall(r'\[0x([0-9A-Fa-f]+)\]', line)
                if len(pairs) == 2:
                    letter_tiles[current].append((int(pairs[0], 16), int(pairs[1], 16)))

        if saudi_order:
            offsets = [0x1EE7, 0x1EF4, 0x1F01, 0x1F0E]
            for row in range(4):
                row_data = []
                for name in saudi_order:
                    tl, tr = letter_tiles[name][row]
                    row_data.extend([tl, tr])
                for j, val in enumerate(row_data):
                    chrdata[offsets[row] + j] = val
            print(f'Imported title_tilemap.txt ({" ".join(saudi_order)})')


with open(CHR_PATH, 'wb') as f:
    f.write(chrdata)
