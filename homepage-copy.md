# Lionscraft homepage v2: copy sheet for Webflow

This sheet maps the new copy onto the **existing** sections and elements in Webflow Designer, top to bottom.
The new version is now the local homepage, `lionscraft-site.webflow/index.html`. The original export is still in git (`git show HEAD:lionscraft-site.webflow/index.html`). lionscraft.io itself only changes once this copy is entered in Webflow.

## The offering in one line

**Strategic Advisory for Digital Assets & Agentic Economy**, through three services:

| | **AI** | **Blockchain & tokenization** |
|---|---|---|
| **Strategy & Growth** · *Where is the real opportunity for us, and how do we capture it?* | Where AI can cut cost or open a new revenue line | Whether and how to launch staking, tokenization or other blockchain services |
| **Process Optimization** · *How do we take the manual work out?* | Agentic workflows for invoices, documents and enquiries | Crypto accounting, reconciliation and onchain operations |
| **Institutional Adoption** · *How do we adopt this safely in a regulated organisation?* | AI governance, risk controls and safe rollout | Custody, staking and slashing risk, validator standards (ValOS) |

The services are what we do and the two technologies are where we do it. A visitor should be able to find their row in under ten seconds.

These map to the three bundles on the 2026/27 Business Model Canvas: Strategy & Specialist Advisory → **Strategy & Growth**, AI Implementation & Workflow Automation → **Process Optimization**, Strategy-to-Implementation → **Institutional Adoption**.

---

## Before publishing: confirm these

1. **AI proof is thin.** Blockchain has stc, Vodafone/Pairpoint, Munich Re and Lido behind it. AI has one SME invoicing project and DocPythia. Add a number to the invoicing proof line (e.g. "cut monthly processing time by X%") and get permission to use it. Until you have an AI client you can name, the AI column is a capability claim.
2. **Process Optimization proof line.** "Invoice automation that significantly cut a client's monthly processing time." Replace "significantly" with the real figure.
3. **Scope and price signal.** Each service lists what you get but not how long or how much. Something like "Strategy sprint · 4–6 weeks" or "Process audit · from $X" makes them concrete.
4. **Naming Vodafone/Pairpoint.** The Institutional Adoption proof line names Vodafone/Pairpoint. Check you're cleared to name Pairpoint publicly.

---

## Spacing (all sections)

One rhythm for every section below the logo strip, so the page feels calm and consistent:

| | Desktop | Tablet | Phone |
|---|---|---|---|
| Space above and below each section | 160px | 96px | 80px |
| Space between a section's heading and its content | 64–80px | 48px | 48px |
| Section headlines | 56–72px | 48–52px | 40–44px |

