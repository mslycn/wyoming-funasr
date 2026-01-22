ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base-debian:bookworm 
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

# 基础依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    sox \
    ffmpeg \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python 依赖
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 代码
COPY server.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 10300

ENTRYPOINT ["./entrypoint.sh"]

