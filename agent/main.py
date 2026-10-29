"""Hermes, the Lionscraft website agent: update the website from Telegram, or from Claude through MCP.

One process runs three things:
- a Telegram bot that only answers the people in TELEGRAM_ALLOWED_USERS
- an MCP server at /mcp/<MCP_KEY>, plus the draft preview at /preview/<PREVIEW_KEY>/
- a loop that keeps the preprod copy in sync with GitHub

The Telegram side uses the Nous Research API (the same one the OpenClaw bots use), which speaks the OpenAI format.
Run `python main.py` to start it, or `python main.py chat` to talk to the agent in the terminal.
Settings come from environment variables; see .env.example.
"""
import functools
import hmac
import inspect
import json
import logging
import os
import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import openai
import requests
import uvicorn
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import FileResponse, PlainTextResponse, RedirectResponse

import website

MODELS = [  # good picks from the Nous API; /model also takes any other model id it offers
    "anthropic/claude-opus-5.5",
    "anthropic/claude-sonnet-5.5",
    "anthropic/claude-fable-5.1",
    "openai/gpt-6.1-sol",
    "google/gemini-3.1-pro-preview",
    "google/gemini-3.8-flash",
    "deepseek/deepseek-v4-pro-0813",
    "deepseek/deepseek-v4.1-flash",
    "moonshotai/kimi-k3",
    "x-ai/grok-4.7",
]
MODEL_FILE = website.DATA / "model.txt"  # the model picked with /model, kept across restarts
MODEL = MODEL_FILE.read_text().strip() if MODEL_FILE.exists() else os.environ.get("MODEL", "anthropic/claude-opus-5.5")
STARTED = datetime.now()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USERS = {u.strip() for u in os.environ.get("TELEGRAM_ALLOWED_USERS", "").split(",") if u.strip()}
ALLOWED_GROUPS = {g.strip() for g in os.environ.get("TELEGRAM_ALLOWED_GROUPS", "").split(",") if g.strip()}
MCP_KEY = os.environ.get("MCP_KEY", "")
SYNC_SECONDS = 60
MAX_HISTORY = 80  # messages kept per chat before it starts fresh
IDLE_RESET_SECONDS = 6 * 3600  # a chat starts fresh after this much quiet time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("agent")
client = openai.OpenAI(
    base_url=os.environ.get("LLM_BASE_URL", "https://inference-api.nousresearch.com/v1"),
    api_key=os.environ.get("NOUS_API_KEY") or "missing",
    timeout=300,
)

# Who Hermes is. Edit SOUL.md to change its personality.
SOUL = (Path(__file__).parent / "SOUL.md").read_text()

SYSTEM = f"""{SOUL}

# The website job

The Lionscraft website is a static site (HTML exported from Webflow) kept in GitHub. Your tools work on a draft copy of it. Use them only when someone wants something about the website; for anything else, just talk.
Keep the design as it is. Small layout fixes are fine when asked; for a redesign, say it is better done on a computer.

How a change goes:
1. Make the change in the draft. Prefer small exact edits: find_text, then replace_text. Keep the existing HTML, classes and look; change only what was asked. When something appears on several pages (menu, footer), use replace_everywhere once instead of editing page by page. Make independent tool calls together in one step.
2. Send the preview link of the changed page and say in a line or two what you changed.
3. Publish only after they say so (yes, ok, publish, go). Use a short commit message like "Add Ventures back to the menu". Publishing puts it on preprod, not live.
4. Release only when they say release (or "make it live"). unreleased_changes shows what would go live. After release, tell them to pull from GitHub in Replit and redeploy.
To undo a published change: recent_changes, then undo_change, then preview and publish as usual. To drop the draft: discard_changes.

Links inside the site are clean root paths: /services/advisory is the file services/advisory.html. Use the same style for new links.
The draft is shared: if show_changes lists changes you did not make in this chat, mention them before publishing.
If a website request is unclear (which page, what wording), ask one short question first.

Preprod site (what is on GitHub main): {website.preprod_url()}"""


