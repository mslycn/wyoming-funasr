import asyncio
import logging
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStop
from wyoming.event import Event
from wyoming.info import AsrModel, AsrProgram, Describe, Info, Attribution
from wyoming.server import AsyncServer, AsyncEventHandler

# Configure Logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("wyoming_stt")

class CustomSTTHandler(AsyncEventHandler):
    """Handles Wyoming events for STT."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_buffer = bytearray()

    async def handle_event(self, event: Event) -> bool:
        # 1. Provide info about this STT service to Home Assistant
        if Describe.is_type(event.type):
            _LOGGER.info("Describe request received")
            info = Info(
                asr=[
                    AsrProgram(
                        name="MyCustomSTT",
                        description="Custom STT Server",
                        attribution=Attribution(name="Me", url=""),
                        installed=True,
                        models=[
                            AsrModel(
                                name="default",
                                languages=["en"], # Add supported languages
                                attribution=Attribution(name="Me", url=""),
                                installed=True,
                            )
                        ],
                    )
                ]
            )
            await self.write_event(info.event())
            return True

        # 2. Transcribe signal (HA is ready to start)
        if Transcribe.is_type(event.type):
            _LOGGER.info("Transcription started")
            self.audio_buffer.clear()
            return True

        # 3. Receive Audio Chunks (16kHz, 16-bit Mono PCM)
        if AudioChunk.is_type(event.type):
            chunk = AudioChunk.from_event(event)
            self.audio_buffer.extend(chunk.audio)
            return True

        # 4. End of audio stream - Send the result
        if AudioStop.is_type(event.type):
            _LOGGER.info("Audio stream stopped. Processing...")
            
            # TODO: Plug in your STT engine here
            # result_text = my_stt_engine.transcribe(self.audio_buffer)
            result_text = "This is a dummy transcription"
            
            _LOGGER.info(f"Sending transcript: {result_text}")
            await self.write_event(Transcript(text=result_text).event())
            
            # Return False to close the connection after finishing
            return False

        return True

async def main():
    # Start server on all interfaces, port 10300
    server = AsyncServer.from_uri("tcp://0.0.0.0:10300")
    _LOGGER.info("Wyoming STT Server started on port 10300")
    await server.run(lambda: CustomSTTHandler())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
