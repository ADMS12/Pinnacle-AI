import json, os
D = json.load(open(os.path.join(os.path.dirname(__file__), 'calc3.json')))
B, S1, T = D['baseline'], D['s1'][1], D['s2']; S1h, S1l = D['s1'][0], D['s1'][2]
Y = T['years']
def m(v): return ('−' if v < 0 else '') + '$' + f"{abs(round(v)):,}"
def k(v): return ('−' if v < 0 else '') + '$' + (f"{abs(v)/1000:.0f}K" if abs(v) >= 100000 else f"{abs(v)/1000:.1f}K")
corpTax = T['c_fed'] + T['c_ca']
s1_spend = S1['econ']['spend'] - 15000; s2_spend = T['econ']['spend'] - 15000; b_spend = B['econ']['spend']
s1_ret = S1['econ']['savings'] + 15000; s2_ret = T['econ']['savings'] + 15000

CSS = """
@page{size:13.33in 7.5in;margin:0}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:#0b0b0b;background:#fff}
.slide{width:13.33in;height:7.5in;padding:.55in .7in .5in;page-break-after:always;position:relative;overflow:hidden;background:#fcfcfb}
.slide:last-child{page-break-after:auto}
h1{font-size:30pt;margin:0 0 6pt;font-weight:700;letter-spacing:-.01em}
h2{font-size:21pt;margin:0 0 10pt;font-weight:650}
h3{font-size:12.5pt;margin:0 0 4pt;font-weight:650}
p,li{font-size:11.5pt;line-height:1.4}
ul{margin:4pt 0;padding-left:16pt}li{margin:3pt 0}
.sub{color:#52514e;font-size:13pt}
.foot{position:absolute;bottom:.3in;left:.7in;right:.7in;font-size:8.5pt;color:#898781;display:flex;justify-content:space-between}
.cols{display:grid;gap:.3in}.c2{grid-template-columns:1fr 1fr}.c3{grid-template-columns:1fr 1fr 1fr}.c21{grid-template-columns:1.25fr 1fr}
.card{background:#fff;border:1px solid rgba(11,11,11,.12);border-radius:10px;padding:10pt 12pt}
.kpi{background:#fff;border:1px solid rgba(11,11,11,.12);border-radius:10px;padding:10pt 12pt}
.kpi .l{font-size:9.5pt;color:#52514e}.kpi .v{font-size:22pt;font-weight:650;white-space:nowrap}.kpi .n{font-size:9pt;color:#898781}
table{width:100%;border-collapse:collapse;font-size:10.5pt;font-variant-numeric:tabular-nums}
th,td{padding:4pt 6pt;text-align:right;border-bottom:1px solid #e1e0d9;vertical-align:top}th:first-child,td:first-child{text-align:left}
th{color:#52514e;font-weight:600}tr.total td{font-weight:650;border-top:2px solid #c3c2b7}
.l{text-align:left!important}
.pos{color:#006300}.neg{color:#d03b3b}.warn{color:#b86a00}
.callout{border-left:4px solid #2a78d6;background:#eef4fc;padding:8pt 12pt;border-radius:6px;font-size:11.5pt}
.callout.o{border-color:#eb6834;background:#fdf0e9}.callout.g{border-color:#1baf7a;background:#e8f7f1}
.tag{display:inline-block;font-size:8.5pt;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:1pt 6pt;border-radius:999px}
.tag.bad{background:rgba(208,59,59,.10);color:#d03b3b}.tag.ok{background:rgba(12,163,12,.10);color:#006300}.tag.mid{background:rgba(250,178,25,.14);color:#b86a00}
.risk{display:grid;grid-template-columns:1fr 1fr;gap:.25in}
.risk .card{border-top:5px solid #e34948}
.risk .card.fix{border-top-color:#1baf7a}
.big{font-size:40pt;font-weight:700;color:#2a78d6;margin:0}
svg text{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
.title{background:#0d366b;color:#fff}.title h1{font-size:40pt;color:#fff}.title .sub{color:#cde2fb;font-size:16pt}.title .foot{color:#86b6ef}
"""

def foot(n): return f'<div class="foot"><span>2026 plan for B LLC and family · prepared October 2026 · confidential</span><span>{n}</span></div>'
def kpi(l, v, n=''): return f'<div class="kpi"><div class="l">{l}</div><div class="v">{v}</div><div class="n">{n}</div></div>'

def stacked_svg(items, width=560, height=250):
    """items: list of (label, [(name,value,color),...])"""
    maxv = max(sum(v for _, v, _ in segs) for _, segs in items)
    n = len(items); bw = 70; gap = (width - 60 - n * bw) / (n + 1)
    out = [f'<svg viewBox="0 0 {width} {height}" width="100%">']
    base = height - 40; scale = (base - 20) / maxv
    for i, (label, segs) in enumerate(items):
        x = 50 + gap + i * (bw + gap); y = base
        for name, v, col in segs:
            h = v * scale; y -= h
            out.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{max(0,h-1.5):.1f}" fill="{col}" rx="2"/>')
            if h > 14: out.append(f'<text x="{x+bw/2}" y="{y+h/2+4:.1f}" text-anchor="middle" font-size="9.5" fill="#fff">{k(v)}</text>')
        out.append(f'<text x="{x+bw/2}" y="{base+16}" text-anchor="middle" font-size="10" fill="#52514e">{label}</text>')
    out.append(f'<line x1="50" y1="{base}" x2="{width-10}" y2="{base}" stroke="#c3c2b7"/>')
    out.append('</svg>')
    return ''.join(out)

