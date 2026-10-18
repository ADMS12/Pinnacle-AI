"""Five progressive scenarios, 2026 and 2027. Base-case cost structure from the 2025 return."""
import json, os
REV = {2026: 600000, 2027: 750000}
VAR_RATE = 40159/289584            # COGS + variable lines as share of revenue (2025)
FIXED_EX_OFFICER = 180292 - 13700  # fixed deductions excluding officer pay
POOL = {y: round(REV[y] - VAR_RATE*REV[y] - FIXED_EX_OFFICER) for y in REV}   # profit before any owner/spouse pay
OTHER = 51695; VC_K1 = 76351; INV_INC = 7230
MORT, CHAR, PROP = 32075, 3039, 11816
SALT_CAP = 40400
SS_BASE = 184500; DEF_401K = 24500; LIMIT_415 = 72000
CA_ADJ = -25557; AFR = 0.04; OLD_LOAN = 125100
B_W2_BASE = 13700; B_UBIA = 129541
AUTO = 12984   # spouse's vehicle cost, $1,082/mo, carried by her employer while she is on its payroll
FED = {'single': [(12400,.10),(50400,.12),(105700,.22),(201775,.24),(256225,.32),(640600,.35),(10**9,.37)],
       'mfj':    [(24800,.10),(100800,.12),(211400,.22),(403550,.24),(512450,.32),(768700,.35),(10**9,.37)]}
CA  = {'single': [(10756,.01),(25499,.02),(40245,.04),(55866,.06),(70606,.08),(360659,.093),(432787,.103),(721314,.113),(10**9,.123)],
       'mfj':    [(21512,.01),(50998,.02),(80490,.04),(111732,.06),(141212,.08),(721318,.093),(865574,.103),(1442628,.113),(10**9,.123)]}
STD = {'single':16100,'mfj':32200}; QBI_TH = {'single':201750,'mfj':403500}; MED_TH = {'single':200000,'mfj':250000}; CA_EX = {'single':153,'mfj':306}
CREDITS = {2026: 10543+22385, 2027: 0}   # energy + general business credits, consumed in 2026

def br(ti,b):
    t=0;lo=0
    for hi,r in b:
        if ti>lo: t+=(min(ti,hi)-lo)*r
        lo=hi
    return t
def marg(ti,b):
    for hi,r in b:
        if ti<=hi: return r
    return b[-1][1]
def fica(w): return min(w,SS_BASE)*0.062 + w*0.0145

def personal(year, fs, w_owner, w_wife, k1_b, b_w2_for_qbi, deferrals=0, health_box1=0, se_health=0, extra_agi=0):
    wages = w_owner + w_wife - deferrals
    agi = wages + health_box1 + OTHER + k1_b - se_health + extra_agi
    ca_ti = max(0, agi + CA_ADJ - (MORT+CHAR+PROP))
    ca = max(0, br(ca_ti, CA[fs]) - CA_EX[fs])
    salt = min(SALT_CAP, PROP + ca)
    itemized = max(STD[fs], salt + MORT + CHAR)
    ti_pre = max(0, agi - itemized)
    if ti_pre > QBI_TH[fs]:
        cap = max(0.5*b_w2_for_qbi, 0.25*b_w2_for_qbi + 0.025*B_UBIA)
        qbi = min(0.2*max(0,k1_b), cap) + 0.2*VC_K1
    else:
        qbi = 0.2*max(0,k1_b) + 0.2*VC_K1
    qbi = min(qbi, 0.2*ti_pre)
    ti = max(0, ti_pre - qbi)
    fed = br(ti, FED[fs])
    cred = min(CREDITS[year], fed)      # simplification: both credits usable against the 2026 bill
    fed_after = fed - cred
    all_wages = w_owner + w_wife + 36000
    add_med = 0.009*max(0, all_wages - MED_TH[fs])
    niit = 0.038*min(INV_INC, max(0, agi - MED_TH[fs]))
    emp_fica = fica(w_owner) + fica(w_wife) + fica(36000)
    return dict(agi=round(agi), itemized=round(itemized), salt=round(salt), qbi=round(qbi), ti=round(ti), fed_gross=round(fed), credits=round(cred),
                fed=round(fed_after+add_med+niit), marginal=marg(ti,FED[fs]), ca=round(ca), emp_fica=round(emp_fica))

