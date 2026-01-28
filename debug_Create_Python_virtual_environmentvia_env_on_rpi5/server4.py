import os
import asyncio
import io
import soundfile as sf
import logging
import datetime
import time

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
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("wyoming_stt")



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
            self.audio_buffer.clear()
            return True

        if AudioChunk.is_type(event.type):
            chunk = AudioChunk.from_event(event)
            self.audio_buffer.extend(chunk.audio)
            return True

        # ---------------- AudioStop ----------------
        if AudioStop.is_type(event.type):
            _LOGGER.info("AudioStop received. Processing...")
            _LOGGER.info("音频停止，开始识别...")
            _LOGGER.info("音频接收完成，数据大小: %d bytes", len(self.audio_buffer))
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - AudioStop received. Processing...")
            
            audio_bytes_io = io.BytesIO(self.audio_buffer)
            
            try:
                audio, sr = sf.read(
                    audio_bytes_io, 
                    samplerate=16000, 
                    channels=1, 
                    format='RAW', 
                    subtype='PCM_16', 
                    dtype="float32"
                )
                
                # 检查是否为空音频
                if len(audio) == 0:
                    _LOGGER.warning("接收到的音频为空")
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 接收到的音频为空...")
                    return False

                # 调用 SenseVoiceSmall 识别
                # 注意：SenseVoiceSmall 强烈建议开启 is_final=True
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
                    # 过滤掉 SenseVoice 可能输出的情感/事件标签 (如 <|HAPPY|>)
                    import re
                    result_text = re.sub(r'<\|.*?\|>', '', result_text).strip()
                else:
                    result_text = ""
                
                _LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 识别结果: {result_text}")
                
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 识别结果: {result_text}")
                await self.write_event(Transcript(text=result_text).event())
                
            except Exception as e:
                _LOGGER.error(f"识别过程出错: {e}", exc_info=True)
                print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} - 识别过程出错")
                await self.write_event(Transcript(text="").event())
            
            self.audio_buffer.clear()

            return True


async def main():
    server = AsyncTcpServer(host="0.0.0.0", port=10800)
    _LOGGER.info("Wyoming STT Server started on port 10800")
    await server.run(CustomSTTHandler)



if __name__ == "__main__":
    asyncio.run(main())
