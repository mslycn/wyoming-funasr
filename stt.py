import numpy as np

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.server import AsyncEventHandler

from funasr import AutoModel


class FunASRSTT(AsyncEventHandler):
    def __init__(self):
        self.model = AutoModel(
            model="paraformer-zh",
            vad_model="fsmn-vad",
            punc_model="ct-punc",
        )

        self.audio_buffer = bytearray()
        self.sample_rate = 16000

    async def handle_event(self, event: Event) -> Event | None:
        if isinstance(event, AudioStart):
            self.audio_buffer.clear()
            self.sample_rate = event.rate
            return None

        if isinstance(event, AudioChunk):
            self.audio_buffer.extend(event.audio)
            return None

        if isinstance(event, AudioStop):
            return None

        if isinstance(event, Transcribe):
            pcm = np.frombuffer(self.audio_buffer, dtype=np.int16)
            audio = pcm.astype(np.float32) / 32768.0

            result = self.model.generate(
                input=audio,
                sampling_rate=self.sample_rate,
            )

            text = result[0]["text"] if result else ""

            return Transcript(
                text=text,
                language="zh-CN",
            )

        return None
