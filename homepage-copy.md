# Lionscraft homepage v2: copy sheet for Webflow

This sheet maps the new copy onto the **existing** sections and elements in Webflow Designer, top to bottom.
The new version is now the local homepage, `lionscraft-site.webflow/index.html`. The original export is still in git (`git show HEAD:lionscraft-site.webflow/index.html`). lionscraft.io itself only changes once this copy is entered in Webflow.

## The offering in one line

**Outperform your market through innovation in AI and digital assets**, through three services:

| | **AI** | **Digital assets** |
|---|---|---|
| **Strategy & Growth** · *Where is the real opportunity for us, and how do we capture it?* | Where AI can cut cost or open a new revenue line | Whether to launch staking, tokenization or digital-asset services, and how |
| **Process Optimization** · *How do we take the manual work out?* | Invoice, document and enquiry processing | Crypto accounting, reconciliation and onchain operations |
| **Institutional Adoption** · *How do we get this past risk, compliance and the board, and make it run?* | AI governance, risk controls and safe rollout | Custody, staking and slashing risk, validator standards (ValOS) |

The services are what we do and the two technologies are where we do it. A visitor should be able to find their row in under ten seconds.

These map to the three bundles on the 2026/27 Business Model Canvas: Strategy & Specialist Advisory → **Strategy & Growth**, AI Implementation & Workflow Automation → **Process Optimization**, Strategy-to-Implementation → **Institutional Adoption**.

---

## Before publishing: confirm these

1. **AI proof is thin.** Digital assets has stc, Vodafone/Pairpoint, Munich Re and Lido behind it. AI has one SME invoicing project and DocPythia. Add a number to the invoicing proof line (e.g. "cut monthly processing time by X%") and get permission to use it. Until you have an AI client you can name, the AI column is a capability claim.
2. **Process Optimization proof line.** "Invoice automation that significantly cut a client's monthly processing time." Replace "significantly" with the real figure.
3. **Scope and price signal.** Each service lists what you get but not how long or how much. Something like "Strategy sprint · 4–6 weeks" or "Process audit · from $X" makes them concrete.
4. **Naming Vodafone/Pairpoint.** The Institutional Adoption proof line names Vodafone/Pairpoint. Check you're cleared to name Pairpoint publicly.

---

## Page settings (SEO)

| Field | New value |
|---|---|
| Title tag / OG title / Twitter title | Lionscraft — Strategy, Process Optimization & Institutional Adoption for AI and Digital Assets |
| Meta / OG / Twitter description | Outperform your market through innovation in AI and digital assets: strategy and growth, process optimization, and institutional adoption. Singapore-based. |

## Navbar

| Element | Old | New |
|---|---|---|
| Menu link 2 (→ #system) | SYSTEM | services |
| Menu link 4 | radar (href `#`) | radar (href `#radar`, which was a dead link before) |
| Button | get in touch | book a call |

## Hero (`section_hero`)

**Left column**
- **New text element above H1** (13px, all caps, white): `AI & digital assets`
- **H1** (old: "Infrastructure for a riskier, more programmable world"): `Outperform your market through innovation`
- **Primary button** (old: "Get in touch"): `Book a 30-min scoping call` → cal.com/team/lionscraft/meet

**Right column**
- Label (old: "introducing lionscraft"): `what we do`
- Paragraph:
  > **Strategy & growth**, **process optimization** and **institutional adoption** — from the business case to working operations.

No numbers in the hero: the client figures live in the Trust section's stat cards, which link to the case studies.

## Opportunity (`#opportunity`)

Big scroll-animated paragraph (old: "Infrastructure is being rebuilt…"):
> Technology is evolving faster than organisations can adopt it. The gap isn't more tools — it's understanding AI and digital assets, identifying where they create an advantage, fitting them into the way you work, and getting them past risk, compliance and the board.

## System → Services (`#system`)

- Eyebrow: `SERVICES` (was SYSTEM)
- H2: `Three services. Two technologies.`

Each card keeps its image. The content column has, in order:
1. Eyebrow: who it's for
2. Title
3. The question it answers (monospace)
4. One-line body
5. Four bullets: what you get
6. A two-column box: **AI** (blue dot) and **Digital assets** (orange dot), one example each
7. Proof line (blue left rule)
8. Button: `Talk to us about this` → cal.com

### Card 1: was "Digital Infrastructure"
- Eyebrow: `For leadership teams & new business units`
- Title: `Strategy & Growth`
- Question: Where is the real opportunity for us, and how do we capture it?
- Body: We assess the opportunity, design the business model, line up the right partners — then help you launch and grow.
- What you get:
  - Opportunity and feasibility assessment
  - Business model, revenue plan and go-to-market
  - Partner and vendor selection
  - Launch support and growth retainer
- AI: Where AI can cut cost or open a new revenue line.
- Digital assets: Whether to launch staking, tokenization or digital-asset services — and how.
- Proof: stc Bahrain: designed and launched an award-winning Web3 business unit.

### Card 2: was "Financial Infrastructure"
- Eyebrow: `For operations, finance & admin teams`
- Title: `Process Optimization`
- Question: How do we take the manual work out?
- Body: We map the process, redesign it, and implement automation that runs with minimal management effort.
- What you get:
  - Process audit and quick-win map
  - Workflow redesign
  - AI implementation and system integration
  - Optional ongoing support
- AI: Invoice, document and enquiry processing.
- Digital assets: Crypto accounting, reconciliation and onchain operations.
- Proof: Invoice automation that significantly cut a client's monthly processing time.

### Card 3: was "Risk Infrastructure"
- Eyebrow: `For banks, insurers, telcos & institutions`
- Title: `Institutional Adoption`
- Question: How do we get this past risk, compliance and the board — and make it run?
- Body: We build the operating model, controls and team know-how that let regulated organisations adopt new technology safely.
- What you get:
  - Operating model, governance and controls
  - Risk assessment, standards and audit readiness
  - Vendor, custody and operator due diligence
  - Executive and team training
- AI: AI governance, risk controls and safe rollout.
- Digital assets: Custody, staking and slashing risk, and validator standards (ValOS).
- Proof: Munich Re, Vodafone/Pairpoint and Lido.

## Trust (`#trust`)

- H2 (was "Trusted by leading operators, institutions and protocols"): `Proof, not promises`
- Paragraph: Telcos, insurers, institutions and protocols come to us for work that holds up to scrutiny. Every result here has a case study behind it.
- Button (was "Get in touch"): `Book a call`
- Stat cards (label / stat line, sentence case), each with a `Read the case study →` link to its page:

| Old label | New label | Old stat | New stat |
|---|---|---|---|
| stc bahrain | stc Bahrain | 3 industry awards infrastructure innovation & technology excellence | 3 industry awards for its Web3 Launchpad |
| munichre | Munich Re | 1M+ Validators for Insurance Unlocked | 1M+ validators unlocked for insurance |
| vodafone | Vodafone | 5 Protocol Infra Services Operational | 5 protocol infrastructure services operational |
| lido | Lido | $35B Secured via Node Operations Standards | $35B secured through node operations standards |

- Remove the dark logo marquee under the stat cards (`trusted_marquee-wrap`). The logo strip under the hero already shows the clients.

## Radar

Not changed in v2. The section still needs at least one real post to stop looking empty.

## Closing CTA (`section_cta`)

- H2 (was "Building infrastructure for a more programmable world."): `Not sure which service fits? Book a 30-minute scoping call.`
- Button: `Book a call`
