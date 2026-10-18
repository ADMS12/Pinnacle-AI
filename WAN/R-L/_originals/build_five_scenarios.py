import json, os
H = os.path.dirname(__file__)
D = json.load(open(os.path.join(H, 'calc4.json')))
STYLE = open(os.path.join(H, 'scen_common.html'), encoding='utf-8').read()
M = D['meta']; S = {k: D[k] for k in ['s1','s2','s3','s4','s5']}
def m(v): return ('−' if v < 0 else '') + '$' + f"{abs(round(v)):,}"
def k(v): return ('−' if v < 0 else '') + '$' + (f"{abs(v)/1000:.0f}K" if abs(v) >= 100000 else f"{abs(v)/1000:.1f}K")
def pct(r): return f"{round(r*100)}%"
POOL = M['pool']

def two_year_table(rows, key):
    a, b = S[key]
    out = ['<table><thead><tr><th></th><th>2026 · revenue $600,000</th><th>2027 · revenue $750,000</th></tr></thead><tbody>']
    for r in rows:
        if r is None: continue
        if len(r) == 2 and r[1] == 'sec': out.append(f'<tr class="sec"><td colspan="3">{r[0]}</td></tr>'); continue
        label, f = r[0], r[1]; cls = r[2] if len(r) > 2 else ''
        out.append(f'<tr class="{cls}"><td>{label}</td><td>{f(a)}</td><td>{f(b)}</td></tr>')
    out.append('</tbody></table>')
    return ''.join(out)

def rows_s(key, with_c=False):
    R = [('B LLC (S corporation)', 'sec'),
         ('Profit before owner and spouse pay', lambda r: m(r['pool'])),
         (('Management fee to the C corp', lambda r: m(-r['ccorp']['fee'])) if with_c else None),
         (('Owner W-2 wages', lambda r: m(-r['w_owner'])) if not with_c else None),
         (('Spouse W-2 wages', lambda r: m(-r['w_wife'])) if not with_c else None),
         (('Employer payroll taxes', lambda r: m(-r['er_payroll'])) if not with_c else None),
         (('Solo 401(k) employer contribution', lambda r: m(-r['employer'])) if (not with_c and S[key][0]['employer']) else None),
         (('Health insurance (family)', lambda r: m(-r['health'])) if (not with_c and S[key][0]['health']) else None),
         ('Interest income on the owner\'s note', lambda r: m(r['loan_interest'] if not with_c else r['ccorp']['int_b'])),
         ('Ordinary income to K-1', lambda r: m(r['k1']), 'total'),
         ('California S-corp tax', lambda r: m(r['ca_corp'])),
         (('Cash set aside for expansion (after tax, stays in B LLC)', lambda r: m(r['setaside'])) if S[key][0]['setaside'] else None)]
    if with_c:
        R += [('C corporation (sibling)', 'sec'),
              ('Management fees from B LLC', lambda r: m(r['ccorp']['fee'])),
              ('Owner and spouse W-2 wages', lambda r: m(-(r['w_owner']+r['w_wife']))),
              ('Employer payroll taxes', lambda r: m(-r['er_payroll'])),
              ('Solo 401(k) employer contribution', lambda r: m(-r['employer'])),
              ('Health insurance (tax-free fringe)', lambda r: m(-r['health'])),
              ('Overhead of a second entity', lambda r: m(-r['ccorp']['admin'])),
              ('Interest income on loans to the owner', lambda r: m(r['ccorp']['int_c'])),
              ('Corporate taxable income', lambda r: m(r['ccorp']['pre']), 'total'),
              ('California 8.84% and federal 21%', lambda r: m(-(r['ccorp']['ca']+r['ccorp']['fed']))),
              ('Retained after tax', lambda r: m(r['ccorp']['after']), 'total'),
              ('Lent to owner and spouse for policy premiums', lambda r: m(r['ccorp']['premiums'])),
              ('Lent to owner to repay B LLC', lambda r: m(r['ccorp']['repay'])),
              ('Kept for acquisitions and expansion', lambda r: m(r['ccorp']['acquisitions'])),
              ('Owner owes the C corp at year end', lambda r: m(r['ccorp']['owes_c']))]
    R += [('Personal return', 'sec'),
          ('Filing status', lambda r: 'single' if r['fs']=='single' else 'married filing jointly'),
          ('Adjusted gross income', lambda r: m(r['p']['agi'])),
          ('Itemized deductions', lambda r: m(-r['p']['itemized'])),
          ('QBI deduction', lambda r: m(-r['p']['qbi'])),
          ('Taxable income', lambda r: m(r['p']['ti']), 'total'),
          ('Federal tax before credits', lambda r: m(r['p']['fed_gross'])),
          ('Credit carryforwards used', lambda r: m(-r['p']['credits'])),
          ('Federal tax', lambda r: m(r['p']['fed']), 'total'),
          ('Federal marginal bracket', lambda r: pct(r['p']['marginal'])),
          ('California income tax', lambda r: m(r['p']['ca'])),
          ('Employee payroll taxes (incl. V C LLC wages)', lambda r: m(r['p']['emp_fica'])),
          ('Household', 'sec'),
          ('All taxes (personal, both halves of payroll, CA S-corp' + (', C corp)' if with_c else ')'), lambda r: m(r['taxes']), 'total'),
          ('Retirement funded (401(k) deferrals, employer, Roth IRAs)', lambda r: m(r['retirement'])),
          ('Health insurance', lambda r: m(r['health'])),
          ('Life insurance premiums', lambda r: m(r['life']) if not with_c else m(r['ccorp']['premiums']) + ' (lent by C corp)'),
          ('Old loan: principal repaid', lambda r: m(r['loan_repay']) if not with_c else m(r['ccorp']['repay']) + ' (lent by C corp)'),
          ('Interest paid on notes (4%)', lambda r: m(r['loan_interest'])),
          ('Retained for expansion', lambda r: m(r['retained'])),
          ('Spendable', lambda r: m(r['spend']), 'total'),
          ('Old loan balance at year end', lambda r: m(r['loan_end'])),
          ('Life insurance in force', lambda r: 'none' if (r['life']==0 and not with_c) else 'owner $1.5M, spouse about $1M')]
    return R

