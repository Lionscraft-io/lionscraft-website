#!/bin/bash
# Installs or updates Hermes, the Lionscraft website agent, on a Debian server that runs Caddy.
# Run as root after copying the agent folder to /opt/lionscraft-website:
#   bash /opt/lionscraft-website/deploy/setup.sh <domain>
# Safe to run again after every code change.
set -euo pipefail

DOMAIN="${1:?usage: setup.sh <domain>}"
NAME=lionscraft-website
DIR=/opt/$NAME
DATA=/var/lib/$NAME
PORT=8791
CADDYFILE=/etc/caddy/Caddyfile
ROUTES=/etc/caddy/routes.d

python3 -c "import ensurepip" 2>/dev/null || apt-get install -y python3-venv
command -v git >/dev/null || apt-get install -y git
id $NAME >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin $NAME
chown -R root:root "$DIR"

[ -d "$DIR/venv" ] || python3 -m venv "$DIR/venv"
"$DIR/venv/bin/pip" install -q --upgrade -r "$DIR/requirements.txt"

# Secrets: created once from the example, readable by root only (systemd reads it)
[ -f "$DIR/.env" ] || cp "$DIR/.env.example" "$DIR/.env"
chown root:root "$DIR/.env"
chmod 600 "$DIR/.env"
set_env() { # name value [always]: fills in a setting that is empty, or always with "always"
	ENV_FILE="$DIR/.env" ENV_NAME="$1" ENV_VALUE="$2" ENV_ALWAYS="${3:-}" python3 - <<'PY'
import os
path, name, value = os.environ["ENV_FILE"], os.environ["ENV_NAME"], os.environ["ENV_VALUE"]
lines = open(path).read().splitlines()
for i, line in enumerate(lines):
    if line.startswith(name + "="):
        if os.environ["ENV_ALWAYS"] == "always" or line == name + "=":
            lines[i] = f"{name}={value}"
        break
else:
    lines.append(f"{name}={value}")
open(path, "w").write("\n".join(lines) + "\n")
PY
}
set_env PUBLIC_URL "https://$DOMAIN" always
set_env MCP_KEY "$(python3 -c 'import secrets; print(secrets.token_hex(16))')"
set_env PREVIEW_KEY "$(python3 -c 'import secrets; print(secrets.token_hex(8))')"

# The key the agent uses to push to GitHub; add its public half on GitHub once
install -d -o $NAME -g $NAME -m 755 $DATA
install -d -o $NAME -g $NAME -m 700 $DATA/ssh
chown -R $NAME:$NAME $DATA
[ -f $DATA/ssh/deploy_key ] || runuser -u $NAME -- ssh-keygen -q -t ed25519 -N "" -C "$NAME@$DOMAIN" -f $DATA/ssh/deploy_key

cp "$DIR/deploy/$NAME.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable $NAME
systemctl restart $NAME

# Caddy: one site block for the domain, shared with the chat bot. Each app adds its own routes file.
# The certificate comes from Let's Encrypt through certbot, not from Caddy itself: the server's self-signed
# certificate for the outreach chat bridge also names this domain, so Caddy would skip it.
CERT=/var/lib/caddy/tls/$NAME
ACME_ROOT=/var/www/acme
mkdir -p $ROUTES $ACME_ROOT
cp "$CADDYFILE" "$CADDYFILE.before-agent"
[ -f $ROUTES/$NAME.caddy ] && cp $ROUTES/$NAME.caddy /tmp/$NAME.caddy.before
write_routes() {
	cat >$ROUTES/$NAME.caddy <<EOF
# Hermes, the Lionscraft website agent: MCP server, draft preview, and the preprod site (GitHub main)
$([ -f $CERT/cert.pem ] && echo "tls $CERT/cert.pem $CERT/key.pem")
handle /.well-known/acme-challenge/* {
	root * $ACME_ROOT
	file_server
}
handle /mcp/* {
	reverse_proxy 127.0.0.1:$PORT
}
handle /preview/* {
	reverse_proxy 127.0.0.1:$PORT
}
# Preprod must not show up in Google
handle /robots.txt {
	respond "User-agent: *
Disallow: /"
}
# Browsers that opened a preview link see the draft instead of preprod
@preview header Cookie *hermes_preview=*
handle @preview {
	rewrite * /draft-site{path}
	reverse_proxy 127.0.0.1:$PORT
}
handle {
	header X-Robots-Tag "noindex, nofollow"
	root * $DATA/preprod/lionscraft-site.webflow
	# Clean links: /services is services.html
	try_files {path} {path}.html {path}/index.html
	file_server
}
EOF
}
reload_caddy() {
	if ! caddy validate --config "$CADDYFILE" --adapter caddyfile; then
		cp "$CADDYFILE.before-agent" "$CADDYFILE"
		if [ -f /tmp/$NAME.caddy.before ]; then mv /tmp/$NAME.caddy.before $ROUTES/$NAME.caddy; else rm $ROUTES/$NAME.caddy; fi
		echo "Caddy rejected the new config, so it was put back as it was." >&2
		exit 1
	fi
	systemctl reload caddy
}
write_routes
if ! grep -qx "# lionscraft $DOMAIN" "$CADDYFILE"; then
	cat >>"$CADDYFILE" <<EOF

# lionscraft $DOMAIN
$DOMAIN {
	import $ROUTES/*.caddy
}
EOF
fi
reload_caddy
if [ ! -f $CERT/cert.pem ]; then
	command -v certbot >/dev/null || apt-get install -y certbot
	certbot certonly --webroot -w $ACME_ROOT -d $DOMAIN --non-interactive --agree-tos \
		--register-unsafely-without-email --deploy-hook "$DIR/deploy/certbot-hook.sh"
	write_routes
	reload_caddy
fi
rm -f /tmp/$NAME.caddy.before

sleep 3
systemctl --no-pager --lines=8 status $NAME || true
MCP_KEY=$(grep '^MCP_KEY=' "$DIR/.env" | cut -d= -f2-)
cat <<EOF

GitHub deploy key (add once: GitHub repo > Settings > Deploy keys > Add deploy key, tick "Allow write access"):
$(cat $DATA/ssh/deploy_key.pub)

Preprod site:  https://$DOMAIN/
MCP server:    https://$DOMAIN/mcp/$MCP_KEY
EOF
