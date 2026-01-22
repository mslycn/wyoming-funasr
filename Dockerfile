FROM debian:bookworm-slim

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    git \
    sox \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY server.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# 使用 venv python
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 10300
ENTRYPOINT ["./entrypoint.sh"]
