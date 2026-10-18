import json, os
H = os.path.dirname(__file__)
D = json.load(open(os.path.join(H, 'calc5.json')))
S = {k: D[k] for k in ['s1','s2','s3','s4','s5']}; M = D['meta']
LIVING = 204000  # $17K a month before the spouse joins B LLC; $16K after (her $1,082/mo of premiums stop)
LIVING_BY = {'s1':204000,'s2':192000,'s3':192000,'s4':192000,'s5':192000}
CUR_L = LIVING
def gap(v, L=None):
    d = v - (L or CUR_L); return f'<span class="{"pos" if d>=0 else "neg"}">{("+" if d>=0 else "−")}${abs(round(d)):,}</span>'
def m(v): return ('−' if v < 0 else '') + '$' + f"{abs(round(v)):,}"
def k(v): return ('−' if v < 0 else '') + '$' + (f"{abs(v)/1000:.0f}K" if abs(v) >= 100000 else f"{abs(v)/1000:.1f}K")
C = dict(blue='#2a78d6', navy='#0d366b', orange='#eb6834', green='#1baf7a', yellow='#eda100', violet='#6250d6', pink='#e87ba4', red='#e34948', ink='#0b0b0b', ink2='#52514e', muted='#898781', grid='#e1e0d9', wash='#eef4fc', wash2='#fdf0e9', wash3='#e8f7f1', washr='#fdeaea')

CSS = f"""
@page{{size:1920px 1080px;margin:0}}
*{{box-sizing:border-box}}html{{background:#d9d9d4}}
body{{margin:0;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:{C['ink']}}}
.slide{{width:1920px;height:1080px;padding:70px 90px 60px;position:relative;overflow:hidden;background:#fcfcfb;margin:24px auto;box-shadow:0 2px 14px rgba(0,0,0,.12);page-break-after:always}}
@media print{{html{{background:#fff}}.slide{{margin:0;box-shadow:none}}}}
h1{{font-size:54px;margin:0 0 10px;font-weight:700;letter-spacing:-.01em}}
h2{{font-size:44px;margin:0 0 26px;font-weight:650;letter-spacing:-.01em}}
h3{{font-size:26px;margin:0 0 12px;font-weight:650}}
p,li{{font-size:22px;line-height:1.45}}ul{{margin:6px 0;padding-left:28px}}li{{margin:8px 0}}
.sub{{color:{C['ink2']};font-size:26px}}
.foot{{position:absolute;bottom:28px;left:90px;right:90px;display:flex;justify-content:space-between;font-size:16px;color:{C['muted']}}}
.row{{display:grid;gap:30px}}.c2{{grid-template-columns:1fr 1fr}}.c3{{grid-template-columns:1fr 1fr 1fr}}.c4{{grid-template-columns:repeat(4,1fr)}}.c5{{grid-template-columns:repeat(5,1fr)}}.c21{{grid-template-columns:1.15fr 1fr}}.c12{{grid-template-columns:1fr 1.2fr}}
.card{{background:#fff;border:1px solid rgba(11,11,11,.10);border-radius:18px;padding:28px 32px}}
.card.h{{border-top:8px solid {C['blue']}}}.card.s{{border-top:8px solid {C['green']}}}.card.w{{border-top:8px solid {C['red']};background:{C['washr']}}}
.kpi{{background:#fff;border:1px solid rgba(11,11,11,.10);border-radius:16px;padding:20px 24px}}
.kpi .l{{font-size:18px;color:{C['ink2']}}}.kpi .v{{font-size:40px;font-weight:700;white-space:nowrap;margin:2px 0}}.kpi .n{{font-size:16px;color:{C['muted']}}}
.kpi.good .v{{color:#006300}}.kpi.bad .v{{color:#d03b3b}}.kpi.warn .v{{color:#b86a00}}
table{{width:100%;border-collapse:collapse;font-size:21px;font-variant-numeric:tabular-nums}}
th,td{{padding:9px 12px;text-align:right;border-bottom:1px solid {C['grid']}}}th:first-child,td:first-child{{text-align:left}}
th{{color:{C['ink2']};font-weight:600;font-size:19px}}tr.total td{{font-weight:700;border-top:3px solid #c3c2b7}}
.pos{{color:#006300}}.neg{{color:#d03b3b}}.warn{{color:#b86a00}}
.badge{{display:inline-flex;align-items:center;justify-content:center;width:64px;height:64px;border-radius:50%;background:{C['blue']};color:#fff;font-weight:700;font-size:30px;margin-right:18px;vertical-align:middle}}
.step{{display:flex;align-items:center;margin-bottom:22px}}.step h2{{margin:0}}
.callout{{border-left:8px solid {C['blue']};background:{C['wash']};padding:18px 24px;border-radius:10px;font-size:22px}}
.callout.o{{border-color:{C['orange']};background:{C['wash2']}}}.callout.g{{border-color:{C['green']};background:{C['wash3']}}}.callout.r{{border-color:{C['red']};background:{C['washr']}}}
.legend span{{display:inline-block;margin-right:18px;font-size:17px;color:{C['ink2']}}}.legend i{{display:inline-block;width:14px;height:14px;border-radius:3px;margin-right:6px;vertical-align:-1px}}
.title{{background:{C['navy']};color:#fff}}.title h1{{color:#fff;font-size:64px}}.title .sub{{color:#cde2fb}}
svg text{{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
.icon{{width:84px;height:84px;flex:none}}
.ir{{display:flex;gap:22px;align-items:flex-start}}
.small{{font-size:18px;color:{C['ink2']}}}
.detail table{{font-size:17.5px}}.detail th,.detail td{{padding:5px 10px}}.detail th{{font-size:16px}}.detail li{{font-size:17.5px;margin:4px 0}}.detail .card{{padding:20px 26px}}.detail h3{{font-size:22px;margin-bottom:8px}}.detail .callout{{font-size:17.5px;padding:10px 16px}}
"""
def foot(n): return f'<div class="foot"><span>Personal finance plan · B LLC and family · October 2026 · v2: spouse&#39;s $125K job from 2027 · confidential</span><span>{n} / 13</span></div>'
def kpi(l, v, n='', cls=''): return f'<div class="kpi {cls}"><div class="l">{l}</div><div class="v">{v}</div><div class="n">{n}</div></div>'

