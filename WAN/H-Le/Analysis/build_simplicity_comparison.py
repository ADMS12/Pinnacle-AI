# -*- coding: utf-8 -*-
"""Builds 'H-Le Simplicity Proposal Comparison' HTML + PDF.
Sources: the two Simplicity proposals in WAN/H-Le/Simplicity (Oct 6 and Oct 8, 2026),
the Aug 2026 Merrill review (H-Le Portfolio Review.html), the NAC annuity statement,
and public fund data pulled Oct 9, 2026 (cited on the last page).
Run:  python -X utf8 build_simplicity_comparison.py --pdf
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.abspath(os.path.join(HERE, "..", "Simplicity"))
OUT_HTML = os.path.join(OUT_DIR, "H-Le Simplicity Proposal Comparison.html")
OUT_PDF = os.path.join(OUT_DIR, "H-Le Simplicity Proposal Comparison.pdf")

ADV = 0.92               # advisory rate agreed for both proposals (proposals were printed at 1.60%)
ADV_PRINTED = 1.60
FEE_ADJ = ADV_PRINTED - ADV   # Simplicity's net returns deducted 1.60%; restate them at 0.92%

# ---------- inputs ----------
INV = 1_210_100          # two IRAs that carry the advisory fee
HH = 1_274_750           # household incl. $64,650 annuity
ANN = 64_650
ROLL, ROTH = 1_180_000, 30_100

# household fee lines as printed (blended over HH), converted to the managed IRAs
A_fee = dict(adv=ADV, mgmt=0.09*HH/INV, er=0.27*HH/INV)
B_fee = dict(adv=ADV, mgmt=0.0,          er=0.06*HH/INV)
C_fee = dict(adv=0.68, mgmt=0.0, er=0.55)        # Merrill: observed 0.68% + est. active-fund ER
tot = lambda f: sum(f.values())
A_pct, B_pct, C_pct = tot(A_fee), tot(B_fee), tot(C_fee)
A_usd, B_usd, C_usd = (INV*A_pct/100, INV*B_pct/100, INV*C_pct/100)

# Simplicity hypothetical returns 07/2021-06/2026, net of proposed advisory fee (Rollover model)
A_ret = dict(ytd=12.02, y1=24.62, y3=18.38, y5=10.66, y10=None, sd=13.03, dd=-22.41, sharpe=2.20, beta=0.93, up=100.88, down=82.17, yld=1.99)
A_bm  = dict(ytd=9.16,  y1=20.76, y3=15.38, y5=7.22,  y10=None, sd=13.65, dd=-24.61, sharpe=1.22)
B_ret = dict(ytd=8.79,  y1=17.27, y3=12.96, y5=6.11,  y10=8.03, sd=12.17, dd=-22.48, sharpe=1.06, beta=0.97, up=96.45, down=98.00, yld=2.64)
B_bm  = dict(ytd=7.79,  y1=16.70, y3=13.92, y5=6.58,  y10=8.32, sd=12.44, dd=-23.85, sharpe=1.16)
ROTH_A = dict(y1=21.49, y3=16.24, y5=8.84, y10=10.11, dd=-22.29, ytd=11.37)
# restate every return at the 0.92% advisory rate (full-year periods +0.68, YTD half-year +0.34)
def restate(d):
    for key in ("y1","y3","y5","y10"):
        if d.get(key) is not None: d[key] = round(d[key] + FEE_ADJ, 2)
    if d.get("ytd") is not None: d["ytd"] = round(d["ytd"] + FEE_ADJ/2, 2)
    return d
for _d in (A_ret, A_bm, B_ret, B_bm, ROTH_A): restate(_d)
A_blend5 = (A_ret['y5']*ROLL + ROTH_A['y5']*ROTH)/INV

# Current Merrill proxy: 95% MSCI ACWI net + 5% US Aggregate, to June 30, 2026, less the 1.23% all-in cost
ACWI = dict(y1=23.87, y3=19.79, y5=11.07, y10=12.92)
AGG  = dict(y1=6.0,   y3=4.0,   y5=-0.3,  y10=1.8)
M_gross = {kk: 0.95*ACWI[kk] + 0.05*AGG[kk] for kk in ACWI}
M_ret = {kk: round(v - 1.23, 2) for kk, v in M_gross.items()}
M_ret.update(ytd=13.7, sd=14.5, dd=-24.4)   # YTD actual (Aug 2026 statements); vol and drawdown from the 80/20 benchmark scaled to 95/5

# household allocation (as printed)
A_alloc = [("US equity",42.10),("International equity",25.28),("Emerging markets",4.75),("Alternatives",18.29),("Fixed income",2.52),("Cash & multi-asset",1.99),("Annuity",5.07)]
B_alloc = [("US equity",39.87),("International equity",18.99),("Emerging markets",8.07),("Alternatives",1.90),("Fixed income",24.21),("Cash & multi-asset",1.90),("Annuity",5.07)]
C_alloc = [("US equity",66.0),("International equity",22.0),("Emerging markets",7.0),("Alternatives",0.0),("Fixed income",3.8),("Cash & multi-asset",1.2),("Annuity",0.0)]  # Merrill IRAs only, approx split of 95% equity

# forward capital-market assumptions (gross, nominal) - conservative, stated on the page
CMA = {"US equity":6.5,"International equity":7.0,"Emerging markets":7.5,"Alternatives":5.0,"Fixed income":4.5,"Cash & multi-asset":4.0,"Annuity":4.5}
def gross_ex_annuity(alloc):
    w = [(k,v) for k,v in alloc if k!="Annuity"]; s=sum(v for _,v in w)
    return sum(CMA[k]*v for k,v in w)/s
A_fwd_gross, B_fwd_gross, C_fwd_gross = gross_ex_annuity(A_alloc), gross_ex_annuity(B_alloc), gross_ex_annuity(C_alloc)
A_fwd, B_fwd, C_fwd = A_fwd_gross-A_pct, B_fwd_gross-B_pct, C_fwd_gross-C_pct

def grow(r, yrs=10, p=INV): return p*(1+r/100)**yrs
proj = {
  "backtest": dict(A=grow(A_blend5), B=grow(B_ret['y5']), C=grow(M_ret['y5'])),
  "forward":  dict(A=grow(A_fwd), B=grow(B_fwd), C=grow(C_fwd)),
}
# cumulative extra fee of A over B, balance growing 6%
bal, extra = INV, 0
for _ in range(10):
    bal *= 1.06; extra += bal*(A_pct-B_pct)/100

VAR = dict(A_up=338_055, A_dn=-163_868, B_up=318_654, B_dn=-147_711, A_lock=12.85, B_lock=11.59, A_floor=1_110_882, B_floor=1_127_039)

money = lambda v: "${:,.0f}".format(v)
k = lambda v: "${:,.0f}K".format(v/1000) if abs(v) < 1_000_000 else "${:,.2f}M".format(v/1_000_000)

# ---------- palette (dataviz reference instance) ----------
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
NAVY = "#0d366b"; RED = "#e34948"; GREEN = "#008300"
INK, INK2, MUTED, LINE, SURF2 = "#0b0b0b", "#52514e", "#8a8984", "#e2e1dc", "#f4f3ef"
FONT = "font-family=\"Segoe UI, Arial, sans-serif\""

# ---------- SVG charts ----------
ALLOC_COLORS = {"US equity":"#1c5cab","International equity":"#5598e7","Emerging markets":"#9ec5f4","Alternatives":ORANGE,"Fixed income":AQUA,"Cash & multi-asset":"#bdbcb5","Annuity":YELLOW}

def alloc_bar(alloc, y, label, W=620, X=150, H=26):
    x = X; parts = [f'<text x="{X-10}" y="{y+H/2+5}" text-anchor="end" font-size="12" fill="{INK}" font-weight="600">{label}</text>']
    for name, v in alloc:
        if v <= 0: continue
        w = W*v/100
        parts.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w-2,0):.1f}" height="{H}" rx="3" fill="{ALLOC_COLORS[name]}"><title>{label}: {name} {v:.1f}%</title></rect>')
        if w > 40: parts.append(f'<text x="{x+w/2:.1f}" y="{y+H/2+4}" text-anchor="middle" font-size="11" fill="#fff" font-weight="600">{v:.0f}%</text>')
        x += w
    return "".join(parts)

def alloc_chart():
    s = [f'<svg viewBox="0 0 800 185" width="100%" {FONT}>']
    s.append(alloc_bar(C_alloc, 12, "Today (Merrill IRAs)"))
    s.append(alloc_bar(A_alloc, 56, "Proposal A · Oct 6"))
    s.append(alloc_bar(B_alloc, 100, "Proposal B · Oct 8"))
    x = 60
    for name, c in ALLOC_COLORS.items():
        s.append(f'<rect x="{x}" y="150" width="12" height="12" rx="2" fill="{c}"/><text x="{x+16}" y="160" font-size="10.5" fill="{INK2}">{name}</text>')
        x += 16 + 5.4*len(name) + 12
    s.append('</svg>'); return "".join(s)

def fee_chart():
    rows = [("Today (Merrill, est.)", C_fee, AQUA), ("Proposal A · Oct 6", A_fee, BLUE), ("Proposal B · Oct 8", B_fee, ORANGE)]
    maxv = 2.3; W=440; X=170
    s = [f'<svg viewBox="0 0 800 168" width="100%" {FONT}>']
    for i,(lab,f,c) in enumerate(rows):
        y = 12 + i*44
        s.append(f'<text x="{X-10}" y="{y+18}" text-anchor="end" font-size="12" fill="{INK}" font-weight="600">{lab}</text>')
        x = X
        for key, shade in (("adv",c),("mgmt","#7a7974"),("er","#bdbcb5")):
            v=f[key]
            if v<=0: continue
            w = W*v/maxv
            s.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w-2,0):.1f}" height="28" rx="3" fill="{shade}"><title>{lab} {key} {v:.2f}%</title></rect>')
            if w>40: s.append(f'<text x="{x+w/2:.1f}" y="{y+18}" text-anchor="middle" font-size="11" fill="#fff" font-weight="600">{v:.2f}%</text>')
            x += w
        s.append(f'<text x="{x+8:.1f}" y="{y+18}" font-size="12" fill="{INK}" font-weight="700">{tot(f):.2f}%  ·  {money(INV*tot(f)/100)} / yr</text>')
    y=156
    s.append(f'<rect x="{X}" y="{y-10}" width="12" height="12" rx="2" fill="{INK2}"/><text x="{X+16}" y="{y}" font-size="10.5" fill="{INK2}">Advisory fee (billed)</text>')
    s.append(f'<rect x="{X+150}" y="{y-10}" width="12" height="12" rx="2" fill="#7a7974"/><text x="{X+166}" y="{y}" font-size="10.5" fill="{INK2}">Strategist fee (billed)</text>')
    s.append(f'<rect x="{X+310}" y="{y-10}" width="12" height="12" rx="2" fill="#bdbcb5"/><text x="{X+326}" y="{y}" font-size="10.5" fill="{INK2}">Fund expense ratios (inside returns)</text>')
    s.append('</svg>'); return "".join(s)

def returns_chart():
    periods = [("1 year", A_ret['y1'], B_ret['y1'], A_bm['y1'], B_bm['y1']), ("3 years", A_ret['y3'], B_ret['y3'], A_bm['y3'], B_bm['y3']), ("5 years", A_ret['y5'], B_ret['y5'], A_bm['y5'], B_bm['y5'])]
    W,H,X0,Y0 = 800, 186, 70, 140; maxv = 28; scale = (Y0-26)/maxv
    s=[f'<svg viewBox="0 0 {W} {H}" width="100%" {FONT}>']
    for g in (0,10,20):
        y=Y0-g*scale; s.append(f'<line x1="{X0}" x2="{W-20}" y1="{y:.1f}" y2="{y:.1f}" stroke="{LINE}"/><text x="{X0-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="{MUTED}">{g}%</text>')
    gw = (W-20-X0)/3
    for i,(lab,a,b,abm,bbm) in enumerate(periods):
        cx = X0 + gw*i + gw/2
        for j,(v,bm,c) in enumerate(((a,abm,BLUE),(b,bbm,ORANGE))):
            x = cx - 70 + j*74; h=v*scale
            s.append(f'<rect x="{x}" y="{Y0-h:.1f}" width="64" height="{h:.1f}" rx="4" fill="{c}"><title>{lab}: {v:.2f}% (benchmark {bm:.2f}%)</title></rect>')
            s.append(f'<rect x="{x}" y="{Y0-4}" width="64" height="4" fill="{c}"/>')
            s.append(f'<text x="{x+32}" y="{Y0-h-6:.1f}" text-anchor="middle" font-size="12" fill="{INK}" font-weight="700">{v:.1f}%</text>')
            yb = Y0-bm*scale
            s.append(f'<line x1="{x-4}" x2="{x+68}" y1="{yb:.1f}" y2="{yb:.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="4 3"/>')
        s.append(f'<text x="{cx}" y="{Y0+18}" text-anchor="middle" font-size="12" fill="{INK}" font-weight="600">{lab}</text>')
    s.append(f'<rect x="{X0}" y="{H-14}" width="12" height="12" rx="2" fill="{BLUE}"/><text x="{X0+16}" y="{H-4}" font-size="11" fill="{INK2}">Proposal A (Multi-Manager Aggressive)</text>')
    s.append(f'<rect x="{X0+250}" y="{H-14}" width="12" height="12" rx="2" fill="{ORANGE}"/><text x="{X0+266}" y="{H-4}" font-size="11" fill="{INK2}">Proposal B (SSGA Moderate Growth)</text>')
    s.append(f'<line x1="{X0+490}" x2="{X0+512}" y1="{H-8}" y2="{H-8}" stroke="{INK}" stroke-width="2" stroke-dasharray="4 3"/><text x="{X0+518}" y="{H-4}" font-size="11" fill="{INK2}">Assigned benchmark, same fee deducted</text>')
    s.append('</svg>'); return "".join(s)

def growth_chart():
    W,H,X0,Y0,X1,Y1 = 800, 196, 80, 156, 560, 10
    yrs=10; maxv=4.0e6; minv=1.0e6
    sx = lambda t: X0 + (X1-X0)*t/yrs
    sy = lambda v: Y0 - (Y0-Y1)*(v-minv)/(maxv-minv)
    s=[f'<svg viewBox="0 0 {W} {H}" width="100%" {FONT}>']
    for g in (1.0e6,1.5e6,2.0e6,2.5e6,3.0e6,3.5e6,4.0e6):
        s.append(f'<line x1="{X0}" x2="{X1}" y1="{sy(g):.1f}" y2="{sy(g):.1f}" stroke="{LINE}"/><text x="{X0-8}" y="{sy(g)+4:.1f}" text-anchor="end" font-size="11" fill="{MUTED}">${g/1e6:.1f}M</text>')
    for t in range(0,11,2):
        s.append(f'<text x="{sx(t):.1f}" y="{Y0+18}" text-anchor="middle" font-size="11" fill="{MUTED}">{"Today" if t==0 else f"Year {t}"}</text>')
    series = [("A backtest", A_blend5, BLUE, "6 3"), ("B backtest", B_ret['y5'], ORANGE, "6 3"), ("Merrill proxy backtest", M_ret['y5'], AQUA, "6 3"),
              ("A forward", A_fwd, BLUE, ""), ("B forward", B_fwd, ORANGE, ""), ("Merrill forward", C_fwd, AQUA, "")]
    for lab,r,c,dash in series:
        pts=" ".join(f"{sx(t):.1f},{sy(grow(r,t)):.1f}" for t in range(0,11))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2.5"{d}><title>{lab}: {r:.1f}%/yr</title></polyline>')
        v=grow(r); s.append(f'<circle cx="{sx(10):.1f}" cy="{sy(v):.1f}" r="4" fill="{c}" stroke="#fff" stroke-width="2"/>')
    # end labels to the right of the plot, stacked top-down with a minimum gap so none collide
    labels = sorted([(grow(A_blend5), f"{k(grow(A_blend5))}  A backtest, {A_blend5:.1f}%/yr", BLUE),
              (grow(B_ret['y5']), f"{k(grow(B_ret['y5']))}  B backtest, {B_ret['y5']:.1f}%/yr", ORANGE),
              (grow(M_ret['y5']), f"{k(grow(M_ret['y5']))}  Merrill proxy backtest, {M_ret['y5']:.1f}%/yr", AQUA),
              (grow(C_fwd), f"{k(grow(C_fwd))}  Merrill forward, {C_fwd:.1f}%/yr", AQUA),
              (grow(B_fwd), f"{k(grow(B_fwd))}  B forward, {B_fwd:.1f}%/yr", ORANGE),
              (grow(A_fwd), f"{k(grow(A_fwd))}  A forward, {A_fwd:.1f}%/yr", BLUE)], key=lambda t: -t[0])
    GAP = 15; last = -1e9
    for v,lab,c in labels:
        y = max(sy(v)+4, last+GAP); last = y
        s.append(f'<line x1="{X1+4}" x2="{X1+14}" y1="{sy(v):.1f}" y2="{y-4:.1f}" stroke="{c}" stroke-width="1.5"/>')
        s.append(f'<text x="{X1+18}" y="{y:.1f}" font-size="11" fill="{INK}" font-weight="600">{lab}</text>')
    s.append(f'<text x="{X0}" y="{H-5}" font-size="10.5" fill="{INK2}">Dashed: 5-year net returns to 06/2026 carried forward. Solid: forward assumptions net of all fees. $1,210,100 start, no contributions.</text>')
    s.append('</svg>'); return "".join(s)

def var_chart():
    W,H = 800, 140; mid=330; scale = 290/350_000
    s=[f'<svg viewBox="0 0 {W} {H}" width="100%" {FONT}>']
    s.append(f'<line x1="{mid}" x2="{mid}" y1="8" y2="{H-28}" stroke="{INK2}" stroke-width="1.5"/>')
    for i,(lab,up,dn,c) in enumerate((("Proposal A", VAR['A_up'], VAR['A_dn'], BLUE),("Proposal B", VAR['B_up'], VAR['B_dn'], ORANGE))):
        y = 18 + i*48
        wu, wd = up*scale, -dn*scale
        s.append(f'<rect x="{mid+2}" y="{y}" width="{wu:.1f}" height="28" rx="4" fill="{c}"><title>{lab} upside {money(up)}</title></rect>')
        s.append(f'<rect x="{mid-2-wd:.1f}" y="{y}" width="{wd:.1f}" height="28" rx="4" fill="{RED}"><title>{lab} downside {money(dn)}</title></rect>')
        s.append(f'<text x="{mid+wu+8:.1f}" y="{y+19}" font-size="12" fill="{INK}" font-weight="700">+{money(up)}  (+{up/HH*100:.1f}%)</text>')
        s.append(f'<text x="{mid-wd-8:.1f}" y="{y+19}" text-anchor="end" font-size="12" fill="{INK}" font-weight="700">−{money(-dn)}  ({dn/HH*100:.1f}%)</text>')
        s.append(f'<text x="{mid-wd-8:.1f}" y="{y-5}" text-anchor="end" font-size="11" fill="{INK2}">{lab}</text>')
    s.append(f'<text x="{mid-6}" y="{H-8}" text-anchor="end" font-size="11" fill="{INK2}">Potential one-year downside (95% confidence)</text><text x="{mid+6}" y="{H-8}" font-size="11" fill="{INK2}">Potential one-year upside</text>')
    s.append('</svg>'); return "".join(s)

# ---------- flat illustrations (inline SVG, flat fills, no gradients, no text) ----------
ILL_PATHS = f'''<svg viewBox="0 0 320 200" width="100%" role="img" aria-label="Two roads leading from one point toward two flags">
<rect x="0" y="150" width="320" height="50" fill="#dfeaf8"/>
<circle cx="256" cy="46" r="22" fill="{YELLOW}"/>
<path d="M30 170 C 110 150, 150 90, 250 70" stroke="{BLUE}" stroke-width="14" fill="none" stroke-linecap="round"/>
<path d="M30 170 C 120 170, 170 130, 280 125" stroke="{ORANGE}" stroke-width="14" fill="none" stroke-linecap="round"/>
<circle cx="30" cy="170" r="12" fill="{NAVY}"/>
<rect x="250" y="40" width="3" height="34" fill="{NAVY}"/><path d="M253 40 l 28 8 l -28 8 z" fill="{BLUE}"/>
<rect x="280" y="95" width="3" height="34" fill="{NAVY}"/><path d="M283 95 l 28 8 l -28 8 z" fill="{ORANGE}"/>
<circle cx="70" cy="60" r="14" fill="#fff"/><circle cx="86" cy="60" r="18" fill="#fff"/><circle cx="104" cy="60" r="12" fill="#fff"/><rect x="56" y="60" width="60" height="12" fill="#fff"/>
</svg>'''
ILL_SCALE = f'''<svg viewBox="0 0 320 200" width="100%" role="img" aria-label="A balance scale weighing coins against a shield">
<rect x="150" y="60" width="20" height="110" rx="4" fill="{NAVY}"/>
<rect x="100" y="166" width="120" height="14" rx="6" fill="{NAVY}"/>
<rect x="40" y="52" width="240" height="10" rx="5" fill="{NAVY}" transform="rotate(-6 160 57)"/>
<line x1="70" y1="52" x2="70" y2="100" stroke="{INK2}" stroke-width="3"/><line x1="250" y1="76" x2="250" y2="124" stroke="{INK2}" stroke-width="3"/>
<path d="M30 100 h80 l-8 26 h-64 z" fill="{BLUE}"/>
<path d="M210 124 h80 l-8 26 h-64 z" fill="{ORANGE}"/>
<ellipse cx="70" cy="92" rx="18" ry="6" fill="{YELLOW}"/><ellipse cx="70" cy="84" rx="18" ry="6" fill="{YELLOW}"/><ellipse cx="70" cy="76" rx="18" ry="6" fill="{YELLOW}"/>
<path d="M250 96 l 18 8 v 14 c 0 12 -8 20 -18 24 c -10 -4 -18 -12 -18 -24 v -14 z" fill="{AQUA}"/>
</svg>'''
ILL_STEPS = f'''<svg viewBox="0 0 320 200" width="100%" role="img" aria-label="Ascending steps with a flag at the top">
<rect x="20" y="150" width="60" height="40" fill="#dfeaf8"/><rect x="80" y="120" width="60" height="70" fill="#b7d3f6"/><rect x="140" y="90" width="60" height="100" fill="#86b6ef"/><rect x="200" y="60" width="60" height="130" fill="{BLUE}"/>
<rect x="262" y="20" width="3" height="40" fill="{NAVY}"/><path d="M265 20 l 30 9 l -30 9 z" fill="{ORANGE}"/>
<circle cx="50" cy="128" r="10" fill="{NAVY}"/><rect x="42" y="138" width="16" height="12" rx="3" fill="{NAVY}"/>
<circle cx="290" cy="150" r="14" fill="{YELLOW}"/>
</svg>'''
ILL_SHIELD = f'''<svg viewBox="0 0 320 200" width="100%" role="img" aria-label="An umbrella over a jar of coins with rain">
<path d="M60 90 Q 160 10 260 90 Z" fill="{BLUE}"/>
<rect x="158" y="90" width="4" height="90" fill="{NAVY}"/>
<path d="M162 180 q 0 14 -14 14" stroke="{NAVY}" stroke-width="4" fill="none"/>
<rect x="110" y="120" width="100" height="70" rx="10" fill="{AQUA}"/>
<ellipse cx="160" cy="150" rx="30" ry="7" fill="{YELLOW}"/><ellipse cx="160" cy="162" rx="30" ry="7" fill="{YELLOW}"/><ellipse cx="160" cy="174" rx="30" ry="7" fill="{YELLOW}"/>
<g fill="#9ec5f4"><rect x="20" y="20" width="4" height="16" rx="2"/><rect x="40" y="60" width="4" height="16" rx="2"/><rect x="290" y="30" width="4" height="16" rx="2"/><rect x="275" y="110" width="4" height="16" rx="2"/><rect x="30" y="120" width="4" height="16" rx="2"/><rect x="300" y="150" width="4" height="16" rx="2"/></g>
</svg>'''

# ---------- page assembly ----------
css = f"""
@page {{ size: Letter; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; background:#fff; color:{INK}; font-family: 'Segoe UI', Arial, Helvetica, sans-serif; font-size: 11.5px; line-height:1.45; }}
.page {{ width: 8.5in; height: 11in; padding: 0.55in 0.6in 0.5in; page-break-after: always; position: relative; overflow:hidden; }}
.page:last-child {{ page-break-after: auto; }}
h1 {{ font-size: 26px; margin: 0 0 4px; letter-spacing:-0.3px; color:{NAVY}; }}
h2 {{ font-size: 17px; margin: 0 0 8px; color:{NAVY}; }}
h3 {{ font-size: 12px; margin: 12px 0 5px; color:{INK}; text-transform: uppercase; letter-spacing: .6px; }}
p {{ margin: 0 0 8px; }}
.kicker {{ font-size: 11px; color:{INK2}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }}
.sub {{ color:{INK2}; font-size: 12px; margin-bottom: 14px; }}
.row {{ display:flex; gap: 16px; }}
.col {{ flex:1; min-width:0; }}
.tiles {{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 10px 0 12px; }}
.tile {{ background:{SURF2}; border-radius: 8px; padding: 10px 12px; }}
.tile .v {{ font-size: 20px; font-weight: 700; color:{INK}; line-height:1.1; }}
.tile .l {{ font-size: 10.5px; color:{INK2}; margin-top: 4px; }}
.tile.a {{ border-left: 5px solid {BLUE}; }} .tile.b {{ border-left: 5px solid {ORANGE}; }} .tile.c {{ border-left: 5px solid {AQUA}; }}
table {{ width:100%; border-collapse: collapse; font-size: 11px; }}
th, td {{ padding: 4px 7px; border-bottom: 1px solid {LINE}; text-align: right; vertical-align: top; }}
th:first-child, td:first-child {{ text-align:left; }}
th {{ background:{SURF2}; color:{INK2}; font-weight:600; font-size: 10.5px; }}
.good {{ color:{GREEN}; font-weight:700; }} .bad {{ color:{RED}; font-weight:700; }}
.verdict {{ background:#eef4fc; border-left: 5px solid {BLUE}; border-radius: 6px; padding: 12px 14px; margin: 12px 0; }}
.verdict b {{ color:{NAVY}; }}
.card {{ border:1px solid {LINE}; border-radius: 8px; padding: 10px 12px; }}
.card.a {{ border-top: 5px solid {BLUE}; }} .card.b {{ border-top: 5px solid {ORANGE}; }}
.card h4 {{ margin: 0 0 4px; font-size: 13px; }}
.card ul {{ margin: 4px 0 0 16px; padding:0; }} .card li {{ margin-bottom: 3px; }}
ul.tight {{ margin: 4px 0 8px 18px; padding:0; }} ul.tight li {{ margin-bottom: 4px; }}
.foot {{ position:absolute; bottom: 0.35in; left:0.6in; right:0.6in; font-size: 9.5px; color:{MUTED}; display:flex; justify-content:space-between; border-top:1px solid {LINE}; padding-top:5px; }}
.ill {{ width: 2.2in; flex: none; }}
.note {{ font-size: 10px; color:{INK2}; }}
.small {{ font-size: 10.5px; }}
.chip {{ display:inline-block; padding:1px 7px; border-radius: 10px; font-size:10px; font-weight:700; color:#fff; }}
.chip.a {{ background:{BLUE}; }} .chip.b {{ background:{ORANGE}; }}
td.l {{ text-align:left; }}
table.compact th, table.compact td {{ padding: 3px 6px; }}
"""

def foot(n): return f'<div class="foot"><span>Huong Le · Simplicity proposal comparison · October 9, 2026, revised at a 0.92% advisory fee · Pinnacle Planning</span><span>Page {n} of 5</span></div>'

page1 = f"""
<div class="page">
 <div class="row">
  <div class="col">
   <div class="kicker">Rollover IRA $1,180,000 · Roth IRA $30,100 · NAC annuity $64,650</div>
   <h1>Two Simplicity proposals for Huong Le</h1>
   <div class="sub">Comparing the October 6 proposal (Multi-Manager Aggressive) with the October 8 revision (State Street Moderate Growth) on fees, potential gain, and risk, against the current Merrill accounts. Both move the two Merrill IRAs to Charles Schwab under Simplicity Wealth. The annuity is unchanged in both. Revised October 9 with the advisory fee at 0.92% instead of the printed 1.60%.</div>
  </div>
  <div class="ill">{ILL_PATHS}</div>
 </div>
 <div class="tiles">
  <div class="tile a"><div class="v">{A_pct:.2f}%</div><div class="l">Proposal A all-in cost on the IRAs · {money(A_usd)} a year</div></div>
  <div class="tile b"><div class="v">{B_pct:.2f}%</div><div class="l">Proposal B all-in cost on the IRAs · {money(B_usd)} a year</div></div>
  <div class="tile c"><div class="v">{C_pct:.2f}%</div><div class="l">Today at Merrill, estimated · {money(C_usd)} a year</div></div>
  <div class="tile a"><div class="v">{A_blend5:.1f}%</div><div class="l">A: 5-year hypothetical return a year, net of the 0.92% fee (07/2021–06/2026); B {B_ret['y5']:.1f}%, Merrill proxy {M_ret['y5']:.1f}%</div></div>
 </div>
 <div class="row">
  <div class="col card a"><h4><span class="chip a">A</span> October 6 · Multi-Manager Aggressive</h4>
   <ul class="small">
    <li><b>Rollover IRA:</b> seven sleeves. Bridgeway Blue Chip stocks 29%, Avantis International ETF 27%, Horizon Upside Plus small/mid stocks 16%, First Trust buffer ETF 11%, First Trust alternatives 10%, Avantis Emerging Markets 5%, global REIT 2%.</li>
    <li><b>Roth IRA:</b> BlackRock Target Allocation 80/20 (iShares ETFs).</li>
    <li>Household mix: 72% stocks, 18% alternatives, 3% bonds, 5% annuity.</li>
   </ul></div>
  <div class="col card b"><h4><span class="chip b">B</span> October 8 · SSGA Moderate Growth</h4>
   <ul class="small">
    <li><b>Both IRAs:</b> one State Street Strategic Asset Allocation ETF model (75/25). SPDR S&P 500 32%, developed ex-US 17%, aggregate bond 15%, emerging markets 9%, mid and small cap 10%, plus other bonds, real estate, commodities.</li>
    <li>All index ETFs, 0.06% weighted expense ratio.</li>
    <li>Household mix: 67% stocks, 24% bonds, 2% alternatives, 5% annuity.</li>
   </ul></div>
 </div>
 <div class="verdict">
  <b>Recommendation: Proposal A (October 6) at the 0.92% advisory rate.</b> Huong is 43 with a 20-plus-year horizon and currently holds 95% stocks. Proposal A keeps a growth posture, adds real diversifiers, and its sleeves beat their benchmark on every period with 82% downside capture. At 0.92% its all-in cost is within {money(abs(A_usd-C_usd))} a year of what she pays Merrill today, so the move is close to cost-neutral. Proposal B is cheaper still, about {money(C_usd-B_usd)} a year below Merrill, and simpler, but it is a 75/25 index model that trails its own benchmark after fees, cuts stock exposure by nearly 30 points from today, and still fell 22% in 2022. Choose B only if the October 8 revision reflects Huong asking for less risk. In that case her tolerance, not the numbers, decides.
 </div>
 <h3>What to watch in either case</h3>
 <ul class="tight small">
  <li><b>The 0.92% rate changes the cost picture.</b> At the printed 1.60%, both proposals cost $5,000 to $9,000 a year more than Merrill. At 0.92%, A costs about the same as today and B costs less. Get the 0.92% in the signed advisory agreement, with the tier schedule, before any transfer.</li>
  <li><b>Hypothetical returns are a backtest</b> of the 2021 to 2026 window, which favored US mega-cap growth and international value. Simplicity printed them net of a 1.60% fee; this report restates them at 0.92% by adding 0.68% a year. They do not reflect actual trading.</li>
  <li><b>The Merrill comparison is a proxy.</b> Simplicity did not back-test the current holdings and the full Merrill fund list was not available, so the current accounts are represented by a 95% global stock, 5% bond index mix less the 1.23% she pays today. Her actual 2026 result through August is 13.7% net.</li>
  <li><b>The annuity is a wash.</b> The NAC VersaChoice 10 was issued March 2026 and carries a $4,371 surrender charge, so it stays in place under both proposals.</li>
 </ul>
 {foot(1)}
</div>"""

page2 = f"""
<div class="page">
 <div class="kicker">Section 1</div><h2>What each proposal holds</h2>
 <p class="small">Household allocation as printed in each proposal, beside the August 2026 Merrill statements. The annuity is counted in both proposals; Merrill's bar shows only the two IRAs.</p>
 {alloc_chart()}
 <h3>Proposal A: seven managers in one account</h3>
 <table>
  <tr><th>Sleeve</th><th>Weight</th><th style="text-align:left">What it is</th><th>Expense</th></tr>
  <tr><td>Bridgeway Blue Chip</td><td>29.1%</td><td class="l">About 37 US mega-cap stocks, roughly equal weight, held directly</td><td>none</td></tr>
  <tr><td>Avantis International (AVDE)</td><td>26.9%</td><td class="l">Developed ex-US stocks with a value and profitability tilt; 1-yr +44.7%, 5-yr 10.6%</td><td>0.23%</td></tr>
  <tr><td>Horizon Upside Plus SMID</td><td>16.4%</td><td class="l">About 25 small and mid-cap stock picks on a 12-month view, 3.7% each</td><td>none</td></tr>
  <tr><td>FT Cboe Vest Buffer (BUFR)</td><td>10.6%</td><td class="l">Laddered S&P 500 buffer ETFs; first 10% of loss cushioned, upside capped</td><td>1.05%</td></tr>
  <tr><td>First Trust Alternatives</td><td>9.6%</td><td class="l">Managed futures, long/short equity, commodities, short-duration bonds</td><td>~1.0%</td></tr>
  <tr><td>Avantis Emerging Markets (AVEM)</td><td>5.1%</td><td class="l">Broad emerging-market stocks, value tilt</td><td>0.33%</td></tr>
  <tr><td>iShares Global REIT (REET)</td><td>2.4%</td><td class="l">Global listed real estate</td><td>0.14%</td></tr>
 </table>
 <div class="row" style="margin-top:10px">
  <div class="col">
   <h3>Proposal B: one index model for both IRAs</h3>
   <p class="small">State Street's Strategic Asset Allocation Moderate Growth model targets about 75% stocks and real assets and 25% bonds and cash, rebalanced yearly. Its public factsheet shows 19.1% for one year, 14.8% for three years, and 7.8% for five years to June 30, 2026 before the advisory fee, which lines up with the 6.1% net figure in the proposal. The weighted expense ratio is 0.06%.</p>
   <h3>How they differ</h3>
   <ul class="tight small">
    <li><b>Stock exposure:</b> A keeps 72%, B drops to 67%, and the Merrill accounts hold 95% today. For a 43-year-old with no withdrawals planned, B is the more conservative posture by a wide margin.</li>
    <li><b>Concentration:</b> 45% of A's Rollover IRA is in two lists of individual stocks. Each small-cap name in the Horizon sleeve is about $7,100 of her money. B holds thousands of stocks through index ETFs.</li>
    <li><b>Transparency:</b> B can be checked against a public factsheet. A's blended result exists only in the proposal, because the mix is custom.</li>
    <li><b>Roth IRA:</b> A gives the $30,100 Roth its own BlackRock 80/20 model. B uses the same 75/25 model as the Rollover. Either is fine at this size.</li>
   </ul>
  </div>
  <div class="ill">{ILL_SCALE}</div>
 </div>
 {foot(2)}
</div>"""

page3 = f"""
<div class="page">
 <div class="kicker">Section 2</div><h2>Fees</h2>
 <p class="small">Simplicity prints fees blended across the whole household including the annuity, at a 1.60% advisory rate. The figures below are restated on the $1,210,100 that actually pays the fee, the two IRAs, at the 0.92% advisory rate now on the table for both proposals.</p>
 {fee_chart()}
 <table style="margin-top:8px">
  <tr><th>Annual cost line</th><th>Today at Merrill (est.)</th><th>Proposal A · Oct 6</th><th>Proposal B · Oct 8</th></tr>
  <tr><td>Advisory fee, billed to the account</td><td>0.68% ({money(INV*0.0068)})</td><td>{ADV:.2f}% ({money(INV*ADV/100)})</td><td>{ADV:.2f}% ({money(INV*ADV/100)})</td></tr>
  <tr><td>Strategist (manager) fee, billed</td><td>none</td><td>{A_fee['mgmt']:.2f}% ({money(INV*A_fee['mgmt']/100)})</td><td>none</td></tr>
  <tr><td>Fund expense ratios, inside returns</td><td>~0.55% ({money(INV*0.0055)})</td><td>{A_fee['er']:.2f}% ({money(INV*A_fee['er']/100)})</td><td>{B_fee['er']:.2f}% ({money(INV*B_fee['er']/100)})</td></tr>
  <tr><td><b>All-in</b></td><td><b>{C_pct:.2f}% ({money(C_usd)})</b></td><td><b>{A_pct:.2f}% ({money(A_usd)})</b></td><td><b>{B_pct:.2f}% ({money(B_usd)})</b></td></tr>
  <tr><td>Change versus today</td><td>—</td><td class="{'bad' if A_usd>C_usd else 'good'}">{'+' if A_usd>C_usd else '−'}{money(abs(A_usd-C_usd))} a year</td><td class="{'bad' if B_usd>C_usd else 'good'}">{'+' if B_usd>C_usd else '−'}{money(abs(B_usd-C_usd))} a year</td></tr>
  <tr><td>At the printed 1.60% rate, for reference</td><td></td><td>{A_pct+FEE_ADJ:.2f}% ({money(INV*(A_pct+FEE_ADJ)/100)})</td><td>{B_pct+FEE_ADJ:.2f}% ({money(INV*(B_pct+FEE_ADJ)/100)})</td></tr>
  <tr><td>A minus B</td><td></td><td colspan="2" style="text-align:center"><b>{money(A_usd-B_usd)} a year</b>, about {money(extra)} over ten years as the balance grows</td></tr>
 </table>
 <div class="row" style="margin-top:14px">
  <div class="col">
   <h3>Reading the fee stack</h3>
   <ul class="tight small">
    <li><b>0.92% is a good rate.</b> It is below the 1.00% to 1.25% that is typical on $1.2 million and well under the 1.60% printed in both proposals. The cut is worth {money(INV*FEE_ADJ/100)} a year, more than twice the 0.32% product-cost gap between A and B.</li>
    <li><b>Merrill's program fee is 0.85%</b> list, reduced to 0.70% or lower for Preferred Rewards members. Huong's statements show about 0.68% being deducted, so she already has the discount. Her real extra cost at Merrill is the active mutual funds, estimated at 0.55%.</li>
    <li><b>Where A's extra cost sits:</b> the buffer ETF at 1.05% and the First Trust alternatives near 1.0% are 20% of the Rollover IRA. The individual-stock sleeves carry no fund expense but a 0.10% strategist fee.</li>
    <li><b>Not in either table:</b> Schwab transaction or custody charges, and trading costs inside Horizon's 12-month stock list. Inside an IRA there is no tax cost to turnover.</li>
   </ul>
   <h3>Before signing</h3>
   <p class="small">The proposals show a single blended rate. Ask Simplicity to reissue the fee page at 0.92% and to confirm whether the rate is flat or tiered, since a tiered schedule can drift back up if the household is split across registrations.</p>
  </div>
  <div class="ill">{ILL_SHIELD}</div>
 </div>
 {foot(3)}
</div>"""

page4 = f"""
<div class="page">
 <div class="kicker">Section 3</div><h2>Potential gain</h2>
 <p class="small">Simplicity's hypothetical returns for the Rollover IRA model, July 2021 to June 2026, restated net of the 0.92% advisory fee. The dashed tick is the benchmark Simplicity assigned to each model, with the same fee deducted.</p>
 {returns_chart()}
 <table style="margin-top:2px">
  <tr><th>Rollover IRA model, net of fee</th><th>YTD 2026</th><th>1 yr</th><th>3 yr</th><th>5 yr</th><th>10 yr</th><th>Volatility</th><th>Worst drop</th><th>Sharpe</th><th>Down capture</th><th>Yield</th></tr>
  <tr><td><span class="chip a">A</span> Multi-Manager Aggressive</td><td>{A_ret['ytd']:.1f}%</td><td>{A_ret['y1']:.1f}%</td><td>{A_ret['y3']:.1f}%</td><td>{A_ret['y5']:.1f}%</td><td>n/a</td><td>{A_ret['sd']:.1f}%</td><td>{A_ret['dd']:.1f}%</td><td>{A_ret['sharpe']:.2f}</td><td>{A_ret['down']:.0f}%</td><td>{A_ret['yld']:.1f}%</td></tr>
  <tr class="note"><td>&nbsp;&nbsp;its benchmark</td><td>{A_bm['ytd']:.1f}%</td><td>{A_bm['y1']:.1f}%</td><td>{A_bm['y3']:.1f}%</td><td>{A_bm['y5']:.1f}%</td><td>n/a</td><td>{A_bm['sd']:.1f}%</td><td>{A_bm['dd']:.1f}%</td><td>{A_bm['sharpe']:.2f}</td><td>100%</td><td></td></tr>
  <tr><td><span class="chip b">B</span> SSGA Moderate Growth</td><td>{B_ret['ytd']:.1f}%</td><td>{B_ret['y1']:.1f}%</td><td>{B_ret['y3']:.1f}%</td><td>{B_ret['y5']:.1f}%</td><td>{B_ret['y10']:.1f}%</td><td>{B_ret['sd']:.1f}%</td><td>{B_ret['dd']:.1f}%</td><td>{B_ret['sharpe']:.2f}</td><td>{B_ret['down']:.0f}%</td><td>{B_ret['yld']:.1f}%</td></tr>
  <tr class="note"><td>&nbsp;&nbsp;its benchmark (75% ACWI / 25% Agg)</td><td>{B_bm['ytd']:.1f}%</td><td>{B_bm['y1']:.1f}%</td><td>{B_bm['y3']:.1f}%</td><td>{B_bm['y5']:.1f}%</td><td>{B_bm['y10']:.1f}%</td><td>{B_bm['sd']:.1f}%</td><td>{B_bm['dd']:.1f}%</td><td>{B_bm['sharpe']:.2f}</td><td>100%</td><td></td></tr>
  <tr class="note"><td>Roth under A: BlackRock 80/20</td><td>{ROTH_A['ytd']:.1f}%</td><td>{ROTH_A['y1']:.1f}%</td><td>{ROTH_A['y3']:.1f}%</td><td>{ROTH_A['y5']:.1f}%</td><td>{ROTH_A['y10']:.1f}%</td><td>13.2%</td><td>{ROTH_A['dd']:.1f}%</td><td>1.69</td><td>98%</td><td>1.7%</td></tr>
 </table>
 <h3 style="margin-top:6px">Potential gain model: the two proposals against the current Merrill accounts</h3>
 <table class="compact">
  <tr><th>Net of all fees, to June 30, 2026</th><th>All-in cost</th><th>YTD 2026</th><th>1 yr</th><th>3 yr</th><th>5 yr</th><th>10 yr</th><th>Gain on $1.21M at the 5-yr rate</th><th>Worst drop</th></tr>
  <tr><td><span class="chip" style="background:{AQUA}">M</span> Today at Merrill (95/5 index proxy)</td><td>{C_pct:.2f}%</td><td>{M_ret['ytd']:.1f}% actual</td><td>{M_ret['y1']:.1f}%</td><td>{M_ret['y3']:.1f}%</td><td>{M_ret['y5']:.1f}%</td><td>{M_ret['y10']:.1f}%</td><td>{money(INV*M_ret['y5']/100)} a year</td><td>about {M_ret['dd']:.0f}%</td></tr>
  <tr><td><span class="chip a">A</span> Multi-Manager Aggressive + BlackRock 80/20</td><td>{A_pct:.2f}%</td><td>{A_ret['ytd']:.1f}%</td><td>{A_ret['y1']:.1f}%</td><td>{A_ret['y3']:.1f}%</td><td>{A_blend5:.1f}%</td><td>n/a</td><td>{money(INV*A_blend5/100)} a year</td><td>{A_ret['dd']:.1f}%</td></tr>
  <tr><td><span class="chip b">B</span> SSGA Moderate Growth, both IRAs</td><td>{B_pct:.2f}%</td><td>{B_ret['ytd']:.1f}%</td><td>{B_ret['y1']:.1f}%</td><td>{B_ret['y3']:.1f}%</td><td>{B_ret['y5']:.1f}%</td><td>{B_ret['y10']:.1f}%</td><td>{money(INV*B_ret['y5']/100)} a year</td><td>{B_ret['dd']:.1f}%</td></tr>
 </table>
 <p class="note" style="margin-top:3px">Merrill proxy: 95% MSCI ACWI net index plus 5% US Aggregate bonds, less the 1.23% she pays today; her actual 2026 result through August was 13.7% net. On this proxy the current all-stock posture out-earned B and sat between A and B over five years, with the deepest drawdown of the three and no buffer.</p>
 <h3 style="margin-top:4px">Ten-year projection of the two IRAs</h3>
 {growth_chart()}
 <table class="compact" style="margin-top:0">
  <tr><th>Basis</th><th>Proposal A</th><th>Proposal B</th><th>Merrill</th><th style="text-align:left">Comment</th></tr>
  <tr><td>5-year net returns carried forward ({A_blend5:.1f}% / {B_ret['y5']:.1f}% / {M_ret['y5']:.1f}%)</td><td>{money(proj['backtest']['A'])}</td><td>{money(proj['backtest']['B'])}</td><td>{money(proj['backtest']['C'])}</td><td class="l note">Optimistic. Assumes the 2021–2026 pattern repeats.</td></tr>
  <tr><td>Forward assumptions net of all fees ({A_fwd:.1f}% / {B_fwd:.1f}% / {C_fwd:.1f}%)</td><td>{money(proj['forward']['A'])}</td><td>{money(proj['forward']['B'])}</td><td>{money(proj['forward']['C'])}</td><td class="l note">Stocks 6.5–7.5%, bonds 4.5%, alternatives 5.0% before fees. Merrill leads only because it stays 95% in stocks.</td></tr>
 </table>
 {foot(4)}
</div>"""

page5 = f"""
<div class="page">
 <div class="kicker">Section 4</div><h2>Risk, suitability, and the call</h2>
 <p class="small">Simplicity's Value at Risk figures for the whole $1,274,750 household, at 95% confidence over one year, and the AssetLock alert floor each proposal sets.</p>
 {var_chart()}
 <div class="row">
  <div class="col">
   <table>
    <tr><th>Risk measure</th><th>Proposal A</th><th>Proposal B</th></tr>
    <tr><td>Potential one-year upside</td><td>+{money(VAR['A_up'])} (+{VAR['A_up']/HH*100:.1f}%)</td><td>+{money(VAR['B_up'])} (+{VAR['B_up']/HH*100:.1f}%)</td></tr>
    <tr><td>Potential one-year downside</td><td>−{money(-VAR['A_dn'])} ({VAR['A_dn']/HH*100:.1f}%)</td><td>−{money(-VAR['B_dn'])} ({VAR['B_dn']/HH*100:.1f}%)</td></tr>
    <tr><td>AssetLock alert threshold</td><td>{VAR['A_lock']:.2f}% ({money(VAR['A_floor'])})</td><td>{VAR['B_lock']:.2f}% ({money(VAR['B_floor'])})</td></tr>
    <tr><td>Worst 5-year drawdown, Rollover model</td><td>{A_ret['dd']:.1f}%</td><td>{B_ret['dd']:.1f}%</td></tr>
    <tr><td>Annualized volatility</td><td>{A_ret['sd']:.1f}%</td><td>{B_ret['sd']:.1f}%</td></tr>
    <tr><td>Beta to benchmark</td><td>{A_ret['beta']:.2f}</td><td>{B_ret['beta']:.2f}</td></tr>
   </table>
   <p class="note" style="margin-top:6px">B's 24% in bonds bought almost no drawdown protection in this window: both models fell about 22% in 2022, when bonds fell with stocks. A's cushion came from the buffer ETF and the alternatives sleeve instead, which is why its downside capture is 82% against B's 98%.</p>
  </div>
  <div class="ill">{ILL_STEPS}</div>
 </div>
 <div class="verdict">
  <b>Recommendation.</b> Go with <b>Proposal A (October 6)</b> for the Rollover IRA, and the BlackRock 80/20 model for the Roth, on three conditions:
  <ol class="small" style="margin:6px 0 0 18px; padding:0">
   <li>Lock the 0.92% advisory rate into the signed agreement, with the tier schedule. The printed proposals still say 1.60%, and the difference is {money(INV*FEE_ADJ/100)} a year.</li>
   <li>Confirm Huong is comfortable that 45% of the Rollover is two lists of individual stocks, including 25 small caps that turn over yearly. If not, ask Simplicity to swap the Horizon sleeve for a small-cap ETF such as Avantis US Small Cap Value and keep the rest.</li>
   <li>Get the AssetLock threshold in writing at the 12.85% shown, with a plan for what happens at the alert. It is a notification, not a stop-loss.</li>
  </ol>
  <p class="small" style="margin:8px 0 0"><b>When B is the right answer.</b> If the October 8 revision came from Huong saying she wants less risk than her Merrill accounts carry, Proposal B matches that request and the fee is lower. In that case, point out that she is paying {B_pct:.2f}% all-in for an index model that trailed its own benchmark on every period, and ask whether Simplicity offers the same 75/25 posture with the buffer and alternatives sleeves from A.</p>
  <p class="small" style="margin:8px 0 0"><b>Either way, name the trade-off plainly.</b> At 0.92%, A costs about the same as Merrill and B saves roughly {money(C_usd-B_usd)} a year, so cost is no longer the obstacle. What changes is risk: both proposals take her from 95% stocks to 67% to 72%, and on a plain index proxy her current posture would have earned as much as A over five years with a deeper drawdown. The case for moving rests on risk management, monitoring, and planning, and it has to be justified on the next downturn, not the last rally.</p>
 </div>
 <h3>Sources and limits</h3>
 <ul class="tight note">
  <li>Simplicity Wealth proposals for Huong Le dated October 6, 2026 (75 pages) and October 8, 2026 (64 pages): allocation, fee, VaR, AssetLock and hypothetical performance pages. Returns are hypothetical, printed net of a 1.60% advisory fee for 07/2021–06/2026, and restated here at 0.92% by adding 0.68% a year (0.34% to the half-year YTD). They are not actual client results.</li>
  <li>Merrill Rollover and Roth IRA statements for August 2026 as analyzed in the H-Le Portfolio Review; NAC VersaChoice 10 contract summary as of September 15, 2026.</li>
  <li>Public data retrieved October 9, 2026: Merrill Guided Investing with Advisor fee 0.85%, reduced for Preferred Rewards (NerdWallet, Merrill CRS); BUFR expense 1.05% and returns (etfrc.com); AVDE returns and 0.23% expense (etfdb.com); State Street Strategic AA Moderate Growth factsheet to June 30, 2026 (ssga.com); BlackRock Target Allocation 80/20 fund returns (blackrock.com); S&P 500 total return 15.2% a year for the ten years to September 30, 2026 (chartrow.com); MSCI ACWI net index returns to June 30, 2026 of 23.9% (1 yr), 19.8% (3 yr), 11.1% (5 yr) and 12.9% (10 yr) via the iShares ACWI ETF page (blackrock.com); US Aggregate bond figures are approximate.</li>
  <li>Merrill fund expense ratio of 0.55% is an estimate; the full holdings page was not available. Forward return assumptions are the analyst's, stated on page 4, and are not forecasts. Nothing here is tax or legal advice.</li>
 </ul>
 {foot(5)}
</div>"""

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>H-Le Simplicity Proposal Comparison</title><style>{css}</style></head><body>{page1}{page2}{page3}{page4}{page5}</body></html>"""
with open(OUT_HTML, "w", encoding="utf-8") as f: f.write(html)
print("wrote", OUT_HTML)
print(f"A {A_pct:.3f}% {A_usd:,.0f} | B {B_pct:.3f}% {B_usd:,.0f} | C {C_pct:.3f}% {C_usd:,.0f} | A5blend {A_blend5:.2f} | fwd A {A_fwd:.2f} B {B_fwd:.2f} C {C_fwd:.2f} | extra10y {extra:,.0f}")
print({kk: {a: round(b) for a, b in v.items()} for kk, v in proj.items()})

if "--pdf" in sys.argv:
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    tmp = os.path.join(os.environ.get("TEMP", HERE), "hle-chrome-profile")
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={tmp}", "--no-pdf-header-footer",
           f"--print-to-pdf={os.path.abspath(OUT_PDF)}", "file:///" + OUT_HTML.replace("\\", "/")]
    if os.path.exists(OUT_PDF):
        try: os.remove(OUT_PDF)
        except OSError as e: print("WARNING: could not remove old PDF (is it open?):", e)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print("chrome exit", r.returncode, [ln for ln in r.stderr.splitlines() if "bytes written" in ln or "print" in ln.lower()])
    print("pdf", os.path.abspath(OUT_PDF), os.path.getsize(OUT_PDF) if os.path.exists(OUT_PDF) else "MISSING")
