FROM registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-cpu-0.4.4

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /models && chmod -R 777 /models



WORKDIR /funAsr
#RUN pip install flask requests funasr modelscope
COPY . .


EXPOSE 10300
ENTRYPOINT ["./entrypoint.sh"]
