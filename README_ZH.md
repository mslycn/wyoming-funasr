## Wyoming Protocol stt server for home assistant

本地离线中文指令

ESP32-S3-Box-3B

RPi5 / 8GB

Wyoming Protocol 1.8.0

funasr=1.3.0

    FunASR SenseVoiceSmall

    Paraformer-zh 模型

## Environment
~~~
CPU: rpi5
OS: [please fill]
Python: [please fill]
PyTorch: [please fill]
FunASR versions: 1.3.0 
~~~    

## Dockerfile

1）FROM debian:bookworm-slim

Wyoming Whisper 也是用轻量 Debian/Ubuntu base 镜像

2）安装系统依赖

pip3 install wyoming==1.8.0： wyoming协议

pip3 install FunASR==1.3.0： ASR 引擎。阿里达摩院开源的高性能语音识别工具包。

FunASR 需要音频处理库：

torchaudio：PyTorch 官方推出的音频处理库。在 ASR 流程中，torchaudio 主要负责把原始音频文件变成模型能读懂的“特征图”。

torch :ai神经网络

numpy : 音频处理

soundfile：音频处理

           libsndfile： Soundfile 基于强大的库libsndfile 

Librosa： 它在底层同时封装了 NumPy 和 Soundfile，更适合工程化使用。

## server.py

how to write a stt server Wyoming=1.8.0 for home assistant voice assistant.

non-streaming STT

Wyoming 1.8.0 事件

Wyoming 1.8.0 -> Speech to Text


### HA Wyoming ASR Client

Send  audio to a STT Wyoming server

~~~
import sounddevice as sd
from wyoming.client import AsyncClient
from wyoming.audio import AudioStart, AudioChunk, AudioStop
from wyoming.event import Event
import asyncio

RATE = 16000
CHANNELS = 1
WIDTH = 2

async def stream_mic():
    async with AsyncClient.from_uri("tcp://localhost:10200") as client:
        await client.write_event(AudioStart(rate=RATE, width=WIDTH, channels=CHANNELS).event())

        def callback(indata, frames, time, status):
            chunk = AudioChunk(audio=indata.tobytes(), rate=RATE, width=WIDTH, channels=CHANNELS)
            asyncio.create_task(client.write_event(chunk.event()))

        with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=RATE):
            await asyncio.sleep(5)  # Record for 5 seconds

        await client.write_event(AudioStop().event())
        response = await client.read_event()
        print("Transcription:", response.data["text"])

asyncio.run(stream_mic())

~~~
source：https://julianbei.github.io/wyoming/07-examples/#asr-client-microphone-to-transcript


###   Execution Flow 

Wyoming ASR Client ← → Wyoming ASR Server

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

## 交互流程日志示例（stt server side）

当对着 Home Assistant 说话时，看到的日志时间顺序是：

~~~
Received event type: describe (必选)  describe event仅在添加 Wyoming Protocol Integration时发生。

Received event type: transcript

Received event type: audio-start

Received event type: audio-chunk (成百上千个)

Received event type: audio-stop

(最后代码要发送 transcript)
~~~

### stt server 必须处理的事件类型
~~~
事件类型    处理逻辑
Describe,  返回 Info 事件（包含模型信息），客户端连接时通常会问一次。
AudioStart 核心入口。在这里清理 audio_buffer，准备接收新一段音频。
AudioChunk 持续将二进制音频数据塞进 self.audio_buffer。
AudioStop  核心出口。停止录音，开始调用 FunASR 模型推理，并返回 Transcript。
~~~

必须处理这些事件：
~~~
AudioStart	开始一段音频→ 声明音频格式
AudioChunk	PCM16 音频流 → 持续发送音频
AudioStop	音频结束
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


## step 1. Wyoming Protocol Implementation

Home Assistant添加Wyoming integration

### Home Assistant Wyoming integration 集成在启动时会：

HA连接你的 Wyoming server TCP服务

HA发送 describe事件 -> Wyoming server

Wyoming server 服务器必须响应 describe 事件,发送Wyoming info 信息结构

Home Assistant解析返回的Wyoming info(Wyoming info for asr) 结构,检查返回结果里是否包含 asr program + model + languages,判断是否支持 STT

