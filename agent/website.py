"""Website tools, shared by the Telegram agent and the MCP server.

The server keeps two copies of the GitHub repo:
- draft: where changes are made. Unpublished changes show at the preview link.
- preprod: always the latest GitHub main. It is served as the preprod site.

Publishing commits the draft and pushes it to GitHub main, so GitHub keeps every version.
Releasing moves the live branch, which Replit deploys, up to main.
"""
import difflib
import html
import logging
import os
import re
import shutil
import subprocess
import threading
import time
from html.parser import HTMLParser
from pathlib import Path

REPO_URL = os.environ.get("GITHUB_REPO", "git@github.com:Lionscraft-io/lionscraft-website.git")
BRANCH = os.environ.get("GITHUB_BRANCH", "main")
LIVE_BRANCH = os.environ.get("LIVE_BRANCH", "live")  # what Replit deploys; moves only on release
SITE_FOLDER = "lionscraft-site.webflow"
DATA = Path(os.environ.get("DATA_DIR", Path(__file__).parent / "data"))
DRAFT = DATA / "draft"
PREPROD = DATA / "preprod"
PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://127.0.0.1:8791").rstrip("/")
PREVIEW_KEY = os.environ.get("PREVIEW_KEY", "")
SSH_KEY = os.environ.get("GIT_SSH_KEY", "")
GIT_NAME = os.environ.get("GIT_NAME", "Lionscraft site agent")
GIT_EMAIL = os.environ.get("GIT_EMAIL", "site-agent@noreply.lionscraft.io")
TEXT_FILES = {".html", ".css", ".js", ".json", ".xml", ".txt", ".svg", ".md"}
MAX_OUTPUT = 20000  # characters a tool sends back, so one page does not flood the chat
FRESH_SECONDS = 120  # how old the draft may be before a tool refreshes it; the background sync runs every minute

log = logging.getLogger("website")
lock = threading.RLock()
last_sync = 0.0


class SiteError(Exception):
    """A problem the agent should explain or work around, like text that was not found."""


# ---------- git ----------

def git(*args, cwd=DRAFT, check=True):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    if SSH_KEY:
        env["GIT_SSH_COMMAND"] = (
            f"ssh -i {SSH_KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new "
            f"-o UserKnownHostsFile={Path(SSH_KEY).parent / 'known_hosts'}"
        )
    r = subprocess.run(
        ["git", "-c", f"user.name={GIT_NAME}", "-c", f"user.email={GIT_EMAIL}", *args],
        cwd=cwd, env=env, capture_output=True, text=True, errors="replace", timeout=120,
    )
    if check and r.returncode:
        raise SiteError(f"git {args[0]} failed: {(r.stderr or r.stdout).strip()}")
    return r.stdout


def ensure_clones():
    DATA.mkdir(parents=True, exist_ok=True)
    for repo in (DRAFT, PREPROD):
        if not (repo / ".git").exists():
            shutil.rmtree(repo, ignore_errors=True)
            git("clone", "-q", "--branch", BRANCH, "--single-branch", REPO_URL, str(repo), cwd=DATA)
            log.info("Cloned %s into %s", REPO_URL, repo)


def has_changes():
    return bool(git("status", "--porcelain").strip())


def sync():
    """Bring preprod up to GitHub main, and the draft too when it has no unpublished changes."""
    global last_sync
    with lock:
        ensure_clones()
        git("fetch", "-q", "origin", BRANCH)  # the only download from GitHub
        if not has_changes():
            git("reset", "-q", "--hard", f"origin/{BRANCH}")
        # Preprod takes the same commit straight from the draft clone
        git("fetch", "-q", str(DRAFT), f"refs/remotes/origin/{BRANCH}", cwd=PREPROD)
        git("reset", "-q", "--hard", "FETCH_HEAD", cwd=PREPROD)
        last_sync = time.time()


def refresh():
    if time.time() - last_sync > FRESH_SECONDS:
        sync()


# ---------- helpers ----------

