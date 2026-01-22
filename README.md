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

Base Images:

ghcr.io/home-assistant/aarch64-homeassistant-base:BASE-VERSION
ghcr.io/home-assistant/amd64-homeassistant-base:BASE-VERSION

source:

https://github.com/home-assistant/docker

https://github.com/home-assistant/docker-base