COL = dict(tax='#e34948', ret='#1baf7a', prem='#eda100', loan='#6250d6', spend='#2a78d6', keep='#e87ba4')
def segs(e, is_base=False, is_t=False):
    ret = e['savings'] + (0 if is_base else 15000)
    prem = e['health'] + e['premium'] + (T['prem_loan'] if is_t else 0)
    loan = (Y[0]['repay'] + Y[0]['expansion'] if is_t else e['loan_repay']) + e['loan_interest']
    spend = e['spend'] - (0 if is_base else 15000)
    return [('Taxes', e['taxes'], COL['tax']), ('Retirement', ret, COL['ret']), ('Health and life', prem, COL['prem']), ('Loan and retained', loan, COL['loan']), ('Spendable', spend, COL['spend'])]
legend = ''.join(f'<span style="display:inline-block;margin-right:12pt;font-size:9.5pt;color:#52514e"><span style="display:inline-block;width:9pt;height:9pt;background:{c};border-radius:2px;margin-right:4pt;vertical-align:-1pt"></span>{n}</span>' for n, c in [('Taxes',COL['tax']),('Retirement',COL['ret']),('Health and life',COL['prem']),('Loan repayment and retained',COL['loan']),('Spendable',COL['spend'])])

slides = []
# 1 title
slides.append(f'''<div class="slide title"><div style="margin-top:1.6in"><h1>Protecting the family, funding retirement,<br>and fixing the loan</h1>
<div class="sub" style="margin-top:14pt">A 2026 plan for B LLC at $600,000 of revenue</div>
<div class="sub" style="margin-top:40pt;font-size:12pt">Two structures compared, built from the 2025 federal and California returns</div></div>{foot(1)}</div>''')

# 2 where we are
slides.append(f'''<div class="slide"><h2>Where things stand after 2025</h2>
<div class="cols c3" style="margin-bottom:12pt">{kpi('Revenue 2025','$289,584','up 64%, profit down 28%')}{kpi('Ordinary income (K-1)','$69,133','24% of revenue, was 77% in 2023')}{kpi('Personal income (AGI)','$126,792','single filer in 2025')}
{kpi('Federal income tax paid','$46','credits erased an $8,655 bill')}{kpi('Company debt','$171,549','Fundbox, Headway, vehicles, cards at about 21%')}{kpi('Loan to shareholder','$125,100','no note, no interest, no payments')}</div>
<div class="cols c2"><div class="card"><h3>What the returns show</h3><ul>
<li>Revenue grew $113K but deductions grew $121K. Travel, meals and vehicles alone were $90K, 31% of revenue.</li>
<li>Interest went from $734 to $30,941 after a Fundbox advance and a Headway loan.</li>
<li>Officer salary was $13,700 against $52K of distributions and $37K of new loans to the owner.</li>
<li>No health insurance, no life insurance, no retirement plan anywhere on either return.</li></ul></div>
<div class="card"><h3>What 2026 brings</h3><ul>
<li>Revenue target $600,000. With the same cost structure the K-1 is about $335K.</li>
<li>Married filing jointly for the first time, which widens the brackets.</li>
<li>Doing nothing: all taxes about {m(B['econ']['taxes'])}, marginal rate 24% federal plus 9.3% California, and every risk below stays open.</li>
<li>Two credit carryforwards worth $32,928 are available once, in 2026.</li></ul></div></div>{foot(2)}</div>''')

# 3 four risks
slides.append(f'''<div class="slide"><h2>Four risks the family is carrying today</h2>
<div class="risk">
<div class="card"><h3>1. The $125,100 shareholder loan</h3><p>No note, no interest, no repayments, no collateral. The company has $7,505 of equity; without this receivable it is $125K underwater. If the IRS treats it as a distribution the owner owes capital gain tax on $117,595; if as wages, payroll tax on all of it. <b>Exposure: $28K to $35K plus penalties.</b> Lenders see it too.</p></div>
<div class="card"><h3>2. No health insurance</h3><p>A family with no coverage carries unlimited medical risk and gets no deduction. Coverage bought through the company is fully deductible and, in the right structure, carries no payroll tax.</p></div>
<div class="card"><h3>3. No life protection</h3><p>The household depends on one person's earnings from three businesses, with $171K of company debt and a new spouse. There is no death benefit in place. A $1.5M policy on a healthy 31-year-old is inexpensive relative to the income it replaces.</p></div>
<div class="card"><h3>4. No retirement savings</h3><p>Nothing has been set aside. At $600K of revenue the business can fund $38K to $48K a year in SEP-IRAs plus $15K in Roth IRAs, all of it tax-deferred or tax-free, without changing how the business runs.</p></div>
</div>
<div class="callout" style="margin-top:12pt"><b>The plan below addresses all four.</b> Both structures end 2026 with the family insured, retirement funded, the loan on a repayment path, and the company paying down its 21% debt.</div>{foot(3)}</div>''')

