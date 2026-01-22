# Raspberry Pi 5 + ARM64 + Wyoming + FunASR - Docker Image

Integrating FunASR with Home Assistant.Wyoming protocol server for the FunASR speech to text system.

## Project structre
~~~
funasr-wyoming/
├── Dockerfile
├── requirements.txt
├── server.py
├── entrypoint.sh
├── models/
│   └── README.md
└── .github/
    └── workflows/
        └── docker-arm64.yml
~~~

## How to use

Docker Image

~~~
docker run -d \
  --name funasr-wyoming \
  --restart=unless-stopped \
  -p 10800:10300 \
  ghcr.io/mslycn/wyoming-whisper:latest

~~~

Home Assistant

HA → Settings → Voice → Speech-to-Text



## Debug

~~~
docker run -it --rm \
  --name funasr-wyoming \
  -p 10800:10300 \
  ghcr.io/mslycn/wyoming-whisper:latest

docker run -it --rm -p 10095:10095 -v /path/to/local/models:/workspace/models modelscope/funasr-runtime-sdk-cpu-0.4.6

~~~

~~~
docker inspect --format '{{.Architecture}}' ghcr.io/mslycn/wyoming-whisper:latest

~~~


Installation Requirements - funasr
~~~
python>=3.8
torch>=1.13
torchaudio
~~~
source:https://github.com/modelscope/FunASR/tree/main

Base Images:

ghcr.io/home-assistant/aarch64-homeassistant-base:BASE-VERSION
ghcr.io/home-assistant/amd64-homeassistant-base:BASE-VERSION

source:

https://github.com/home-assistant/docker

Home Assistant Base Images

https://github.com/home-assistant/docker-base


https://github.com/modelscope/FunASR/blob/main/runtime/readme.md


Wyoming Protocol

https://www.home-assistant.io/integrations/wyoming

