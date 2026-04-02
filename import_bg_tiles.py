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


# --- Title tilemap ---
if os.path.exists('title_tilemap.txt'):
    with open('title_tilemap.txt') as f:
        content = f.read()
    title_match = re.search(r'=== CURRENT TITLE: (\w+) ===', content)
    if title_match:
        title_name = title_match.group(1)
        section = content.split(title_match.group(0))[1]
        if '=== BROS.' in section:
            section = section.split('=== BROS.')[0]

        letter_order = []
        current = None
        letter_tiles = {}  # letter -> list of rows, each row is list of tile IDs
        for line in section.split('\n'):
            m = re.match(r'^# ([A-Z]\d?)\s', line.strip())
            if m:
                current = m.group(1)
                letter_order.append(current)
                letter_tiles[current] = []
            elif current and '[0x' in line:
                tiles = [int(h, 16) for h in re.findall(r'\[0x([0-9A-Fa-f]+)\]', line)]
                if tiles:
                    letter_tiles[current].append(tiles)

        if letter_order:
            num_rows = min(len(rows) for rows in letter_tiles.values())
            mario_rows = []
            for row in range(num_rows):
                row_data = []
                for name in letter_order:
                    row_data.extend(letter_tiles[name][row])
                mario_rows.append(row_data)
            mario_width = len(mario_rows[0])

            # --- BROS. section ---
            bros_rows = None
            bros_match = re.search(r'=== BROS\. ===', content)
            if bros_match:
                bros_section = content.split(bros_match.group(0))[1]
                bros_order = []
                current = None
                bros_tiles = {}
                for line in bros_section.split('\n'):
                    m = re.match(r'^# (\S+)\s', line.strip())
                    if m:
                        current = m.group(1)
                        bros_order.append(current)
                        bros_tiles[current] = []
                    elif current and '[0x' in line:
                        tiles = [int(h, 16) for h in re.findall(r'\[0x([0-9A-Fa-f]+)\]', line)]
                        if tiles:
                            bros_tiles[current].append(tiles)
                if bros_order:
                    bros_rows = []
                    for row in range(num_rows):
                        row_data = []
                        for name in bros_order:
                            row_data.extend(bros_tiles[name][row])
                        bros_rows.append(row_data)

            # Parse shadow config: left=0x5F right=0x7A gap=0x78 pad=0x95
            shadow_cfg = {'left': 0x5F, 'right': 0x7A, 'gap': 0x78, 'pad': 0x95}
            cfg_match = re.search(r'Shadow:\s*(.*)', section)
            if cfg_match:
                for k, v in re.findall(r'(\w+)=0x([0-9A-Fa-f]+)', cfg_match.group(1)):
                    shadow_cfg[k] = int(v, 16)

            # Rows 0-4 are letter rows, row 5 is shadow
            num_letter_rows = min(num_rows, 5)

            # Assemble full 20-tile rows: MARIO + space + BROS + pad to 20
            full_rows = []
            for row in range(num_letter_rows):
                full = list(mario_rows[row]) + [0x26]  # MARIO + space
                if bros_rows:
                    full.extend(bros_rows[row])
                while len(full) < 20:
                    full.append(0x26)
                full = full[:20]
                full_rows.append(full)

            # Write letter rows to CHR-ROM
            # All rows are data(20) entries (row 2 was converted from repeat encoding)
            row_offsets = [0x1F1B, 0x1F32, 0x1F49, 0x1F60, 0x1F77]

            for row in range(num_letter_rows):
                tiles = full_rows[row]
                offset = row_offsets[row]
                for j, val in enumerate(tiles):
                    chrdata[offset + j] = val

            # Assemble shadow row (row 5) from letter row 5 tiles
            if num_rows >= 6:
                shadow_mid = list(mario_rows[5]) + [shadow_cfg['gap']]
                if bros_rows:
                    shadow_mid.extend(bros_rows[5])
                while len(shadow_mid) < 20:
                    shadow_mid.append(shadow_cfg['pad'])
                shadow_mid = shadow_mid[:20]
                shadow_full = [shadow_cfg['left']] + shadow_mid + [shadow_cfg['right']]
                for j, val in enumerate(shadow_full[:22]):
                    chrdata[0x1F8E + j] = val

            bros_info = f' + BROS. ({" ".join(bros_order)})' if bros_rows else ''
            print(f'Imported title_tilemap.txt MARIO ({" ".join(letter_order)}){bros_info}')

    # --- SUPER section ---
    super_match = re.search(r'=== SUPER ===', content)
    if super_match:
        super_section = content.split(super_match.group(0))[1]
        if '===' in super_section:
            super_section = super_section.split('===')[0]
        super_order = []
        current = None
        super_tiles = {}
        for line in super_section.split('\n'):
            m = re.match(r'^# ([A-Z])\s', line.strip())
            if m:
                current = m.group(1)
                super_order.append(current)
                super_tiles[current] = []
            elif current and '[0x' in line:
                tiles = [int(h, 16) for h in re.findall(r'\[0x([0-9A-Fa-f]+)\]', line)]
                if tiles:
                    super_tiles[current].append(tiles)
        if super_order:
            super_offsets = [0x1EE7, 0x1EF4, 0x1F01, 0x1F0E]
            num_rows = min(len(rows) for rows in super_tiles.values())
            for row in range(min(num_rows, 4)):
                row_data = []
                for name in super_order:
                    row_data.extend(super_tiles[name][row])
                for j, val in enumerate(row_data[:10]):
                    chrdata[super_offsets[row] + j] = val
            print(f'Imported title_tilemap.txt SUPER ({" ".join(super_order)})')



with open(CHR_PATH, 'wb') as f:
    f.write(chrdata)
