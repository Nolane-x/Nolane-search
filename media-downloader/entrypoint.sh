#!/bin/sh
set -eu

# HTTPS interception certificates are created by Cloudflare at container startup.
# Trust them at runtime; never bake this ephemeral certificate into the image.
if [ -f /etc/cloudflare/certs/cloudflare-containers-ca.crt ]; then
  install -m 0644 /etc/cloudflare/certs/cloudflare-containers-ca.crt \
    /usr/local/share/ca-certificates/cloudflare-containers.crt
  update-ca-certificates >/dev/null
fi

exec setpriv --reuid=10001 --regid=10001 --init-groups python3 -u /app/server.py
