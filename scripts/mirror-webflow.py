"""Mirror lionscraft-site.webflow.io into a self-contained static folder.

Usage: python3 -I mirror.py <out_dir>
"""
import os
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

SITE = "https://lionscraft-site.webflow.io"
PAGES = {
    "index.html": "/",
    "legal/privacy-policy.html": "/legal/privacy-policy",
    "404.html": "/404",
    "401.html": "/401",
}
# Hosts whose files we copy locally. Other CDNs (jsdelivr, tagembed, gtag) stay external.
ASSET_URL = re.compile(
    r"https://(?:cdn\.prod\.website-files\.com|d3e54v103j8qbb\.cloudfront\.net|uploads-ssl\.webflow\.com)"
    r"/[^\"'\s<>,&]+"
)
CSS_URL = re.compile(r"""url\(\s*(?:"([^"]+)"|'([^']+)'|([^'")\s]+))\s*\)""")
UA = {"User-Agent": "Mozilla/5.0"}

OUT = os.path.abspath(sys.argv[1])
url_to_local = {}  # absolute asset url -> path relative to site root
used_names = {}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def folder_for(name):
    ext = os.path.splitext(name)[1].lower()
    if ext == ".css":
        return "css"
    if ext == ".js":
        return "js"
    if ext in (".mp4", ".webm", ".mov"):
        return "videos"
    if ext in (".woff", ".woff2", ".ttf", ".otf", ".eot"):
        return "fonts"
    return "images"


def local_name(url):
    path = urllib.parse.urlsplit(url).path
    base = urllib.parse.unquote(urllib.parse.unquote(path)).split("/")[-1]
    base = re.sub(r"^[0-9a-f]{24}_", "", base)
    base = re.sub(r"^[0-9a-f]{32}_", "", base)
    name, ext = os.path.splitext(base)
    name = re.sub(r"[^A-Za-z0-9._]+", "-", name.replace("+", " ")).strip("-") or "asset"
    rel = f"{folder_for(base)}/{name}{ext.lower()}"
    # keep names unique when two different urls clean to the same file name
    stem, n = rel, 2
    while rel in used_names and used_names[rel] != url:
        rel = re.sub(r"(\.[^.]+)$", rf"-{n}\1", stem)
        n += 1
    used_names[rel] = url
    return rel


def trim(url):
    # file names may contain "(1)"; a ")" with no matching "(" closes a css url()
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url


def register(url):
    url = trim(url)
    if url not in url_to_local:
        url_to_local[url] = local_name(url)
    return url_to_local[url]


def save(rel, data):
    dest = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)


def relative(from_file, target):
    return os.path.relpath(target, os.path.dirname(from_file) or ".").replace(os.sep, "/")


# 1. Fetch pages and collect asset urls
pages = {}
for out_name, path in PAGES.items():
    html = fetch(SITE + path).decode("utf-8")
    pages[out_name] = html
    for u in ASSET_URL.findall(html):
        register(u)
print(f"pages: {len(pages)}, assets referenced in html: {len(url_to_local)}")

# 2. Download assets; CSS gets its own url() references localized
failures = []


def download(item):
    url, rel = item
    try:
        return url, rel, fetch(url)
    except Exception as e:  # noqa: BLE001 - report and continue
        failures.append((url, str(e)))
        return url, rel, None


with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(download, list(url_to_local.items())))

css_assets = {}
for url, rel, data in results:
    if data is None:
        continue
    if rel.endswith(".css"):
        css = data.decode("utf-8")
        for groups in CSS_URL.findall(css):
            ref = next(g for g in groups if g)
            if ref.startswith("data:"):
                continue
            absu = trim(urllib.parse.urljoin(url, ref))
            if ASSET_URL.match(absu):
                css_assets[absu] = register(absu)
                css = css.replace(ref, relative(rel, url_to_local[absu]))
        data = css.encode("utf-8")
    save(rel, data)

with ThreadPoolExecutor(max_workers=8) as pool:
    for url, rel, data in pool.map(download, list(css_assets.items())):
        if data is not None:
            save(rel, data)

# 3. Rewrite pages: asset urls -> local files, internal links -> .html files
INTERNAL = {"/": "index.html", "/legal/privacy-policy": "legal/privacy-policy.html"}
for out_name, html in pages.items():
    # longest first so a url that prefixes another is not replaced partially
    for url in sorted(url_to_local, key=len, reverse=True):
        html = html.replace(url, relative(out_name, url_to_local[url]))
    for href, target in INTERNAL.items():
        html = html.replace(f'href="{href}"', f'href="{relative(out_name, target)}"')
    # jquery is requested with a ?site= query string; keep the local file name clean
    html = re.sub(r'(js/jquery[^"?]*\.js)\?site=[0-9a-f]+', r"\1", html)
    # local css is rewritten, so the cdn's subresource-integrity hashes no longer match
    html = re.sub(r'\s+integrity="[^"]*"', "", html)
    # webflow.js adds the "Made in Webflow" badge when a webflow.io domain runs elsewhere;
    # webflow's own code export omits this attribute
    html = re.sub(r'\s+data-wf-domain="[^"]*"', "", html)
    html = html.replace('<link href="https://cdn.prod.website-files.com" rel="preconnect" crossorigin="anonymous"/>', "")
    save(out_name, html.encode("utf-8"))

print(f"assets saved: {len(url_to_local) - len(failures)}, failed: {len(failures)}")
for url, err in failures:
    print("  FAIL", url, err)
