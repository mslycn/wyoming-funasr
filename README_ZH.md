Wyoming Protocol 1.8.0

funasr=1.3.0

Paraformer-zh 模型

## Dockerfile

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

how to write a stt server Wyoming=1.8.0 for home assistant voice assistant

Wyoming 1.8.0 事件

Wyoming 1.8.0 -> Speech to Text
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

必须处理这些事件：
~~~
AudioStart	开始一段音频
AudioChunk	PCM16 音频流
AudioStop	音频结束
Transcribe	Home Assistant 主动触发
~~~

必须返回
~~~
Transcript(text="xxx")
~~~


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

要让 HA 识别STT 服务，Wyoming 服务必须：

能被 HA 连接（TCP 10300）

能响应 info / describe

能处理 audio-start / audio-chunk / audio-stop

能返回 transcript


Home Assistant 的 Wyoming 集成在启动时会：

连接你的 Wyoming TCP服务

发送 info

Wyoming 服务器必须响应 info 事件

Home Assistant解析返回的 asr 结构,检查返回结果里是否包含 asr program + model + languages,判断是否支持 STT

如果 info 不返回或者结构不符合，HA 就不会显示你的服务。

Home Assistant 发现流程：

连接 TCP

发送 info

解析返回的 asr 结构





wyoming ≥ 1.6,新写法是：
~~~
AsyncTcpServer(
    host="0.0.0.0",
    port=10300,
    handler=YourHandler(...)
)

~~~

Paraformer-zh 模型：Paraformer-zh 是一个非流式（Non-streaming）模型，非常适合智能家居场景下的短指令识别，具有极高的准确率。

Paraformer-zh (v2.0.4)：这是 FunASR 1.3.0 推荐的 Paraformer 中文版本，识别率极高，且完全不需要联网（在镜像内已固化）。

内存建议：Paraformer-zh 在运行时约需 800MB - 1.2GB 内存，在树莓派上请注意监控资源。

代码严格实现 Wyoming 1.8.0 的握手与传输协议。


Home Assistant 的 base-debian 是 multi-arch manifest
