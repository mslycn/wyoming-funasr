ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    sox \
    ffmpeg \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY server.py entrypoint.sh ./
COPY models ./models
RUN chmod +x entrypoint.sh

EXPOSE 10300
ENTRYPOINT ["./entrypoint.sh"]
