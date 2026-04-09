#!/bin/bash
set -e
rm -f fceux/snaps/*
docker compose up --build
./fceux/fceux64.exe output/saudi-mario-bros.nes