def tool_schema(fn):
    """Function definition in the OpenAI format, from the signature and the "Args:" part of the docstring."""
    summary, _, args_doc = (inspect.getdoc(fn) or "").partition("Args:")
    descriptions = dict(re.findall(r"^\s*(\w+): (.+)$", args_doc, re.M))
    types = {str: "string", int: "integer", bool: "boolean"}
    properties, required = {}, []
    for name, param in inspect.signature(fn).parameters.items():
        properties[name] = {"type": types[param.annotation], "description": descriptions.get(name, "")}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": summary.strip(),
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


TOOLS = [tool_schema(fn) for fn in website.TOOLS]
TOOLS_BY_NAME = {fn.__name__: fn for fn in website.TOOLS}
SOMETHING_WRONG = "Sorry, something went wrong on my side. Try again, or send /new to start fresh."
HELP = (
    "I'm Hermes. Chat with me about anything, or ask me to change the Lionscraft website, like "
    "\"change the homepage headline to ...\". I show you a preview first, publish to preprod only when you say so, "
    "and release to the live branch only when you say \"release\". Then pull and redeploy in Replit.\n\n"
    "/status shows the model, draft and release state\n"
    "/models lists the models I can use, /model switches (like /model sonnet)\n"
    "/new starts a fresh conversation"
)
COMMANDS = [
    ("help", "What I can do"),
    ("status", "Model, draft and release state"),
    ("models", "Models I can use"),
    ("model", "Switch model, like /model sonnet"),
    ("new", "Start a fresh conversation"),
]


# One conversation per chat: {"messages": [...], "last": time, "lock": Lock}
chats = {}
chats_lock = threading.Lock()


def get_chat(key):
    with chats_lock:
        if key not in chats:
            chats[key] = {"messages": [], "last": 0.0, "lock": threading.Lock()}
        return chats[key]


def run_tool(call):
    fn = TOOLS_BY_NAME.get(call.function.name)
    if not fn:
        return f"Error: unknown tool {call.function.name}."
    try:
        return fn(**json.loads(call.function.arguments or "{}"))
    except website.SiteError as e:
        return f"Error: {e}"
    except Exception as e:
        log.exception("Tool %s failed", call.function.name)
        return f"Error: {type(e).__name__}: {e}"


def reply(key, text):
    """Answer one message in one chat, using the website tools as needed."""
    chat = get_chat(key)
    with chat["lock"]:
        if len(chat["messages"]) > MAX_HISTORY or time.time() - chat["last"] > IDLE_RESET_SECONDS:
            chat["messages"] = []
        chat["last"] = time.time()

        # Work on a copy so a failed call leaves the saved conversation untouched
        messages = chat["messages"] + [{"role": "user", "content": text}]
        try:
            for _ in range(40):
                response = client.chat.completions.create(
                    model=MODEL,
                    max_tokens=16000,
                    messages=[{"role": "system", "content": SYSTEM}, *messages],
                    tools=TOOLS,
                )
                message = response.choices[0].message
                if not message.tool_calls:
                    messages.append({"role": "assistant", "content": message.content or ""})
                    break
                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [call.model_dump() for call in message.tool_calls],
                })
                for call in message.tool_calls:
                    messages.append({"role": "tool", "tool_call_id": call.id, "content": run_tool(call)})
            else:
                return "That took too many steps, so I stopped. Send /new and try a smaller change."
        except openai.APIError as e:
            log.error("Model call failed: %s", e)
            return SOMETHING_WRONG

        chat["messages"] = messages
        return (message.content or "").strip() or SOMETHING_WRONG


# ---------- Telegram ----------

def telegram_api(method, **payload):
    r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}", json=payload, timeout=60)
    if not r.ok:
        log.error("Telegram %s failed: %s", method, r.text)
    return r


def keep_typing(chat_id, done):
    while not done.wait(4):
        telegram_api("sendChatAction", chat_id=chat_id, action="typing")


def models_text():
    lines = [f"{i}. {m}" + ("  <- now" if m == MODEL else "") for i, m in enumerate(MODELS, 1)]
    if MODEL not in MODELS:
        lines.append(f"Now: {MODEL}")
    return "\n".join(lines) + "\n\nSwitch with /model 2 or /model sonnet."