def run(year, fs, w_owner, w_wife, plan, health_s, life_personal, setaside, loan_repay, loan_bal_start, ccorp=None, name='', c_bal_start=0):
    pool = POOL[year]
    # --- retirement plan amounts ---
    if plan == '401k':
        d_o = min(DEF_401K, w_owner); d_w = min(DEF_401K, w_wife)
        er_o = min(0.25*w_owner, LIMIT_415 - d_o); er_w = min(0.25*w_wife, LIMIT_415 - d_w)
        deferrals = d_o + d_w; employer = er_o + er_w
    else:
        deferrals = employer = 0
    roth = 15000 if plan == '401k' else 0
    other_payroll = 1000 if (w_owner + w_wife) > 20000 else 0
    er_payroll = fica(w_owner) + fica(w_wife) + other_payroll
    int_b = AFR * loan_bal_start; int_c = AFR * c_bal_start; loan_interest = int_b + int_c   # owner pays 4% to each lender
    if ccorp is None:
        auto = AUTO if w_wife > 0 else 0
        k1 = pool - w_owner - w_wife - er_payroll - employer - health_s - auto + int_b   # interest income to B LLC
        ca_corp = max(800, round(0.015*max(0, k1 - 23732)))
        p = personal(year, fs, w_owner, w_wife, k1, b_w2_for_qbi=w_owner+w_wife, deferrals=deferrals, health_box1=health_s, se_health=health_s)
        corp_tax = 0; c = None
    else:
        fee = ccorp['fee']; admin = ccorp['admin']
        auto = AUTO if w_wife > 0 else 0
        c_pre = fee - w_owner - w_wife - er_payroll - employer - health_s - admin - auto + int_c
        c_ca = max(800, 0.0884*c_pre); c_fed = 0.21*(c_pre - c_ca); c_after = c_pre - c_ca - c_fed
        k1 = pool - fee + int_b
        ca_corp = max(800, round(0.015*max(0, k1 - 23732)))
        p = personal(year, fs, w_owner, w_wife, k1, b_w2_for_qbi=0, deferrals=deferrals)   # C corp health is a tax-free fringe
        corp_tax = c_ca + c_fed
        prem = ccorp['premiums']; repay = min(loan_repay, max(0, c_after - prem))   # fund premiums first, then the payoff
        c = dict(fee=fee, admin=admin, pre=round(c_pre), ca=round(c_ca), fed=round(c_fed), after=round(c_after), premiums=prem, repay=round(repay),
                 acquisitions=round(c_after - prem - repay), int_b=round(int_b), int_c=round(int_c))
        loan_repay = repay
        er_payroll_total = er_payroll
    retirement = deferrals + employer + roth
    taxes = p['fed'] + p['ca'] + ca_corp + p['emp_fica'] + er_payroll + corp_tax
    if ccorp is None:
        spend = pool + OTHER - taxes - retirement - health_s - life_personal - setaside - loan_repay - loan_interest
        retained = setaside
    else:
        # premiums and the loan repayment are funded by C corp loans to the owner (inside 'retained'); owner pays interest only
        spend = pool + OTHER - taxes - retirement - health_s - c['after'] - loan_interest
        retained = c['after']
    return dict(name=name, year=year, fs=fs, pool=pool, w_owner=w_owner, w_wife=w_wife, w_ext=0, ext_401k=0, auto=auto, living=192000 if w_wife>0 else 204000, er_payroll=round(er_payroll), deferrals=round(deferrals), employer=round(employer), roth=roth,
                health=health_s, life=life_personal, setaside=setaside, loan_repay=loan_repay, loan_interest=round(loan_interest), loan_end=loan_bal_start-loan_repay,
                k1=round(k1), ca_corp=ca_corp, p=p, ccorp=c, corp_tax=round(corp_tax), retirement=round(retirement), taxes=round(taxes), spend=round(spend), retained=round(retained))