def stacked(cols, year_idx, width=600, height=260):
    # cols: list of (label, row)
    segs = []
    for label, r in cols:
        prem = r['health'] + (r['life'] if not r['ccorp'] else 0)
        loan = r['loan_repay'] + r['loan_interest'] if not r['ccorp'] else r['loan_interest']
        kept = r['retained']
        segs.append((label, [('Taxes', r['taxes'], '#e34948'), ('Retirement', r['retirement'], '#1baf7a'), ('Health and life', prem, '#eda100'), ('Loan payoff and interest', loan, '#6250d6'), ('Retained / set aside', kept, '#e87ba4'), ('Spendable', r['spend'], '#2a78d6')]))
    maxv = max(sum(v for _, v, _ in s) for _, s in segs)
    n = len(segs); bw = 72; gap = (width - 60 - n*bw)/(n+1); base = height - 44; scale = (base - 16)/maxv
    out = [f'<svg viewBox="0 0 {width} {height}" width="100%">']
    for i, (label, s) in enumerate(segs):
        x = 50 + gap + i*(bw+gap); y = base
        for name, v, col in s:
            h = v*scale; y -= h
            out.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{max(0,h-1.5):.1f}" fill="{col}" rx="2"/>')
            if h > 13: out.append(f'<text x="{x+bw/2}" y="{y+h/2+4:.1f}" text-anchor="middle" font-size="9.5" fill="#fff">{k(v)}</text>')
        out.append(f'<text x="{x+bw/2}" y="{base+14}" text-anchor="middle" font-size="10" fill="var(--ink2)">{label}</text>')
    out.append(f'<line x1="50" y1="{base}" x2="{width-10}" y2="{base}" stroke="var(--axis)"/></svg>')
    return ''.join(out)
LEG = ''.join(f'<span style="--c:{c}">{n}</span>' for n,c in [('Taxes','#e34948'),('Retirement','#1baf7a'),('Health and life','#eda100'),('Loan payoff and interest','#6250d6'),('Retained / set aside','#e87ba4'),('Spendable','#2a78d6')])