def set_model(choice):
    """Switches the model for every chat, and keeps it after a restart."""
    global MODEL
    if not choice:
        return models_text()
    if choice.isdigit() and 1 <= int(choice) <= len(MODELS):
        new = MODELS[int(choice) - 1]
    else:
        matches = [m for m in MODELS if choice.lower() in m.lower()]
        new = matches[0] if len(matches) == 1 else choice if not matches and "/" in choice else None
        if not new:
            return f"Which one? {', '.join(matches) or 'No match.'} Send /models for the list."
    try:
        offered = {m.id for m in client.models.list()}
        if offered and new not in offered:
            return f"The Nous API doesn't offer {new}."
    except openai.APIError:
        pass  # can't check the list right now; try the model anyway
    MODEL = new
    website.DATA.mkdir(parents=True, exist_ok=True)
    MODEL_FILE.write_text(MODEL)
    return f"Now using {MODEL}."


def status_text(chat_key):
    lines = [
        f"Model: {MODEL}",
        f"This chat: {len(get_chat(chat_key)['messages'])} messages in memory (/new clears it)",
        f"Running since {STARTED:%d %b %H:%M}",
    ]
    try:
        with website.lock:
            pages = website.changed_pages()
            pending = website.pending_release()
        lines.append(f"Draft: {len(pages)} unpublished file(s): {', '.join(pages[:5])}" if pages else "Draft: nothing unpublished")
        if pending is None:
            lines.append("Live: there is no live branch yet")
        else:
            lines.append(f"Live: {len(pending)} published change(s) waiting for release" if pending else "Live: same as preprod")
    except website.SiteError as e:
        lines.append(f"GitHub: {e}")
    lines.append(f"Preprod: {website.preprod_url()}")
    return "\n".join(lines)


def handle_telegram(msg):
    chat_id = msg["chat"]["id"]
    user_id = str(msg.get("from", {}).get("id", ""))
    text = msg.get("text", "").strip()
    group = msg["chat"]["type"] != "private"
    if group:
        if str(chat_id) not in ALLOWED_GROUPS:
            log.info("Ignored message in Telegram group %s", chat_id)
            return
        text = re.sub(re.escape(f"@{bot_user.get('username')}"), "", text, flags=re.I).strip()
    elif user_id not in ALLOWED_USERS:
        telegram_api("sendMessage", chat_id=chat_id, text=f"This is a private bot. Your Telegram ID is {user_id}.")
        log.info("Ignored message from Telegram user %s", user_id)
        return

    def say(answer):
        # In a group, answer as a reply so it is clear who it is for
        extra = {"reply_parameters": {"message_id": msg["message_id"]}} if group else {}
        for i in range(0, len(answer), 4000):
            telegram_api("sendMessage", chat_id=chat_id, text=answer[i:i + 4000], link_preview_options={"is_disabled": True}, **extra)

    if not text:
        say(HELP if group else "I can only read text messages for now.")
        return
    command, _, arg = text.partition(" ")
    command = command.split("@")[0].lower() if command.startswith("/") else ""
    if command in ("/start", "/help"):
        say(HELP)
        return
    if command == "/new":
        get_chat(chat_id)["messages"] = []
        say("OK, fresh start.")
        return
    if command == "/status":
        say(status_text(chat_id))
        return
    if command == "/models":
        say(models_text())
        return
    if command == "/model":
        say(set_model(arg.strip()))
        return
    done = threading.Event()
    telegram_api("sendChatAction", chat_id=chat_id, action="typing")
    threading.Thread(target=keep_typing, args=(chat_id, done), daemon=True).start()
    try:
        answer = reply(chat_id, text)
    finally:
        done.set()
    say(answer)


bot_user = {}  # Hermes's own Telegram user, from getMe


def telegram_loop():
    telegram_api("deleteWebhook")
    bot_user.update(telegram_api("getMe").json().get("result", {}))
    telegram_api("setMyCommands", commands=[{"command": c, "description": d} for c, d in COMMANDS])
    offset = None
    log.info("Telegram agent listening")
    while True:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
                params={"timeout": 25, "offset": offset, "allowed_updates": '["message"]'},
                timeout=35,
            )
            data = r.json()
            if not data.get("ok"):
                log.error("Telegram getUpdates failed: %s", data)
                time.sleep(5)
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                if update.get("message"):
                    threading.Thread(target=handle_telegram, args=(update["message"],), daemon=True).start()
        except requests.exceptions.Timeout:
            log.info("Telegram poll timed out, trying again")
        except Exception:
            log.exception("Telegram polling error")
            time.sleep(5)


