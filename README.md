# Raspberry Pi 5 + ARM64 + Wyoming + FunASR

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
~~~
docker run -d \
  --name funasr-wyoming \
  --restart=unless-stopped \
  -p 10800:10300 \
  ghcr.io/mslycn/wyoming-whisper:latest

~~~

Base Images:

ghcr.io/home-assistant/aarch64-homeassistant-base:BASE-VERSION
ghcr.io/home-assistant/amd64-homeassistant-base:BASE-VERSION

source:

https://github.com/home-assistant/docker

https://github.com/home-assistant/docker-base
