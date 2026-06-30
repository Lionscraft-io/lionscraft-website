# Lionscraft Website

Static website for Lionscraft — a Web3 venture and innovation studio.

This is a static export from Webflow (the design lives in `lionscraft-site.webflow/`).
CMS-driven content (the "ecosystem works" section) and a handful of assets that
Webflow's exporter omitted were recovered from the live site (lionscraft.io) and
baked into the static files.

## Run locally

```bash
cd lionscraft-site.webflow
python3 -m http.server 8000
# open http://localhost:8000
```

## Structure

- `lionscraft-site.webflow/` — exported site (HTML, CSS, JS, images, videos, fonts)
  - `index.html` — homepage
  - `detail_works.html`, `detail_post.html` — Webflow CMS single-item templates
  - `legal/privacy-policy.html`
  - `css/`, `js/`, `images/`, `videos/`, `fonts/`

## Notes

- Forms do not submit (Webflow handled the backend).
- Some third-party widgets (analytics, embeds) load from external CDNs and need internet.
