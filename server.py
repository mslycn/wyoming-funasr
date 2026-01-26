import asyncio
import logging
from typing import Optional

from funasr import AutoModel
from wyoming.asr import AsrStart, AsrStop, Transcript
from wyoming.audio import AudioChunk, AudioStop
from wyoming.event import Event
from wyoming.info import AsrModel, AsrProgram, Info, Attribution
from wyoming.server import AsyncServer

# 配置日志
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

# 初始化 FunASR 1.3.0 Paraformer 模型
_LOGGER.info("正在初始化 FunASR 1.3.0 (Paraformer-zh)...")
model = AutoModel(
    model="paraformer-zh", 
    model_revision="v2.0.4",
    device="cpu", 
    disable_update=True
)

class FunASRHandler:
    def __init__(self, reader, writer, info_event: Event):
        self.reader = reader
        self.writer = writer
        self.info_event = info_event
        self.audio_data = bytearray()
        self.language: Optional[str] = None

    async def handle(self):
        while True:
            event = await Event.read_event(self.reader)
            if event is None:
                break

            # 1. 响应 Describe (Wyoming 1.8.0 握手)
            if event.type == "describe":
                await self.info_event.write_event(self.writer)
                _LOGGER.info("已响应 Describe 请求")

            # 2. 识别开始信号
            elif AsrStart.is_event(event):
                start = AsrStart.from_event(event)
                self.language = start.language
                self.audio_data.clear()
                _LOGGER.info(f"ASR 会话开始 (语言: {self.language})")

            # 3. 接收音频切片 (PCM 16bit 16Khz Mono)
            elif AudioChunk.is_event(event):
                chunk = AudioChunk.from_event(event)
                self.audio_data.extend(chunk.audio)

            # 4. 音频传输结束，触发推理
            elif AudioStop.is_event(event) or AsrStop.is_event(event):
                _LOGGER.info(f"开始推理，音频长度: {len(self.audio_data)} 字节")
                
                # FunASR 1.3.0 推理接口
                res = model.generate(
                    input=bytes(self.audio_data),
                    language="zh", 
                    use_itn=True
                )
                
                # 提取识别文本
                if res and len(res) > 0:
                    text = res[0]['text'].strip()
                else:
                    text = ""

                _LOGGER.info(f"识别结果: {text}")

                # 将结果封装为 Transcript 事件返回给 HA
                await Transcript(text=text).write_event(self.writer)
                self.audio_data.clear()
                break

async def main():
    # 符合 1.8.0 规范的元数据
    wyoming_info = Info(
        asr=[
            AsrProgram(
                name="FunASR-Paraformer",
                description="FunASR 1.3.0 with Paraformer-zh",
                attribution=Attribution(name="Alibaba DAMO", url="https://github.com/alibaba-damo-academy/FunASR"),
                installed=True,
                models=[
                    AsrModel(
                        name="Paraformer-zh",
                        description="中文通用语音识别模型",
                        attribution=Attribution(name="Alibaba", url="https://github.com/alibaba-damo-academy/FunASR"),
                        installed=True,
                        languages=["zh"],
                    )
                ],
            )
        ]
    ).event()

    server = AsyncServer.from_uri("tcp://0.0.0.0:10300")
    _LOGGER.info("Wyoming 1.8.0 服务已启动，监听端口: 10300")
    await server.run(lambda r, w: FunASRHandler(r, w, wyoming_info).handle())

if __name__ == "__main__":
    asyncio.run(main())
