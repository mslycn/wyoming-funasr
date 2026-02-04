# 使用的基础镜像
FROM debian:bookworm-slim
ARG TARGETARCH
ARG TARGETVARIANT


# 安装系统依赖
# Docker里绝对不要用 venv,因为Docker 本身就是“超级虚拟环境”
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app 

# 
RUN pip3 install --no-cache-dir --break-system-packages \
    sherpa-onnx 

# Audio Processing
RUN pip3 install --no-cache-dir --break-system-packages \
    numpy

# Wyoming Protocol
# Install the Wyoming library in your Python environment
# Peer-to-peer protocol for home assistant voice assistants
# wyoming 1.8.0: https://pypi.org/project/wyoming/1.8.0/
# https://github.com/OHF-Voice/wyoming

RUN pip3 install --no-cache-dir --break-system-packages \
    wyoming==1.8.0

# ===== 代码 =====
COPY server.py .

# 暴露端口
EXPOSE 10300

# Dockerfile 调试模板
# -u：关闭缓冲,日志立刻刷出来
ENTRYPOINT ["python3", "-u", "server.py"]


# ENTRYPOINT ["python3", "server.py"]    
  

        


         


