AS = ca65
LD = ld65

OUT_DIR = output

.PHONY: clean

build: $(OUT_DIR)/main.nes

%.o: src/%.asm import_sprites
	$(AS) -g --create-dep "$@.dep" --debug-info $< -o $@

$(OUT_DIR):
	mkdir -p $(OUT_DIR)

$(OUT_DIR)/main.nes: layout main.o | $(OUT_DIR)
	$(LD) --dbgfile $@.dbg -C $^ -o $@

import_sprites: mario_sprites.txt | chr.bin
	python sprite_tools.py import -a -f mario_sprites.txt -c chr.bin

chr.bin: original-rom.nes
	python sprite_tools.py getchr -f original-rom.nes -o chr.bin

original-rom.nes:
	curl -L -o "original-rom.nes" \
	  "https://raw.githubusercontent.com/vmartinv/nek/master/roms/Super%20Mario%20Bros.%20(Japan%2C%20USA).nes"

clean:
	rm -rf *.nes *.dep *.o *.dbg __pycache__ *.bin output

include $(wildcard *.dep)