# flat icons
def icon(kind, color):
    base = f'<svg class="icon" viewBox="0 0 84 84"><circle cx="42" cy="42" r="40" fill="{color}" opacity=".14"/>'
    if kind == 'shield': return base + f'<path d="M42 18 L62 26 V42 C62 56 52 64 42 68 C32 64 22 56 22 42 V26 Z" fill="{color}"/><path d="M34 42 L40 48 L52 34" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    if kind == 'heart': return base + f'<path d="M42 64 C30 54 20 46 20 36 C20 29 25 24 31 24 C36 24 40 27 42 31 C44 27 48 24 53 24 C59 24 64 29 64 36 C64 46 54 54 42 64 Z" fill="{color}"/></svg>'
    if kind == 'piggy': return base + f'<ellipse cx="44" cy="46" rx="22" ry="16" fill="{color}"/><circle cx="26" cy="44" r="8" fill="{color}"/><rect x="32" y="58" width="6" height="8" fill="{color}"/><rect x="50" y="58" width="6" height="8" fill="{color}"/><rect x="40" y="26" width="10" height="4" rx="2" fill="#fff"/><circle cx="24" cy="42" r="2" fill="#fff"/></svg>'
    if kind == 'warn': return base + f'<path d="M42 18 L68 64 H16 Z" fill="{color}"/><rect x="39" y="34" width="6" height="16" rx="2" fill="#fff"/><circle cx="42" cy="56" r="3.5" fill="#fff"/></svg>'
    if kind == 'rings': return base + f'<circle cx="34" cy="44" r="13" stroke="{color}" stroke-width="6" fill="none"/><circle cx="50" cy="44" r="13" stroke="{color}" stroke-width="6" fill="none"/></svg>'
    if kind == 'building': return base + f'<rect x="24" y="22" width="36" height="42" rx="3" fill="{color}"/><rect x="31" y="30" width="7" height="7" fill="#fff"/><rect x="46" y="30" width="7" height="7" fill="#fff"/><rect x="31" y="42" width="7" height="7" fill="#fff"/><rect x="46" y="42" width="7" height="7" fill="#fff"/><rect x="38" y="52" width="8" height="12" fill="#fff"/></svg>'
    if kind == 'lock': return base + f'<rect x="26" y="38" width="32" height="26" rx="5" fill="{color}"/><path d="M32 38 V31 A10 10 0 0 1 52 31 V38" stroke="{color}" stroke-width="6" fill="none"/><circle cx="42" cy="50" r="3.5" fill="#fff"/></svg>'
    if kind == 'arrows': return base + f'<path d="M22 36 H54 L46 28" stroke="{color}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M62 48 H30 L38 56" stroke="{color}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    return base + '</svg>'

def stacked(cols, width=820, height=420):
    segs = []
    for label, r in cols:
        prem = r['health'] + (r['life'] if not r['ccorp'] else 0)
        loan = (r['loan_repay'] if not r['ccorp'] else 0) + r['loan_interest']
        segs.append((label, [('Taxes', r['taxes'], C['red']), ('Retirement', r['retirement'], C['green']), ('Health and life', prem, C['yellow']), ('Loan payoff', loan, C['violet']), ('Set aside / retained', r['retained'], C['pink']), ('Spendable', r['spend'], C['blue'])]))
    maxv = max(sum(v for _, v, _ in s) for _, s in segs)
    n = len(segs); bw = 110; gap = (width - 80 - n*bw)/(n+1); base = height - 50; scale = (base - 20)/maxv
    out = [f'<svg viewBox="0 0 {width} {height}" width="100%">']
    for i, (label, s) in enumerate(segs):
        x = 70 + gap + i*(bw+gap); y = base
        for name, v, col in s:
            h = v*scale; y -= h
            out.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{max(0,h-2):.1f}" fill="{col}" rx="3"/>')
            if h > 22: out.append(f'<text x="{x+bw/2}" y="{y+h/2+6:.1f}" text-anchor="middle" font-size="16" fill="#fff">{k(v)}</text>')
        out.append(f'<text x="{x+bw/2}" y="{base+28}" text-anchor="middle" font-size="18" fill="{C["ink2"]}">{label}</text>')
    out.append(f'<line x1="70" y1="{base}" x2="{width-10}" y2="{base}" stroke="#c3c2b7"/></svg>')
    return ''.join(out)