s1,s2,s3,s4,s5 = [S[x] for x in ['s1','s2','s3','s4','s5']]
# 5-year payoff schedule for scenario 1 at $25K/yr
sched = []; bal = M['old_loan']
for y in range(2026, 2031):
    i = round(bal*0.04); bal -= 25000; sched.append((y, 25000, i, max(0,bal)))

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Five Scenarios, Guided</title>{STYLE}
<style>.step{{display:flex;gap:10px;align-items:center;margin:40px 0 8px}}.step .n{{width:34px;height:34px;border-radius:50%;background:var(--s1);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:16px;flex:none}}.step h2{{margin:0;border:0;padding:0}}
.next{{border-left:4px solid var(--s3);background:var(--wash3);padding:10px 14px;border-radius:6px;margin:14px 0 0}} .next b{{color:var(--good)}}
.fact{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}}</style></head><body><div class="wrap">
<h1>From today's return to a protected, funded household: five scenarios, step by step</h1>
<div class="sub">B LLC and its owner. Each scenario builds on the one before. Revenue $600,000 in 2026 and $750,000 in 2027 (25% growth). Figures come from one engine built on the 2025 federal and California returns.</div>

<h2>How to read this page</h2>
<div class="grid g2"><div class="card"><h3>What stays constant</h3><ul>
<li><b>The business.</b> Cost of goods and the variable lines (subcontractors, permits, commissions, supplies, equipment rental, payroll processing) grow with sales at 13.9% of revenue; every other 2025 expense is held flat. That leaves a profit pool before any owner or spouse pay of <b>{m(POOL['2026'])}</b> in 2026 and <b>{m(POOL['2027'])}</b> in 2027.</li>
<li><b>Other household income</b> of $51,695 (V C LLC wages and K-1, the V, LLC items, interest, dividends, capital loss) is held at 2025 levels. The rental loss stays suspended.</li>
<li><b>Credits.</b> The energy credit ($10,543) and general business credit ($22,385) are used in 2026 and gone in 2027.</li>
<li><b>Rates.</b> 2026 federal brackets (single or joint as the scenario says), California 2025 brackets, SALT cap $40,400, CA S-corp 1.5% with an $800 minimum, 4% applicable federal rate on any note. 2027 uses the same tables.</li></ul></div>
<div class="card"><h3>What each step adds</h3><ol>
<li><b>Freeze the loan.</b> Same structure as 2025, married filing jointly (married in 2026), spouse not working for B LLC, loan documented and repaid over time.</li>
<li><b>Married, spouse on payroll.</b> Joint filing, $12,000 W-2 for the spouse, revenue $600K, otherwise as today.</li>
<li><b>Retirement, health, expansion, loan payoff.</b> Owner $140,000 salary, solo 401(k), Roth IRAs, family health plan, $100K a year set aside in B LLC, the loan paid off in 2026 and 2027.</li>
<li><b>Life insurance.</b> Cash-value policies: $24,000 a year for the owner, $12,000 for the spouse, paid personally.</li>
<li><b>Sibling C corp.</b> A C corporation owned by the owner takes the maximum management fee, runs payroll, retirement and health, retains earnings for acquisitions, and lends the premiums and the loan payoff under split-dollar notes.</li></ol>
<p class="small">"Spendable" is the household's cash after taxes, retirement contributions, premiums, loan payments, interest and anything set aside or retained. It is the number to watch alongside "retirement funded" and "life insurance in force."</p></div></div>

