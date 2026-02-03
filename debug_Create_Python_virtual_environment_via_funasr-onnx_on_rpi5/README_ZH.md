## funasr 和funasr-onnx  sherpa-onnx的模型是什么关系

funasr-onnx 是 FunASR 框架的“轻量化部署版”。它们的关系就像是模具与成品的关系。

### FunASR (PyTorch 版): 基于 PyTorch 框架，主要用于模型的训练、微调以及研究。模型文件通常是 .pb 或 .pt 格式。

### funasr-onnx:  ONNX 是一种通用格式，脱离了 PyTorch 的重型环境。一个专门的推理库。它将 FunASR 中的预训练模型导出为 ONNX (Open Neural Network Exchange) 格式。
使用 funasr-onnx 时，不需要安装庞大的 PyTorch，只需要一个轻量的推理引擎（如 ONNX Runtime）。

在 CPU 环境下，ONNX 的推理速度通常比 PyTorch 快 2-3 倍。




### sherpa-onnx

sherpa-onnx: 一个开源项目，提供离线的语音识别、文本转语音、说话人识别和语音活动检测（VAD）功能。项目基于下一代 Kaldi 和 onnxruntime，支持多种平台和操作系统，包括嵌入式系统、Android、iOS、Raspberry Pi、RISC-V 和 x86_64 服务器。

sherpa-onnx 支持多种编程语言，包括：C++  Python C#

项目使用的框架: Kaldi: 下一代 Kaldi 是该项目的基础，用于语音处理和识别。

项目使用的技术: onnxruntime: 用于神经网络计算的 ONNX 运行时，替代 PyTorch 进行模型推理。WebSocket: 用于实时通信。


## Install


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

### 选择sherpa-onnx所使用的模型

对于 sherpa-onnx 官方仓库针对 SenseVoiceSmall 的导出版本，目前最完整、最新的资源主要集中在 k2-fsa/sherpa-onnx 的 Releases 页面以及其配套的文档中

其中：sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09  2025年9月更新版

[https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09.tar.bz2](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2025-09-09.tar.bz2)   158M  8位量化版本，体积更小（约 230MB），适合移动端及嵌入式 CPU。

https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2025-09-09.tar.bz2   845M  标准 Float32 精度模型，适合 PC 端/显卡推理。




sherpa-onnx

https://k2-fsa.github.io/sherpa/onnx/index.html

