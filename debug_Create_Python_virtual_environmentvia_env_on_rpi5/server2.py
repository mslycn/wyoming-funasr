#!/usr/bin/env python3
"""
Wyoming Protocol Server Test
Tests Wyoming service discovery and protocol compliance

This tool validates that a Wyoming ASR server properly handles:
- Service  (Recieved Describe -> Send Info)
"""

import asyncio
import logging

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioStart, AudioChunk, AudioStop
from wyoming.event import Event
from wyoming.info import (
    AsrModel,
    AsrProgram,
    Attribution,
    Describe,
    Info,
)
from wyoming.server import AsyncTcpServer, AsyncEventHandler



logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("wyoming_stt")

from wyoming.info import Info, AsrProgram, AsrModel, Attribution




class CustomSTTHandler(AsyncEventHandler):

    """
    Handle a single Wyoming TCP connection for ASR.

    Expects Describe? → Transcribe? → AudioStart → AudioChunk* → AudioStop,
    and responds with Info (optional) and a final Transcript.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_buffer = bytearray()

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            _LOGGER.info("Describe request received：Received Describe event from client")

             # see:https://github.com/Johnson145/voxtral_wyoming/blob/main/src/voxtral_wyoming/server.py
            attribution = Attribution(
                 name="Voxtral Wyoming",
                 url="https://github.com/Johnson145/voxtral_wyoming",
             )
            asr_model = AsrModel(
                  name="voxtral",
                  attribution=attribution,
                  installed=True,
                  description="Offline STT with Mistral Voxtral",
                  version="1.0.0",
                  languages=["zh"],
             )
            asr_program = AsrProgram(
                  name="voxtral-wyoming",
                  attribution=attribution,
                  installed=True,
                  description="Wyoming-compatible STT service",
                  version="1.0.0",
                  models=[asr_model],
                  supports_transcript_streaming=False,
             )

             #try:
             #     await async_write_event(Info(asr=[asr_program]).event(), writer)
             #except (ConnectionResetError, BrokenPipeError, OSError):
             #     _LOGGER.warning("Client disconnected during Info write: ")

            # await self.write_event(Info(asr=[asr_program]).event())


 
            info = Info(asr=[asr_program])
            await self.write_event(info.event())
            return True

        if Transcribe.is_type(event.type):
            _LOGGER.info("Transcribe received")
            return True

        if AudioStart.is_type(event.type):
            _LOGGER.info("AudioStart received")
            self.audio_buffer.clear()
            return True

        if AudioChunk.is_type(event.type):
            chunk = AudioChunk.from_event(event)
            self.audio_buffer.extend(chunk.audio)
            return True

        if AudioStop.is_type(event.type):
            _LOGGER.info("AudioStop received. Processing...")
            result_text = "This is a dummy transcription"
            await self.write_event(Transcript(text=result_text))
            return True

        if Transcribe.is_type(event.type):
            _LOGGER.info("Transcribe received")
            return True

        return True


async def main():
    server = AsyncTcpServer(host="0.0.0.0", port=10800)
    _LOGGER.info("Wyoming STT Server started on port 10800")
    await server.run(CustomSTTHandler)



if __name__ == "__main__":
    asyncio.run(main())
