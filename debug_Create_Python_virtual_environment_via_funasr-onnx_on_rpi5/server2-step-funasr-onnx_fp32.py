
#!/usr/bin/env python3
"""
Wyoming Protocol Server Test

一个基于 Wyoming 协议 的语音转文字（STT）服务端脚本，使用阿里开源的 SenseVoiceSmall onnx模型。

step 1. Install sherpa-onnx
pip3 install sherpa-onnx

pip3 install numpy

pip3 install Wyoming

step 2. server.py

from funasr_onnx import SenseVoiceSmall

"""

import os
import asyncio
import io

import numpy as np
import logging
import datetime
import time
import re





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


# ---------------- 1. 日志设置 ----------------
# ---------------- Logging ----------------
_LOGGER = logging.getLogger("wyoming-funasr-onnx")


import sherpa_onnx
_LOGGER.info(f"Sherpa-ONNX Version: {sherpa_onnx.__version__}")


# ---------------- 2. 初始化 Sherpa-ONNX----------------
# 在脚本启动时加载一次，确保响应速度
# --------------------------------
_LOGGER.info("%s - start excute sherpa-onnx" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])




start_model = time.time()

# 请确保路径指向你下载的模型文件夹
# MODEL_DIR = "/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2025-09-09"
MODEL_DIR = "/funasr-wyoming-sherpa-onnx/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2025-09-09"

def create_recognizer():
    _LOGGER.info(f"Loading Sherpa-ONNX model from {MODEL_DIR}")
    # 参数配置
    recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
        model=f"{MODEL_DIR}/model.onnx",
        tokens=f"{MODEL_DIR}/tokens.txt",
        num_threads=4,      # 适配树莓派核心数

        debug=False,
    )
    return recognizer

# 全局初始化模型
recognizer = create_recognizer()

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
        """Handle Wyoming protocol events"""

        # Handle service discovery 
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
                  name="funasr-wyoming-sherpa_onnx",
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

        # Handle transcription requests
        if Transcribe.is_type(event.type):
            _LOGGER.info("Transcribe received")
            return True

        # Handle audio stream start
        if AudioStart.is_type(event.type):
            _LOGGER.info("AudioStart received")
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - AudioStart Event received. Processing...")
            self.audio_buffer.clear()
            return True

        # Handle audio data chunks
        if AudioChunk.is_type(event.type):
            chunk = AudioChunk.from_event(event)
            self.audio_buffer.extend(chunk.audio)


            return True


 # ---------------- AudioStop (Optimized with NumPy) ----------------
        # Handle audio stream end
        if AudioStop.is_type(event.type):
            _LOGGER.info(f"Processing {len(self.audio_buffer)} bytes of audio...")
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - AudioStop received. Processing...")

            if not self.audio_buffer:
                await self.write_event(Transcript(text="").event())
                return False

            try:
                # Direct NumPy conversion: Bytes -> Int16 -> Float32 Normalization
                audio = np.frombuffer(self.audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0

                # 推理过程            
                stream = recognizer.create_stream()
                stream.accept_waveform(16000, audio)
                recognizer.decode_stream(stream)
                
                res = stream.result.text

                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 过滤掉 SenseVoice 可能输出的情感/事件标签")
                if res and len(res) > 0:
                    result_text = res

                    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 识别结果原文: {result_text}")
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
            return True # Close session after transcription

        return True


async def main():
    server = AsyncTcpServer(host="0.0.0.0", port=10900)
    _LOGGER.info("Wyoming STT Server started on port 10800")
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - Wyoming Sherpa-ONNX Server started on port 10900")
    await server.run(CustomSTTHandler)



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
