

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

## server.py

Wyoming 1.8.0 事件
事件	作用
AudioStart	开始一段音频
AudioChunk	PCM16 音频流
AudioStop	音频结束
Transcribe	Home Assistant 主动触发

从 Wyoming 1.8.0 开始，Info 描述是强约束结构体
~~~
AsrProgram(
    name,
    description,
    attribution,   ✅ 必填
    installed,     ✅ 必填
    version        ✅ 必填
)

~~~

Speech to Text
~~~
Speech to Text
→ transcribe event with name of model to use or language (optional)
→ audio-start (required)
→ audio-chunk (required)
Send audio chunks until silence is detected
→ audio-stop (required)
← transcript (required)
Contains text transcription of spoken audio
~~~

wyoming ≥ 1.6,新写法是：
~~~
AsyncTcpServer(
    host="0.0.0.0",
    port=10300,
    handler=YourHandler(...)
)

~~~