# 4 the loan explained
slides.append(f'''<div class="slide"><h2>The loan: how it reduced tax, and what it costs if challenged</h2>
<div class="cols c21"><div><table><thead><tr><th class="l">If the $36,870 taken in 2025 had been</th><th class="l">Tax result</th><th>Cash cost</th></tr></thead><tbody>
<tr><td>Salary</td><td class="l">payroll tax 15.3% plus California; federal absorbed by credit</td><td>≈ $8,500</td></tr>
<tr><td>Distribution</td><td class="l">exceeds $7,505 basis, capital gain at 15%; California</td><td>≈ $2,600</td></tr>
<tr class="total"><td>Loan (what was done)</td><td class="l">nothing reported, nothing paid</td><td>$0</td></tr></tbody></table>
<p style="margin-top:8pt">The company also deducted $30,941 of interest it paid to Fundbox, Headway, the vehicle lenders and card issuers, while charging the owner nothing. Up to about $12K of that deduction is exposed because borrowed money funded the owner's loan.</p>
<table style="margin-top:6pt"><thead><tr><th class="l">If the IRS recharacterizes the full $125,100</th><th>Cost</th></tr></thead><tbody>
<tr><td>As a distribution: $117,595 of capital gain</td><td class="neg">≈ $28K to $35K plus 20% penalty</td></tr>
<tr><td>As wages</td><td class="neg">≈ $19K payroll tax plus income tax plus penalties</td></tr>
<tr><td>Loan respected but below market (§7872)</td><td class="warn">≈ $5K a year of phantom income</td></tr></tbody></table></div>
<div class="card"><h3>What makes a loan a loan</h3><ul><li>A signed note</li><li>Interest at or above the federal rate (about 4%)</li><li>A repayment schedule that is actually followed</li><li>Collateral</li><li>Consistent treatment on the books</li></ul><p><b>None of these is visible in the 2025 return.</b> Every year the balance grows without payments, the case for calling it a loan gets weaker.</p>
<div class="callout o" style="margin-top:6pt">Both plans convert this into a documented, interest-bearing note that is repaid, and send the repayments to the company's most expensive debt.</div></div></div>{foot(4)}</div>''')

# 5 baseline
slides.append(f'''<div class="slide"><h2>$600,000 of revenue with no changes (married, 2026)</h2>
<div class="cols c3" style="margin-bottom:12pt">{kpi('K-1 to the owner',m(B['corp']['k1']),'profit pool $350,201 less $13,700 salary')}{kpi('All taxes',m(B['econ']['taxes']),'federal '+m(B['p']['fed'])+', California '+m(B['p']['ca'])+', S-corp '+m(B['corp']['ca_corp']))}{kpi('Spendable',m(b_spend),'but nothing protected or saved')}</div>
<div class="cols c2"><div class="card"><h3>Why the tax bill is manageable even without changes</h3><ul>
<li>Joint brackets: taxable income of {m(B['p']['ti'])} lands in the 24% bracket, not 35%.</li>
<li>The QBI deduction on the K-1 is {m(B['p']['qbi'])} because joint income is under the $403,500 threshold.</li>
<li>The energy credit and general business credit carryforwards absorb $32,928, but only once.</li>
<li>From 2027 the same income costs about $33K more federal tax because the credits are gone.</li></ul></div>
<div class="card"><h3>What this leaves open</h3><ul>
<li>Loan: still $125,100 and growing.</li><li>Health: no coverage, no deduction.</li><li>Life: no death benefit.</li><li>Retirement: $0.</li>
<li>Reasonable compensation: $13,700 of salary against $335K of profit is the second thing an examiner looks at after the loan.</li></ul>
<p class="small" style="font-size:10pt;color:#52514e">The spendable figure is the whole $401,896 pool less taxes. It is the number the other scenarios are measured against, and it is not a safe number to keep.</p></div></div>{foot(5)}</div>''')

