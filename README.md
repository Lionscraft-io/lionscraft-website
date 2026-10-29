# Lionscraft Website

Static website for Lionscraft — digital, financial and risk infrastructure.

This repo is the only source of the site. Everything is in `lionscraft-site.webflow/`
(the folder name is from the old Webflow export; Webflow itself is no longer used):
pages, CSS, JS, images, videos and fonts, so it runs on any static host.

## How changes go live

- Edit the pages here, or ask Hermes (the Telegram website agent) to do it.
- `main` is preprod: https://v2202609411057512877.hotsrv.de/ shows it within a minute.
- `live` is what Replit deploys. It only moves when you tell Hermes "release".
  Then in Replit: Pull, then Redeploy.

## Run locally

```bash
python3 -m http.server 8000 --directory lionscraft-site.webflow
# open http://localhost:8000
```

## Replit

The `.replit` file serves `lionscraft-site.webflow/` when you press Run and
deploys it as a static site (Deploy → Static, public directory
`lionscraft-site.webflow`). The Repl follows the `live` branch.

## Structure

- `lionscraft-site.webflow/` (served with clean URLs: `/services/advisory` → `services/advisory.html`)
  - `index.html` — homepage; `our-story.html`
  - `services.html` + `services/` — Advisory, Build, Operate, Structure
  - `intelligence.html` + `intelligence/` — Research (with articles in `intelligence/research/`), Data & Tools, Training
  - `case-studies.html` + `case-studies/` — one page per case study
  - `latest.html`, `ventures.html`
  - `legal/privacy-policy.html`, `404.html`, `401.html`, `sitemap.xml`, `robots.txt`
  - `css/`, `js/`, `images/`, `videos/`, `fonts/` (all linked root-relative, e.g. `/images/...`)

## Notes

- The pages still use the scripts that came with the Webflow export (`js/webflow*.js`)
  for the menu, animations and sliders. They run locally; no Webflow account is needed.
- Some third-party scripts stay external and need internet: Google Analytics,
  Finsweet cookie consent, Swiper, and the cal.com booking links.