def site_root(repo=DRAFT):
    return repo / SITE_FOLDER


def site_path(page, must_exist=True):
    root = site_root().resolve()
    path = (root / page.strip().lstrip("/")).resolve()
    if not path.is_relative_to(root) or path == root:
        raise SiteError(f"{page} is not a file in the website folder.")
    if must_exist and not path.is_file():
        raise SiteError(f"{page} does not exist. Use list_pages to see the pages.")
    return path


def rel(path):
    return path.relative_to(site_root().resolve()).as_posix()


def text_file(page, must_exist=True):
    path = site_path(page, must_exist)
    if path.suffix.lower() not in TEXT_FILES:
        raise SiteError(f"{page} is not a text file I can edit.")
    return path


def clean_url(page):
    """The site uses clean links: services/advisory.html is /services/advisory, index.html is /."""
    page = re.sub(r"(^|/)index\.html$", r"\1", page)
    return page[:-5] if page.endswith(".html") else page


def site_file(repo, url_path):
    """The file a clean link points to (/services -> services.html), or None."""
    root = site_root(repo).resolve()
    url_path = url_path.strip("/")
    names = [url_path, f"{url_path}.html", f"{url_path}/index.html"] if url_path else ["index.html"]
    for name in names:
        path = (root / name).resolve()
        if path.is_relative_to(root) and path.is_file():
            return path
    return None


def preview_url(page):
    if not PREVIEW_KEY:
        return "(preview is off: PREVIEW_KEY is not set)"
    return f"{PUBLIC_URL}/preview/{PREVIEW_KEY}/{clean_url(page)}"


def preprod_url(page=""):
    return f"{PUBLIC_URL}/{clean_url(page)}"


def clip(text, limit=MAX_OUTPUT):
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... (cut off, {len(text) - limit} more characters)"


def changed_pages():
    pages = []
    for line in git("status", "--porcelain", "-uall", "--", SITE_FOLDER).splitlines():
        name = line[3:].split(" -> ")[-1].strip('"')
        if name.startswith(SITE_FOLDER + "/"):
            pages.append(name[len(SITE_FOLDER) + 1:])
    return pages


def word_diff(old, new):
    """Only the changed words, as [-old-]{+new+} with a little text around them.
    The Webflow pages have very long lines, so a normal line diff would show whole pages."""
    a, b = old.splitlines(), new.splitlines()
    parts = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op != "equal":
            parts += changed_words("\n".join(a[i1:i2]), "\n".join(b[j1:j2]))
    return "\n".join(parts)


def changed_words(old, new, context=80):
    # Skip what both share at the start and end (backing up to a word edge), then compare the words between
    start = len(os.path.commonprefix([old, new]))
    end = len(os.path.commonprefix([old[start:][::-1], new[start:][::-1]]))
    while start and old[start - 1].isalnum():
        start -= 1
    while end and old[-end].isalnum():
        end -= 1
    head, tail = old[:start], old[len(old) - end:]
    words = re.compile(r"\w+|\s+|[^\w\s]")
    a, b = words.findall(old[start:len(old) - end]), words.findall(new[start:len(new) - end])
    ops = []
    for op in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        # A change, a space, and another change read better as one change
        if ops and ops[-1][0] != "equal" and (op[0] != "equal" or not "".join(a[op[1]:op[2]]).strip()):
            ops[-1] = ("replace", ops[-1][1], op[2], ops[-1][3], op[4])
        else:
            ops.append(op)
    parts = []
    for op, i1, i2, j1, j2 in ops:
        if op == "equal":
            continue
        before = (head + "".join(a[:i1]))[-context:]
        after = ("".join(a[i2:]) + tail)[:context]
        removed, added = "".join(a[i1:i2]), "".join(b[j1:j2])
        change = (f"[-{removed}-]" if removed else "") + (f"{{+{added}+}}" if added else "")
        parts.append(f"  ...{before}{change}{after}...")
    return parts


