import asyncio
import io
import numpy as np
import soundfile as sf

from funasr import AutoModel

from wyoming.server import AsyncTcpServer
from wyoming.event import Event
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop


# ===== FunASR 模型 =====
model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc",
    device="cpu",
)


class FunASRHandler:
    def __init__(self):
        self.audio_bytes = bytearray()
        self.sample_rate = 16000

    async def handle_event(self, event: Event):
        # 音频开始
        if isinstance(event, AudioStart):
            self.audio_bytes.clear()
            self.sample_rate = event.rate or 16000
            return None

        # 音频流
        if isinstance(event, AudioChunk):
            self.audio_bytes.extend(event.audio)
            return None

        # 音频结束 → 触发识别
        if isinstance(event, AudioStop):
            text = self.run_asr()
            return Transcript(text=text)

        # STT 请求（兼容 HA）
        if isinstance(event, Transcribe):
            text = self.run_asr()
            return Transcript(text=text)

        return None

    def run_asr(self) -> str:
        if not self.audio_bytes:
            return ""

        # PCM16 → float32
        audio_np = np.frombuffer(self.audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        # FunASR 推理
        result = model.generate(
            input=audio_np,
            sample_rate=self.sample_rate,
        )

        if not result:
            return ""

        return result[0].get("text", "")


async def main():
    server = AsyncTcpServer(
        host="0.0.0.0",
        port=10300,
        handler_factory=FunASRHandler,
    )
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
