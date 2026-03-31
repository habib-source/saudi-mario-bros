FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc6-dev make git ca-certificates python3 \
    && rm -rf /var/lib/apt/lists/*

# Build asm6f (6502 assembler, compatible with SMBDIS.ASM syntax)
RUN git clone https://github.com/freem/asm6f.git /opt/asm6f \
    && cd /opt/asm6f \
    && make \
    && cp asm6f /usr/local/bin/

WORKDIR /build
COPY SMBDIS.ASM .
COPY build.sh .
COPY build_rom.py .
RUN chmod +x build.sh

# If CHR ROM exists, copy it in
COPY chr-ro[m] chr-rom/

CMD ["./build.sh"]
