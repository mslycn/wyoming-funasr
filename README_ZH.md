## Wyoming Protocol stt server for home assistant

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

how to write a stt server Wyoming=1.8.0 for home assistant voice assistant.

non-streaming STT

Wyoming 1.8.0 事件

Wyoming 1.8.0 -> Speech to Text

代码严格实现 Wyoming 1.8.0 的握手与传输协议。

~~~
Speech to Text
→ describe (required)
← info (required)


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




要让 HA 识别STT 服务，Wyoming 服务必须：

能被 HA 连接（TCP 10300）

能响应  describe

能处理 audio-start / audio-chunk / audio-stop

能返回 transcript


Home Assistant Wyoming integration 集成在启动时会：

连接你的 Wyoming TCP服务

发送 describe

Wyoming 服务器必须响应 describe 事件,发送 info

Home Assistant解析返回的 asr 结构,检查返回结果里是否包含 asr program + model + languages,判断是否支持 STT

如果 info 不返回或者结构不符合，HA 就不会显示你的服务。

Home Assistant 发现流程：

连接 TCP

发送 escribe

解析返回的 info ->asr 结构

## Wyoming info for stt

Home Assistant's Wyoming integration is quite strict about the Describe/Info handshake.

从 Wyoming 1.8.0 开始，Info 描述是强约束结构体.

1. Wyoming info 分为 stt 和 tts等多种信息结构。
2. 本文用到是stt Wyoming info
3. 经测试，没有返回Wyoming info，或者返回的Wyoming info结构体字段不对，ha无法链接到  Wyoming stt server。

 Wyoming info 响应结构(1.8.0)
~~~
describe - request for available voice services

info
├─ asr (optional)
│  ├─ supports_transcript_streaming
│  └─ models (required)
│     ├─ name (required)
│     ├─ languages (required)
│     ├─ installed (required)
│     ├─ description (optional)
│     ├─ version (optional)
│     └─ attribution (required)
│        ├─ name (required)
│        └─ url (required)

~~~
source:https://pypi.org/project/wyoming/#:~:text=wyoming%201.8.0,Peer%2Dto%2Dpeer%20protocol%20for%20voice%20assistants

~~~
Each model within the asr list adheres to the following required fields: 
models (required):
    name: A unique name for the model.
    languages: A list of supported language codes (e.g., en-US, es-ES).
    installed: A boolean (true if the model is currently installed and ready for use).
    description (optional): A human-readable description of the model.
    version (optional): The version of the model.
    attribution: An object containing:
       name: The name of the creator or organization.
       url: A URL for the creator or project.

supports_transcript_streaming: A boolean (true if the program can stream transcript chunks
~~~

1. wyoming_faster_whisper
~~~
 wyoming_info = Info(
        asr=[
            AsrProgram(
                name="faster-whisper",
                description="Faster Whisper transcription with CTranslate2",
                attribution=Attribution(
                    name="Guillaume Klein",
                    url="https://github.com/guillaumekln/faster-whisper/",
                ),
                installed=True,
                version=__version__,
                models=[
                    AsrModel(
                        name=model_name,
                        description=model_name,
                        attribution=Attribution(
                            name="Systran",
                            url="https://huggingface.co/Systran",
                        ),
                        installed=True,
                        languages=sorted(
                            list(
                                # pylint: disable=protected-access
                                set(faster_whisper.tokenizer._LANGUAGE_CODES).union(
                                    PARAKEET_LANGUAGES
                                )
                            )
                        ),
                        version=faster_whisper.__version__,
                    )
                ],
            )
        ],
    )

~~~
source:https://github.com/rhasspy/wyoming-faster-whisper/blob/main/wyoming_faster_whisper/__main__.py


~~~
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True
~~~
source:https://github.com/rhasspy/wyoming-faster-whisper/blob/main/wyoming_faster_whisper/dispatch_handler.py


~~~
 attribution = Attribution(
                    name="Voxtral Wyoming",
                    url="https://github.com/Johnson145/voxtral_wyoming",
                )
                asr_model = AsrModel(
                    name="voxtral",
                    attribution=attribution,
                    installed=True,
                    description="Offline STT with Mistral Voxtral",
                    version=VW_VERSION,
                    languages=SUPPORTED_LANGUAGES,
                )
                asr_program = AsrProgram(
                    name="voxtral-wyoming",
                    attribution=attribution,
                    installed=True,
                    description="Wyoming-compatible STT service",
                    version=VW_VERSION,
                    models=[asr_model],
                    supports_transcript_streaming=False,
                )
                try:
                    await async_write_event(Info(asr=[asr_program]).event(), writer)
                except (ConnectionResetError, BrokenPipeError, OSError):
                    _LOGGER.warning("Client disconnected during Info write: %s", addr)
                    break
~~~
source:https://github.com/Johnson145/voxtral_wyoming/blob/main/src/voxtral_wyoming/server.py

~~~
def build_info() -> Info:
    return Info(
        name="MyCustomSTT",
        description="Custom Wyoming Speech-to-Text Server",
        asr=AsrProgram(
            name="mycustomstt",
            supports_transcript_streaming=False,
            models=[
                AsrModel(
                    name="default",
                    languages=["en"],
                    installed=True,
                    description="Default English ASR model",
                    version="1.0.0",
                    attribution=Attribution(
                        name="Your Name or Organization",
                        url="https://example.com"
                    ),
                )
            ],
        ),
    )
~~~


wyoming ≥ 1.6,新写法是：
~~~
AsyncTcpServer(
    host="0.0.0.0",
    port=10300,
    handler=YourHandler(...)
)

~~~

## funasr model

1. Paraformer-zh (v2.0.4)  - rpi5 killed 

Paraformer-zh 模型：Paraformer-zh 是一个非流式（Non-streaming）模型，非常适合智能家居场景下的短指令识别，具有极高的准确率。

Paraformer-zh (v2.0.4)：这是 FunASR 1.3.0 推荐的 Paraformer 中文版本，识别率极高，且完全不需要联网（在镜像内已固化）。

内存建议：Paraformer-zh 在运行时约需 800MB - 1.2GB 内存，在树莓派上请注意监控资源。

2. iic/SenseVoiceSmall

~~~
model = AutoModel(
        model="iic/SenseVoiceSmall",
        device="cpu",        # 树莓派5使用 CPU
        disable_update=True  # 禁用自动更新加速启动，启动更快
    )
~~~



## checklist

~~~
netstat -lntp | grep 10300
~~~


Home Assistant 的 base-debian 是 multi-arch manifest

Wyoming Protocol 1.8.0

https://github.com/OHF-Voice/wyoming/tree/main

https://pypi.org/project/wyoming/#:~:text=wyoming%201.8.0,Peer%2Dto%2Dpeer%20protocol%20for%20voice%20assistants

https://github.com/modelscope/FunASR

