#!/bin/bash
set -e
rm -rf __pycache__
rm -f fceux/snaps/*
docker run --rm -v "C:\Users\a\Desktop\dev\saudi-mario-bros:/build" smb-build bash -c "python3 sprite_tools.py import && ./build.sh"
./fceux/fceux64.exe output/saudi-mario-bros.nes
