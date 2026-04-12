#!/bin/bash
set -e

echo "=== Saudi Mario Bros Build ==="

# Step 1: Patch SMBDIS.ASM for asm6f compatibility
# asm6f doesn't support x816's .index/.mem directives
echo "[1/4] Preparing source for asm6f..."
sed \
    -e 's/^[[:space:]]*\.index 8/;.index 8  ; removed for asm6f/' \
    -e 's/^[[:space:]]*\.mem 8/;.mem 8    ; removed for asm6f/' \
    SMBDIS.ASM > smb_asm6f.asm

# Step 2: Assemble PRG-ROM
echo "[2/4] Assembling PRG-ROM..."
asm6f smb_asm6f.asm smb_prg.bin
PRG_SIZE=$(stat -c%s smb_prg.bin)
echo "       PRG-ROM size: $PRG_SIZE bytes"

# Step 3: Build the iNES ROM
echo "[3/4] Building iNES ROM..."
python3 build_rom.py

# Step 4: Copy to output
echo "[4/4] Copying to output..."
mkdir -p output
cp saudi-mario-bros.nes output/
echo ""
echo "=== Build complete: output/saudi-mario-bros.nes ==="
echo "    Open in any NES emulator to play."