# 6 scenario 1 structure
slides.append(f'''<div class="slide"><h2>Scenario 1: W-2 wages, SEP-IRA, health through the S corp, personal life policy</h2>
<div class="cols c21"><div class="card"><svg viewBox="0 0 600 300" width="100%">
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#898781"/></marker></defs>
<rect x="10" y="100" width="170" height="95" rx="10" fill="#eef4fc" stroke="#2a78d6"/><text x="95" y="124" text-anchor="middle" font-size="12.5" font-weight="600">B LLC (S corp)</text><text x="95" y="142" text-anchor="middle" font-size="11" fill="#52514e">revenue $600K</text><text x="95" y="157" text-anchor="middle" font-size="11" fill="#52514e">profit pool $350.2K</text><text x="95" y="172" text-anchor="middle" font-size="11" fill="#52514e">K-1 {k(S1['corp']['k1'])} to owner</text>
<rect x="230" y="10" width="160" height="50" rx="10" fill="#fdf0e9" stroke="#eb6834"/><text x="310" y="31" text-anchor="middle" font-size="12" font-weight="600">Owner W-2 $140K</text><text x="310" y="48" text-anchor="middle" font-size="10.5" fill="#52514e">+ $18K health in box 1</text>
<rect x="230" y="75" width="160" height="50" rx="10" fill="#fdf0e9" stroke="#eb6834"/><text x="310" y="96" text-anchor="middle" font-size="12" font-weight="600">Spouse W-2 $12K</text><text x="310" y="113" text-anchor="middle" font-size="10.5" fill="#52514e">part-time, documented</text>
<rect x="230" y="140" width="160" height="50" rx="10" fill="#e8f7f1" stroke="#1baf7a"/><text x="310" y="161" text-anchor="middle" font-size="12" font-weight="600">SEP-IRAs $38K</text><text x="310" y="178" text-anchor="middle" font-size="10.5" fill="#52514e">$35K owner, $3K spouse</text>
<rect x="230" y="205" width="160" height="50" rx="10" fill="#fdf0e9" stroke="#eb6834"/><text x="310" y="226" text-anchor="middle" font-size="12" font-weight="600">Payroll taxes</text><text x="310" y="243" text-anchor="middle" font-size="10.5" fill="#52514e">{k(S1['corp']['er_payroll'])} employer side</text>
<line x1="182" y1="120" x2="228" y2="35" stroke="#eb6834" stroke-width="2" marker-end="url(#a)"/><line x1="182" y1="140" x2="228" y2="100" stroke="#eb6834" stroke-width="2" marker-end="url(#a)"/><line x1="182" y1="160" x2="228" y2="165" stroke="#1baf7a" stroke-width="2" marker-end="url(#a)"/><line x1="182" y1="180" x2="228" y2="230" stroke="#eb6834" stroke-width="2" marker-end="url(#a)"/>
<rect x="430" y="40" width="160" height="95" rx="10" fill="#eef4fc" stroke="#2a78d6"/><text x="510" y="62" text-anchor="middle" font-size="12" font-weight="600">Household</text><text x="510" y="80" text-anchor="middle" font-size="10.5" fill="#52514e">taxes {k(S1['econ']['taxes'])}</text><text x="510" y="95" text-anchor="middle" font-size="10.5" fill="#52514e">life premium $24K, loan $30K</text><text x="510" y="110" text-anchor="middle" font-size="10.5" fill="#52514e">Roth $15K</text><text x="510" y="125" text-anchor="middle" font-size="10.5" fill="#52514e">spendable {k(s1_spend)}</text>
<rect x="430" y="150" width="160" height="45" rx="10" fill="#e8f7f1" stroke="#1baf7a"/><text x="510" y="169" text-anchor="middle" font-size="12" font-weight="600">Retirement $53K</text><text x="510" y="186" text-anchor="middle" font-size="10.5" fill="#52514e">SEP + Roth</text>
<rect x="430" y="210" width="160" height="45" rx="10" fill="#e8f7f1" stroke="#1baf7a"/><text x="510" y="229" text-anchor="middle" font-size="12" font-weight="600">Life policy $1.5M</text><text x="510" y="246" text-anchor="middle" font-size="10.5" fill="#52514e">owned personally</text>
<line x1="392" y1="35" x2="428" y2="70" stroke="#eb6834" stroke-width="2" marker-end="url(#a)"/><line x1="392" y1="100" x2="428" y2="95" stroke="#eb6834" stroke-width="2" marker-end="url(#a)"/><line x1="392" y1="165" x2="428" y2="172" stroke="#1baf7a" stroke-width="2" marker-end="url(#a)"/><line x1="560" y1="137" x2="560" y2="208" stroke="#1baf7a" stroke-width="2" marker-end="url(#a)"/>
<polyline points="430,128 412,128 412,285 95,285 95,197" fill="none" stroke="#6250d6" stroke-width="2" marker-end="url(#a)"/><text x="255" y="281" text-anchor="middle" font-size="10" fill="#52514e">$25K principal + $5K interest back to B LLC on the old loan</text></svg></div>
<div><div class="card"><h3>How it works</h3><ul>
<li>Owner $140,000 and spouse $12,000 in W-2 wages. The S corp contributes 25% of both to SEP-IRAs ($38,000) and pays the $18,000 family health premium, both deductible.</li>
<li>Life insurance is bought personally: an S corp cannot fund a policy for its owner on a tax-favored basis. $24,000 a year after tax for about $1.5M of coverage.</li>
<li>The old loan goes on a 4% note and is repaid $25,000 a year from salary; B LLC uses the cash to pay down Fundbox and Headway.</li>
<li>Backdoor Roth IRAs, $7,500 each, from personal cash.</li></ul></div>
<div class="callout g" style="margin-top:10pt">Simple, one entity, every risk addressed. The cost is that protection and the loan are paid with after-tax dollars.</div></div></div>{foot(6)}</div>''')