<div class="step"><div class="n">1</div><h2>Freeze the loan from B LLC</h2></div>
<div class="callout o"><b>What changes:</b> nothing in the business yet. The $125,100 loan to the shareholder is frozen: no new draws, a signed note at the 4% federal rate, and $25,000 a year of principal repaid. Everything else is as filed for 2025, scaled to $600K and $750K of revenue. The owner married in 2026, so the return is filed jointly, but the spouse does not work for B LLC yet and the owner stays on a $13,700 salary.</div>
<div class="grid g2"><div class="card"><h3>Why freeze it</h3><ul>
<li><b>It is the largest asset on the balance sheet</b> (67% of total assets) and the company has $7,505 of equity. Without the receivable B LLC is about $125K underwater.</li>
<li><b>None of the loan tests are met:</b> no note, no interest, no repayment schedule, no payments, no collateral. Each year it grows the case for calling it a loan weakens.</li>
<li><b>Recharacterization costs real money:</b> as a distribution, capital gain on $117,595 (about $28K to $35K plus a 20% penalty); as wages, about $19K of payroll tax plus income tax.</li>
<li><b>It was funded with borrowed money.</b> The company took $60.6K from Fundbox and Headway in 2025 while lending the owner $36.9K; up to $12K of the $30.9K interest deduction is exposed under tracing rules.</li>
<li><b>Lenders see it.</b> A receivable from the owner equal to two-thirds of assets is a renewal problem at the moment revenue is supposed to double.</li></ul></div>
<div class="card"><h3>Recommended payoff: $25,000 a year plus interest</h3>
<table><thead><tr><th>Year</th><th>Principal</th><th>Interest at 4%</th><th>Balance at year end</th></tr></thead><tbody>{''.join(f"<tr><td>{y}</td><td>{m(p)}</td><td>{m(i)}</td><td>{m(b)}</td></tr>" for y,p,i,b in sched)}</tbody></table>
<p class="small">The interest is income to B LLC and flows back through the K-1. Every repayment should go straight to the Fundbox and Headway balances, which cost the company about 20% a year. Scenarios 3 to 5 accelerate this to two years.</p></div></div>
<div class="card" style="margin-top:12px"><h3>Scenario 1 numbers</h3>{two_year_table(rows_s('s1'), 's1')}
<ul style="margin-top:8pt"><li>Joint filing keeps 2026 federal tax at {m(s1[0]['p']['fed'])} after the credits; with no credits left, 2027 federal tax reaches {m(s1[1]['p']['fed'])} at the {pct(s1[1]['p']['marginal'])} bracket. This is the cost of doing nothing beyond the loan.</li>
<li>In 2026 joint income is under the $403,500 threshold, so the full 20% QBI deduction applies ({m(s1[0]['p']['qbi'])}). In 2027 the K-1 pushes taxable income over the threshold and the deduction is capped by B LLC's $13,700 of wages: {m(s1[1]['p']['qbi'])} instead of 20% of {m(s1[1]['k1'])}.</li></ul>
<div class="next"><b>Next:</b> the spouse joins the payroll at $12,000 for documented part-time work.</div></div>

<div class="step"><div class="n">2</div><h2>Married, spouse on payroll, revenue $600K, otherwise as today</h2></div>
<div class="callout o"><b>What changes:</b> the spouse is paid $12,000 in W-2 wages by B LLC for documented part-time work; the owner keeps the $13,700 salary; the loan is frozen as in step 1. Still no retirement plan, no health insurance, no life insurance.</div>
<div class="card"><h3>Scenario 2 numbers</h3>{two_year_table(rows_s('s2'), 's2')}
<ul style="margin-top:8pt"><li>Putting the spouse on payroll at $12,000 changes total taxes by {m(s2[0]['taxes']-s1[0]['taxes'])} in 2026 and {m(s2[1]['taxes']-s1[1]['taxes'])} in 2027: her wages are deductible to B LLC and taxed on the joint return, so the income tax is a wash and the net cost is payroll tax. What it buys is Social Security credits for her and a documented role that supports the retirement contributions in step 3.</li>
<li>The QBI deduction is {m(s2[0]['p']['qbi'])} in 2026 (full 20%) and {m(s2[1]['p']['qbi'])} in 2027, when the wage cap applies; the spouse's wages raise the cap slightly.</li>
<li>Spendable is high ({m(s2[0]['spend'])} in 2026) only because nothing is being protected or saved. The four risks are all still open.</li></ul>
<div class="next"><b>Next:</b> put the owner on a real salary and use the business to fund retirement, health coverage, an expansion reserve, and a fast payoff of the loan.</div></div>

