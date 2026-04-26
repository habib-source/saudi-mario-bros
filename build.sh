#!/bin/bash
set -e

echo "=== Saudi Mario Bros Build ==="

# Step 1: Assemble PRG-ROM
echo "[2/4] Assembling PRG-ROM..."
asm6f smbdis.asm smb_prg.bin
PRG_SIZE=$(stat -c%s smb_prg.bin)
echo "       PRG-ROM size: $PRG_SIZE bytes"

# Step 2: Build the iNES ROM
echo "[3/4] Building iNES ROM..."
mkdir -p output
python3 sprite_tools.py build -p smb_prg.bin -c chr.bin -o output/saudi-mario-bros.nes

echo ""
echo "=== Build complete: output/saudi-mario-bros.nes ==="
echo "    Open in any NES emulator to play."
