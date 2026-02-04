## funasr 和funasr-onnx  sherpa-onnx的模型是什么关系

funasr-onnx 是 FunASR 框架的“轻量化部署版”。它们的关系就像是模具与成品的关系。

### FunASR (PyTorch 版)

基于 PyTorch 框架，主要用于模型的训练、微调以及研究。模型文件通常是 .pb 或 .pt 格式。

### funasr-onnx

ONNX 是一种通用格式，脱离了 PyTorch 的重型环境。一个专门的推理库。它将 FunASR 中的预训练模型导出为 ONNX (Open Neural Network Exchange) 格式。
使用 funasr-onnx 时，不需要安装庞大的 PyTorch，只需要一个轻量的推理引擎（如 ONNX Runtime）。

在 CPU 环境下，ONNX 的推理速度通常比 PyTorch 快 2-3 倍。


### sherpa-onnx

sherpa-onnx: 一个开源项目，Sherpa-ONNX 语音识别服务器.提供离线的语音识别、文本转语音、说话人识别和语音活动检测（VAD）功能。项目基于下一代 Kaldi 和 onnxruntime，支持多种平台和操作系统，包括嵌入式系统、Android、iOS、Raspberry Pi、RISC-V 和 x86_64 服务器。using onnx with onnxruntime to replace PyTorch

sherpa-onnx 支持多种编程语言，包括：C++  Python C#

项目使用的框架: Kaldi: 下一代 Kaldi 是该项目的基础，用于语音处理和识别。

项目使用的技术: onnxruntime: 用于神经网络计算的 ONNX 运行时，替代 PyTorch 进行模型推理。WebSocket: 用于实时通信。

funasr-onnx 不需要那么多环境变量设置（因为它不走 PyTorch 的线程管理），它主要依赖 ONNX Runtime。

sherpa-onnx-asr和funasr的效果基本一样，但内存占用仅不到1g，而funasr占用3g起步。替换后可以大大降低配置需求.

使用 sherpa-onnx 是在树莓派等嵌入式设备上运行 SenseVoice 的最优解。相比 funasr 库，sherpa-onnx 去掉了复杂的 PyTorch 依赖，直接调用 C++ 优化的 ONNX 运行时，推理速度提升非常明显，且内存占用极低。


## Install   sherpa-onnx CPU篇

This method installs a CPU-only version of sherpa-onnx

###  step 1. Install the Python package sherpa-onnx - (From pre-compiled wheels, CPU only)

sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09 2025-09-09 的模型需要安装sherpa-onnx最新版


detail:https://k2-fsa.github.io/sherpa/onnx/python/install.html#method-1-from-pre-compiled-wheels-cpu-only


### 测试安装

使用 sherpa-onnx 提供的命令行工具测试
~~~
# 使用非流式（Offline）API 进行识别
./build/bin/sherpa-onnx-offline \
  --tokens=./tokens.txt \
  --sense-voice-model=./model.int8.onnx \
  --num-threads=4 \
  --debug=0 \
  ./test_wavs/zh.wav
~~~



## How to use




https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models

### 下载模型文件并放置在正确的目录中

sherpa-onnx的预训练模型下载

1. 在sherpa-onnx官方不同章节（如ASR/TTS/Keyword spotting的对应官方文档章节）里找对应的模型下载. https://k2-fsa.github.io/sherpa/onnx/index.html

2. 本文选择sherpa-onnx所使用的stt模型 - funasr's SenseVoiceSmall

对于 sherpa-onnx 官方仓库针对 SenseVoiceSmall 的导出版本，目前最完整、最新的资源主要集中在 k2-fsa/sherpa-onnx 的 Releases 页面以及其配套的文档中

其中：sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09  2025年9月更新版

[https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09.tar.bz2](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2025-09-09.tar.bz2)   158M  8位量化版本，体积更小（约 230MB），适合移动端及嵌入式 CPU。

https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2025-09-09.tar.bz2   845M  标准 Float32 精度模型，适合 PC 端/显卡推理。

3. download

Please use the following commands to download it:

~~~
cd /funasr-wyoming-sherpa-onnx

wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09.tar.bz2
tar xvf sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09.tar.bz2
rm sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09.tar.bz2
~~~

source: https://k2-fsa.github.io/sherpa/onnx/sense-voice/pretrained.html#sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17
   

## server.py

### 准备工作

1.安装server.py 运行时所用到的依赖包
sherpa_onnx
wyoming
numpy

 
2. 使用代码前，确保你已经下载了 SenseVoice 的 ONNX 模型文件



useful links 

sherpa-onnx

https://k2-fsa.github.io/sherpa/onnx/index.html

github repository:https://github.com/k2-fsa/sherpa-onnx

3. how to export models to onnx format.

3.1 https://k2-fsa.github.io/icefall/model-export/export-onnx.html

3.2 samples

sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17-int8 

This model is converted from https://www.modelscope.cn/models/iic/SenseVoiceSmall using the script export-onnx.py(https://github.com/k2-fsa/sherpa-onnx/blob/master/scripts/sense-voice/export-onnx.py)

source:https://k2-fsa.github.io/sherpa/onnx/sense-voice/pretrained.html#sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17




