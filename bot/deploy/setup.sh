#!/bin/bash
# Installs or updates the Lionscraft bot on a Debian server that runs Caddy.
# Run as root after copying the bot folder to /opt/lionscraft-bot:
#   bash /opt/lionscraft-bot/deploy/setup.sh <domain>
# Safe to run again after every code change.
set -euo pipefail

DOMAIN="${1:?usage: setup.sh <domain>}"
DIR=/opt/lionscraft-bot
PORT=8790
CADDYFILE=/etc/caddy/Caddyfile
ROUTES=/etc/caddy/routes.d

python3 -c "import ensurepip" 2>/dev/null || apt-get install -y python3-venv
id lionscraft-bot >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin lionscraft-bot

[ -d "$DIR/venv" ] || python3 -m venv "$DIR/venv"
"$DIR/venv/bin/pip" install -q --upgrade -r "$DIR/requirements.txt"

# Secrets: created once from the example, readable by root only (systemd reads it)
[ -f "$DIR/.env" ] || cp "$DIR/.env.example" "$DIR/.env"
chown root:root "$DIR/.env"
chmod 600 "$DIR/.env"

cp "$DIR/deploy/lionscraft-bot.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable lionscraft-bot
systemctl restart lionscraft-bot

# Caddy: one site block for the domain, shared with the website agent. Each app adds its own routes file.
# Caddy gets the https certificate itself.
mkdir -p "$ROUTES"
if [ ! -f "$ROUTES/lionscraft-bot.caddy" ] || ! grep -qx "# lionscraft $DOMAIN" "$CADDYFILE"; then
	cp "$CADDYFILE" "$CADDYFILE.before-bot"
	cat >"$ROUTES/lionscraft-bot.caddy" <<EOF
handle /whatsapp {
	reverse_proxy 127.0.0.1:$PORT
}
EOF
	if ! grep -qx "# lionscraft $DOMAIN" "$CADDYFILE"; then
		cat >>"$CADDYFILE" <<EOF

# lionscraft $DOMAIN
$DOMAIN {
	import $ROUTES/*.caddy
}
EOF
	fi
	if ! caddy validate --config "$CADDYFILE" --adapter caddyfile; then
		cp "$CADDYFILE.before-bot" "$CADDYFILE"
		rm "$ROUTES/lionscraft-bot.caddy"
		echo "Caddy rejected the new config, so it was put back as it was." >&2
		exit 1
	fi
	systemctl reload caddy
fi

sleep 2
systemctl --no-pager --lines=5 status lionscraft-bot
echo
echo "WhatsApp webhook URL: https://$DOMAIN/whatsapp"