**One box system.** All boxes line up with the section's thin lines, with no gaps and no floating boxes:
- **Split sections** (01 Who we work with, 02 Services, 06 Ventures, 07 Let's connect): text on the left, a thin vertical divider at the same place in every section (about 45% across), and the rows / newsletter box filling the space from that divider to the right edge. Exception: the three venture cards stay separate boxes with gaps.
- **Hover:** every clickable row and every box lightens slightly under the mouse, including the Technology specializations boxes and the Latest posts.
- **Stacked sections** (03 Trust, 04 Technology specializations, 05 Latest): heading on top with a line under it, then full-width cells separated by thin vertical lines, then a line and the "see all" link.
- Every box has 32px inner padding on desktop and 24px on tablet and phone; on phone every box runs edge to edge.
- No empty bars between sections: each section starts right where the previous one ends.

Section-specific details:
- **Who we work with:** client rows about 28px top and bottom, names 24px.
- **Services:** tighter than the other sections so it fits on one screen (about 760px tall): 96px above and below, the three service rows are stacked with a thin line between them, each about 176px tall; names 32px; pictures 200px wide.
- **Intelligence:** 80px above and below, rows 24px top and bottom (about 440px tall).
- **Trust, Technology specializations, Latest, Ventures, Let's connect:** same 160px rhythm.
- **Footer links:** 112px above, 80px below.

## Section colours

Dark and light alternate from Services on:

| Section | Background |
|---|---|
| Hero, logo strip, 01 Who we work with | dark `#0b0b04` |
| 02 Services (+ Intelligence) | light `#fbfaf3` |
| 03 Trust | dark (client logos shown inverted to white) |
| 04 Technology specializations | light |
| 05 Latest | dark |
| 06 Our ventures | light tint `#eceadf` |
| 07 Let's connect, footer | dark |

Dark sections use white text, grey `#a1a1a1`/`#d4d4d4` for secondary text and `#3a3a36` lines (a touch brighter than the export's `#242424`; in Webflow, change the `Border Alternate` colour variable); light sections use `#0b0b04` text, `#5c5c55` secondary and warm-grey lines `#bab8ae` (between the original and a softer grey, a little lighter than the export's `#a7a7a7`; in Webflow, set `Border Primary` to this on the page content only, so the header's Menu button keeps its `#a7a7a7` outline).

## Background videos on phones

Some phones block autoplay (for example iPhones in Low Power Mode) and then show a big play button on top of the hero video and the animated lion in the footer. The site now hides that native play button on all background videos, shows the poster frame instead, and starts the video as soon as the phone allows: on load, when the page becomes visible again, and at the first touch, tap or scroll. Note: iPhones in Low Power Mode block autoplay completely, so there the poster frame shows until the visitor touches the page. In Webflow: add this to the site's custom code (head):

```
<style>
.w-background-video video{pointer-events:none}
.w-background-video video::-webkit-media-controls,.w-background-video video::-webkit-media-controls-start-playback-button,.w-background-video video::-webkit-media-controls-panel{display:none !important;-webkit-appearance:none;opacity:0;pointer-events:none}
</style>
```

## Cookie consent

The cookie banner stays as it is. The small floating cookie icon in the bottom-left corner (the Finsweet "manager" button, `fs-cc-manager2_component`) is removed on every page. In Webflow: delete that element from the page template. If visitors should still be able to change their cookie choice later, add a `Cookie settings` link in the footer instead.

## Page settings (SEO)

| Field | New value |
|---|---|
| Title tag / OG title / Twitter title | Lionscraft | Strategic Advisory for Digital Assets & Agentic Economy |
| Meta / OG / Twitter description | Strategic advisory for digital assets and agentic economy: strategy and growth, process optimization, and institutional adoption. Singapore-based. |

## Navbar and menu

The inline menu links are gone. The header is now: logo on the left, and on the right a matching pair, both 44px tall in the same small mono capitals: a white `Book a call` pill (dark text) and an outlined `Menu` button (two lines + the word). On phone the Menu button shows only the two lines.

**Header behaviour:** at the top of the page the header is fully transparent and shows the logo and the `Menu` button; `Book a call` is hidden. Scrolling down, it stays transparent and slides up out of view once the page has moved past the header height (about 80px); it never turns into a dark bar on the way down. When the visitor scrolls up, it comes back after a few pixels as a blurred, 80% see-through bar (black at 20%) with `Book a call` fading in next to `Menu`. Back at the very top it is fully transparent again and `Book a call` hides. The header always stays visible while the menu is open, with its Close button.

**Menu overlay** (dark glass over the page, black at 94% with blur; fades in with the links and the Get in touch block sliding up one after another; the button turns into `✕ Close`; Escape or any link closes it):

- **Left column:** two groups with small mono labels and a line:
  - **Services:** Strategy & Growth · Process Optimization · Institutional Adoption (all → `#system` until service pages exist) · Intelligence (→ `#intelligence`)
  - **Read more:** Who we work with (→ `#clients`) · Case studies · Latest (→ `#radar`) · Ventures (→ `#ventures`) · Our story
- **Right column:** `Get in touch`, the line "Have a technology challenge or a project in mind? A short call is the easiest way to start.", a white pill `Book a call`, and round X / LinkedIn icons.
- On phone the two columns stack.

The same menu is on the case study, case studies and Our story pages, where the links point back to the homepage sections.

## Hero (`section_hero`)

**Left column**
- **H1** (old: "Infrastructure for a riskier, more programmable world"): `Strategic Advisory for Digital Assets & Agentic Economy`
- **Primary button** (old: "Get in touch"): `Let's talk` → cal.com/team/lionscraft/meet

**Load animation** (inspired by stablewatch.io, about 1.5 seconds, plays once on page load):
- The background video fades in from black while it goes from blurred to sharp and settles from a slight zoom.
- The headline appears letter by letter, each letter going from blurred and faded to sharp (about 14ms between letters, each letter half a second).
- Then the `Let's talk` button rises in, followed by the right column (icon, label, paragraph, link) one after another.
- Visitors who have "reduce motion" switched on see everything straight away. In Webflow this is a page-load Interaction (blur + opacity + move on the background, a split-text reveal on the H1, then staggered fades).

**Right column**
- Label: `introducing lionscraft` (unchanged)
- Paragraph:
  > We're a specialist technology company working across enterprise systems, digital assets and AI. We deliver hands-on solutions, and make specialist knowledge available through research, intelligence and training.
- Link under the text: `Our story ↗` → `our-story.html`

No numbers in the hero: the client figures live in the Trust section's stat cards, which link to the case studies.

## Opportunity (`#opportunity`)

**Removed.** Delete the whole section, and the custom code that animated its paragraph letter by letter.

## System → Services (`#system`)

**Dark section** (black, thin grey lines, square corners, like the rest of the site). Two parts: Services on top, Intelligence below. On phone everything stacks.

**Services: left column**
- Label: `02 / Services`
- Big title: `Services.`
- Text: We help you find the opportunity, build what matters and run it safely inside your organisation.
- Link right under the text: `See our work ↗` → `case-studies.html`

**Services: right column**, three stacked rows. Each row is a link to the scoping call, with an ↗ arrow and one of the site's dotted pictures on the right (the images the old service cards used):

| Label | Title | Line | Picture |
|---|---|---|---|
| 01 / Strategy | Strategy & Growth | Opportunity, business model, partners and go-to-market. | BG-6 |
| 02 / Optimization | Process Optimization | Workflow redesign, agentic AI and system integration. | BG-7 |
| 03 / Adoption | Institutional Adoption | Operating model, governance, risk controls and training. | Bildschirmfoto-2026-03-02 |

**Intelligence** (same section, under Services, on the same lines: same divider, and the picture in the same column as the service pictures)
- Left: label `Knowledge / Research / Education`, big title `Intelligence.`, text "Specialist research, practical knowledge and tools you can use, free and paid.", link `Explore intelligence ↗` → `#radar`
- Right: a numbered list, each row a link with an ↗ arrow, and the pink dotted trees picture (former Opportunity image) beside the rows, 200px wide like the service pictures (on phone it sits above the rows):

| # | Name | Line | Links to |
|---|---|---|---|
| 01 | Research | Reports, primers and insights | `#radar` |
| 02 | Repositories | Data, models and living knowledge | github.com/Lionscraft-io |
| 03 | Education | Workshops, courses and training | scoping call |

The longer service detail (the question each service answers, the four deliverables and the proof line) is no longer on the homepage. Keep it for service pages later:

- **Strategy & Growth** · Where is the real opportunity for us, and how do we capture it? · Opportunity and feasibility assessment; business model, revenue plan and go-to-market; partner and vendor selection; launch support and growth retainer · Proof: stc Bahrain.
- **Process Optimization** · How do we take the manual work out? · Process audit and quick-win map; workflow redesign; AI implementation and system integration; optional ongoing support · Proof: invoice automation (needs a number).
- **Institutional Adoption** · How do we adopt this safely in a regulated organisation? · Operating model, governance and controls; risk assessment, standards and audit readiness; vendor, custody and operator due diligence; executive and team training · Proof: Munich Re, Vodafone/Pairpoint, Lido.

## Technologies (`#technologies`)

**Removed.** Services is followed directly by Trust.

## Who we work with (`#clients`, new, dark)

**Position:** first section after the logo strip, before Services.

Two columns.

**Layout:** compact two columns (about 600px tall on desktop), left 5 parts, right 7 parts.

**Colours:** black background like the logo strip above it; white headline, light grey text, thin dark-grey lines, outlined white button.

**Left**
- Label: `01 / Who we work with` (12px, mono)
- H2 (44px, sans): `Different worlds.` / `Shared ambition.`
- Text (16px, grey): We work with established organizations and emerging technology businesses that need deep expertise, practical judgement and hands-on delivery.
- Outlined pill button: `Book a 30-min scoping call` (no image behind it)

**Right:** a numbered list with thin lines. Each row is just the number, the group name and a small ↗ arrow (no description line).

| # | Group | Links to |
|---|---|---|
| 01 | Enterprises & telecom operators | stc Bahrain case study |
| 02 | Financial institutions | Munich Re case study |
| 03 | Web3 protocols & infrastructure providers | Lido case study |
| 04 | SMEs & growing businesses | scoping call |
| 05 | Public sector & development organizations | scoping call |

**Section labels are numbered:** `01 / Who we work with`, `02 / Services`, `03 / Trust`, `04 / Technology specializations`, `05 / Latest`, `06 / Our ventures`, `07 / Let's connect`.

## Trust (`#trust`)

New full-width layout (replaces the old "text left, cards right" grid). Styled like the other sections:

- **Top row:** label `03 / Trust` (12px mono, no dot), H2 `Proof, not promises` (64px sans), the line "Telcos, insurers, institutions and protocols come to us for work that holds up to scrutiny."
- **Below:** four case cards in one row (2×2 on tablet, stacked on phone). Each whole card links to its case study and shows: logo, client, big number (mono), stat line, case title (22px sans), `Read the case study ↗`.

| Client | Number | Stat line | Case title |
|---|---|---|---|
| stc Bahrain | 3 | industry awards for its Web3 Launchpad | Launching an award-winning Web3 business unit |
| Munich Re | 1M+ | validators unlocked for insurance | Making validator risk insurable |
| Vodafone | 5 | protocol infrastructure services operational | From Web3 strategy to live protocol infrastructure |
| Lido | $35B | secured through node operations standards | Turning validator best practice into an auditable standard |

- **Under the cards, left:** underline link `See all case studies ↗` → `case-studies.html` (same style as "See our work" and "View all updates").
- The dark logo marquee under the old cards is removed.

## Technology specializations (`#specializations`, new, dark)

**Position:** right after Trust, before Radar.

- Label: `04 / Technology specializations`
- H2 (large, sans): `Deep in each domain.` / `Stronger at the intersections.`
- Text (grey): Our work combines enterprise systems, crypto-native infrastructure and practical AI and automation.
- Three columns divided by thin lines (stacked on phone):

| Label | Title | Line |
|---|---|---|
| 01 / Foundations | Enterprise technology | Architecture, integration, data engineering, BI, operating models, governance and delivery. |
| 02 / Decentralized | Digital assets & Web3 | Blockchain networks, validators, oracles, DeFi, tokenization, payments and on-chain infrastructure. |
| 03 / Intelligent | AI & automation | Intelligent workflows, AI agents, knowledge systems, integrations and practical process automation. |

- Bottom strip: **Where we specialize** · Web3 × Enterprise · Web3 × AI · SME × AI · and the convergence of all three.

## Case studies page (`case-studies.html`, new)

- Dark header: `Case studies`, with the line "How telcos, insurers, institutions and protocols turned AI and blockchain into working business with us."
- The four case cards in a 2×2 grid, each also showing the sector and the service.
- Each case page's back link now says `← All case studies` and goes here.

## Our story page (`our-story.html`, new)

- Dark header: `Operators, not just advisors`
- Sections: Who we are · Our journey (timeline) · How we work (four principles) · The team · Our work (button to all case studies)
- Still has 7 TBC markers: founding year and reason, three milestone years, team names and roles, photos.

## Radar → 05 / Latest (`#radar`)

**Replaces the Radar section** (same anchor, so the menu link keeps working; the menu label changes from `radar` to `latest`). Dark background.

- Same layout as Trust and Technology specializations: label, H2 and text stacked on top, a line under them, then three posts as full-width cells side by side with thin lines between them (stacked on phone).
- Label: `05 / Latest`
- H2 (large, sans): `What's happening` / `at Lionscraft.`
- Text under the H2: Research, publications, events and project milestones. New ways to engage with what we're thinking and building.
- Posts (one small label each; the second tag "Community / Free insight / Example post" was removed to keep the cards calm):

| Label | Title | Line | Link |
|---|---|---|---|
| Event / ValOS | ValOS joins Lido Poolside | Conversations on Ethereum validator security, operational assurance and adoption. | `View announcement ↗` → LinkedIn |
| Research / Digital assets | Understanding digital asset custody | A practical primer on custody architectures, operational arrangements and infrastructure decisions. | `Explore the primer ↗` → LinkedIn |
| Meet us / Events | Heading to Devcon? Let's meet. | An example of an event update with an easy route to schedule a one-to-one conversation. | `Schedule a meeting ↗` → scoping call |

- Under the posts, after a line: `View all updates ↗` → LinkedIn

**To do before going live:** point "View announcement" and "Explore the primer" at the real post and primer, and replace the third (example) post with a real event.

## 06 / Our ventures (`#ventures`, new, light tinted)

**Position:** after Latest.

- Left: label `06 / Our ventures`, H2 `Beyond client work.`, text "We also develop our own ideas, products and ventures. Here's what we're building.", link `Explore ventures ↗`
- Right: three cards in each project's colours. Risk and Protect: navy `#0b0d1f` with white text, status in turquoise `#2ae6e6` (Risk) or green `#2af297` (Protect). PookieScroll: black `#0b0b04` with white text and the status in its icon green `#4ce29d`. The three cards are separate boxes with a 16px gap between them, set 32px in from the divider and the right edge (stacked on phone). Top to bottom: status, app icon, name, line, and an ↗ arrow:

| Icon | Status | Name | Line | Links to |
|---|---|---|---|---|
| `images/venture-risk.svg` (turquoise square with a dark lion) | Incubating | Risk | Structured catastrophe risk and market intelligence | risk.lionscraft.io |
| `images/venture-protect.svg` (green square with a dark lion) | Incubating | Protect | Early-warning and disaster protection infrastructure | protect.lionscraft.io |
| `images/venture-pookiescroll.png` (green app icon) | Focus app | PookieScroll | Tools for attention and focus | Our story (no site yet) |

- **To do:** link PookieScroll to its own site or app store page once it has one; "Explore ventures" still goes to Our story.

## Closing CTA → 07 / Let's connect (`#connect`, dark)

**Replaces the closing CTA** ("Building infrastructure for a more programmable world.").

**Left**
- Label `07 / Let's connect`, H2 `What are you` / `working on?`
- Text: Have a technology challenge, a project in mind, or just want to explore an idea? There are plenty of ways to start a conversation.
- White pill `Book a meeting ↗` → scoping call · link `Message on LinkedIn ↗`

**Right: newsletter box** (`#newsletter`, a line above and below, filling the space from the divider to the right edge)
- Label `Stay in the loop`, title `Good intelligence.` / `No noise.`
- Text: Research, updates, events and occasional opportunities to collaborate, sent when we have something worthwhile to share.
- Label `Your email address`, email field (placeholder `you@company.com`) and an arrow submit button
- Note: "Homepage concept: signup is not yet connected to an email platform."
- **To do:** connect the form to an email tool (e.g. Webflow forms, Mailchimp) and remove the note.

On the case study, case studies and Our story pages the label reads just `Let's connect`.

## Footer (one combined footer)

Replaces both the old footer bottom line and the separate links block. One dark footer, top to bottom:

1. **Links row** (three columns, stacked on phone)
   - Description: Enterprise technology, Web3 and AI. Specialist solutions, research and intelligence, with real-world experience behind them.
   - **Explore:** Solutions (→ #system) · Intelligence (→ #intelligence) · Case studies · Latest (→ #radar) · Ventures (→ #ventures)
   - **Company:** About Lionscraft (→ Our story) · Newsletter (→ #newsletter) · LinkedIn · X / Twitter
2. **The big animated LIONSCRAFT wordmark** (unchanged, used once as the sign-off)
3. **One bottom line:** `Lionscraft Pte. Ltd. · Singapore · UEN 202322784R` on the left; `© 2026 Lionscraft` plus the X and LinkedIn icons on the right

Removed: the small "lionscraft" text logo, the second company line ("…All rights reserved."), "Book a meeting" in the footer (it's in Let's connect right above), and the extra X / LinkedIn links under the Let's connect buttons.