LEG = '<div class="legend">' + ''.join(f'<span><i style="background:{c}"></i>{n}</span>' for n, c in [('Taxes',C['red']),('Retirement',C['green']),('Health and life',C['yellow']),('Loan payoff',C['violet']),('Set aside / retained',C['pink']),('Spendable',C['blue'])]) + '</div>'

def detail_table(key, with_c=False):
    global CUR_L; CUR_L = LIVING_BY[key]
    a, b = S[key]
    rows = [('Business profit before owner and spouse pay', lambda r: m(r['pool']))]
    if with_c: rows += [('Fee paid to the C corp', lambda r: m(-r['ccorp']['fee']))]
    else: rows += [('Owner salary', lambda r: m(-r['w_owner'])), ('Spouse salary', lambda r: m(-r['w_wife'])), ('Spouse&#39;s vehicle, now a business expense', lambda r: m(-r['auto']))]
    if not with_c and a['employer']: rows += [('401(k) employer contribution, 20% of pay', lambda r: m(-r['employer'])), ('Health insurance', lambda r: m(-r['health']))]
    rows += [('Business income to the owner (K-1)', lambda r: m(r['k1']), 'total'), ('Spouse&#39;s outside W-2 (new job)', lambda r: m(r['w_ext'])), ('Spouse&#39;s deferral at the new employer', lambda r: m(-r['ext_401k']))]
    if with_c: rows += [('C corp: wages, 401(k), health, vehicle, overhead', lambda r: m(-(r['w_owner']+r['w_wife']+r['er_payroll']+r['employer']+r['health']+r['auto']+r['ccorp']['admin']))), ('C corp tax (21% + 8.84%)', lambda r: m(-(r['ccorp']['ca']+r['ccorp']['fed']))), ('C corp keeps', lambda r: m(r['ccorp']['after']), 'total')]
    rows += [('Household income (AGI)', lambda r: m(r['p']['agi'])), ('Federal tax', lambda r: m(r['p']['fed'])), ('California tax', lambda r: m(r['p']['ca'])), ('Payroll taxes, both halves', lambda r: m(r['p']['emp_fica']+r['er_payroll'])),
             ('All taxes', lambda r: m(r['taxes']), 'total'), ('Retirement funded', lambda r: m(r['retirement'])), ('Health and life premiums', lambda r: m(r['health']+r['life']+(r['ccorp']['premiums'] if with_c else 0)) + (' (lent by C corp)' if with_c else '')),
             ('Loan repaid', lambda r: m(r['loan_repay'] if not with_c else r['ccorp']['repay']) + (' (lent by C corp)' if with_c else '')), ('Set aside or retained', lambda r: m(r['retained'])), ('Spendable', lambda r: m(r['spend']), 'total'), ('Living expenses ($17K a month, $16K while the spouse is on B LLC payroll)', lambda r: m(-r['living'])), ('Surplus or shortfall', lambda r: gap(r['spend'], r['living']), 'total'), ('Loan balance at year end', lambda r: m(r['loan_end']))]
    out = ['<table><thead><tr><th></th><th>2026 · $600K revenue</th><th>2027 · $750K revenue</th></tr></thead><tbody>']
    for r in rows:
        cls = r[2] if len(r) > 2 else ''
        out.append(f'<tr class="{cls}"><td>{r[0]}</td><td>{r[1](a)}</td><td>{r[1](b)}</td></tr>')
    out.append('</tbody></table>'); return ''.join(out)

def summary_card(key, prot, loan_txt):
    global CUR_L; CUR_L = LIVING_BY[key]
    a, b = S[key]
    return f'''<div class="card s"><h3>Summary</h3><div class="row c2" style="gap:16px">
{kpi('All taxes 2026 / 2027', k(a['taxes'])+' / '+k(b['taxes']))}{kpi('Spendable 2026 / 2027', k(a['spend'])+' / '+k(b['spend']))}
{kpi('Retirement funded 2026 / 2027', m(a['retirement'])+(' / '+m(b['retirement']) if b['retirement']!=a['retirement'] else ''), '', 'good' if a['retirement'] else 'bad')}{kpi('Protection', prot, '', 'good' if prot!='none' else 'bad')}
{kpi('Loan at end of 2027', m(b['loan_end']), loan_txt, 'good' if b['loan_end']==0 else 'warn')}{kpi('Spendable vs living cost', gap(a['spend'],a['living'])+' / '+gap(b['spend'],b['living']), '2026 / 2027 vs '+k(a['living'])+(' / '+k(b['living']) if b['living']!=a['living'] else ''))}</div></div>'''