# ---------- GitHub sync ----------

def sync_loop():
    while True:
        try:
            website.sync()
        except Exception as e:
            log.warning("Could not sync with GitHub (is the deploy key added?): %s", e)
        time.sleep(SYNC_SECONDS)


# ---------- MCP server and draft preview ----------

mcp = MCPServer(
    name="lionscraft-website",
    instructions=(
        "Tools for content updates on the Lionscraft website (a static Webflow export kept in GitHub). "
        "Changes go into a draft first. Show the user the preview link and what you changed, "
        "and call publish only after they agree. Publishing pushes to GitHub main and updates the preprod site "
        f"({website.preprod_url()}). Call release only when the user says so: it moves the live branch that "
        "Replit deploys; the user then pulls and redeploys in Replit."
    ),
)


def mcp_tool(fn):
    """Registers a website tool so its error messages reach Claude, not just "Error executing tool"."""
    @functools.wraps(fn)
    def run(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except website.SiteError as e:
            raise ToolError(str(e)) from e
    mcp.tool()(run)


for fn in website.TOOLS:
    mcp_tool(fn)


# The site links to root paths like /services, so the draft can't live under /preview/<key>/. Instead the
# preview link sets a cookie, and Caddy sends every request that has it to draft_site.
PREVIEW_COOKIE = "hermes_preview"


def is_preview_key(key):
    return bool(website.PREVIEW_KEY) and hmac.compare_digest(key.encode(), website.PREVIEW_KEY.encode())


@mcp.custom_route("/preview/{key}/{path:path}", methods=["GET"])
async def preview(request):
    """Turns on the draft preview in this browser for an hour, then opens the page."""
    key = request.path_params["key"]
    if not is_preview_key(key):
        return PlainTextResponse("not found", status_code=404)
    response = RedirectResponse("/" + request.path_params["path"], status_code=303)
    response.set_cookie(PREVIEW_COOKIE, key, max_age=3600, httponly=True, secure=True, samesite="lax")
    return response


@mcp.custom_route("/preview-off", methods=["GET"])
async def preview_off(request):
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(PREVIEW_COOKIE)
    return response


@mcp.custom_route("/draft-site/{path:path}", methods=["GET"])
async def draft_site(request):
    """The site as it is in the draft, unpublished changes included, for browsers with the preview cookie."""
    repo = website.DRAFT if is_preview_key(request.cookies.get(PREVIEW_COOKIE, "")) else website.PREPROD
    path = website.site_file(repo, request.path_params["path"])
    if not path:
        return PlainTextResponse("not found", status_code=404)
    return FileResponse(path, headers={"X-Robots-Tag": "noindex", "Cache-Control": "no-store"})


def http_app():
    # Without MCP_KEY only the preview is served; the random path stops anyone else from using the tools
    return mcp.streamable_http_app(
        streamable_http_path=f"/mcp/{MCP_KEY}" if MCP_KEY else "/mcp-off",
        stateless_http=True,
        json_response=True,
        # Caddy in front sends the public host name; the secret path is the protection here
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )


def terminal_chat():
    website.sync()
    print(HELP + "\n(type 'quit' to stop)\n")
    while (text := input("you> ").strip()) != "quit":
        if text:
            print("agent>", reply("terminal", text), "\n")


if __name__ == "__main__":
    if sys.argv[1:] == ["chat"]:
        terminal_chat()
        sys.exit()
    threading.Thread(target=sync_loop, daemon=True).start()
    if TELEGRAM_TOKEN:
        threading.Thread(target=telegram_loop, daemon=True).start()
    else:
        log.info("No TELEGRAM_BOT_TOKEN set, Telegram is off")
    if not MCP_KEY:
        log.info("No MCP_KEY set, the MCP server is off")
    # access_log is off so the secret keys in the paths stay out of the logs
    uvicorn.run(
        http_app(),
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8791")),
        access_log=False,
    )
