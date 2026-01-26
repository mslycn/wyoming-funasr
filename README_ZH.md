

Dockerfile

FROM debian:bookworm-slim

Wyoming Whisper 也是用轻量 Debian/Ubuntu base 镜像

2）安装系统依赖

FunASR 需要音频处理库：

sox / ffmpeg：音频转码

libsndfile1：soundfile 依赖

build-essential：部分 Python 库需要编译

funasr：ASR 引擎

torch + torchaudio：PyTorch

wyoming：协议层

numpy、soundfile：音频处理