如果 Wyoming info不返回或者结构不符合HA的要求，HA 就不会显示服务。

### Home Assistant 发现流程：

连接 TCP

发送 describe

解析返回的 info ->asr 结构

## Wyoming info for stt

Home Assistant's Wyoming integration is quite strict about the Describe/Info handshake.

### 从 Wyoming 1.8.0 开始，Info 描述是强约束结构体.

为了让 HA 识别出这是一个stt server，在连接初期HA 会主动发送一个 describe事件,你还需要回复一个Wyoming info。

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

2. Johnson145/voxtral_wyoming

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

## step 2.1 Transcribe Event

关于Transcribe Event的处理

Transcribe:非必须。	Home Assistant 主动触发→ 请求输出识别结果。Transcribe 事件本质：客户端请求执行语音转文字

Wyoming 协议支持两种不同的 ASR 交互模式，客户端会根据需求二选一：

- 模式 A（显式请求）：客户端先发一个 Transcribe 事件（告诉服务器：我要开始转录了，语言是 xx），然后再发音频数据。

- 模式 B（直接发送 - 最常见）：客户端为了降低延迟，不发送 Transcribe，而是直接从 AudioStart 开始。

结论： 绝大多数基于 Wyoming 的客户端（包括 Home Assistant 的 Assist 功能）在发起语音识别请求时，会直接跳过 Transcribe 步骤，直接发送 AudioStart

## step 2.2 AudioStart Event

input
~~~
{
  "type": "audio.start",
  "rate": 16000,
  "width": 2,
  "channels": 1
}

~~~

server.py对应处理事件：if AudioStart.is_type(event.type):

~~~
DEBUG:sherpa_onnx_addon:Received event: Event(type='audio-chunk', data={'rate': 16000, 'width': 2, 'channels': 1, 'timestamp': None}, 
~~~

AudioChunk Event
~~~
AudioChunk(
    audio=bytes,
    rate=16000,
    width=2,
    channels=1
)

~~~
width = 2 = 16-bit PCM（int16）,每个 sample = 2 字节.signed int16,不带 header，纯 PCM,是STT server（Vosk / FunASR / Whisper）默认且最稳的格式


## 用 FunASR 开发 ASR Server的两种路径

要用FunASR搭建 Server，通常有两种路径：

- way 1. 快速原型（Python + FastAPI/Flask）

直接用 FunASR 的 Python API

test - A. 使用原型（Python + FastAPI/Flask）直接用 FunASR 的 Python API
~~~
from funasr import AutoModel
import torchaudio

# 1. 加载模型 (Paraformer 是目前常用的高精度非流式模型)
model = AutoModel(model="paraformer-zh", vad_model="fsmn-vad", punc_model="ct-punc")

# 2. 预测
res = model.generate(input="test.wav")
print(res)
~~~

客户端调用FunASR 提供的 Python API，输入音频流获取文本结果。

- way 2. 工业级部署（Runtime SDK）

要开发支撑高并发的 Server，使用官方提供的 Runtime SDK。它集成了 C++ 推理引擎，支持 WebSocket 和 gRPC 协议。

官方提供的 Runtime SDK（通常基于 Docker 部署）

~~~
# 示例命令，具体参数参考官方文档
sudo docker run -p 10095:10095 -it registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:runtime-sdk-cpu-0.4.5
~~~

客户端调用FunASR 提供了 Python/JS/C++ 的客户端 demo，直接发送音频流即可获取结果。

典型案例：

https://github.com/mslycn/FunAsr

https://github.com/yaming116/FunAsr

## Inference  Framework

~~~
Inference  Framework
   ├── FunASR (PyTorch)
   ├── funasr-onnx
   └── Sherpa-ONNX
~~~

## Pipeline
~~~
Mode: offline
VAD + ASR (+ punctuation)
~~~

## 阿里asr模型种类：

~~~

FunAudioLLM 语音体系
   ├── FunASR（语音识别框架 / 模型集合）
   │       └── Paraformer（纯ASR模型）        :阿里最经典的非流式识别模型
   │       └── SenseVoice（多任务音频模型）   : 主打情感和事件检测,需要听出音频里的背景音（如猫叫、敲门声）： 选 SenseVoice。它能过滤掉咳嗽、叹气等非语言杂音，不会把这些杂音强行转录成奇怪的字。
   │       └── Gummy（语音大模型 / 多模态方向) :主打实时翻译
   ├── Qwen3-ASR（2026年发布，Qwen 家族分支）
   │       └── 
   │       └── 
   │       └── 
   │
   └── 

