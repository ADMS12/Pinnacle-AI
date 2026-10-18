import json, os
H = os.path.dirname(__file__)
D = json.load(open(os.path.join(H, 'calc5.json')))
def m(v): return ('−' if v < 0 else '') + '$' + f"{abs(round(v)):,}"
def k(v): return ('−' if v < 0 else '') + '$' + (f"{abs(v)/1000:.0f}K" if abs(v) >= 100000 else f"{abs(v)/1000:.1f}K")
def g(r):
    d = r['spend'] - r['living']; return f'<span class="{"pos" if d >= 0 else "neg"}">{("+" if d >= 0 else "−")}${abs(round(d)):,}</span>'
S = {x: D[x] for x in ['s1','s2','s3','s4','s5']}
s1, s2, s3, s4, s5 = [S[x] for x in ['s1','s2','s3','s4','s5']]
R = 'C:/Durendal-Vault/Durendal/GitHub/Pinnacle-AI/WAN/R-L/'
h = open(R + '2026-Plan-Blueprint.html', encoding='utf-8').read()
head = h[:h.index('<body>')]
cols = [s1, s2, s3, s4, s5]
row_tax = ''.join(f"<td>{k(x[0]['taxes'])} / {k(x[1]['taxes'])}</td>" for x in cols)
row_ret = ''.join(f"<td>{(k(x[0]['retirement']) if x[0]['retirement'] else '$0')} / {(k(x[1]['retirement']) if x[1]['retirement'] else '$0')}</td>" for x in cols)
row_loan = ''.join(f"<td class=\"{'pos' if x[1]['loan_end'] == 0 else ''}\">{m(x[1]['loan_end'])}</td>" for x in cols)
row_spend = ''.join(f"<td>{k(x[0]['spend'])} / {k(x[1]['spend'])}</td>" for x in cols)
row_gap = ''.join(f"<td>{g(x[0])} / {g(x[1])}</td>" for x in cols)
body = f'''<body><div class="wrap">
<div class="tags"><span class="tag">Strategic Advisory Blueprint</span><span class="tag">Entity Diagnostics</span><span class="tag">Plan Summary · v2</span></div>
<h1>R.L. and B LLC Case: Financial Architecture</h1>
<p class="lede">Protecting the family, funding retirement and fixing the shareholder loan as B LLC grows from $289,584 of revenue in 2025 to $600,000 in 2026 and $750,000 in 2027. Built from the 2025 federal and California returns under 2026 rules, married filing jointly. v2 adds the spouse&#39;s $125,000 outside job from 2027, her vehicle as a business expense, a 20% employer 401(k) contribution, the existing $165K policy and the household&#39;s living costs.</p>

<div class="grid g21">
  <div class="card soft">
    <div class="hd"><h2><span class="ico">⚠</span>Core Blocker: The $125,100 Shareholder Loan</h2><span class="pill">Fix before anything else</span></div>
    <p>Over several years the owner took $125,100 out of B LLC as a "loan": no written note, no interest, no repayments, no collateral. It is the largest asset on the books, and without it the company is about $125K underwater. If the IRS calls it a distribution or hidden wages, the bill is roughly $28,000 to $35,000 plus penalties. Lenders and the IRS read this line first, so every scenario starts by freezing and documenting it.</p>
    <div class="mini">
      <div class="box"><div class="k">1. B LLC (S corp), 2025</div><div class="t">Grew fast, kept little</div><div class="d">Revenue $289,584, up 64%. Profit to the owner $69,133, down 28% and only 24% of revenue (77% in 2023). Travel, meals and vehicles $90K. Debt $171,549 at about 21% interest.</div></div>
      <div class="box"><div class="k">2. The household</div><div class="t">Thin margins at home</div><div class="d">2025 income $126,792, federal tax $46, California $1,699. Married in 2026. Living costs about $17,000 a month ($204K a year); $16,000 while the spouse&#39;s vehicle is carried by B LLC. Spouse starts a $125,000 job in 2027 and keeps her $12,000 B LLC role.</div></div>
      <div class="box"><div class="k">3. The family&#39;s gaps</div><div class="t">Four open risks</div><div class="d">Undocumented loan · no health insurance · minimal life protection (one $165K policy with $15K cash value against $171K of guaranteed debt) · no retirement savings at age 31.</div></div>
    </div>
    <div class="ctx"><span>⊘</span><span>Constant across scenarios: variable costs grow with sales, other costs held at 2025 levels; profit before owner and spouse pay $350,201 (2026) and $479,399 (2027); other household income $51,695; credits of $32,928 used once in 2026.</span></div>
  </div>
  <div class="card soft2">
    <div class="hd"><h2><span class="ico">⚖</span>The 2026 Baseline</h2></div>
    <p>What $600K of revenue looks like if nothing changes but the loan freeze (scenario 1).</p>
    <div class="stat"><div class="k">Profit to the owner (K-1)</div><div class="v">{m(s1[0]['k1'])} <small>from $69,133 in 2025</small></div></div>
    <div class="stat"><div class="k">All taxes 2026 / 2027</div><div class="v">{k(s1[0]['taxes'])} / {k(s1[1]['taxes'])} <small>2027 has no credits left; spouse&#39;s salary taxed on top</small></div></div>
    <div class="stat"><div class="k">Spendable 2026 / 2027</div><div class="v">{k(s1[0]['spend'])} / {k(s1[1]['spend'])} <small>nothing protected or saved</small></div></div>
    <div class="note"><b>Why the baseline is not a plan</b>Spendable clears the $204K living bar by {m(s1[0]['spend']-204000)} in 2026 only because no gap is funded. With a $13,700 salary and $340K of profit, reasonable compensation is the next thing an examiner raises, and 2027 federal tax reaches {m(s1[1]['p']['fed'])} once the credits are gone.</div>
  </div>
</div>

<div class="grid g12" style="margin-top:14px">
  <div class="card soft">
    <div class="hd"><div><h2><span class="ico">▭</span>Debt Prioritization</h2><div class="sub">Loan payoff first, then the 21% company debt</div></div></div>
    <div class="big"><div class="v">$125,100</div><div class="k">Shareholder loan to document and repay</div></div>
    <ul class="dots">
      <li><b>Steps 1 and 2:</b> freeze all withdrawals, sign a 4% note, repay $25,000 a year from after-tax cash. Balance $75,100 at the end of 2027.</li>
      <li><b>Steps 3 and 4:</b> repay $62,550 in 2026 and $62,550 in 2027 through distributions the owner immediately pays back; tax-free because the income is already taxed. Loan cleared end of 2027.</li>
      <li><b>Step 5:</b> the C corp lends the owner the payoff at 4%: {m(s5[0]['ccorp']['repay'])} in 2026 after the premiums, the remaining {m(s5[1]['ccorp']['repay'])} in 2027.</li>
      <li><b>Every repayment goes to the company&#39;s most expensive debt:</b> Fundbox $53.6K, Headway $7K, cards $17K, vehicle loans $94K.</li>
    </ul>
    <div class="note"><b>Sequencing imperative</b>Steps 3 and 4 front-load the payoff, $100K of expansion set-aside, retirement and health into 2026, leaving {m(s3[0]['spend'])} (step 3) or {m(s4[0]['spend'])} (step 4) against $192K of living costs. 2027 covers costs in every protected scenario once the spouse&#39;s salary arrives and the health premium drops. For 2026, start the set-aside in 2027 or spread the payoff over three years.</div>
  </div>
  <div class="card">
    <div class="hd"><div><h2><span class="ico">⚙</span>Planning Alternatives</h2><div class="sub">Steps 3, 4 and 5 of the plan; steps 1 and 2 are housekeeping</div></div><span class="pill b">3 evaluative models</span></div>
    <div class="grid g3">
      <div class="alt"><div class="h"><span class="hz">Step 3 · 2026 start</span><span>◎</span></div><h3>Put the business to work for the family</h3><p>Owner $140K and spouse $12K on payroll; her vehicle ($12,984 a year) becomes a B LLC expense. 401(k): owner defers $24,500, spouse $12,000, B LLC contributes 20% of pay. Health plan paid by B LLC in 2026, by her employer from 2027. $100K a year set aside. Loan cleared in two years.</p><div class="kv"><b>{m(s3[0]['retirement'])} / yr into retirement</b><span>All taxes {k(s3[0]['taxes'])} (2026), {k(s3[1]['taxes'])} (2027) · spendable {k(s3[0]['spend'])} then {k(s3[1]['spend'])} · vs living cost {g(s3[0])} / {g(s3[1])}</span></div></div>
      <div class="alt"><div class="h"><span class="hz">Step 4 · protection</span><span>◈</span></div><h3>Insure the people who make it work</h3><p>The existing $165K policy stays. Cash-value policies added: $24K a year on the owner (about $1.5M), $12K on the spouse (about $1M), paid personally. A $1.5M term policy under $1K a year bridges the gap now.</p><div class="kv"><b>$36K after tax ≈ $54K of earnings</b><span>Same taxes as step 3 · spendable {k(s4[0]['spend'])} (2026), {k(s4[1]['spend'])} (2027) · vs living cost {g(s4[0])} / {g(s4[1])}</span></div></div>
      <div class="alt"><div class="h"><span class="hz">Step 5 · 2027 decision</span><span>▤</span></div><h3>Let a second company carry the load</h3><p>A sibling C corp bills B LLC $320K then $440K, runs payroll, the 401(k) and health, pays about 28% tax, and lends what it keeps to the family on 4% notes: premiums first, then the loan payoff, then acquisitions.</p><div class="kv"><b>Collateral structure</b><span>Policies pledged to the C corp · all taxes {k(s5[0]['taxes'])} (2026), {k(s5[1]['taxes'])} (2027) · spendable {k(s5[0]['spend'])} then {k(s5[1]['spend'])} · vs living cost {g(s5[0])} / {g(s5[1])} · owner owes C corp {k(s5[1]['ccorp']['owes_c'])} by end-2027</span></div></div>
    </div>
    <table><thead><tr><th>2026 / 2027</th><th>Step 1</th><th>Step 2</th><th>Step 3</th><th>Step 4</th><th>Step 5</th></tr></thead><tbody>
      <tr><td>All taxes</td>{row_tax}</tr>
      <tr><td>Retirement funded</td>{row_ret}</tr>
      <tr><td>Protection</td><td class="neg">$165K only</td><td class="neg">$165K only</td><td class="amb">health</td><td class="pos">health + life</td><td class="pos">health + life</td></tr>
      <tr><td>Loan at end of 2027</td>{row_loan}</tr>
      <tr><td>Spendable</td>{row_spend}</tr>
      <tr><td>vs living cost ($17K/mo; $16K while spouse on payroll)</td>{row_gap}</tr>
    </tbody></table>
    <div class="caution"><span>Caution: a C corp cannot own an S corp without ending the S election; the holding entity must be a sibling. The fee needs a real services agreement, interest actually paid each year, collateral assignments filed, and board minutes for the acquisition plan. Anything later paid out as a dividend is taxed twice. The spouse&#39;s vehicle deduction holds only to the extent of documented business use.</span><span>Posture: Diagnostic inquiry</span></div>
  </div>
</div>

<div class="card soft" style="margin-top:14px">
  <div class="hd"><div><h2><span class="ico">☑</span>Immediate Execution Matrix</h2><div class="sub">From the decisions and action items on the closing slide</div></div><span class="pill b">Recommended path: steps 1 to 3 now, term bridge, C corp for 2027</span></div>
  <div class="grid g2">
    <div class="card"><div class="person"><span class="who"><span class="av">O</span>Owner and spouse</span><span class="tag">Decisions and 30-day actions</span></div>
      <div class="task"><span class="g">▤</span><div>Decide today: payoff pace (two years vs five), owner salary ($140,000 as modeled), when the $100K expansion set-aside starts (at $16K a month of living costs, 2026 only works if the set-aside or the payoff pace gives way), permanent policies now or term now, and whether to form the C corporation for 2027.<div class="due">Due: this meeting</div></div></div>
      <div class="task"><span class="g">⚇</span><div>Sign a 4% note on the $125,100 loan and make the first payment. Put the owner and spouse on payroll with withholding set to cover the projected tax; document her role and the business use of her vehicle. Enroll the family health plan through B LLC.<div class="due">Due: within 30 days</div></div></div>
      <div class="task"><span class="g">◈</span><div>Keep the $165K policy in force and review its cost against the $15K cash value; bind a $1.5M term policy on the owner; request permanent-policy illustrations for both. Open the 401(k) with the 20% employer contribution and the Roth IRAs. Send every loan repayment to the Fundbox and Headway balances.<div class="due">Due: within 30 days</div></div></div>
    </div>
    <div class="card"><div class="person"><span class="who"><span class="av">A</span>Advisors and preparer</span><span class="tag">Next 90 days</span></div>
      <div class="task"><span class="g">▤</span><div>Preparer to confirm the $32,928 of credit carryforwards and rerun 2026 estimates; set up California estimates on the prior-year safe harbor and a reserve for the April 2027 federal bill.<div class="due">Due: within 90 days</div></div></div>
      <div class="task"><span class="g">⚇</span><div>Attorney to draft the services agreement and split-dollar notes if the C corp proceeds; document the acquisition plan that justifies retained earnings.<div class="due">Due: within 90 days</div></div></div>
      <div class="task"><span class="g">◈</span><div>Confirm the spouse&#39;s job start date and her employer&#39;s family health coverage and cost; review travel, meals and vehicle spending ($90K in 2025); revisit the California pass-through entity election (about $9K to $12K of federal tax); confirm life insurance amounts with an insurer&#39;s illustration.<div class="due">Due: within 90 days</div></div></div>
    </div>
  </div>
</div>

<p class="small" style="margin-top:14px">Summarizes 2026-Plan-12-Slides v2.html (13 slides). Supporting detail: five-scenarios-guided.html, loan-scenarios.html and the scenario pages. Planning analysis built from the 2025 returns under 2026 rules; not tax, legal or insurance advice. The preparer, an attorney and a licensed insurance professional should review before anything is signed.</p>
</div></body></html>'''
open(R + '2026-Plan-Blueprint.html', 'w', encoding='utf-8').write(head + body)
open(os.path.join(H, 'blueprint_v2.html'), 'w', encoding='utf-8').write(head + body)
print('blueprint rebuilt')
