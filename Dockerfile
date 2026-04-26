FROM python:slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc6-dev make git ca-certificates curl unzip\
    && rm -rf /var/lib/apt/lists/

# Build asm6f (6502 assembler, compatible with SMBDIS.ASM syntax)
RUN git clone https://github.com/freem/asm6f.git /opt/asm6f \
    && cd /opt/asm6f \
    && make \
    && cp asm6f /usr/local/bin/

WORKDIR SMB

RUN curl -L -o "original-rom.nes" \
  "https://raw.githubusercontent.com/vmartinv/nek/master/roms/Super%20Mario%20Bros.%20(Japan%2C%20USA).nes"

COPY . .

RUN python sprite_tools.py getchr -f original-rom.nes -o chr.bin

RUN chmod +x build.sh

# Source files are mounted at runtime via -v, not baked in.
# Mount the project root to /build and output lands in /build/output.
CMD python sprite_tools.py import -a -f saudi_sprites_final.txt -c chr.bin && ./build.sh && sleep infinity