# 7 scenario 1 numbers
def c1(e): return m(e)
slides.append(f'''<div class="slide"><h2>Scenario 1 at three owner salary levels</h2>
<div class="cols c21"><table><thead><tr><th></th><th>Baseline<br>no changes</th><th>Owner $180K</th><th>Owner $140K</th><th>Owner $100K</th></tr></thead><tbody>
<tr><td>Ordinary income to K-1</td><td>{m(B['corp']['k1'])}</td><td>{m(S1h['corp']['k1'])}</td><td>{m(S1['corp']['k1'])}</td><td>{m(S1l['corp']['k1'])}</td></tr>
<tr><td>Adjusted gross income</td><td>{m(B['p']['agi'])}</td><td>{m(S1h['p']['agi'])}</td><td>{m(S1['p']['agi'])}</td><td>{m(S1l['p']['agi'])}</td></tr>
<tr><td>Federal tax after credits</td><td>{m(B['p']['fed'])}</td><td>{m(S1h['p']['fed'])}</td><td>{m(S1['p']['fed'])}</td><td>{m(S1l['p']['fed'])}</td></tr>
<tr><td>California tax</td><td>{m(B['p']['ca'])}</td><td>{m(S1h['p']['ca'])}</td><td>{m(S1['p']['ca'])}</td><td>{m(S1l['p']['ca'])}</td></tr>
<tr><td>Payroll taxes, both halves</td><td>{m(B['p']['emp_fica']+B['corp']['er_payroll'])}</td><td>{m(S1h['p']['emp_fica']+S1h['corp']['er_payroll'])}</td><td>{m(S1['p']['emp_fica']+S1['corp']['er_payroll'])}</td><td>{m(S1l['p']['emp_fica']+S1l['corp']['er_payroll'])}</td></tr>
<tr class="total"><td>All taxes</td><td>{m(B['econ']['taxes'])}</td><td>{m(S1h['econ']['taxes'])}</td><td>{m(S1['econ']['taxes'])}</td><td>{m(S1l['econ']['taxes'])}</td></tr>
<tr><td>Change vs baseline</td><td>–</td><td class="neg">{m(S1h['econ']['taxes']-B['econ']['taxes'])}</td><td class="neg">{m(S1['econ']['taxes']-B['econ']['taxes'])}</td><td class="neg">{m(S1l['econ']['taxes']-B['econ']['taxes'])}</td></tr>
<tr><td>Retirement (SEP + Roth)</td><td>$0</td><td class="pos">{m(S1h['econ']['savings']+15000)}</td><td class="pos">{m(S1['econ']['savings']+15000)}</td><td class="pos">{m(S1l['econ']['savings']+15000)}</td></tr>
<tr><td>Health and life premiums</td><td>$0</td><td>$42,000</td><td>$42,000</td><td>$42,000</td></tr>
<tr><td>Old loan repaid plus interest</td><td>$0</td><td>$30,004</td><td>$30,004</td><td>$30,004</td></tr>
<tr class="total"><td>Spendable</td><td>{m(b_spend)}</td><td>{m(S1h['econ']['spend']-15000)}</td><td>{m(s1_spend)}</td><td>{m(S1l['econ']['spend']-15000)}</td></tr>
<tr><td>Death benefit in force</td><td class="neg">none</td><td class="pos">$1.5M</td><td class="pos">$1.5M</td><td class="pos">$1.5M</td></tr></tbody></table>
<div><div class="card"><h3>Reading it</h3><ul>
<li>Taxes rise only {m(S1['econ']['taxes']-B['econ']['taxes'])} at $140K. Payroll tax on the wages is offset by the SEP and health deductions.</li>
<li>Spendable drops {m(b_spend-s1_spend)}, but {m(s1_ret)} of that is retirement, $42,000 is insurance and $30,004 is loan repayment. Those are uses of cash, not costs of the structure.</li>
<li>Higher salary buys more SEP: $180K adds $10,000 of SEP for $3,822 more tax. $100K does the reverse.</li>
<li>$140K is the recommended middle: solid reasonable-compensation position, $53K of retirement, room to carry the loan.</li></ul></div></div></div>{foot(7)}</div>''')

# 8 scenario 2 structure
slides.append(f'''<div class="slide"><h2>Scenario 2: a sibling C corporation funds protection, retirement and the loan payoff</h2>
<div class="cols c21"><div class="card"><svg viewBox="0 0 600 330" width="100%">
<defs><marker id="b" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#898781"/></marker></defs>
<polyline points="95,38 95,14 505,14 505,38" fill="none" stroke="#2a78d6" stroke-width="2" marker-end="url(#b)"/><text x="300" y="11" text-anchor="middle" font-size="10.5" fill="#52514e">K-1 distribution {k(T['corp']['k1'])}</text>
<rect x="10" y="40" width="170" height="105" rx="10" fill="#eef4fc" stroke="#2a78d6"/><text x="95" y="62" text-anchor="middle" font-size="12.5" font-weight="600">B LLC (S corp)</text><text x="95" y="80" text-anchor="middle" font-size="11" fill="#52514e">revenue $600K</text><text x="95" y="95" text-anchor="middle" font-size="11" fill="#52514e">profit pool $350.2K</text><text x="95" y="110" text-anchor="middle" font-size="11" fill="#52514e">K-1 {k(T['corp']['k1'])} to owner</text><text x="95" y="125" text-anchor="middle" font-size="11" fill="#52514e">gets {k(Y[0]['repay'])} of loan repaid</text>
<rect x="215" y="40" width="170" height="120" rx="10" fill="#fdf0e9" stroke="#eb6834"/><text x="300" y="62" text-anchor="middle" font-size="12.5" font-weight="600">C corp (sibling)</text><text x="300" y="80" text-anchor="middle" font-size="11" fill="#52514e">fees $300K</text><text x="300" y="95" text-anchor="middle" font-size="11" fill="#52514e">wages $132K, SEP $33K</text><text x="300" y="110" text-anchor="middle" font-size="11" fill="#52514e">health $18K, tax {k(corpTax)}</text><text x="300" y="125" text-anchor="middle" font-size="11" fill="#52514e">retained {k(T['c_after'])}</text><text x="300" y="140" text-anchor="middle" font-size="11" fill="#52514e">lent to owner, 4% note</text>
<line x1="182" y1="75" x2="213" y2="75" stroke="#eb6834" stroke-width="2" marker-end="url(#b)"/><text x="197" y="68" text-anchor="middle" font-size="10" fill="#52514e">$300K fee</text>
<rect x="420" y="40" width="170" height="105" rx="10" fill="#eef4fc" stroke="#2a78d6"/><text x="505" y="62" text-anchor="middle" font-size="12.5" font-weight="600">Owner household</text><text x="505" y="80" text-anchor="middle" font-size="11" fill="#52514e">W-2 $132K + K-1 {k(T['corp']['k1'])}</text><text x="505" y="95" text-anchor="middle" font-size="11" fill="#52514e">taxes {k(T['p']['fed']+T['p']['ca']+T['p']['emp_fica'])}, Roth $15K</text><text x="505" y="110" text-anchor="middle" font-size="11" fill="#52514e">AFR interest {k(Y[0]['interest'])}</text><text x="505" y="125" text-anchor="middle" font-size="11" fill="#52514e">spendable {k(s2_spend)}</text>
<line x1="387" y1="65" x2="418" y2="65" stroke="#eb6834" stroke-width="2" marker-end="url(#b)"/><text x="402" y="58" text-anchor="middle" font-size="10" fill="#52514e">wages</text>
<rect x="215" y="225" width="170" height="60" rx="10" fill="#e8f7f1" stroke="#1baf7a"/><text x="300" y="247" text-anchor="middle" font-size="12" font-weight="600">SEP-IRAs $33K</text><text x="300" y="265" text-anchor="middle" font-size="10.5" fill="#52514e">$30K owner, $3K spouse</text>
<rect x="420" y="225" width="170" height="60" rx="10" fill="#e8f7f1" stroke="#1baf7a"/><text x="505" y="247" text-anchor="middle" font-size="12" font-weight="600">Life policy $1.5M</text><text x="505" y="265" text-anchor="middle" font-size="10.5" fill="#52514e">owner-owned, assigned to corp</text>
<line x1="260" y1="162" x2="260" y2="223" stroke="#1baf7a" stroke-width="2" marker-end="url(#b)"/><line x1="340" y1="162" x2="470" y2="223" stroke="#1baf7a" stroke-width="2" marker-end="url(#b)"/><text x="420" y="188" text-anchor="middle" font-size="10" fill="#52514e">$24K premium loan</text>
<polyline points="505,223 505,200 95,200 95,147" fill="none" stroke="#6250d6" stroke-width="2" marker-end="url(#b)"/><text x="300" y="212" text-anchor="middle" font-size="10" fill="#52514e">{k(Y[0]['repay'])} lent to owner, paid to B LLC on the old loan</text>
<line x1="560" y1="223" x2="560" y2="147" stroke="#898781" stroke-width="2" stroke-dasharray="4 4"/><text x="578" y="188" text-anchor="middle" font-size="9" fill="#898781">collateral</text>
<text x="300" y="316" text-anchor="middle" font-size="10.5" fill="#52514e">At death the policy repays the corporation; the family keeps the rest tax free.</text></svg></div>
<div><div class="card"><h3>How it works</h3><ul>
<li>The owner holds B LLC and a new C corp side by side (a C corp cannot own an S corp). B LLC pays the C corp $300,000 a year for management, sales and admin services under a written agreement.</li>
<li>The C corp pays the owner $120,000 and the spouse $12,000, contributes $33,000 to SEP-IRAs, and provides the $18,000 health plan as a tax-free fringe benefit.</li>
<li>After 28% corporate tax it keeps {m(T['c_after'])}. It lends $24,000 to the owner each year for the life policy (split-dollar, collateral assignment) and the rest to repay B LLC; the old loan is gone in year 3.</li>
<li>B LLC uses the repayments to retire its 21% debt, raising profit from year 2 on.</li></ul></div>
<div class="callout g" style="margin-top:10pt">Protection and the loan payoff are funded with corporate dollars taxed at 28%, not personal dollars taxed at 33%. Money kept inside builds toward expansion and, after five years, possible QSBS treatment.</div></div></div>{foot(8)}</div>''')