def flow_svg(kind):
    a4 = S['s4'][0]; a5 = S['s5'][0]; c5 = a5['ccorp']
    W, Hh = 880, 760
    def box(x,y,w,h,title,lines,fill,stroke,big=False):
        t = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/><text x="{x+w/2}" y="{y+30}" text-anchor="middle" font-size="{21 if big else 18}" font-weight="700" fill="{C["ink"]}">{title}</text>'
        for i,l in enumerate(lines): t += f'<text x="{x+w/2}" y="{y+56+i*21}" text-anchor="middle" font-size="16" fill="{C["ink2"]}">{l}</text>'
        return t
    def arrow(x1,y1,x2,y2,label,color,dy=-8):
        t = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="3" marker-end="url(#ar)"/>'
        if label: t += f'<text x="{(x1+x2)/2}" y="{min(y1,y2)+dy}" text-anchor="middle" font-size="15" fill="{C["ink2"]}">{label}</text>'
        return t
    o = [f'<svg viewBox="0 0 {W} {Hh}" width="100%"><defs><marker id="ar" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#898781"/></marker></defs>']
    if kind == 4:
        a = a4
        o.append(box(20,20,200,110,'Revenue $600K',['customers pay B LLC'],C['wash'],C['blue'],True))
        o.append(box(20,180,200,150,'B LLC (S corp)',['costs '+k(600000-a['pool']),'profit pool '+k(a['pool']),'K-1 '+k(a['k1'])+' to owner'],C['wash'],C['blue'],True))
        o.append(arrow(120,132,120,178,'',C['blue']))
        o.append(box(300,20,250,80,'Salaries $152K',['owner $140K, spouse $12K'],C['wash2'],C['orange']))
        o.append(box(300,120,250,80,'401(k) employer '+k(a['employer']),['plus '+k(a['deferrals'])+' from salaries'],C['wash3'],C['green']))
        o.append(box(300,220,250,80,'Health plan $18K',['deductible, no payroll tax'],C['wash3'],C['green']))
        o.append(box(300,320,250,80,'Payroll taxes '+k(a['er_payroll']+a['p']['emp_fica']),['both halves'],C['washr'],C['red']))
        o.append(box(300,420,250,80,'Set aside $100K',['stays in B LLC for growth'],'#fbe9f1',C['pink']))
        for y in (60,160,260,360,460): o.append(arrow(222,255,298,y,'',C['muted']))
        o.append(box(630,60,230,170,'Household',['AGI '+k(a['p']['agi']),'income tax '+k(a['p']['fed']+a['p']['ca']),'spendable '+k(a['spend'])],C['wash'],C['blue'],True))
        o.append(arrow(552,60,628,120,'',C['orange']))
        o.append(box(630,280,230,80,'Life policies $36K',['paid from take-home'],C['wash3'],C['green']))
        o.append(box(630,380,230,80,'Roth IRAs $15K',['paid from take-home'],C['wash3'],C['green']))
        o.append(box(630,480,230,80,'Loan payoff $62.5K',['distribution paid straight back'],'#efecfb',C['violet']))
        o.append(arrow(745,232,745,278,'',C['green'])); o.append(arrow(745,362,745,378,'',C['green'])); o.append(arrow(745,462,745,478,'',C['violet']))
        o.append(f'<polyline points="630,520 580,520 580,600 120,600 120,332" fill="none" stroke="{C["violet"]}" stroke-width="3" marker-end="url(#ar)"/><text x="350" y="592" text-anchor="middle" font-size="15" fill="{C["ink2"]}">$62.5K + $5K interest back to B LLC, used to pay down 21% debt</text>')
        o.append(f'<text x="440" y="680" text-anchor="middle" font-size="18" font-weight="600" fill="{C["ink"]}">One company. Everything the family keeps or protects is paid with after-tax dollars.</text>')
        o.append(f'<text x="440" y="712" text-anchor="middle" font-size="16" fill="{C["ink2"]}">All taxes {k(a["taxes"])} · retirement {k(a["retirement"])} · spendable {k(a["spend"])}</text>')
    else:
        a = a5
        o.append(box(20,20,200,110,'Revenue $600K',['customers pay B LLC'],C['wash'],C['blue'],True))
        o.append(box(20,180,200,150,'B LLC (S corp)',['costs '+k(600000-a['pool']),'fee to C corp $320K','K-1 '+k(a['k1'])+' to owner'],C['wash'],C['blue'],True))
        o.append(arrow(120,132,120,178,'',C['blue']))
        o.append(box(300,160,250,190,'C corp (sibling)',['fees $320K','wages $152K, 401(k) '+k(a['employer']),'health $18K, overhead $6K','corp tax '+k(c5['ca']+c5['fed']),'keeps '+k(c5['after'])],C['wash2'],C['orange'],True))
        o.append(arrow(222,250,298,250,'$320K fee',C['orange']))
        o.append(box(630,20,230,150,'Household',['W-2 $152K + K-1 '+k(a['k1']),'income tax '+k(a['p']['fed']+a['p']['ca']),'spendable '+k(a['spend'])],C['wash'],C['blue'],True))
        o.append(arrow(552,200,628,110,'wages + health',C['orange'],34))
        o.append(f'<polyline points="120,178 120,150 600,150 600,100 628,100" fill="none" stroke="{C["blue"]}" stroke-width="3" marker-end="url(#ar)"/><text x="400" y="142" text-anchor="middle" font-size="15" fill="{C["ink2"]}">K-1 {k(a["k1"])}</text>')
        o.append(box(630,210,230,80,'401(k) '+k(a['deferrals']+a['employer'])+' + Roth $15K',['from C corp and salaries'],C['wash3'],C['green']))
        o.append(arrow(552,230,628,250,'',C['green']))
        o.append(box(300,420,250,90,'Life policies $36K',['premiums lent at 4%','policies pledged to C corp'],C['wash3'],C['green']))
        o.append(box(630,420,230,90,'Loan payoff '+k(c5['repay']),['lent at 4%, paid to B LLC','rest cleared in 2027'],'#efecfb',C['violet']))
        o.append(arrow(400,352,400,418,'C corp loan',C['green'],-10))
        o.append(arrow(520,352,700,418,'C corp loan',C['violet'],-10))
        o.append(f'<polyline points="630,480 580,480 580,640 120,640 120,332" fill="none" stroke="{C["violet"]}" stroke-width="3" marker-end="url(#ar)"/><text x="350" y="632" text-anchor="middle" font-size="15" fill="{C["ink2"]}">{k(c5["repay"])} back to B LLC, used to pay down 21% debt</text>')
        o.append(box(300,530,250,60,'Acquisitions reserve',['from 2027: '+k(S['s5'][1]['ccorp']['acquisitions'])],'#fbe9f1',C['pink']))
        o.append(f'<text x="440" y="680" text-anchor="middle" font-size="18" font-weight="600" fill="{C["ink"]}">Two companies. Protection and the payoff are funded with corporate dollars taxed at 28%.</text>')
        o.append(f'<text x="440" y="712" text-anchor="middle" font-size="16" fill="{C["ink2"]}">All taxes {k(a["taxes"])} · retirement {k(a["retirement"])} · spendable {k(a["spend"])} · owner owes C corp {k(c5["owes_c"])}</text>')
    o.append('</svg>'); return ''.join(o)