out = {}
# S1: freeze the loan; everything else as 2025 (single filer, owner W-2 $13,700). Loan documented at AFR, repaid $25K/yr from 2026.
out['s1'] = [run(2026,'mfj',B_W2_BASE,0,'none',0,0,0,25000,OLD_LOAN,name='1. Freeze the loan'),
             run(2027,'mfj',B_W2_BASE,0,'none',0,0,0,25000,OLD_LOAN-25000,name='1. Freeze the loan')]
# S2: married, wife $12K W-2, $600K, otherwise as today (loan frozen, $25K/yr)
out['s2'] = [run(2026,'mfj',B_W2_BASE,12000,'none',0,0,0,25000,OLD_LOAN,name='2. Married, wife on payroll'),
             run(2027,'mfj',B_W2_BASE,12000,'none',0,0,0,25000,OLD_LOAN-25000,name='2. Married, wife on payroll')]
# S3: owner $140K, solo 401(k), Roth, health, $100K set-aside, loan paid off 2026-2027 via distributions within basis
out['s3'] = [run(2026,'mfj',140000,12000,'401k',18000,0,100000,62550,OLD_LOAN,name='3. Retirement, health, expansion, loan payoff'),
             run(2027,'mfj',140000,12000,'401k',18000,0,100000,62550,OLD_LOAN-62550,name='3. Retirement, health, expansion, loan payoff')]
# S4: S3 + life insurance paid personally ($24K owner + $12K wife)
out['s4'] = [run(2026,'mfj',140000,12000,'401k',18000,36000,100000,62550,OLD_LOAN,name='4. Add cash-value life insurance'),
             run(2027,'mfj',140000,12000,'401k',18000,36000,100000,62550,OLD_LOAN-62550,name='4. Add cash-value life insurance')]
# S5: sibling C corp takes maximum fee; does payroll, 401(k), health; retains earnings; split-dollar premiums; lends owner the loan payoff
FEE = {2026: 320000, 2027: 440000}
b_bal = OLD_LOAN; c_bal = 0; rows = []
for y in (2026, 2027):
    r = run(y,'mfj',140000,12000,'401k',18000,0,0,b_bal,b_bal,ccorp=dict(fee=FEE[y],admin=6000,premiums=36000),name='5. Sibling C corp',c_bal_start=c_bal)
    b_bal -= r['ccorp']['repay']; c_bal += r['ccorp']['premiums'] + r['ccorp']['repay']
    r['loan_end'] = round(b_bal); r['ccorp']['owes_c'] = round(c_bal); r['ccorp']['interest_next'] = round(c_bal*AFR); rows.append(r)
out['s5'] = rows
out['meta'] = dict(pool=POOL, rev=REV, other=OTHER, var_rate=round(VAR_RATE,4), fixed=FIXED_EX_OFFICER, fee=FEE, old_loan=OLD_LOAN)
json.dump(out, open(os.path.join(os.path.dirname(__file__),'calc4.json'),'w'), indent=1)
for key in ['s1','s2','s3','s4','s5']:
    for r in out[key]:
        print(key, r['year'], 'pool', r['pool'], 'K-1', r['k1'], 'AGI', r['p']['agi'], 'TI', r['p']['ti'], 'fed', r['p']['fed'], 'ca', r['p']['ca'], 'fica', r['p']['emp_fica'], 'er', r['er_payroll'],
              'corp', r['corp_tax'], 'taxes', r['taxes'], 'ret', r['retirement'], 'spend', r['spend'], 'retained', r['retained'], 'loan_end', r['loan_end'], 'cc', r['ccorp'])
