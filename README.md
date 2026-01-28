# Raspberry Pi 5 + ARM64 + Wyoming + FunASR - Docker Image

Wyoming protocol server for the funasr  speech to text system.

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
  ghcr.io/mslycn/funasr-wyoming:latest

~~~

Home Assistant

HA → Settings → Voice → Speech-to-Text



## Debug

~~~
docker run -it --rm \
  --name funasr-wyoming \
  -p 10800:10300 \
  ghcr.io/mslycn/funasr-wyoming:latest

docker run -it --rm -p 10095:10095 -v /path/to/local/models:/workspace/models modelscope/funasr-runtime-sdk-cpu-0.4.6

~~~

CPU Architecture - multiarch

~~~
docker buildx imagetools inspect ghcr.io/mslycn/funasr-wyoming:latest

or

docker manifest inspect ghcr.io/mslycn/funasr-wyoming:latest

~~~

output

~~~
  Platform:    linux/amd64
               
  Name:        ghcr.io/mslycn/funasr-wyoming:latest@sha256:8acb1101d7ba1d4ca397de272e26cbd5fb0309ccfc269037ddaa4e38b5bdd37a
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    linux/arm64

~~~


Debug - server.py
~~~
docker run -it --entrypoint /bin/bash ghcr.io/mslycn/funasr-wyoming:main

/app# python3 server.py
~~~

~~~
sudo netstat -pnltu | grep ':10800'
tcp        0      0 0.0.0.0:10800           0.0.0.0:*               LISTEN      1136319/python3
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

funasr

https://github.com/modelscope/FunASR

funasr 1.3.1

https://pypi.org/project/funasr/#:~:text=seconds%20(s).-,SenseVoice,text%22%5D)%20print(text)