def structure_slide(n):
    return f"""<div class="slide"><h2>Two ways to run it: one company or two (2026)</h2>
<div class="row c2"><div class="card" style="border-top:8px solid {C['blue']}"><h3 style="margin-bottom:4px">Scenario 4 · B LLC only</h3>{flow_svg(4)}</div>
<div class="card" style="border-top:8px solid {C['orange']}"><h3 style="margin-bottom:4px">Scenario 5 · B LLC plus a sibling C corp</h3>{flow_svg(5)}</div></div>{foot(n)}</div>"""

s1,s2,s3,s4,s5 = [S[x] for x in ['s1','s2','s3','s4','s5']]
slides = []
# 1 summary 2025 + warning
slides.append(f'''<div class="slide"><h1>2025 in one page, and one warning</h1><div class="sub" style="margin-bottom:28px">B LLC grew fast, kept little of it, and the family is carrying four open risks.</div>
<div class="row c4" style="margin-bottom:26px">{kpi('Revenue','$289,584','up 64% from 2024')}{kpi('Profit to the owner','$69,133','down 28%; 24% of revenue','warn')}{kpi('Income tax paid','$1,745','$46 federal, $1,699 California','good')}{kpi('Company debt','$171,549','at about 21% interest','bad')}</div>
<div class="row c21"><div class="card w"><div class="ir">{icon('warn', C['red'])}<div><h3>The $125,100 loan to the owner</h3><p>Over several years the owner took $125,100 out of the company as a "loan": no written note, no interest, no repayments, no collateral. It is the largest asset on the books, and without it the company is about $125K underwater.</p>
<p><b>If the IRS calls it what it looks like,</b> a distribution or hidden wages, the bill is roughly <b>$28,000 to $35,000</b> plus penalties. Lenders and the IRS both read this line first. Every scenario that follows starts by fixing it.</p><p><b>The yardstick:</b> the household spends about $17,000 a month, $204,000 a year. Once the spouse is on B LLC&#39;s payroll her $1,082 a month of vehicle cost becomes a deductible business expense, so while she is an employee the household is checked against $16,000 a month, $192,000 a year.</p><p><b>New for 2027:</b> the spouse starts a $125,000 W-2 job with another employer. She keeps her $12,000 B LLC role and her 401(k) stays with B LLC. Her pay joins the household and her employer plan covers the family&#39;s health insurance (saving the $18,000 premium).</p></div></div></div>
<div class="card"><h3>Four gaps</h3>
<div class="ir" style="margin-bottom:12px">{icon('lock', C['red'])}<div><b style="font-size:22px">Undocumented loan</b><div class="small">$125,100 and growing each year</div></div></div>
<div class="ir" style="margin-bottom:12px">{icon('heart', C['red'])}<div><b style="font-size:22px">No health insurance</b><div class="small">unlimited medical risk, no deduction</div></div></div>
<div class="ir" style="margin-bottom:12px">{icon('shield', C['red'])}<div><b style="font-size:22px">Minimal life protection</b><div class="small">one $165K policy ($15K cash value) against $171K of guaranteed debt and $204K a year of living costs</div></div></div>
<div class="ir">{icon('piggy', C['red'])}<div><b style="font-size:22px">No retirement savings</b><div class="small">nothing set aside at age 31</div></div></div></div></div>{foot(1)}</div>''')

