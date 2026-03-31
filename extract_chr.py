#!/usr/bin/env python3
"""
Extracts CHR-ROM (8 KB) from an original Super Mario Bros .nes ROM.
Usage: python3 extract_chr.py <path_to_smb.nes>

The extracted chr.bin is used during the build to provide tile graphics.
"""
import sys
import os

INES_HEADER_SIZE = 16
PRG_ROM_SIZE = 32768  # 32 KB for SMB
CHR_ROM_SIZE = 8192   # 8 KB for SMB

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_smb.nes>")
        sys.exit(1)

    rom_path = sys.argv[1]
    with open(rom_path, "rb") as f:
        data = f.read()

    # Verify iNES header
    if data[:4] != b'NES\x1a':
        print("ERROR: Not a valid iNES ROM file", file=sys.stderr)
        sys.exit(1)

    prg_banks = data[4]
    chr_banks = data[5]
    print(f"ROM: {prg_banks} PRG banks, {chr_banks} CHR banks")

    chr_offset = INES_HEADER_SIZE + (prg_banks * 16384)
    chr_data = data[chr_offset:chr_offset + CHR_ROM_SIZE]

    if len(chr_data) < CHR_ROM_SIZE:
        print(f"WARNING: CHR data is only {len(chr_data)} bytes", file=sys.stderr)

    os.makedirs("chr-rom", exist_ok=True)
    output_path = "chr-rom/chr.bin"
    with open(output_path, "wb") as f:
        f.write(chr_data)

    print(f"Extracted {len(chr_data)} bytes of CHR-ROM to {output_path}")

if __name__ == "__main__":
    main()
