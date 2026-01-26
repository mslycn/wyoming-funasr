FROM debian:bookworm-slim
ARG TARGETARCH
ARG TARGETVARIANT


RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \

RUN \
    pip3 install --no-cache-dir \
       wyoming==1.8.0        

        


         