def overview(n, num, title, how, key, prot, loan_txt, iconkind, heading='How and why we get here'):
    return f'''<div class="slide"><div class="step"><span class="badge">{num}</span><h2>{title}</h2></div>
<div class="row c2"><div class="card h"><div class="ir">{icon(iconkind, C['blue'])}<div><h3>{heading}</h3><ul>{''.join(f'<li>{x}</li>' for x in how)}</ul></div></div></div>{summary_card(key, prot, loan_txt)}</div>{foot(n)}</div>'''
def detail(n, title, key, with_c, notes, callout=None):
    a, b = S[key]
    return f'''<div class="slide detail"><h2>{title}</h2><div class="row c12"><div class="card">{detail_table(key, with_c)}</div>
<div><div class="card"><h3>Where the money goes</h3>{stacked([('2026',a),('2027',b)], 760, 270)}{LEG}</div>
<div class="card" style="margin-top:16px"><h3>Supporting points</h3><ul>{''.join(f'<li>{x}</li>' for x in notes)}</ul></div>{('<div class="callout o" style="margin-top:14px">'+callout+'</div>') if callout else ''}</div></div>{foot(n)}</div>'''

# Scenario 1
slides.append(overview(2, 1, 'Freeze the loan, document it, pay it down', [
 'Stop all new withdrawals from B LLC. Sign a note at the 4% federal rate and pay $25,000 of principal a year.',
 'Nothing else changes: revenue $600K then $750K, the owner stays on a $13,700 salary, married filing jointly, spouse not working for the company.',
 'This turns a tax exposure into an ordinary debt and sends cash back to the company to retire its 21% loans.'], 's1', 'none', 'paid off in five years', 'lock', 'First, close the open door'))
slides.append(detail(3, 'Scenario 1 in numbers', 's1', False, [
 f"Married filing jointly keeps 2026 federal tax at {m(s1[0]['p']['fed'])} with help from one-time credits of $32,928.",
 f"In 2027 the credits are gone and profit is higher: federal tax {m(s1[1]['p']['fed'])}, total taxes {m(s1[1]['taxes'])}.",
 f"Spendable covers $204K of living costs with {m(s1[0]['spend']-204000)} to spare in 2026, but only because nothing is being protected or saved. Every one of the four gaps is still open.",
 'With a $13,700 salary and $340K of profit, the "reasonable compensation" question is the next thing an examiner raises.'],
 'Freezing the loan is the floor, not the plan. The next steps use the business to fund the gaps.'))
# Scenario 2
slides.append(overview(4, 2, 'Bring the spouse into the business', [
 'The spouse is paid $12,000 a year in W-2 wages for documented part-time work (bookkeeping, scheduling, marketing).',
 'Her wages are deductible to B LLC and taxed on the joint return, so income tax is a wash; the net cost is about $2K of payroll tax.', 'As a B LLC employee her vehicle ($1,082 a month, $12,984 a year) becomes a business expense on B LLC&#39;s books, deductible to the extent of documented business use. Household living costs drop from $17K to $16K a month ($192,000 a year) while she is on payroll.',
 'What it buys: Social Security credits for her, a documented role, and eligibility for the retirement plan in the next step.', 'From 2027 she adds a $125,000 W-2 job elsewhere while keeping her $12,000 B LLC role; household income rises and her new employer&#39;s plan covers the family&#39;s health.'], 's2', 'none', 'paid off in five years', 'rings', 'Make it a family business'))
slides.append(detail(5, 'Scenario 2 in numbers', 's2', False, [
 f"Total taxes move by {m(s2[0]['taxes']-s1[0]['taxes'])} in 2026 and {m(s2[1]['taxes']-s1[1]['taxes'])} in 2027 compared with step 1.",
 'Still no retirement plan, no health insurance, no life insurance.',
 'The loan is still paid down at $25,000 a year; balance $75,100 at the end of 2027.'],
 'Steps 1 and 2 are housekeeping. Step 3 is where the household\'s position changes.'))
