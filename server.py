import asyncio
import logging
import tempfile
import os

import numpy as np
import soundfile as sf

from funasr import AutoModel
from wyoming.asr import AsrStart, AsrChunk, AsrStop, AsrResult
from wyoming.event import Event
from wyoming.server import AsyncServer

logging.basicConfig(level=logging.INFO)

MODEL_PATH = "./models/paraformer-zh"


class FunASRService:
    def __init__(self):
        logging.info("Loading FunASR model...")
        self.model = AutoModel(
            model=MODEL_PATH,
            vad_model="fsmn-vad",
            punc_model="ct-punc",
            device="cpu",
        )
        logging.info("FunASR model loaded")

    async def handle(self, event: Event):
        if isinstance(event, AsrStart):
            self.audio = bytearray()
            self.sample_rate = event.sample_rate
            return None

        if isinstance(event, AsrChunk):
            self.audio.extend(event.audio)
            return None

        if isinstance(event, AsrStop):
            return await self.recognize()

        return None

    async def recognize(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name

        audio_np = np.frombuffer(self.audio, dtype=np.int16)
        sf.write(wav_path, audio_np, self.sample_rate)

        result = self.model.generate(input=wav_path)
        os.unlink(wav_path)

        text = ""
        if result and isinstance(result, list):
            text = result[0].get("text", "")

        logging.info("ASR result: %s", text)
        return AsrResult(text=text)


async def main():
    service = FunASRService()
    server = AsyncServer.from_stdin_stdout(service.handle)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
