# Shahawi (I-S) engagement — working notes for Claude

Client: Ihab Shahawi (63) and Vivian El-Shahawi (67). Advisory firms named in every document: Pinnacle Planning (lead and coordinator), Wealth Advisory Now (fiduciary investments), M&M Wealth Associates (insurance). Last updated 2026-10-17.

## Client documents in this folder (all client-facing, same house style)

| File | What it is | Status |
|---|---|---|
| Ihab_Shahawi_Intro.html | 14-slide 1920x1080 deck (footer version v20261018): 3 intro slides, Wealth & Legacy Architecture (interactive SVG), how-to-read, 5 asset-protection slides (risks, trusts, asset-by-asset, measures, ring architecture), Advisory Team radial + matrix, closing quote slide, then a two-slide acronym glossary (general definitions, not family-specific). All 2053 figures in THIS deck use a 3.0% growth assumption (estate $149M, tax $36M); the other documents still cite RightCapital's $180.7M / $46.4M | complete |
| Estate_Trust_Info_Generic.html | 6-slide 1920x1080 concepts deck (part one): contents + sections 1-5 (what a trust is, six trusts, four more vehicles, waterfall, toolkit applied); nav bar links to the Ihab deck | complete; footers "n / 6" |
| Estate_Trust_Info_Live_HomePage.html | 26-slide Trust Planning module: contents, the Recommended Trust Structure matrix (slide 2, must match intro page 4), 12 worked examples, dynasty/GST, waterfall (3 slides, the first carried over from the Generic deck's page 5 with the Shahawi fit set to optional), Trust Team (2), appendices HEMS, CLAT (slides 24-25), Section 303. Trust dashboard nav, permanent anchors (rlt-, slat-, idgt-, ilit-, dynasty-, grat-, crt-, clat-, gst-, family-dynasty-, bypass-, qtip-, insurance-, living-benefits-, waterfall-example; trust-matrix) and a summary banner that opens on arrival | complete; footers "n / 26" |
| Ihab_Trust_Plan_Proposal.html | scrolling trust education proposal, 13 sections, from TrustPlan.md | complete |
| Ihab_Estate_Legacy_Proposal.html | family-specific plan, 11 sections, from the Family Profile (was an addendum, reframed as standalone) | complete |
| Ihab_Shahawi_Pinnacle_Plan.html | five-pillar comprehensive plan; nav links to both proposals | revised 2026-10-16 |
| Ihab_Shahawi_Blueprint.html | earlier blueprint | not touched this round |

RM-Intro.html and RM-Blueprint.html belong to a DIFFERENT client (B LLC, the R-L engagement). Spec .md files sometimes say "RM-Intro.html" when they mean the Shahawi intro. Confirm before editing an RM file.

## Source material

Ihab_Shahawi_RightCapital.pdf (projections, $67.1M balance sheet, $180.7M estate in 2053), Ihab Family Profile.docx (children, properties, insurance view, foundation), IABA Research and Education Foundation.pdf (RCOC application), PlanOutline01.docx. Spec prompts arrive as .md files; the user opens one and says "process it".

## Facts and assumptions used throughout (flagged as to-confirm in the documents)

- Net worth $67.1M: Institute (C corp) $47M incl. $5M portfolio at 13% and $2M cash; LLC2 $17M (7 properties incl. Beverly Hills, Pasadena which loses money); LLC1 $3M (2 properties); $100K cash + $200K RE account. Seven foreign properties (5 UK, Egypt, Colombia) held personally, unvalued, kept outside US trusts with local wills.
- Family: son 21; daughter 31 married in London; son 42 unmarried; daughter 46 divorced, mother of the two grandsons (16, 14). A son died in 2013 at 24. Legacy: 20% to each child, 20% to the grandchildren; the open-class question is flagged.
- Ihab "doesn't believe in life insurance": the ILIT ($20M second-to-die, ~$350K/yr premium) stays recommended, shown against section 303 reserve, 6166 and Graegin alternatives. Rockefeller waterfall is optional, not recommended.
- Existing living trust is 12 years old: restate, don't replace.
- IABA Foundation: Ihab founded and leads it; treated as the charitable hub; assumed public charity, status to confirm via determination letter. UCLA ~$175K/yr routed through it as a named autism research grant.
- Tax parameters: 40% estate tax, $15M exemption per spouse (2026), 30% valuation discount, 45% combined ordinary and 37.1% combined capital gains, 5% IRS rate, $19K annual exclusion.
- The 42-year-old son is the placeholder family trustee / ILIT trustee / distribution adviser until the family names someone.

## Conventions

- Slide decks: 1920x1080 `.slide` divs, footer `.foot` at bottom 28px; content must end above y=1024. Inline SVG only, no external assets. Arrow markers are defined once globally at the top of Estate_Trust_Info_Generic.html.
- When adding slides to Estate_Trust_Info_Generic.html: add an `id`, append a nav-bar link and a Contents entry, and renumber every footer "n / N".
- Render-check before reporting: headless Chrome screenshot per slide, plus an injected script that measures content bottom against the footer and checks each SVG text bbox against its enclosing rect. Keep all scratch files in the scratchpad, never in this folder.
- Final messages to the user flag every figure that is a placeholder pending appraisal, quotes or the foundation's status.

## Planning portal (added 2026-10-17)

- portal.js in this folder is the shared module bar. Every portal page includes `<script src="portal.js" data-module="KEY"></script>` as the first thing in `<body>`. The MODULES list at the top of portal.js is the single registry: Overview (the intro), Trust Planning (Live HomePage), Asset Protection (the intro's asset protection slides until Asset_Protection_HomePage.html exists), and planned Retirement, Tax, Business Succession and Charitable modules. To add a module: build the page, include portal.js, flip its status to "live".
- Intro page 4 (s-arch): every trust box and family node is an `<a class="tlink">` to an anchor in the Live HomePage. Trust data for the matrix and the arrival banner lives in one dict in the integration script and in the TRUSTS JSON at the bottom of the Live page; if page 4 changes, update both the matrix slide and that JSON.
- portal.js also adds casual-copy deterrents (no right-click, no Ctrl/Cmd+U/S, no F12 or dev-tools shortcuts; printing allowed). They are not real protection; the Vercel password gate is. Opt a page out with data-protect="off".
- Publishing: portal.js must be deployed next to any page that includes it.

## Publishing

The intro deck is published at https://shahawi-intro.vercel.app (Vercel project shahawi-intro, Basic-auth password in the SITE_PASSWORD env var). Deploy folder: Deploy/ in this folder (git-ignored). Workflow: keep editing Ihab_Shahawi_Intro.html; when a version is ready, copy it to Ihab_Shahawi_Intro_YYYYMMDDx.html, copy that over Deploy/index.html, run `vercel deploy --prod --yes` in Deploy/, and verify with curl (401 without the password, 200 with it). First snapshot: Ihab_Shahawi_Intro_20261017a.html.

## Open items the client has not yet answered

Grandchildren's clause (open class vs named vs per stirpes); insurance decision after quotes; a memorial program in the son's name; which two children join the foundation board first; whether the Egypt and Colombia properties are homes or investments; values and basis for every property; the foundation's IRS determination letter.
