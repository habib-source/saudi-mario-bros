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

RUN curl -L -G \
     -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0" \
     -H "Referer: https://vimm.net/" \
     -d "mediaId=818" \
     "https://dl3.vimm.net/" -o SMB.zip


RUN unzip -p SMB.zip "Super Mario Bros. (World).nes" > original-rom.nes

COPY . .

RUN python extract_chr.py original-rom.nes

RUN chmod +x build.sh

# Source files are mounted at runtime via -v, not baked in.
# Mount the project root to /build and output lands in /build/output.
CMD python sprite_tools.py import && python import_bg_tiles.py && ./build.sh