class TextOutline(HTMLParser):
    """Collects the visible text of a page with its line number, tag and link."""

    SKIP = {"script", "style", "noscript", "svg", "head"}
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # (tag, href)
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img" and attrs.get("alt") and not self.skipping():
            self.rows.append(f"L{self.getpos()[0]} img alt: {attrs['alt']}")
        if tag not in self.VOID:
            self.stack.append((tag, attrs.get("href")))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def skipping(self):
        return any(tag in self.SKIP for tag, _ in self.stack)

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text or self.skipping():
            return
        tag = self.stack[-1][0] if self.stack else ""
        href = next((h for t, h in reversed(self.stack) if t == "a" and h), None)
        self.rows.append(f"L{self.getpos()[0]} {tag}: {text}" + (f"  (link: {href})" if href else ""))


# ---------- tools ----------

def list_pages() -> str:
    """List every page of the website with its title."""
    with lock:
        refresh()
        rows = []
        for path in sorted(site_root().rglob("*.html")):
            match = re.search(r"<title>(.*?)</title>", path.read_text(errors="replace"), re.S)
            title = html.unescape(match.group(1).strip()) if match else ""
            rows.append(f"{rel(path.resolve())}: {title}")
        return "\n".join(rows)


def page_text(page: str) -> str:
    """Show the visible text of a page, line by line, with tags and links. Use it to see what a page says.

    Args:
        page: Page file, like index.html or legal/privacy-policy.html.
    """
    with lock:
        refresh()
        parser = TextOutline()
        parser.feed(text_file(page).read_text(errors="replace"))
        return clip("\n".join(parser.rows) or "(no visible text)")


def find_text(text: str, page: str = "") -> str:
    """Find text in the HTML of the website. Shows file, line number and the HTML around each match.

    Text split by tags (like <span>) will not match as a whole, so search for a short piece.

    Args:
        text: Text to look for. Not case sensitive.
        page: Only search this page. Leave empty to search every page.
    """
    with lock:
        refresh()
        files = [text_file(page)] if page else sorted(site_root().rglob("*.html"))
        needles = {text.lower(), html.escape(text, quote=False).lower()}
        hits = []
        for path in files:
            for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
                low = line.lower()
                spot = min((low.find(n) for n in needles if n in low), default=-1)
                if spot < 0:
                    continue
                start, end = max(spot - 200, 0), min(spot + len(text) + 200, len(line))
                snippet = ("..." if start else "") + line[start:end] + ("..." if end < len(line) else "")
                hits.append(f"{rel(path.resolve())}:{number}: {snippet.strip()}")
                if len(hits) >= 40:
                    return clip("\n".join(hits) + "\n(stopped after 40 matches)")
        return clip("\n".join(hits)) if hits else f"No match for {text!r}."


def read_html(page: str, start_line: int, end_line: int) -> str:
    """Show the raw HTML of a page between two line numbers.

    Args:
        page: Page file, like index.html.
        start_line: First line to show (from 1).
        end_line: Last line to show.
    """
    with lock:
        refresh()
        lines = text_file(page).read_text(errors="replace").splitlines()
        shown = [f"{n}: {lines[n - 1]}" for n in range(max(start_line, 1), min(end_line, len(lines)) + 1)]
        return clip("\n".join(shown) or f"The page has {len(lines)} lines.")


def replace_text(page: str, old: str, new: str, replace_all: bool = False) -> str:
    """Replace exact text in a file of the draft. The old text must match the HTML exactly, including tags and spaces.

    Args:
        page: File to change, like index.html or css/lionscraft.css.
        old: The exact text to replace. Copy it from find_text or read_html.
        new: The text to put in its place.
        replace_all: Replace every match. Without it, the old text must appear exactly once.
    """
    with lock:
        refresh()
        path = text_file(page)
        content = path.read_text(errors="replace")
        count = content.count(old)
        if not old or count == 0:
            raise SiteError(f"The old text was not found in {page}. Check it with find_text or read_html.")
        if count > 1 and not replace_all:
            raise SiteError(f"The old text appears {count} times in {page}. Add more text around it, or use replace_all.")
        path.write_text(content.replace(old, new))
        return f"Changed {count} place(s) in {page}. Preview: {preview_url(page)}"


