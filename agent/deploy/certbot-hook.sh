#!/bin/bash
# certbot runs this after it gets or renews the certificate: copy it where Caddy can read it, then reload Caddy.
set -euo pipefail
DEST=/var/lib/caddy/tls/lionscraft-website
install -d -o caddy -g caddy -m 750 $DEST
install -o caddy -g caddy -m 644 "$RENEWED_LINEAGE/fullchain.pem" $DEST/cert.pem
install -o caddy -g caddy -m 600 "$RENEWED_LINEAGE/privkey.pem" $DEST/key.pem
systemctl reload caddy
