# Lionscraft chat bot

One bot that answers on **WhatsApp** (and Telegram, if you want it). It:

- answers questions about Lionscraft (only from `knowledge.md`)
- shares the booking link (cal.com/team/lionscraft/meet)
- sends new leads to the team
- signs people up for the newsletter

To change what it knows, edit `knowledge.md`. To change how it talks, edit `SYSTEM` in `main.py`.

It runs on the netcup server, at `https://v2202609411057512877.hotsrv.de/whatsapp`.

## Install or update on the server

From this repo on your Mac:

```bash
rsync -a --exclude .env --exclude subscribers.csv --exclude __pycache__ bot/ netcup:/opt/lionscraft-bot/
```

```bash
ssh netcup bash /opt/lionscraft-bot/deploy/setup.sh v2202609411057512877.hotsrv.de
```

Run both again after every change. Your keys in `.env` are kept.

## Add the keys

```bash
ssh -t netcup nano /opt/lionscraft-bot/.env
```

```bash
ssh netcup systemctl restart lionscraft-bot
```

## WhatsApp: test number first (today)

1. developers.facebook.com → **Create app** → choose **WhatsApp**.
2. **WhatsApp → API Setup**: copy the **Phone number ID** and the **temporary token** (it lasts 24 hours). In "To", add your own phone.
3. **App settings → Basic**: copy the **App secret**.
4. In `.env`, fill in `ANTHROPIC_API_KEY`, `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_APP_SECRET`, and make up a word for `WHATSAPP_VERIFY_TOKEN`. Restart the bot.
5. **WhatsApp → Configuration → Webhook**: Callback URL `https://v2202609411057512877.hotsrv.de/whatsapp`, Verify token = your word. Then subscribe to **messages**.
6. Send a WhatsApp message to the test number. The bot answers.

## WhatsApp: going live

- Add a phone number that is **not** used in the normal WhatsApp app.
- Verify the business in Meta (company documents, takes a few days).
- Make a permanent token: Business Settings → **System users** → generate a token with `whatsapp_business_messaging`. Put it in `WHATSAPP_TOKEN`.

Meta charges per conversation. Answering people who message you first is the cheapest kind.

## Telegram (optional)

1. In Telegram, open **@BotFather**, send `/newbot`, and put the token in `TELEGRAM_BOT_TOKEN`.
2. For lead alerts: add the bot to a team group, send `/chatid`, and put the number in `TEAM_TELEGRAM_CHAT_ID`.

## Check on it

```bash
ssh netcup journalctl -u lionscraft-bot -n 50
```

Newsletter signups are saved on the server in `/var/lib/lionscraft-bot/subscribers.csv`.

## Test on your Mac

```bash
pip install -r bot/requirements.txt
```

```bash
ANTHROPIC_API_KEY=sk-... python bot/main.py chat
```

## Good to know

- It uses Claude Opus 5.5 on low effort, roughly a few cents per conversation.
- Each person can send 40 messages a day (`DAILY_MESSAGE_LIMIT`), so nobody can run up your bill.
- Chats are kept in memory. A restart starts everyone fresh. Leads and signups are not lost.
- Later you can use `bot.lionscraft.io` instead: point it to `89.58.62.79` in your DNS, then run the setup script with that name.