<div class="step"><div class="n">3</div><h2>Retirement plan, health insurance, expansion reserve, loan paid off in two years</h2></div>
<div class="callout o"><b>What changes:</b> owner salary $140,000, spouse $12,000. A solo 401(k): each defers $24,500 (the spouse's whole $12,000), and B LLC adds 25% of wages, {m(s3[0]['employer'])} in total, for {m(s3[0]['deferrals']+s3[0]['employer'])} a year into the plan. Backdoor Roth IRAs of $7,500 each. B LLC pays the $18,000 family health premium (in the owner's W-2 box 1, deducted above the line, no payroll tax). B LLC sets aside $100,000 a year of after-tax cash for expansion. The loan is repaid $62,550 in 2026 and $62,550 in 2027 through distributions within basis that the owner immediately pays back, which is tax-free because the K-1 income is already taxed.</div>
<div class="card"><h3>Scenario 3 numbers</h3>{two_year_table(rows_s('s3'), 's3')}
<ul style="margin-top:8pt"><li><b>Taxes fall</b> to {m(s3[0]['taxes'])} in 2026 (from {m(s2[0]['taxes'])}) even though wages carry payroll tax: the 401(k) deferrals and employer contribution plus the health premium take {m(s3[0]['deferrals']+s3[0]['employer']+s3[0]['health'])} out of taxable income.</li>
<li><b>Retirement:</b> {m(s3[0]['retirement'])} a year, of which {m(s3[0]['deferrals']+s3[0]['employer'])} is pre-tax.</li>
<li><b>Spendable drops to {m(s3[0]['spend'])} in 2026.</b> That is the result of front-loading: $100,000 set aside, $62,550 of loan payoff, {m(s3[0]['retirement'])} of retirement and $18,000 of health in one year. 2027 recovers to {m(s3[1]['spend'])}. If {m(s3[0]['spend'])} is too little to live on, the two levers are the set-aside (start it in 2027) or a three-year payoff; either adds the same amount back to spendable.</li>
<li><b>The old loan is gone at the end of 2027.</b> B LLC receives $125,100 of cash over two years and should use it to retire the 21% debt, which raises profit from 2027 on (not included above).</li></ul>
<div class="next"><b>Next:</b> with income, retirement and health covered, protect the household against the loss of either earner.</div></div>

<div class="step"><div class="n">4</div><h2>Add cash-value life insurance for both spouses</h2></div>
<div class="callout o"><b>What changes:</b> permanent (cash-value) policies, $24,000 a year for the owner and $12,000 for the spouse, paid personally with after-tax money. Roughly $1.5M of death benefit on the owner and $1M on the spouse at these ages, subject to an insurer's illustration. Nothing else moves.</div>
<div class="grid g2"><div class="card"><h3>Scenario 4 numbers</h3>{two_year_table(rows_s('s4'), 's4')}</div>
<div class="card"><h3>What the policies do</h3><ul>
<li><b>Protection.</b> If the owner dies, $1.5M income-tax free replaces roughly ten years of spendable income, clears the company's debt (which he has almost certainly guaranteed personally) and any remaining notes. The spouse's policy covers the loss of her contribution and final expenses.</li>
<li><b>Cash value.</b> Premiums build a tax-deferred account that can be borrowed against tax free later, a second retirement reserve outside the 401(k).</li>
<li><b>Cost.</b> $36,000 a year from after-tax income is about $54,000 of pre-tax earnings at the household's 33% combined marginal rate. Spendable falls to {m(s4[0]['spend'])} in 2026 and {m(s4[1]['spend'])} in 2027.</li>
<li><b>Why an S corp cannot help.</b> Premiums a corporation pays for a more-than-2% shareholder are taxable to him, and split-dollar loans from an S corp lose their main advantage because the S corp has no separately taxed retained earnings to lend. That is what step 5 changes.</li>
<li><b>Bridge:</b> a 20-year term policy of $1.5M costs under $1,000 a year and can be bound this month while the permanent policies are designed.</li></ul>
<div class="callout" style="margin-top:8px">2026 spendable of {m(s4[0]['spend'])} is not realistic to live on. In practice the set-aside or the payoff pace gives way in year 1; the point of this step is to see what full protection costs when paid personally.</div></div></div>
<div class="next" style="margin-top:12px"><b>Next:</b> move payroll, benefits and the premium funding into a sibling C corporation that pays its own, lower tax and lends its retained earnings back to the family.</div>