~~~

- FunASR ：语音识别推理框架，训练框架，模型管理平台；
- FunASR:  支持的模型
  - Paraformer    阿里较早一代ASR模型
  - SenseVoice    阿里新一代多任务语音基础模型，类似语音领域的 LLM，。新的语音 AI 架构。包括：ASR（语音识别）SER（情感识别）LID（语言识别）音频事件识别。不像传统 ASR 只做“语音转文字”
    - SenseVoice Large  精度更高,需要GPU,适合服务器
    - SenseVoice Small  资源占用低,适合边缘设备,适合树莓派
  - ...

- Gummy ：统一语音理解大模型。类似：GPT（文本）

当前使用的是FunASR + SenseVoiceSmall模型

## 模型的流式Speech Recognition (Streaming) vs 非流式Speech Recognition (Non-streaming)：

- Speech Recognition (Non-streaming) - 非流式
Fun-ASR-Nano
Paraformer-large： 适合离线长语音转写（准确率最高）。
SenseVoiceSmall:   是非流式模型（录完一段再处理）

- Speech Recognition (Streaming) - 流式

Paraformer-online： 适合实时直播字幕或语音助手。

paraformer-zh-streaming:边说边出字

Zipformer： 小米新一代 Kaldi 团队的 ASR 模型

## offline mode vs online mode

在 ASR 领域，通常把在线模式称为 Streaming ASR（流式识别），离线模式称为 Offline/Batch ASR（离线/批处理识别）。

## funasr model

在 RPi5 上直接跑原生环境： 可以基于 python:3.10-slim 镜像，手动安装 modelscope 和 funasr。RPi5 的 CPU 性能可以直接运行 PyTorch（CPU版）。

1. Paraformer-zh (v2.0.4)  - rpi5 killed 

Paraformer-zh 模型：Paraformer-zh 是一个非流式（Non-streaming）模型，非常适合智能家居场景下的短指令识别，具有极高的准确率。

Paraformer-zh (v2.0.4)：这是 FunASR 1.3.0 推荐的 Paraformer 中文版本，识别率极高，且完全不需要联网（在镜像内已固化）。

内存建议：Paraformer-zh 在运行时约需 800MB - 1.2GB 内存，在树莓派上请注意监控资源。


2. SenseVoice

2.1 SenseVoice-Large

主要用于云端或高性能服务器，追求极高的语种覆盖和精度


2.2 iic/SenseVoiceSmall

~~~
model = AutoModel(
        model="iic/SenseVoiceSmall",
        device="cpu",        # 树莓派5使用 CPU
        disable_update=True  # 禁用自动更新加速启动，启动更快
    )
~~~
准确率：首先保证准确率，准确率与模型精度强关联 SenseVoiceSmall 默认是 FP32（32位浮点数）

VAD 模型：fsmn-vad v2.0.4 ：VAD 会增加预处理延迟： 它需要先切分音频再喂给 ASR。关闭。优化点

标点模型：ct-punc v2.0.4:推理完文字后还要跑一遍标点模型。 音频很短（<30秒），直接关掉，只跑单一推理模型。 优化点

3. model  download

~~~
model = AutoModel(
    model=model_dir,
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
    device="cuda:0",
)
~~~
   
model_dir: The name of the model, or the path to the model on the local disk.

model=model_dir: model_dir可以是字符串 ID，也可以是绝对/相对路径

在 FunASR 1.3.0 中，AutoModel 的 model 参数设计灵活：既可以是模型 ID（如 model_id = 'iic/SenseVoiceSmall'），也可以接收本地磁盘路径（local_dir = './models/SenseVoiceSmall'）。


 

 source:https://github.com/modelscope/FunASR

 4. funasr-onnx  模型优化




