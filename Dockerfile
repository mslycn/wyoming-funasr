ARG BUILD_FROM=ghcr.io/home-assistant/base-debian:bookworm
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/opt/venv

# 安装系统依赖 + python venv
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    git \
    sox \
    ffmpeg \
    libglib2.0-0 \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 创建 venv
RUN python3 -m venv ${VENV_PATH}

# 把 venv 的 pip 升级
RUN ${VENV_PATH}/bin/pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .

# 使用 venv pip 安装依赖（关键）
RUN ${VENV_PATH}/bin/pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# 让容器默认使用 venv 的 python
ENV PATH="${VENV_PATH}/bin:$PATH"

EXPOSE 10300

ENTRYPOINT ["./entrypoint.sh"]
