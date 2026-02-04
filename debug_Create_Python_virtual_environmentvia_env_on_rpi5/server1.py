#!/usr/bin/env python3
"""
Wyoming Protocol Server Test
Tests Wyoming service discovery and protocol compliance

This tool validates that a Wyoming ASR server properly handles:
- Wyoming Event Types

result:wyoming protocol failed to connect

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



class CustomSTTHandler(AsyncEventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_buffer = bytearray()

    async def handle_event(self, event: Event) -> bool:
        """
        Handle incoming events
        https://github.com/OHF-Voice/wyoming?tab=readme-ov-file#event-types
        """
        if Describe.is_type(event.type):
            _LOGGER.info("Describe request received")
           
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
    _LOGGER.info("Wyoming STT Server started on port 10300")
    await server.run(lambda: CustomSTTHandler())


if __name__ == "__main__":
    asyncio.run(main())
