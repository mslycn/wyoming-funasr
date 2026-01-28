#!/usr/bin/env python3
"""
Wyoming Protocol Server4 Test

This tool validates that a Wyoming ASR server properly handles:
- ncpu=4
"""

import os
import asyncio
import io
import soundfile as sf
import numpy as np
import logging
import datetime
import time
import re

import torch

# 必须在 import funasr 之前设置
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
torch.set_num_threads(4)
torch.set_num_interop_threads(1)

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
from funasr import AutoModel

# ---------------- 1. 日志设置 ----------------
# ---------------- Logging ----------------
_LOGGER = logging.getLogger(__name__)


# ---------------- 2. 全局模型加载 ----------------
# 在脚本启动时加载一次，确保响应速度
# ---------------- FunASR Paraformer-zh v2.0.4 ----------------
_LOGGER.info("%s - start excute AutoModel" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])



# model_conf


start_model = time.time()

model_dir = "/root/.cache/modelscope/hub/iic/SenseVoiceSmall"

model = AutoModel(
    model="iic/SenseVoiceSmall",
    device="cpu",
    ncpu=4,                # Optimized for Raspberry Pi 5 cores
    disable_update=True,
    trust_remote_code=True,
    # vad_model="fsmn-vad",   # Essential for audio > 30s
    # vad_kwargs={"max_single_segment_time": 30000}
)

end_model = time.time()
load_time_ms = (end_model - start_model) * 1000
print(f'加载模型SenseVoiceSmall耗时 {load_time_ms:.2f} 毫秒')







# ---------------- 3. 事件处理器 ----------------
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
        
            print(f'Describe request received：Received Describe event from client')

             # see:https://github.com/Johnson145/voxtral_wyoming/blob/main/src/voxtral_wyoming/server.py
            attribution = Attribution(
                 name="FunASR Wyoming",
                 url="https://github.com/mslycn/wyoming-funasr",
             )
            asr_model = AsrModel(
                  name="SenseVoiceSmall",
                  attribution=attribution,
                  installed=True,
                  description="Offline STT with FunASR SenseVoiceSmall",
                  version="1.0.0",
                  languages=["zh"],
             )
            asr_program = AsrProgram(
                  name="funasr-wyoming",
                  attribution=attribution,
                  installed=True,
                  description="Wyoming-compatible FunASR STT service",
                  version="1.0.0",
                  models=[asr_model],
                  supports_transcript_streaming=False,
             )

   
            info = Info(asr=[asr_program])
            await self.write_event(info.event())
            return True

        if Transcribe.is_type(event.type):
            _LOGGER.info("Transcribe received")
            return True

        if AudioStart.is_type(event.type):
            _LOGGER.info("AudioStart received")
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - AudioStart Event received. Processing...")
            self.audio_buffer.clear()
            return True

        if AudioChunk.is_type(event.type):
            chunk = AudioChunk.from_event(event)
            self.audio_buffer.extend(chunk.audio)
            return True

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


async def main():
    server = AsyncTcpServer(host="0.0.0.0", port=10800)
    _LOGGER.info("Wyoming STT Server started on port 10800")
    await server.run(CustomSTTHandler)



if __name__ == "__main__":
    asyncio.run(main())