当使用 funasr=1.3.0 识别音频时，内部流程如下：
~~~
接收：从 Wyoming 协议接收到 bytearray（原始字节）。

转换 (NumPy)：通过 np.frombuffer(audio_data, dtype=np.int16) 将字节转换成数字数组。

标准化 (NumPy)：将 int16（-32768 到 32767）转换为 float32（-1.0 到 1.0），这是深度学习模型最喜欢的格式。

读取/保存 (SoundFile)：如果你需要将识别失败的音频存下来调试，你会调用 sf.write('debug.wav', data, samplerate)。

~~~

~~~
            # Convert buffer to numpy array
            audio_bytes = bytes(self.audio_buffer)
            
            # Convert based on sample width
            if self.sample_width == 2:  # 16-bit
                audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
            elif self.sample_width == 4:  # 32-bit
                audio_data = np.frombuffer(audio_bytes, dtype=np.int32)
            else:
                raise ValueError(f"Unsupported sample width: {self.sample_width}")
            
            # Convert to float32 and normalize
            audio_data = audio_data.astype(np.float32)
            if self.sample_width == 2:
                audio_data /= 32768.0
            else:
                audio_data /= 2147483648.0
~~~

source：https://github.com/vrsttl/wyoming-parakeet-silero-wrapper/blob/ce1ac3116135a1d277ec60c59c71bc941c1f4f7d/wyoming_vad_asr_server.py

## step 2.3 AudioChunk Event

### AudioChunk 

在 wyoming 协议中，AudioChunk 是一个高频触发的事件（通常每秒触发数十次）.

Wyoming 通常每 20ms-50ms 发送一个 Chunk。音频会在缓冲区堆积

ha client -> server.py
~~~
audio.chunk
audio.chunk
audio.chunk

~~~

server.py -> if AudioChunk.is_type(event.type):



### Audio Format(input) - Home Assistant sends audio as 16,000Hz, 16-bit, Mono PCM.

1. ESP32-S3-Box 3
~~~
ESP32 采集：双声道，16kHz 或 48kHz。

ESPHome/Firmware 处理：进行 AEC（回声消除）和降噪。

Wyoming 协议封装：强制下采样并转换为 16kHz, 单声道, 16-bit PCM。

被HA 统一规范化为 单声道 16kHz
~~~

2. Home Assistant Wyoming Integration 发送到 STT 服务的音频是 Raw PCM (无文件头格式原始音频，就是一堆数据)。

~~~
参数,规格
容器格式,None (Raw) - 没有 .wav 那种文件头
编码 (Codec),"PCM_16 (Signed 16-bit, Little Endian)"
采样率 (Sample Rate),"16,000 Hz (16kHz)"
声道 (Channels),1 (Mono)
比特率 (Bitrate),256 kbps (16000 * 16 * 1)

~~~

3. Wyoming 送来的音频是： PCM 16kHz mono 如何读取效率最高
   


### 音频的读取

音频在计算机中本质上是一串数值（振幅）。当你使用 NumPy 时，你可以直接操作这些数字。

处理已经加载好的数据： 用 NumPy。FunASR 的模型推理接口（model.generate）接收的标准数据格式就是 NumPy 数组 - 性能提升点1

处理硬盘里的文件变成数据： 你必须用 Soundfile。用于**“读入”**。将硬盘里的 .wav 文件加载进内存。


### Speech Recognition (no Streaming)

1. Home Assistant Wyoming integration（client）
~~~
import sounddevice as sd
from wyoming.client import AsyncClient
from wyoming.audio import AudioStart, AudioChunk, AudioStop
from wyoming.event import Event
import asyncio

RATE = 16000
CHANNELS = 1
WIDTH = 2

async def stream_mic():
    async with AsyncClient.from_uri("tcp://localhost:10200") as client:
        await client.write_event(AudioStart(rate=RATE, width=WIDTH, channels=CHANNELS).event())

        def callback(indata, frames, time, status):
            chunk = AudioChunk(audio=indata.tobytes(), rate=RATE, width=WIDTH, channels=CHANNELS)
            asyncio.create_task(client.write_event(chunk.event()))

        with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=RATE):
            await asyncio.sleep(5)  # Record for 5 seconds

        await client.write_event(AudioStop().event())
        response = await client.read_event()
        print("Transcription:", response.data["text"])