# Scenario 3
slides.append(overview(6, 3, 'Fund retirement and health, set aside for growth, clear the loan in two years', [
 'Owner salary $140,000; spouse $12,000. Both join B LLC&#39;s 401(k): the owner defers $24,500, the spouse defers her full $12,000, and B LLC contributes 20% of pay for each ($28,000 and $2,400). With $15,000 of Roth IRAs that is $81,900 a year, the same in 2027; the spouse does not use her new employer&#39;s plan.',
 'B LLC pays the $18,000 family health premium in 2026; from 2027 the spouse&#39;s employer plan covers the family and the premium disappears.',
 'B LLC sets aside $100,000 of after-tax cash each year for expansion.', 'Living costs: with the spouse on B LLC payroll her $1,082 a month vehicle cost is a B LLC expense ($12,984 a year, reducing the K-1), so the household bar is $16K a month ($192,000 a year) while she is an employee. The shortfall tiles use that bar.',
 'The $125,100 loan is repaid $62,550 in 2026 and $62,550 in 2027 with distributions the owner immediately pays back, tax-free because the income is already taxed.'], 's3', 'health only', 'cleared end of 2027', 'piggy', 'Put the business to work for the family'))
slides.append(detail(7, 'Scenario 3 in numbers', 's3', False, [
 f"Taxes fall to {m(s3[0]['taxes'])} in 2026 even with payroll tax on the salaries: the 401(k) and health deductions remove {m(s3[0]['deferrals']+s3[0]['employer']+s3[0]['health'])} from taxable income.",
 f"Retirement: {m(s3[0]['retirement'])} a year, {m(s3[0]['deferrals']+s3[0]['employer'])} of it pre-tax.",
 f"2026 spendable of {m(s3[0]['spend'])} is low because everything is front-loaded: set-aside, payoff, retirement and health in one year. 2027 recovers to {m(s3[1]['spend'])}.",
 f"Against $192K of living costs, 2026 is short by {m(192000-S['s3'][0]['spend'])}; 2027 shows a surplus of {m(S['s3'][1]['spend']-192000)}. 2027 covers living costs once the spouse&#39;s salary arrives and the health premium drops. For 2026, deferring the $100K set-aside and paying the loan over three years lifts spendable to about {m(S['s3'][0]['spend']+100000+62550-41700)}."],
 'The loan is gone at the end of 2027 and $125,100 returns to the company to retire its most expensive debt. The set-aside is the lever: it is after-tax cash the family can only spare in a year when the loan is not also being repaid.'))
# Scenario 4
slides.append(overview(8, 4, 'Protect the family with cash-value life insurance', [
 'The owner already holds a $165K policy with $15K of cash value. It stays in force, but it covers less than one year of living costs; the plan adds permanent policies of $24,000 a year for the owner (about $1.5M) and $12,000 for the spouse (about $1M), paid from personal, after-tax money.',
 'If the owner dies, $1.5M income-tax free replaces about ten years of spendable income and clears the company debt he has guaranteed.',
 'Cash value grows tax deferred and can be borrowed against later, a second retirement reserve.',
 'A $1.5M 20-year term policy costs under $1,000 a year and can be bound now while the permanent policies are designed.'], 's4', 'health + $1.5M / $1M life', 'cleared end of 2027', 'shield', 'Insure the people who make it work'))
slides.append(detail(9, 'Scenario 4 in numbers', 's4', False, [
 'Taxes, retirement and the loan payoff are identical to step 3. The only change is $36,000 a year of premiums.',
 'Paid personally, $36,000 after tax is about $54,000 of earnings at the household\'s combined 33% marginal rate.',
 f"Spendable: {m(s4[0]['spend'])} in 2026 and {m(s4[1]['spend'])} in 2027, with the spouse's salary and the dropped premium adding about $81,500 to 2027.",
 f"With $192K of living costs the household is short by {m(192000-S['s4'][0]['spend'])} in 2026 and {m(192000-S['s4'][1]['spend'])} in 2027 if everything is funded at once; the spouse's salary turns a {m(192000-111462)} 2027 gap into {m(192000-S['s4'][1]['spend'])}. The existing $165K policy and a term bridge hold the protection need until cash allows the permanent policies.", 'An S corporation cannot pay these premiums for its owner on a tax-favored basis. That is what step 5 changes.'],
 f"{m(s4[0]['spend'])} in 2026 does not cover $192K of living costs. In practice the set-aside or the payoff pace gives way in year one; this step shows what full protection costs when paid personally."))
