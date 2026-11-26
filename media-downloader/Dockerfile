FROM node:22-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:\${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv ffmpeg ca-certificates tini util-linux \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir \
       "yt-dlp[default]==2026.11.23" \
       "yt-dlp-ejs==0.8.0"

WORKDIR /app
COPY server.py /app/server.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod 0755 /app/entrypoint.sh \
    && mkdir -p /data/jobs \
    && chmod 0700 /data /data/jobs

EXPOSE 8080
ENTRYPOINT ["/usr/bin/tini", "--", "/app/entrypoint.sh"]