<div class="step"><div class="n">5</div><h2>A sibling C corporation takes the management fee, retains earnings, and funds the policies and the loan payoff</h2></div>
<div class="callout o"><b>What changes:</b> the owner forms a C corporation that he owns alongside B LLC (a C corp cannot own an S corp without ending the S election). Under a services agreement the C corp provides all sales, marketing, HR and management and bills B LLC {m(M['fee']['2026'])} in 2026 and {m(M['fee']['2027'])} in 2027, about 90% of B LLC's profit, leaving B LLC a small K-1. The C corp employs the owner ($140,000) and spouse ($12,000), sponsors the solo 401(k), provides the health plan as a tax-free fringe benefit, and pays 21% federal and 8.84% California tax on what is left. Its retained earnings are lent to the family under documented 4% notes: the $36,000 of policy premiums first (split-dollar, with the policies assigned as collateral), then the money to repay B LLC's loan, and whatever remains is kept for acquisitions and expansion. The $100K set-aside in B LLC is replaced by the C corp's retention.</div>
<div class="card"><h3>Scenario 5 numbers</h3>{two_year_table(rows_s('s5', True), 's5')}
<ul style="margin-top:8pt"><li><b>Personal tax collapses:</b> {m(s5[0]['p']['fed'])} federal and {m(s5[0]['p']['ca'])} California in 2026 on {m(s5[0]['p']['agi'])} of AGI, because most of the profit is now taxed in the corporation at 28% instead of on the 1040 at 24% plus 9.3%. Total taxes are {m(s5[0]['taxes'])} in 2026 and {m(s5[1]['taxes'])} in 2027, close to scenario 3.</li>
<li><b>Spendable is {m(s5[0]['spend'])} in 2026 and {m(s5[1]['spend'])} in 2027,</b> far above scenario 4, because the premiums and the loan payoff are funded with corporate dollars rather than take-home pay. The household pays only the 4% interest on what it borrows.</li>
<li><b>The C corp cannot do everything in year 1.</b> After paying the premiums it has {m(s5[0]['ccorp']['repay'])} left for the loan in 2026; the remaining {m(s5[0]['loan_end'])} is cleared in 2027, when retained earnings reach {m(s5[1]['ccorp']['after'])}. Acquisition money starts in 2027 ({m(s5[1]['ccorp']['acquisitions'])}).</li>
<li><b>What the owner owes at the end of 2027:</b> {m(s5[1]['ccorp']['owes_c'])} to the C corp on documented notes, secured by the policies, with {m(s5[1]['ccorp']['interest_next'])} a year of interest. The undocumented B LLC loan is gone.</li>
<li><b>QBI and double tax.</b> B LLC's small K-1 still gets the 20% deduction; the C corp income gets none. Anything later paid out as a dividend is taxed again (about 29%), so this works only for money that stays inside or goes out as salary, benefits or loans.</li>
<li><b>Conditions:</b> an arm's-length services agreement that reflects real work, notes with interest actually paid, collateral assignments filed with the insurers, and board minutes documenting the acquisition plan to hold off the accumulated earnings tax after the $250K credit is used.</li></ul></div>

<h2>All five side by side</h2>
<div class="grid g2">
<div class="card"><h3>2026</h3><table><thead><tr><th></th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th></tr></thead><tbody>
<tr><td>All taxes</td>{''.join(f"<td>{m(x[0]['taxes'])}</td>" for x in [s1,s2,s3,s4,s5])}</tr>
<tr><td>Retirement funded</td>{''.join(f"<td>{m(x[0]['retirement'])}</td>" for x in [s1,s2,s3,s4,s5])}</tr>
<tr><td>Health insurance</td><td class="neg">none</td><td class="neg">none</td><td class="pos">yes</td><td class="pos">yes</td><td class="pos">yes</td></tr>
<tr><td>Life insurance</td><td class="neg">none</td><td class="neg">none</td><td class="neg">none</td><td class="pos">both</td><td class="pos">both</td></tr>
<tr><td>Loan balance at year end</td>{''.join(f"<td>{m(x[0]['loan_end'])}</td>" for x in [s1,s2,s3,s4,s5])}</tr>
<tr><td>Set aside or retained</td>{''.join(f"<td>{m(x[0]['retained'])}</td>" for x in [s1,s2,s3,s4,s5])}</tr>
<tr class="total"><td>Spendable</td>{''.join(f"<td>{m(x[0]['spend'])}</td>" for x in [s1,s2,s3,s4,s5])}</tr></tbody></table>
<div class="legend" style="margin-top:10px">{LEG}</div>{stacked([('1',s1[0]),('2',s2[0]),('3',s3[0]),('4',s4[0]),('5',s5[0])],0)}</div>
<div class="card"><h3>2027</h3><table><thead><tr><th></th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th></tr></thead><tbody>
<tr><td>All taxes</td>{''.join(f"<td>{m(x[1]['taxes'])}</td>" for x in [s1,s2,s3,s4,s5])}</tr>
<tr><td>Retirement funded</td>{''.join(f"<td>{m(x[1]['retirement'])}</td>" for x in [s1,s2,s3,s4,s5])}</tr>
<tr><td>Health insurance</td><td class="neg">none</td><td class="neg">none</td><td class="pos">yes</td><td class="pos">yes</td><td class="pos">yes</td></tr>
<tr><td>Life insurance</td><td class="neg">none</td><td class="neg">none</td><td class="neg">none</td><td class="pos">both</td><td class="pos">both</td></tr>
<tr><td>Loan balance at year end</td>{''.join(f"<td>{m(x[1]['loan_end'])}</td>" for x in [s1,s2,s3,s4,s5])}</tr>
<tr><td>Set aside or retained</td>{''.join(f"<td>{m(x[1]['retained'])}</td>" for x in [s1,s2,s3,s4,s5])}</tr>
<tr class="total"><td>Spendable</td>{''.join(f"<td>{m(x[1]['spend'])}</td>" for x in [s1,s2,s3,s4,s5])}</tr></tbody></table>
<div class="legend" style="margin-top:10px">{LEG}</div>{stacked([('1',s1[1]),('2',s2[1]),('3',s3[1]),('4',s4[1]),('5',s5[1])],1)}</div></div>