# 9 scenario 2 numbers
slides.append(f'''<div class="slide"><h2>Scenario 2 in numbers</h2>
<div class="cols c3"><div><h3>C corporation, year 1</h3><table><tbody>
<tr><td>Fees from B LLC</td><td>{m(T['fee'])}</td></tr><tr><td>Wages, owner and spouse</td><td>{m(-(T['c_wages']+T['c_wages_wife']))}</td></tr><tr><td>Payroll taxes</td><td>{m(-T['c_er'])}</td></tr><tr><td>SEP-IRAs (25%)</td><td>{m(-T['c_sep'])}</td></tr><tr><td>Health (tax-free fringe)</td><td>{m(-T['c_health'])}</td></tr><tr><td>Overhead</td><td>{m(-T['c_admin'])}</td></tr>
<tr class="total"><td>Taxable income</td><td>{m(T['c_pre'])}</td></tr><tr><td>California 8.84% + federal 21%</td><td>{m(-corpTax)}</td></tr><tr class="total"><td>Retained</td><td>{m(T['c_after'])}</td></tr>
<tr><td>Lent for life premium</td><td>{m(T['prem_loan'])}</td></tr><tr><td>Lent to repay B LLC</td><td>{m(Y[0]['repay'])}</td></tr></tbody></table></div>
<div><h3>Personal return (MFJ)</h3><table><tbody>
<tr><td>W-2 wages</td><td>{m(T['c_wages']+T['c_wages_wife'])}</td></tr><tr><td>K-1 from B LLC</td><td>{m(T['corp']['k1'])}</td></tr><tr><td>Other income</td><td>$51,695</td></tr><tr class="total"><td>AGI</td><td>{m(T['p']['agi'])}</td></tr>
<tr><td>Itemized deductions</td><td>{m(-T['p']['itemized'])}</td></tr><tr><td>QBI deduction</td><td>{m(-T['p']['qbi'])}</td></tr><tr class="total"><td>Taxable income</td><td>{m(T['p']['ti'])}</td></tr>
<tr><td>Federal tax after credits</td><td>{m(T['p']['fed'])}</td></tr><tr><td>California tax</td><td>{m(T['p']['ca'])}</td></tr><tr><td>Employee payroll tax</td><td>{m(T['p']['emp_fica'])}</td></tr><tr><td>AFR interest to the C corp</td><td>{m(Y[0]['interest'])}</td></tr></tbody></table></div>
<div><h3>Five-year loan plan</h3><table><thead><tr><th>Year</th><th>Premium</th><th>Repay B LLC</th><th>Old loan left</th></tr></thead><tbody>
{''.join(f"<tr><td>{y['year']}</td><td>{m(y['premium'])}</td><td>{m(y['repay'])}</td><td class='{'warn' if y['b_balance'] else 'pos'}'>{m(y['b_balance'])}</td></tr>" for y in Y)}</tbody></table>
<p style="font-size:10pt;margin-top:6pt">From 2028 the surplus ({m(Y[2]['expansion'])} then {m(Y[3]['expansion'])} a year) becomes the expansion reserve. The owner ends 2028 owing the C corp {m(Y[2]['owes_c'])} on a documented 4% note, secured by the policy.</p>
<div class="callout" style="font-size:10.5pt">All taxes {m(T['econ']['taxes'])} · retirement {m(s2_ret)} · $1.5M protection · spendable {m(s2_spend)}</div></div></div>{foot(9)}</div>''')

