"""Serves site/ for previews, with clean links like the deployed site: /services opens services.html.

Run `python3 serve.py` (Replit's Run button does this). Set PORT to change the port (default 8080).
"""
import functools
import http.server
import os
from pathlib import Path

SITE = Path(__file__).parent / "site"
PORT = int(os.environ.get("PORT", "8080"))


class CleanLinks(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        full = super().translate_path(path)
        page = full.rstrip("/") + ".html"
        # /services is services.html, even though there is also a services/ folder
        if os.path.exists(page) and not os.path.isfile(os.path.join(full, "index.html")):
            return page
        return full

    def send_error(self, code, message=None, explain=None):
        if code == 404 and (SITE / "404.html").exists():
            body = (SITE / "404.html").read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().send_error(code, message, explain)


if __name__ == "__main__":
    print(f"Lionscraft site: http://localhost:{PORT}")
    handler = functools.partial(CleanLinks, directory=str(SITE))
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), handler).serve_forever()
