# Glynn (K-G) engagement — working notes for Claude

Client: Kollen Glynn, 52 (born Nov 1973), single, Newcastle, Washington. SAP executive (about $700K W-2; RightCapital models a $650K salary). Goals: leave SAP in 2 to 3 years (RightCapital "Retire at 55" = 2028), buy and run an existing business, live on $20K a month. Advisory firms named in every document: Pinnacle Planning (quarterback), Wealth Advisory Now (fiduciary investments; prepared the RightCapital report), M&M Wealth Associates (life insurance and annuities). Last updated 2026-10-18.

## Client documents in this folder

| File | What it is | Status |
|---|---|---|
| Kollen_Glynn_Intro.html | 20-slide 1920x1080 intro deck (footer v20261018), built from KG-Pplanning-010.md on the Ihab intro framework: exec summary (2), financial position (2), retirement readiness, transition before leaving SAP, tax calendar, acquisition capital and structure (2), estate exposure and trust fit, Wealth & Legacy Architecture (interactive SVG, layers + zoom), trust roadmap, asset protection (asset table + ring architecture), advisory team radial + matrix, action plan, coordination quote, open items, glossary | first version, client to review |
| portal.js | Glynn Planning Portal module bar (same mechanics as WAN/I-S/portal.js). Section modules link to anchors in the intro until their own pages exist: #s-retire, #s-acq-1, #s-estate-1, #s-ap-1, #s-tax; Retirement Income is planned | live |
| Analysis/K-G Portfolio Review.html | September 2026 review of the Fidelity statements (gain ladder, option analysis). It treated C.H. Robinson as the employer; the intro follows the newer spec (SAP) | earlier work |

## Source material

Kollen_Glynn_RightCapital.pdf (166 pages, generated 2026-10-18), Statement07312026.pdf (Fidelity TOD account plus CHRW stock plan), Statement06302026.pdf (Whistler Ventures Inc. Solo 401(k)), Kollen_Glynn_Profile.docx (EMPTY, 0 bytes). Spec prompts arrive as .md files the user opens and asks to "process". pdftotext output of the RightCapital PDF is garbled; use PyMuPDF `get_text("blocks", sort=True)` (run python without -I so fitz imports).

## Facts and readings used throughout (flagged as to-confirm in the deck)

- Balance sheet $15.23M, net worth $14.95M: Fidelity brokerage $6.78M; Germany ESOP $3.0M; CHRW options $1.2M (RightCapital calls them "Logistics RSU"); NAC IRA annuity $790K, NAC Roth IRA annuity $170K, SAP 401(k) $42K, Solo 401(k) $28K; IUL cash value $708K (NAC IUL Cash Growth $2.8M DB, Kaizen $2.8M DB, CLU IUL Protection $1.25M DB = $6.85M); home $1.9M in the "Whisler Family Trust", mortgage $280K at 5%; land $500K personal; cash $115K.
- RightCapital quirks: the ESOP and the IUL cash values are NOT in the retirement projection (invested assets start at $7.93M); "Whisler" is the trust entered as a co-client with Kollen's birth date (adds ~$1.45M phantom health/LTC cost); 87% of the portfolio is classed "Other"; taxes are overstated (whole return taxed yearly); state income tax is zero (Washington) and the estate projection shows Washington estate tax.
- Fidelity TOD account on 31 Jul 2026: $2.11M (QQQ $1.15M, CHRW 6,255 sh $0.92M), $3.93M moved to another Fidelity account during 2026 (statement not in folder). CHRW options 18,246 vested NSOs: 7,890 at $88.87 expire 5 Dec 2028; 10,356 at $72.74 expire 5 Feb 2030.
- Cash flow 2026: salary $650K vs living $144K, housing $48K, IUL premiums $390K, tax $361K, 401(k) $24.5K = net -$321K. Premiums $390K to 2028, $270K 2029-32, $30K 2033-36; policy loans $268K/yr from 61, $388K/yr from 65.
- Pinnacle analysis: retirement core needed at 55 (RightCapital flows, 4%): $5.3M with all policy income, $7.9M with half, $10.5M with none; available $9.1M + $3.0M ESOP. Acquisition equity budget $2.5M target, $3.5M ceiling (mostly the ESOP); transition reserve $0.75M to $1M. Illustrative $7.5M purchase: $2.5M equity, $4.25M SBA 7(a), $0.75M seller note.
- Estate if he died today: gross $21.1M (DB replaces CV), Washington estate tax ~$5.1M ($3M exclusion, 10-35%), federal ~$0.4M ($15M exemption); ILIT saves ~$2.8M. ~$4.9M would pass through probate. No heirs named.
- Readiness score (Pinnacle's, not RightCapital's): 61 today, 85 target by the exit; weights 30/15/15/15/10/15.
- The spec said "California tax considerations"; Kollen is a Washington resident, so the deck covers Washington (no income tax, 7%/9.9% capital gains excise, 35% estate tax with no gift tax, B&O) and treats California as a what-if.

## Conventions

- Same house style and CSS as WAN/I-S/Ihab_Shahawi_Intro.html; footers "n / 20"; content must end above y=1024. One generic tooltip script handles every `.tipwrap` container; the architecture slide keeps its own layer/zoom script.
- Render-check before reporting: headless Chrome per slide plus a measuring script (content bottom vs 1024, card overflow, SVG text bounds). Keep scratch files in the scratchpad, never in this folder.
- Final messages flag every placeholder and assumption.

## Open items the client has not yet answered

Employer and pay (SAP vs the CHRW relationship, unvested SAP equity, deferred comp); the second Fidelity account; ESOP plan, custodian, basis and foreign reporting; the trust document (Whisler vs Whistler spelling); heirs and charitable intent; IUL in-force illustrations and Kaizen financing terms; homeowners/auto/umbrella policies; health coverage and HSA eligibility; acquisition thesis; residency (two Newcastle addresses); a completed client profile.
