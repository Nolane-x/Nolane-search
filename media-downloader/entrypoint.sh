#!/bin/sh
set -eu

# Cloudflare creates this certificate at runtime when HTTPS outbound interception
# is enabled. Never bake it into the image.
if [ -f /etc/cloudflare/certs/cloudflare-containers-ca.crt ]; then
  install -m 0644 /etc/cloudflare/certs/cloudflare-containers-ca.crt \
    /usr/local/share/ca-certificates/cloudflare-containers.crt
  update-ca-certificates >/dev/null
fi

exec python3 -u /app/server.py