# Scenario 5
slides.append(overview(10, 5, 'A sibling C corporation pays for protection and the payoff', [
 'The owner forms a C corporation alongside B LLC (it cannot own B LLC without ending the S election). It handles sales, marketing, HR and management and bills B LLC $320,000 in 2026 and $440,000 in 2027.',
 'The C corp runs payroll, the 401(k) with its 20% employer contribution and, in 2026, the health plan (a tax-free benefit there); from 2027 the spouse&#39;s new employer covers health while she keeps her $12,000 C corp role. The C corp pays its own tax at about 28%.',
 'What it keeps is lent to the family on documented 4% notes: the $36,000 of premiums first (policies pledged as collateral), then the loan payoff to B LLC, then money for acquisitions.',
 'At death the policies repay the C corp and the family keeps the rest tax free.'], 's5', 'health + $1.5M / $1M life', 'cleared end of 2027', 'building', 'Let a second company carry the load'))
slides.append(detail(11, 'Scenario 5 in numbers', 's5', True, [
 f"Personal tax nearly disappears: {m(s5[0]['p']['fed'])} federal and {m(s5[0]['p']['ca'])} California in 2026, because most profit is taxed in the C corp at 28% instead of 24% plus 9.3% at home.",
 f"Spendable is {m(s5[0]['spend'])} in 2026 and {m(s5[1]['spend'])} in 2027, far above step 4, because premiums and the payoff come from corporate dollars; the family pays only 4% interest.",
 f"Year one the C corp funds the premiums and {m(s5[0]['ccorp']['repay'])} of the payoff; the rest of the loan clears in 2027 and acquisition money ({m(s5[1]['ccorp']['acquisitions'])}) starts.",
 f"By the end of 2027 the owner owes his own C corp {m(s5[1]['ccorp']['owes_c'])} on documented notes. That is real debt, not a tax exposure.", f"Against $192K of living costs the shortfall is {m(192000-S['s5'][0]['spend'])} in 2026 and {m(192000-S['s5'][1]['spend'])} in 2027 with both policies funded; the spouse&#39;s salary nearly closes 2027 on its own, and the C corp still keeps {m(S['s5'][1]['ccorp']['acquisitions'])} for acquisitions that year."],
 'Conditions: a real services agreement, interest actually paid each year, collateral assignments filed, and board minutes for the acquisition plan. Anything later paid out as a dividend is taxed twice.'))
# 12 Q&A
slides.append(structure_slide(12))
slides.append(f'''<div class="slide"><h2>Questions, decisions and next steps</h2>
<div class="row c3"><div class="card"><h3>Decisions to make today</h3><ul>
<li>Pace of the loan payoff: two years (steps 3 to 5) or five years (steps 1 and 2)?</li>
<li>Owner salary: $140,000 as modeled, or a different level?</li>
<li>Expansion set-aside: $100K a year starting 2026, or start in 2027? At $16K a month of living costs, 2026 only works if the set-aside or the payoff pace gives way.</li>
<li>Life insurance: permanent policies now, or term now and permanent later?</li>
<li>Form the C corporation for 2027, or stay with one entity?</li>
<li>Spouse&#39;s job: confirm the start date, the employer health plan&#39;s family coverage and cost, and the 401(k) match; those three drive the 2027 numbers.</li></ul></div>
<div class="card"><h3>Action items in the next 30 days</h3><ul>
<li>Sign a 4% note on the $125,100 loan and make the first payment.</li>
<li>Put the owner and spouse on payroll; set withholding to cover the projected tax.</li>
<li>Enroll the family health plan through B LLC.</li>
<li>Keep the existing $165K policy in force and review its cost against the $15K cash value; bind a $1.5M term policy on the owner; request permanent-policy illustrations for both.</li>
<li>Open the solo 401(k) and Roth IRAs.</li>
<li>Send every loan repayment to the Fundbox and Headway balances.</li></ul></div>
<div class="card"><h3>For the next 90 days</h3><ul>
<li>Preparer to confirm the credit carryforwards and rerun 2026 estimates.</li>
<li>Attorney to draft the services agreement and split-dollar notes if the C corp proceeds.</li>
<li>Decide the acquisition plan that justifies retained earnings.</li>
<li>Review travel, meals and vehicle spending ($90K in 2025).</li>
<li>Revisit the California pass-through entity election.</li></ul></div></div>
<div class="callout g" style="margin-top:26px"><b>Recommended path:</b> execute steps 1 to 3 now, bridge protection with term insurance, design the permanent policies, and form the C corporation for 2027 if the owner wants to retain earnings for acquisitions and fund the policies through it.</div>
<div class="small" style="margin-top:22px">Planning analysis built from the 2025 federal and California returns under 2026 rules. Not tax, legal or insurance advice; the preparer, an attorney and a licensed insurance professional should review before anything is signed. Supporting detail: five-scenarios-guided.html and the scenario pages.</div>{foot(13)}</div>''')

html = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>2026 Plan, 12 Slides</title><style>{CSS}</style></head><body>{"".join(slides)}</body></html>'
open(os.path.join(H, 'deck3.html'), 'w', encoding='utf-8').write(html); print('slides', len(slides))
