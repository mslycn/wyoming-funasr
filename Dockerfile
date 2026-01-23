# =========================
# 1) Build Stage
# =========================
FROM python:3.11-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies into /app/.venv
RUN python -m venv /app/.venv \
    && /app/.venv/bin/pip install --upgrade pip \
    && /app/.venv/bin/pip install -r requirements.txt

# Copy source code
COPY wyoming_funasr /app/wyoming_funasr

# =========================
# 2) Runtime Stage
# =========================
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/wyoming_funasr /app/wyoming_funasr

ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 10300

# Entry
CMD ["python", "-m", "wyoming_funasr", "--host", "0.0.0.0", "--port", "10300"]