<div class="card" style="margin-top:12px"><h3>What the progression shows</h3><ul>
<li><b>Steps 1 and 2 are housekeeping</b> that removes the audit exposure and brings the spouse into the business. They leave the family unprotected and unsaved.</li>
<li><b>Step 3 is the core.</b> Salary, 401(k), health and the two-year payoff cut taxes below step 2 while funding {m(s3[0]['retirement'])} a year of retirement. Its only problem is cash in year 1, which is a pacing choice.</li>
<li><b>Step 4 shows the true cost of protection paid personally:</b> $36,000 a year of after-tax money, which at the household's marginal rate is $54,000 of earnings.</li>
<li><b>Step 5 pays for protection and the loan payoff with corporate dollars</b> taxed at 28% and keeps spendable near {m(s5[0]['spend'])} to {m(s5[1]['spend'])}, at the price of a second entity, double tax on any future dividend, and {m(s5[1]['ccorp']['owes_c'])} of documented debt to the family's own corporation by the end of 2027.</li>
<li><b>Recommended sequence:</b> execute steps 1 to 3 now (note, payroll, 401(k), health, term life as a bridge), design the permanent policies, and form the C corp for 2027 if the owner wants to retain earnings for acquisitions and fund the policies through it.</li></ul></div>

<h2>Assumptions</h2>
<div class="card small"><ul>
<li>Profit pool: revenue less variable costs at 13.9% of revenue less fixed costs of {m(M['fixed'])}: {m(POOL['2026'])} (2026) and {m(POOL['2027'])} (2027). Interest savings from paying down B LLC's debt are not included.</li>
<li>Spouse: $12,000 W-2 in steps 2 to 5; her entire wage is deferred into the 401(k) in steps 3 to 5 (payroll tax still applies). Owner $140,000 in steps 3 to 5. Other payroll costs $1,000.</li>
<li>Solo 401(k): $24,500 deferral per person plus 25% employer, capped at $72,000 per person. Backdoor Roth IRAs $7,500 each, not deductible.</li>
<li>Health $18,000; life premiums $24,000 and $12,000; death benefits are placeholders pending illustrations. Loan payoff in steps 3 and 4 is funded by distributions within basis; in step 5 by C corp loans to the owner.</li>
<li>C corp: fee {m(M['fee']['2026'])} and {m(M['fee']['2027'])}, overhead $6,000, no dividends, premiums funded before the loan payoff, remainder kept for acquisitions. Owner's interest to each lender at 4% on the opening balance.</li>
<li>Credits of $32,928 applied in 2026; none in 2027. 2027 uses 2026 tax tables. All scenarios are married filing jointly; in scenario 1 the spouse has no wages.</li>
<li>Planning analysis, not tax, legal or insurance advice. The preparer, an attorney and a licensed insurance professional should review before anything is signed.</li></ul></div>
</div></body></html>'''
open('C:/Durendal-Vault/Durendal/GitHub/Pinnacle-AI/WAN/R-L/five-scenarios-guided.html', 'w', encoding='utf-8').write(html)
print('written', len(html))
