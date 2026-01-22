
import asyncio
from wyoming.server import AsyncServer
from wyoming.asr import AsrService
from funasr import AutoModel

MODEL_NAME = "paraformer-zh"

class FunASRService(AsrService):
    def __init__(self):
        self.model = AutoModel(
            model="paraformer-zh",
            vad_model="fsmn-vad",
            punc_model="ct-punc",
            device="cpu"
        )

    async def transcribe(self, audio, sample_rate):
        res = self.model.generate(
            input=audio,
            sample_rate=sample_rate
        )
        return res[0]["text"]

async def main():
    server = AsyncServer.from_uri("tcp://0.0.0.0:10300")
    server.add_service(FunASRService())
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
