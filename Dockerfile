FROM python:slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    make curl cc65\
    && rm -rf /var/lib/apt/lists/

WORKDIR SMB


COPY . .

CMD make && sleep infinity
