FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc6-dev make git ca-certificates python3 \
    && rm -rf /var/lib/apt/lists/*

# Build asm6f (6502 assembler, compatible with SMBDIS.ASM syntax)
RUN git clone https://github.com/freem/asm6f.git /opt/asm6f \
    && cd /opt/asm6f \
    && make \
    && cp asm6f /usr/local/bin/

WORKDIR /build

# Source files are mounted at runtime via -v, not baked in.
# Mount the project root to /build and output lands in /build/output.
CMD ["./build.sh"]