asyncio.run(stream_mic())
~~~
发送了3个事件，- AudioStart- AudioChunk- AudioStop

source:https://julianbei.github.io/wyoming/07-examples/#asr-client-microphone-to-transcript

2. stt server（server）

需要对三个事件先做出处理、然后进行回应
- AudioStart
- AudioChunk
- AudioStop

## step 2.4 AudioStop Event

AudioStop (soundfile）

...

AudioStop (NumPy）
~~~
# ---------------- AudioStop (Optimized with NumPy) ----------------
        if AudioStop.is_type(event.type):
            _LOGGER.info(f"Processing {len(self.audio_buffer)} bytes of audio...")
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - AudioStop received. Processing...")

            if not self.audio_buffer:
                await self.write_event(Transcript(text="").event())
                return False

            try:
                # Direct NumPy conversion: Bytes -> Int16 -> Float32 Normalization
                audio = np.frombuffer(self.audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0

                # Inference
                res = model.generate(
                    input=audio, 
                    sampling_rate=16000,
                    language="zh", 
                    use_itn=True,
                    is_final=True,
                    batch_size=1,
                )
                
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 过滤掉 SenseVoice 可能输出的情感/事件标签")
                if res and len(res) > 0:
                    result_text = res[0]["text"]
                    # Regex to strip emotional/event tags like <|HAPPY|>
                    result_text = re.sub(r'<\|.*?\|>', '', result_text).strip()
                else:
                    result_text = ""
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 接收到的音频为空...")     
          
                _LOGGER.info(f"Result: {result_text}")
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 识别结果: {result_text}")
                await self.write_event(Transcript(text=result_text).event())
                
            except Exception as e:
                _LOGGER.error(f"Inference error: {e}", exc_info=True)
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 识别过程出错")
                await self.write_event(Transcript(text="").event())
            
            self.audio_buffer.clear()
            return False # Close session after transcription

        return True
~~~

### AudioStop (Optimized with NumPy)

1. SenseVoiceSmall 接收 16000Hz 的音频
在音频进入 model.generate 之前，确保它已经是 16k 的 numpy 数组。

如果你的采集设备或前端传过来的是 44100Hz 或 48000Hz，则转换为16k 的 numpy 数组

2.SenseVoiceSmall 默认是 FP32（32位浮点数）

~~~
# ---------------- AudioStop (Optimized with NumPy) ----------------
        if AudioStop.is_type(event.type):
            _LOGGER.info(f"Processing {len(self.audio_buffer)} bytes of audio...")
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - AudioStop received. Processing...")

            if not self.audio_buffer:
                await self.write_event(Transcript(text="").event())
                return False

            try:
                # Direct NumPy conversion: Bytes -> Int16 -> Float32 Normalization
                audio = np.frombuffer(self.audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0

                # Inference
                res = model.generate(
                    input=audio, 
                    sampling_rate=16000,
                    language="zh", 
                    use_itn=True,
                    is_final=True,
                    batch_size=1,
                )
                
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 过滤掉 SenseVoice 可能输出的情感/事件标签")
                if res and len(res) > 0:
                    result_text = res[0]["text"]
                    # Regex to strip emotional/event tags like <|HAPPY|>
                    result_text = re.sub(r'<\|.*?\|>', '', result_text).strip()
                else:
                    result_text = ""
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 接收到的音频为空...")     
          
                _LOGGER.info(f"Result: {result_text}")
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 识别结果: {result_text}")
                await self.write_event(Transcript(text=result_text).event())
                
            except Exception as e:
                _LOGGER.error(f"Inference error: {e}", exc_info=True)
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 识别过程出错")
 event = Event(
            type="stt.text",
            data={"text": text}
        )
~~~

### AudioStop 15 秒

AudioStop 是客户端ESP32 s3 box3B发出的.

从日志来看，AudioStart 到 AudioStop 之间的时间间隔差异巨大（有的 3 秒，有的长达 15 秒），非常影响体验。

原因：

AudioStop 事件是由 发送方（ESP32 s3 box3B） 或 中间处理层（HA Assist） 决定的。导致 15 秒才停止的原因有：

1.静音检测（VAD）未触发： ESP32 box3B 在等待你说话结束。它认为你“一直在说话”，直到触发 15秒强制超时。

2.日志中 20:52:09 到 20:52:24 正好是 15秒，恰好是系统默认的“最长录音限制”。是一个典型的 硬超时（Hard Timeout）。说明在这 15 秒内，ESP32 认为环境一直不静默。

3.Wi-Fi 信号不稳定

### 优化：

1.修改server.py 增加超时保护

虽然 AudioStop 是客户端发的，在服务端增加一个逻辑：如果 audio_buffer 长度超过一定限度（比如对应 10 秒的采样），强制进行一次识别。 识别后，  客户端也会发AudioStop，

2.当客户端随后发送迟到的 AudioStop 时，服务端应该直接忽略，而不是再次识别。需要回应客户端吗

3.在 Wyoming 协议中，AudioStop 是一个单向终结信号。当客户端发送 AudioStop 时，它其实是在告诉你：“我传完了，我准备好听你的结果了（或者准备断开连接了）”。

以下是处理迟到 AudioStop 的两个核心原则：

 协议层面：不需要新的 Response
由于你在 10 秒超时处已经调用了 _process_audio 并通过 self.write_event(Transcript(...)) 把识别结果发给 Home Assistant 了，此时 HA 端的逻辑其实已经触发（比如灯已经开了）。

当迟到的 AudioStop 到达时：

不要再次发送 Transcript：如果你再发一次，HA 可能会尝试执行第二次指令。

不要忽略这个事件：在代码逻辑中，你必须返回 False（在 AsyncEventHandler 的 handle_event 中），这会告诉服务端框架：“这个连接可以安全关闭了”。


## 优化点 Optimized
- 不用 soundfile（快 2–3 倍），换NumPy -  AudioStop (Optimized with NumPy) 
- audiochunk  实时解析
- 
- 模型本地加载
- 模型预热
- 模型参数优化 - 4cpu # Optimized for Raspberry Pi 5 cores
- 模型参数优化 - disable_update=True # 禁止联网检查更新
- 
- 模型换funasr-onnx （快 2–3 倍）- 用sherpa-onnx-asr替换funasr

## 使用代码自动下载模型

~~~
#安装ModelScope
pip install modelscope
~~~

~~~
#SDK模型下载
from modelscope import snapshot_download
model_dir = snapshot_download('iic/SenseVoiceSmall')
~~~

source：https://www.modelscope.cn/models/iic/SenseVoiceSmall

## ASR (语音识别) 流程的标准英文日志
~~~
调试步骤 (Step)	英文日志 (English Log)	中文说明
Connection	New client connection established.	新客户端连接已建立。
Stream Start	Audio stream initialized. Clearing buffer.	音频流初始化，正在清空缓冲区。
Chunk Trace	Ingesting chunk: size={n}, dtype=float32	正在摄取音频片段：大小={n}。
VAD/Silence	Low signal detected. Possible silence.	检测到微弱信号，可能是静默。
End of Stream	AudioStop received. Total samples: {n}	收到停止事件。总采样数：{n}。
Inference	Starting offline inference with Sherpa-ONNX.	开始使用 Sherpa-ONNX 进行离线推理。
Final Result	Transcription success: "{text}" (Latency: {ms}ms)	识别成功：“{文本}”（延迟：{毫秒}）。
Error	Inference failed: {error_msg}	推理失败：{错误信息}。

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

Wyoming info 1.8.0

https://github.com/vrsttl/wyoming-parakeet-silero-wrapper/blob/ce1ac3116135a1d277ec60c59c71bc941c1f4f7d/wyoming_vad_asr_server.py

SenseVoice多语言语音理解模型Small使用手册

https://www.modelscope.cn/models/iic/SenseVoiceSmall

https://huggingface.co/FunAudioLLM/SenseVoiceSmall/blob/main/README_zh.md