def replace_everywhere(old: str, new: str) -> str:
    """Replace exact text on every HTML page of the draft at once. Use it for things on many pages, like the menu or footer.

    Args:
        old: The exact text to replace, as it is in the HTML.
        new: The text to put in its place.
    """
    with lock:
        refresh()
        if not old:
            raise SiteError("The old text is empty.")
        changed = []
        for path in sorted(site_root().rglob("*.html")):
            content = path.read_text(errors="replace")
            if old in content:
                path.write_text(content.replace(old, new))
                changed.append(f"{rel(path.resolve())} ({content.count(old)}x)")
        if not changed:
            raise SiteError("The old text was not found on any page. Check it with find_text.")
        return f"Changed {len(changed)} pages: {', '.join(changed)}. Preview: {preview_url('index.html')}"


def copy_page(source: str, new_page: str) -> str:
    """Copy a page to a new file, as a starting point for a new page. Then change its text with replace_text.

    Args:
        source: Existing page to copy, like case-lido.html.
        new_page: Name of the new page, like case-acme.html.
    """
    with lock:
        refresh()
        src, dest = text_file(source), text_file(new_page, must_exist=False)
        if dest.exists():
            raise SiteError(f"{new_page} already exists.")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        return f"Copied {source} to {new_page}. Preview: {preview_url(new_page)}"


def write_file(page: str, content: str) -> str:
    """Create a text file, or replace a whole file, in the draft. For small edits use replace_text instead.

    Args:
        page: File to write, like robots.txt or a new page.
        content: The full content of the file.
    """
    with lock:
        refresh()
        path = text_file(page, must_exist=False)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return f"Wrote {page}. Preview: {preview_url(page)}"


def delete_file(page: str) -> str:
    """Delete a file from the draft.

    Args:
        page: File to delete, like old-page.html or images/old.png.
    """
    with lock:
        refresh()
        site_path(page).unlink()
        return f"Deleted {page} in the draft."


def show_changes() -> str:
    """Show what is changed in the draft and not published yet, with preview links."""
    with lock:
        if not has_changes():
            return "No unpublished changes. The draft is the same as GitHub."
        report = []
        for page in changed_pages():
            path = site_root() / page
            link = f" (preview: {preview_url(page)})" if page.endswith(".html") and path.exists() else ""
            existed = git("ls-tree", "--name-only", "HEAD", f"{SITE_FOLDER}/{page}").strip()
            if not path.exists():
                report.append(f"{page}: deleted")
            elif not existed:
                report.append(f"{page}: new file{link}")
            elif path.suffix.lower() in TEXT_FILES:
                old = git("show", f"HEAD:{SITE_FOLDER}/{page}")
                report.append(f"{page}{link}\n{word_diff(old, path.read_text(errors='replace'))}")
            else:
                report.append(f"{page}: changed{link}")
        return clip("\n\n".join(report))


def publish(message: str) -> str:
    """Publish the draft: save all its changes to GitHub. The preprod site updates right after.
    Only do this when the user said to publish.

    Args:
        message: Short summary of the change, like "Add Ventures back to the menu".
    """
    with lock:
        if not has_changes():
            return "Nothing to publish: the draft has no changes."
        git("add", "-A", SITE_FOLDER)
        git("commit", "-q", "-m", message.strip() or "Update website")
        # On any failure, undo the local commit so the change stays in the draft
        try:
            git("fetch", "-q", "origin", BRANCH)
        except SiteError as e:
            git("reset", "-q", "--soft", "HEAD~1")
            raise SiteError(f"Could not reach GitHub, the change is still in the draft. {e}")
        try:
            git("rebase", "-q", f"origin/{BRANCH}")
        except SiteError:
            git("rebase", "--abort", check=False)
            git("reset", "-q", "--soft", "HEAD~1")
            raise SiteError("GitHub has newer changes to the same lines. Discard the draft and make the change again.")
        try:
            git("push", "-q", "origin", f"HEAD:{BRANCH}")
        except SiteError as e:
            git("reset", "-q", "--soft", "HEAD~1")
            raise SiteError(f"Could not push to GitHub, the change is still in the draft. {e}")
        commit = git("rev-parse", "--short", "HEAD").strip()
        sync()
        return (
            f"Published as {commit} on GitHub. Preprod is updated: {preprod_url()}\n"
            "It is not live yet. When they say release, call release."
        )


