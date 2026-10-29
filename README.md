# Lionscraft Website

Static website for Lionscraft — digital, financial and risk infrastructure.

The site in `lionscraft-site.webflow/` is a self-contained copy of the Webflow
site at https://lionscraft-site.webflow.io: pages, CSS, JS, images, videos and
fonts are all stored locally, so it runs on any static host (Replit, Netlify,
Vercel, GitHub Pages) without Webflow.

## Run locally

```bash
python3 -m http.server 8000 --directory lionscraft-site.webflow
# open http://localhost:8000
```

## Replit

The `.replit` file serves `lionscraft-site.webflow/` when you press Run and
deploys it as a static site (Deploy → Static, public directory
`lionscraft-site.webflow`).

## Updating from Webflow

After publishing changes in Webflow, refresh the copy with:

```bash
rm -rf lionscraft-site.webflow
python3 scripts/mirror-webflow.py lionscraft-site.webflow
```

The script downloads every published page and the assets they use from the
Webflow CDN, rewrites links to the local files, and removes the Webflow-only
bits that break off Webflow (CSS integrity hashes and the `data-wf-domain`
attribute that triggers the "Made in Webflow" badge).

## Structure

- `lionscraft-site.webflow/` (served with clean URLs: `/services/advisory` → `services/advisory.html`)
  - `index.html` — homepage; `our-story.html`
  - `services.html` + `services/` — Advisory, Build, Operate, Structure
  - `intelligence.html` + `intelligence/` — Research (with articles in `intelligence/research/`), Data & Tools, Training
  - `case-studies.html` + `case-studies/` — one page per case study
  - `legal/privacy-policy.html`, `404.html`, `401.html`, `sitemap.xml`, `robots.txt`
  - `css/`, `js/`, `images/`, `videos/`, `fonts/` (all linked root-relative, e.g. `/images/...`)
- `scripts/mirror-webflow.py` — refreshes the copy from Webflow

## Notes

- Some third-party scripts stay external and need internet: Google Analytics,
  Finsweet cookie consent, Swiper, and the cal.com booking links.
