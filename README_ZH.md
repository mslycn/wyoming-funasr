## Wyoming Protocol stt server for home assistant

本地离线中文指令

ESP32-S3-Box-3B

RPi5 / 8GB

Wyoming Protocol 1.8.0

funasr=1.3.0

    FunASR SenseVoiceSmall

    Paraformer-zh 模型

## Dockerfile

1）FROM debian:bookworm-slim

Wyoming Whisper 也是用轻量 Debian/Ubuntu base 镜像

2）安装系统依赖

pip3 install wyoming==1.8.0： wyoming协议

pip3 install FunASR==1.3.0： ASR 引擎

FunASR 需要音频处理库：

torchaudio：PyTorch / ffmpeg：音频转码

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

### 代码严格实现 Wyoming 1.8.0 的握手与传输协议。

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


## step 1. Home Assistant添加Wyoming integration

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

VAD 模型：fsmn-vad v2.0.4

标点模型：ct-punc v2.0.4

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

~~~
DEBUG:sherpa_onnx_addon:Received event: Event(type='audio-chunk', data={'rate': 16000, 'width': 2, 'channels': 1, 'timestamp': None}, 
~~~

~~~
AudioChunk(
    audio=bytes,
    rate=16000,
    width=2,
    channels=1
)

~~~
width = 2 = 16-bit PCM（int16）,每个 sample = 2 字节.signed int16,不带 header，纯 PCM,是STT server（Vosk / FunASR / Whisper）默认且最稳的格式

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

AudioStop (soundfile）
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

### AudioStop (Optimized with NumPy
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

## 优化点 Optimized
- 不用 soundfile（快 2–3 倍），换NumPy -  AudioStop (Optimized with NumPy) 
- audiochunk  实时解析
- 
- 模型本地加载
- 模型预热
- 模型参数优化 - 4cpu # Optimized for Raspberry Pi 5 cores
- 模型参数优化 - disable_update=True # 禁止联网检查更新
- 
- 模型换funasr-onnx （快 2–3 倍）

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