# 10 side by side
items = [('Baseline', segs(B['econ'], True)), ('Scenario 1', segs(S1['econ'])), ('Scenario 2', segs(T['econ'], is_t=True))]
slides.append(f'''<div class="slide"><h2>Side by side: taxes, protection, retirement, spendable</h2>
<div class="cols c21"><div><table><thead><tr><th></th><th>Baseline</th><th>Scenario 1 ($140K)</th><th>Scenario 2 (C corp)</th></tr></thead><tbody>
<tr class="total"><td>All taxes</td><td>{m(B['econ']['taxes'])}</td><td>{m(S1['econ']['taxes'])}</td><td>{m(T['econ']['taxes'])}</td></tr>
<tr><td>Change vs baseline</td><td>–</td><td class="neg">{m(S1['econ']['taxes']-B['econ']['taxes'])}</td><td class="neg">{m(T['econ']['taxes']-B['econ']['taxes'])}</td></tr>
<tr><td>Retirement funded (SEP + Roth)</td><td class="neg">$0</td><td class="pos">{m(s1_ret)}</td><td class="pos">{m(s2_ret)}</td></tr>
<tr><td>Health insurance</td><td class="neg">none</td><td class="pos">family, pre-tax</td><td class="pos">family, tax-free fringe</td></tr>
<tr><td>Life insurance death benefit</td><td class="neg">none</td><td class="pos">$1.5M, paid after tax</td><td class="pos">$1.5M, premium lent by C corp</td></tr>
<tr><td>Old loan after year 1</td><td class="neg">$125,100, undocumented</td><td class="warn">$100,100 on a note</td><td class="warn">{m(Y[0]['b_balance'])} on a note</td></tr>
<tr><td>Old loan cleared</td><td class="neg">never</td><td>year 5</td><td>year 3</td></tr>
<tr><td>Company debt at 21% paid down</td><td class="neg">$0</td><td>$25,000 / yr</td><td>{m(Y[0]['repay'])} / yr</td></tr>
<tr><td>Money building inside a corporation</td><td>$0</td><td>$0</td><td>{m(T['c_after'])} / yr</td></tr>
<tr class="total"><td>Spendable</td><td>{m(b_spend)}</td><td>{m(s1_spend)}</td><td>{m(s2_spend)}</td></tr>
<tr><td>Entities, returns, payroll</td><td>1</td><td>1</td><td>2</td></tr></tbody></table></div>
<div><div class="card">{stacked_svg(items)}<div style="margin-top:4pt">{legend}</div></div>
<p style="font-size:10.5pt;margin-top:8pt">Same $401,896 pool in every column. The baseline's spendable figure is larger only because nothing is protected, saved or repaid.</p></div></div>{foot(10)}</div>''')

# 11 life insurance protection
slides.append(f'''<div class="slide"><h2>What the life insurance does for the family</h2>
<div class="cols c2"><div class="card"><h3>Protection today</h3><ul>
<li><b>$1.5M death benefit</b> replaces roughly 10 years of the household's current spendable income if the owner dies.</li>
<li>It clears the company's $171K of debt (the owner has almost certainly guaranteed the Fundbox and Headway balances) and the documented loans, so the spouse does not inherit a leveraged business and a note.</li>
<li>Income-tax free to the beneficiary under both scenarios.</li>
<li>Underwriting at 31 and in good health locks in the lowest lifetime cost; waiting makes every year more expensive and risks insurability.</li></ul></div>
<div class="card"><h3>Cash value over time (permanent policy)</h3><ul>
<li>Premiums of $24,000 a year build cash value that grows tax deferred. Early years are thin (cost of insurance and commissions); by year 10 cash value typically approaches cumulative premiums.</li>
<li>Policy loans against the cash value are tax free, a second source of retirement or emergency cash.</li>
<li>In Scenario 2 the corporation holds a collateral assignment: at death it is repaid first, the family receives the balance. In Scenario 1 the family receives all of it, but premiums came from after-tax income.</li>
<li>A $1.5M 20-year term policy costs under $1,000 a year and can be put in force now while the permanent policy is designed. Protection should not wait for the structure.</li></ul></div></div>
<div class="cols c2" style="margin-top:12pt"><div class="callout"><b>Scenario 1:</b> family owns the policy outright. Cost $24,000 a year out of take-home, roughly $36,000 of pre-tax income at 33%.</div>
<div class="callout g"><b>Scenario 2:</b> the C corp lends the premium from earnings taxed at 28%. The owner pays about 4% interest and nothing else; the corporation is made whole at death. The family keeps the policy and the rest of the benefit.</div></div>
<p style="font-size:10pt;color:#52514e;margin-top:10pt">Death benefit and cash value figures are placeholders until an insurer's illustration is obtained. Disability coverage, not modeled here, is the other gap for a household dependent on one earner.</p>{foot(11)}</div>''')