def discard_changes() -> str:
    """Throw away all unpublished changes in the draft, so it is the same as GitHub again."""
    with lock:
        git("reset", "-q", "--hard")
        git("clean", "-q", "-fd", "--", SITE_FOLDER)
        sync()
        return "Draft discarded. It is the same as GitHub again."


def recent_changes(count: int = 10) -> str:
    """List the latest published changes on GitHub (newest first).

    Args:
        count: How many changes to show.
    """
    with lock:
        refresh()
        return git("log", f"-n{min(max(count, 1), 50)}", "--date=short", "--format=%h %ad %an: %s", f"origin/{BRANCH}")


def undo_change(commit: str) -> str:
    """Undo a published change: puts the reverse of that commit into the draft. Preview it, then publish.

    Args:
        commit: The commit id from recent_changes, like a1b2c3d.
    """
    with lock:
        sync()
        if has_changes():
            raise SiteError("The draft has unpublished changes. Publish or discard them first.")
        files = git("show", "--name-only", "--format=", commit).split()
        if any(not f.startswith(SITE_FOLDER + "/") for f in files):
            raise SiteError(f"{commit} also changed files outside the website. Undo it on a computer instead.")
        git("revert", "--no-commit", commit)
        git("revert", "--quit", check=False)
        pages = changed_pages()
        links = "\n".join(f"{p}: {preview_url(p)}" for p in pages if p.endswith(".html"))
        return f"Undo of {commit} is in the draft. Preview:\n{links or ', '.join(pages)}"


def fetch_live():
    """Fetches the live branch; False when it does not exist yet."""
    try:
        git("fetch", "-q", "origin", f"+refs/heads/{LIVE_BRANCH}:refs/remotes/origin/{LIVE_BRANCH}")
        return True
    except SiteError:
        return False


def pending_release():
    """Published commits that are not on the live branch yet, newest first; None when there is no live branch."""
    sync()
    if not fetch_live():
        return None
    return git("log", "--date=short", "--format=%h %ad %an: %s", f"origin/{LIVE_BRANCH}..origin/{BRANCH}").splitlines()


def unreleased_changes() -> str:
    """List the published changes that are on preprod but not live yet (not on the branch Replit deploys)."""
    with lock:
        pending = pending_release()
        if pending is None:
            return f"There is no {LIVE_BRANCH} branch yet. release will create it from preprod."
        return "\n".join(pending) or "Nothing to release: live is the same as preprod."


def release() -> str:
    """Release: make the live branch, which Replit deploys, the same as preprod (GitHub main).
    Only do this when the user says release. After it, they pull and redeploy in Replit.
    """
    with lock:
        pending = pending_release()
        if pending == []:
            return "Nothing to release: live is the same as preprod."
        try:
            # Not forced, so GitHub refuses if live has commits that main does not have
            git("push", "-q", "origin", f"refs/remotes/origin/{BRANCH}:refs/heads/{LIVE_BRANCH}")
        except SiteError as e:
            raise SiteError(f"Could not move {LIVE_BRANCH}; it may have changes that are not on main. {e}")
        released = "\n".join(pending) if pending else "everything (new live branch)"
        return f"Released to {LIVE_BRANCH}:\n{released}\nTo go live: in Replit, pull from GitHub and redeploy."


TOOLS = [
    list_pages, page_text, find_text, read_html, replace_text, replace_everywhere, copy_page, write_file, delete_file,
    show_changes, publish, discard_changes, recent_changes, undo_change, unreleased_changes, release,
]
