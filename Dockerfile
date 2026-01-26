FROM debian:bookworm-slim
ARG TARGETARCH
ARG TARGETVARIANT




RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
    funasr==1.3.0

RUN pip3 install --no-cache-dir --break-system-packages \
    wyoming==1.8.0
  

        


         


