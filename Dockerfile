FROM debian:bookworm-slim
ARG TARGETARCH
ARG TARGETVARIANT


RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
    \
    && python3 -m venv .venv \
    && .venv/bin/pip3 install --no-cache-dir -U \
        torch \
        wheel \

RUN \        
    .venv/bin/pip3 install --no-cache-dir \
        --extra-index-url 'https://download.pytorch.org/whl/cpu' \
        'torch==2.6.0' \
    \
    && rm -rf /var/lib/apt/lists/*

         