# 12 recommendation
slides.append(f'''<div class="slide"><h2>Recommendation and next steps</h2>
<div class="cols c2"><div class="card"><h3>Start with Scenario 1 now, build toward Scenario 2</h3><ul>
<li><b>Immediately (this quarter):</b> put the owner and spouse on payroll at $140K and $12K; enroll the family health plan through B LLC; bind a $1.5M term policy; sign a 4% note on the $125,100 loan and make the first payment; stop all undocumented withdrawals.</li>
<li><b>By year end:</b> open SEP-IRAs and fund $38,000 for 2026 (can be paid until the extended due date); fund backdoor Roth IRAs; send every loan repayment to the Fundbox and Headway balances.</li>
<li><b>Then decide on the C corp:</b> if the owner wants to retain earnings for acquisitions and fund the permanent policy with corporate dollars, form the sibling C corp for 2027 with a services agreement, and move payroll, SEP, health and the loan payoff into it as in Scenario 2.</li></ul></div>
<div class="card"><h3>What this achieves</h3><table><tbody>
<tr><td class="l">Loan exposure ($28K to $35K)</td><td class="pos">documented note, repaid, cash goes to 21% debt</td></tr>
<tr><td class="l">No health insurance</td><td class="pos">family covered, fully deductible</td></tr>
<tr><td class="l">No life protection</td><td class="pos">$1.5M in force, tax-free to the family</td></tr>
<tr><td class="l">No retirement savings</td><td class="pos">$48K to $53K a year, tax-deferred and Roth</td></tr>
<tr><td class="l">Reasonable compensation</td><td class="pos">resolved by real W-2 wages</td></tr>
<tr><td class="l">Taxes</td><td class="warn">{m(S1['econ']['taxes']-B['econ']['taxes'])} to {m(T['econ']['taxes']-B['econ']['taxes'])} more than doing nothing; the price of fixing all of the above</td></tr></tbody></table>
<div class="callout o" style="margin-top:8pt">Open items for the next round: the California pass-through entity election (worth roughly $9K to $12K of federal tax), a solo 401(k) in place of the SEP, and expense discipline on the $90K of travel, meals and vehicles.</div></div></div>{foot(12)}</div>''')

# 13 assumptions
slides.append(f'''<div class="slide"><h2>Assumptions and sources</h2>
<div class="cols c2"><div class="card"><h3>Projection assumptions</h3><ul style="font-size:10.5pt">
<li>Revenue $600,000; cost of goods, subcontractors, permits, commissions, supplies, equipment rental and payroll processing grow with sales; all other 2025 expenses held flat. Profit pool before owner pay $350,201.</li>
<li>Married filing jointly for 2026; spouse has no other income and is paid $12,000 for documented part-time work.</li>
<li>Other household income held at 2025: V C LLC wages $36,000 and K-1 $76,351, the V, LLC items, interest, dividends, capital loss. Rental loss suspended above $150K of income.</li>
<li>Health insurance $18,000; permanent life policy $24,000 a year, about $1.5M death benefit (illustration required); SEP at 25% of wages; backdoor Roth $7,500 each.</li>
<li>Old loan: 4% applicable federal rate. Scenario 1 repays $25,000 a year from salary; Scenario 2 repays from C corp loans to the owner.</li>
<li>C corp: $300,000 fee, owner $120,000, spouse $12,000, overhead $6,000, 21% federal and 8.84% California tax, no dividends.</li>
<li>2026 federal MFJ brackets and $32,200 standard deduction; SALT cap $40,400; QBI threshold $403,500; California 2025 MFJ brackets; CA S-corp 1.5%, $800 minimum. Energy credit $10,543 and general business credit $22,385 applied in 2026.</li></ul></div>
<div class="card"><h3>Sources and caveats</h3><ul style="font-size:10.5pt">
<li>2025 Form 1120-S (pages 1 to 5, Schedules K, L, M-1, M-2 and detail), Schedule K-1, Forms 1125-E and 4562, Other Deductions Worksheet, Two-Year Comparison, Form 100S.</li>
<li>2025 Form 1040 with Schedules 1, 2, 3, A, D, E, Form 8995, Tax Summary Report, carryover worksheets, Form 540.</li>
<li>The projection engine reproduces the 2025 federal tax within $1 under 2025 rules.</li>
<li>Interest savings at B LLC from paying down its debt are not included in the year-1 figures; they raise the K-1 from year 2.</li>
<li>Spendable is a cash view: the $401,896 pool less taxes, savings, premiums, loan payments and amounts retained; it ignores non-cash items and personal debt service.</li>
<li>Supporting pages: 2026-Planning-Baseline.html, loan-scenarios.html, scenario-1-w2-sep.html, scenario-2-c-corp.html.</li>
<li>This is planning analysis, not tax, legal or insurance advice. The preparer, an attorney and a licensed insurance professional should review before anything is signed.</li></ul></div></div>{foot(13)}</div>''')

html = f'<!doctype html><html><head><meta charset="utf-8"><title>2026 Plan Presentation</title><style>{CSS}</style></head><body>{"".join(slides)}</body></html>'
out = os.path.join(os.path.dirname(__file__), 'deck.html')
open(out, 'w', encoding='utf-8').write(html)
print('deck written', len(slides), 'slides')
