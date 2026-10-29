# Hermes, the Lionscraft website agent

Update the website content (text, links, case studies, articles, new pages) by chatting on **Telegram**, or from **Claude** (MCP server). Both use the same tools.

1. You ask for a change. Hermes changes a draft and sends you a preview link.
2. You say "publish". The change is saved to GitHub `main` (your backup) and the preprod site updates.
3. Check preprod. When it's good, say "release". Hermes moves the `live` branch to match preprod.
4. In Replit, pull from GitHub and press Redeploy. Replit follows the `live` branch, so it never gets changes you haven't released.

- Preprod (always the same as GitHub): https://v2202609411057512877.hotsrv.de/
- MCP server: `https://v2202609411057512877.hotsrv.de/mcp/<MCP_KEY>` (the key is in `.env` on the server)

It runs on the netcup server, next to the chat bot in `bot/`.

## First-time setup

**Replit, once:** open the Repl → Git pane → switch the branch to `live`. From then on, Pull + Redeploy gets only released changes.

1. **Telegram bot:** in Telegram, open **@BotFather**, send `/newbot`, copy the token.
2. **Token:** open the settings file and fill in `TELEGRAM_BOT_TOKEN` and `NOUS_API_KEY` (the same Nous key the OpenClaw bots use).

   ```bash
   ssh -t netcup nano /opt/lionscraft-website/.env
   ```

   ```bash
   ssh netcup systemctl restart lionscraft-website
   ```

3. **Your Telegram ID:** message your new bot. It answers with your ID. Put it in `TELEGRAM_ALLOWED_USERS` (several IDs: separate with commas) and restart again.
4. **GitHub access:** GitHub repo → Settings → Deploy keys → Add deploy key. Paste the key below and tick **Allow write access**.

   ```bash
   ssh netcup cat /var/lib/lionscraft-website/ssh/deploy_key.pub
   ```

5. **Claude (optional):** get the MCP link:

   ```bash
   ssh netcup grep MCP_KEY /opt/lionscraft-website/.env
   ```

   - Claude app: Settings → Connectors → Add custom connector → paste `https://v2202609411057512877.hotsrv.de/mcp/<MCP_KEY>`.
   - Claude Code: `claude mcp add --transport http lionscraft-website https://v2202609411057512877.hotsrv.de/mcp/<MCP_KEY>`

## Install or update on the server

From this repo on your Mac:

```bash
rsync -a --exclude .env --exclude data --exclude __pycache__ agent/ netcup:/opt/lionscraft-website/
```

```bash
ssh netcup bash /opt/lionscraft-website/deploy/setup.sh v2202609411057512877.hotsrv.de
```

Run both again after every change. Your keys in `.env` are kept.

## Using it

- Hermes chats about anything; its personality is in `SOUL.md` (edit it and redeploy to change it).
- `/status` shows the model, the draft and what's waiting for release. `/models` lists models, `/model sonnet` (or `/model 2`) switches for everyone and is kept after a restart.
- For the website, talk normally: "change the homepage headline to ...", "add a case study like the Lido one for ...", "undo the last change".
- `/new` starts a fresh conversation.
- In a private chat, only the people in `TELEGRAM_ALLOWED_USERS` can use it. In the groups in `TELEGRAM_ALLOWED_GROUPS`, Hermes answers every message from everyone. For that, the bot must be an admin of the group (otherwise Telegram only passes it messages that mention it or reply to it).
- "What's not live yet?" lists published changes that aren't released.

## Check on it

```bash
ssh netcup journalctl -u lionscraft-website -n 50
```

## Good to know

- It can only change files in `lionscraft-site.webflow/`.
- Telegram and Claude share one draft. "Publish" sends everything in it.
- Preprod pulls from GitHub every minute, so changes you push from your Mac show up there too.
- The MCP link lets anyone who has it change the draft, so don't share it. To make new keys, empty `MCP_KEY` and `PREVIEW_KEY` in `.env` and run the setup script again.
- It uses the Nous Research API, the same account as the OpenClaw bots, with Claude Opus 5.5. To use another model, change `MODEL` in `.env`.
- Chats are kept in memory; a restart starts fresh.
- The https certificate comes from Let's Encrypt through certbot (renews by itself), not from Caddy: the outreach chat bridge's self-signed certificate also names this server, so Caddy would skip it.

## Test on your Mac

```bash
pip install -r agent/requirements.txt
```

```bash
NOUS_API_KEY=... python agent/main.py chat
```

This works on a copy of the repo in `agent/data/` and publishes to the real GitHub, so use it with care.
