#!/usr/bin/env python3
"""
Builds a complete iNES (.nes) ROM from assembled PRG-ROM and CHR-ROM data.

Super Mario Bros uses mapper 0 (NROM):
- 32 KB PRG-ROM (1 bank)
- 8 KB CHR-ROM (1 bank)
- Vertical mirroring
"""
import os
import sys

PRG_ROM_SIZE = 32768  # 32 KB
CHR_ROM_SIZE = 8192   # 8 KB
OUTPUT = "saudi-mario-bros.nes"

def make_ines_header(prg_banks=1, chr_banks=1, mapper=0, mirroring=1):
    """Create a 16-byte iNES header.
    mirroring: 0=horizontal, 1=vertical
    """
    header = bytearray(16)
    header[0:4] = b'NES\x1a'       # Magic number
    header[4] = prg_banks           # PRG-ROM banks (16 KB each) — SMB uses 2 (=32KB)
    header[5] = chr_banks           # CHR-ROM banks (8 KB each)
    header[6] = (mapper << 4) | mirroring  # Flags 6
    header[7] = mapper & 0xF0              # Flags 7
    return bytes(header)

def main():
    # Read assembled PRG-ROM
    if not os.path.exists("smb_prg.bin"):
        print("ERROR: smb_prg.bin not found. Assembly failed?", file=sys.stderr)
        sys.exit(1)

    with open("smb_prg.bin", "rb") as f:
        prg_data = f.read()

    print(f"  PRG-ROM: {len(prg_data)} bytes")

    # Pad or trim PRG to exactly 32 KB
    if len(prg_data) < PRG_ROM_SIZE:
        print(f"  Padding PRG-ROM from {len(prg_data)} to {PRG_ROM_SIZE} bytes")
        prg_data = prg_data + b'\xff' * (PRG_ROM_SIZE - len(prg_data))
    elif len(prg_data) > PRG_ROM_SIZE:
        print(f"  WARNING: PRG-ROM is {len(prg_data)} bytes, expected {PRG_ROM_SIZE}", file=sys.stderr)
        prg_data = prg_data[:PRG_ROM_SIZE]

    # Look for CHR-ROM data
    chr_data = None
    chr_sources = ["chr-rom/chr.bin", "chr-rom/smb.chr", "chr.bin", "smb.chr"]
    for path in chr_sources:
        if os.path.exists(path):
            with open(path, "rb") as f:
                chr_data = f.read()
            print(f"  CHR-ROM: {len(chr_data)} bytes (from {path})")
            break

    if chr_data is None:
        print("  CHR-ROM: not found — generating blank 8 KB placeholder")
        print("  NOTE: To get proper graphics, extract CHR-ROM from an original SMB ROM:")
        print("        python3 extract_chr.py original_smb.nes")
        chr_data = b'\x00' * CHR_ROM_SIZE

    # Pad CHR to exactly 8 KB
    if len(chr_data) < CHR_ROM_SIZE:
        chr_data = chr_data + b'\x00' * (CHR_ROM_SIZE - len(chr_data))
    elif len(chr_data) > CHR_ROM_SIZE:
        chr_data = chr_data[:CHR_ROM_SIZE]

    # SMB = 32 KB PRG = 2 x 16 KB banks
    header = make_ines_header(prg_banks=2, chr_banks=1, mapper=0, mirroring=1)

    with open(OUTPUT, "wb") as f:
        f.write(header)
        f.write(prg_data)
        f.write(chr_data)

    total = len(header) + len(prg_data) + len(chr_data)
    print(f"  Output: {OUTPUT} ({total} bytes)")

if __name__ == "__main__":
    main()
