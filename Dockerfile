FROM debian:bookworm-slim
ARG TARGETARCH
ARG TARGETVARIANT



# Docker里绝对不要用 venv,因为Docker 本身就是“超级虚拟环境”
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app 

# Torch深度学习 / 神经网络计算核心库
RUN pip3 install --no-cache-dir --break-system-packages \
    torch 

# orchaudio：音频读取、预处理、特征提取、音频增强
RUN pip3 install --no-cache-dir --break-system-packages \
    torchaudio

RUN pip3 install --no-cache-dir --break-system-packages \
    funasr==1.3.0

# Peer-to-peer protocol for home assistant voice assistants
# wyoming 1.8.0: https://pypi.org/project/wyoming/1.8.0/
# https://github.com/OHF-Voice/wyoming

RUN pip3 install --no-cache-dir --break-system-packages \
    wyoming==1.8.0

# ===== 代码 =====
COPY server.py .

EXPOSE 10300

ENTRYPOINT ["python3", "server.py"]    
  

        


         


