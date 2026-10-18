# Adraneda (V-A) engagement — working notes for Claude

Client: Vanessa Pepino Adraneda, 40 (born 28 Oct 1985), single mother of Luke (born 29 Apr 2012). Lake County, Indiana (Crown Point / Saint John addresses; the SEP IRA statement uses Crete, IL). Healthcare entrepreneur. Goals from the spec: protect Luke, go from five businesses to one, reduce stress, move from operator to owner to consultant, long-term security. Advisory firms named in every document: Pinnacle Planning (quarterback), Wealth Advisory Now (fiduciary investments; prepared the RightCapital report), M&M Wealth Associates (life insurance and annuities). Last updated 2026-10-18.

## Client documents in this folder

| File | What it is | Status |
|---|---|---|
| Vanessa_Adraneda_Intro.html | 24-slide 1920x1080 intro deck (footer v20261018), from Vanessa_Estate_Plan_001.md on the Ihab/Glynn framework. Narrative: single mom, protected family, simplified owner, consultant. Slides: title, who is Vanessa, plan on one page, balance sheet, cash flow and businesses, reading RightCapital (7 data findings), simplification x2, what-happens-if (incapacity/death/Luke's money), trust fit matrix, Wealth & Legacy Architecture (interactive layers + zoom), asset protection x2 (exposures, ring), transition roadmap (Gantt) and workstreams, retirement scenarios, education, tax, team radial + matrix, ranked action plan, priority map (interactive), coordination quote, open items, glossary | first version, client to review |
| portal.js | Adraneda Planning Portal module bar (same mechanics as WAN/I-S and WAN/K-G). Modules point at anchors in the intro until their pages exist: #s-protect (Estate), #s-trusts (Trust), #s-ap-1, #s-retire, #s-tax, #s-transition | live |
| 01 Vanessa-Accounts-Current.html, 02-Simplicity-Account-Mapping.html, 04-Current-to-Simplicity.html, Analysis/ (margin call, margin exit, portfolio review) | earlier account and portfolio work (Sep to Oct 2026) | earlier work |

## Source material

Vanessa_Adraneda_RightCapital.pdf (137 pages, generated 2026-10-18; use PyMuPDF `get_text("blocks", sort=True)`), the account statements in this folder, and the Pearl Hospice diligence in TrueCare/Pearl DD (Vanessa is the seller there). Spec prompts arrive as .md files the user opens and asks to "process".

## Facts and readings used throughout (flagged as to-confirm in the deck)

- Net worth $10,030,993, no liabilities entered: rentals (9) $5.0M, Devoted Health $1.76M, home $0.9M, Pearl Hospice $0.75M, Distinct Home Care $0.15M, VCG Healthcare Inc. $0, bank $647K (incl. $300K "Business Account"), invested $654K (SEP IRA $254,650, Robinhood $220K net, old 401(k) $40K, E*TRADE $11K from 2020, UTMA $107,856, child savings $20,065), IUL cash value $170K. 85% illiquid.
- Living trust dated 11 Apr 2024 holds only Centier checking + CD (~$217K per statements; RightCapital says $312K). RightCapital's estate checklist marks will, POA, living will, proxy, beneficiaries and trust as "created": unverified.
- Robinhood margin loan $216,911 (31 Jul 2026), netted away in RightCapital.
- Income 2026 $424K (Devoted distributions $200K, Fergus retainer $120K, Devoted W-2 $104K); taxes $307K because RightCapital taxes all $556K of company profit; net -$95K. IUL premiums $78K/yr to 60.
- Businesses in RightCapital: Devoted ($3.57M rev, $352K profit, kept to 90), Pearl ($891K rev, $171K profit, sold 2027 at $750K), Distinct ($858K, $33K, sold 2027 at $150K), VCG ($0, closed 2028). The deck counts the 9 rentals as the fifth business (spec says five; confirm).
- Pearl reality (Pinnacle diligence, Oct 2026): 2025 receipts $806K at a loss, UPIC 100% prepayment review since June 2026, license to July 2027, competing 36-month management offer; realistic $100K to $150K. Deck uses $125K.
- RightCapital: retire at 51 (2036) on $15K/mo, 16% success, invested assets out at 69. The rentals have no rent and are never sold; the "529" is really the UTMA + child savings.
- Rental income (user instruction 2026-10-18): $12K a month ($144K a year) from 2026, rising 2.5% a year, treated as net of property costs and taxed at about 25% after depreciation. This replaced the earlier 3%/4% yield placeholders everywhere in the deck.
- Pinnacle scenarios (scratch model, RightCapital cash flows and implied returns to 50, 6% after, today's dollars, plotted to 89 because RightCapital pays the $3.8M death benefit into the portfolio at 90): Pearl at $125K alone runs out about 59-61; + the $12K a month of rent never runs out ($3.2M at 51, low of $2.6M at 65, $3.2M at 89; withdrawal rate at 51 3.7% vs 12.9%); + consulting to 60: $3.7M at 65. If the $12K is gross and costs take 35%, it runs out at 77 unless consulting continues to 60. With the rent, 2026 cash flow is about +$13K instead of -$95K. On the same basis the as-entered plan runs out at 63.
- Indiana: no estate or inheritance tax, 2.95% income tax 2026 + county, CollegeChoice 529 credit 20% up to $1,500, UTMA to 21, legacy trust (self-settled APT) statute, PTET election. Federal exemption $15M. These are flagged for counsel/CPA.

## Conventions

- Same house style and CSS as the Glynn intro; footers "n / 24"; content must end above y=1024. One generic tooltip script handles every `.tipwrap`; the architecture slide keeps its own layer/zoom script.
- Render-check before reporting: headless Chrome per slide plus a measuring script (content bottom vs 1024, overflow, SVG text outside its viewBox or rect, text collisions). Keep scratch files in the scratchpad, never in this folder.
- Sensitive topics handled with care in client copy: Luke's father (open item, not speculated), Pearl's Medicare review (stated factually, she is the owner).
- Final messages flag every placeholder and assumption.

## Open items the client has not yet answered

Real-estate schedule (addresses, states, titling, rents, costs, debt); the 2024 trust and other documents; guardian and trustee choices; Luke's father's status; entity types, tax elections, 2025 returns and guarantees for the four companies; the $300K business account; the fifth business and what Fergus is; Pearl buyer and terms, Distinct interest; IUL illustrations and beneficiaries, P&C policies, health coverage; the old 401(k) and 2020 E*TRADE account; confirm $15K/mo from 51 and whether consulting continues.
