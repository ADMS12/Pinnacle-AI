"""Scenario engine, 2026, married filing jointly. Revenue $600K, base-case costs."""
import json, os
POOL = 350201            # B LLC profit before any owner compensation (base case: 336,501 K-1 + 13,700 officer comp)
OTHER = 51695            # all other household income held at 2025: V C LLC wages 36,000 + K-1s, interest, dividends, losses (rental loss excluded)
VC_K1 = 76351; INV_INC = 7230
MORT, CHAR, PROP = 32075, 3039, 11816
SALT_CAP = 40400; STD_MFJ = 32200
ENERGY_CF, GBC_CF = 10543, 22385
SS_BASE = 184500; SEP_MAX = 72000; DEF_401K = 24500
FED = [(24800,.10),(100800,.12),(211400,.22),(403550,.24),(512450,.32),(768700,.35),(10**9,.37)]
CA  = [(21512,.01),(50998,.02),(80490,.04),(111732,.06),(141212,.08),(721318,.093),(865574,.103),(1442628,.113),(10**9,.123)]
CA_ADJ = -25557; CA_EXEMPT = 306; QBI_THRESH = 403500
AFR = 0.04

def br(ti, b):
    t=0; lo=0
    for hi,r in b:
        if ti>lo: t+=(min(ti,hi)-lo)*r
        lo=hi
    return t
def marg(ti,b):
    for hi,r in b:
        if ti<=hi: return r
    return b[-1][1]
def fica_emp(w):  # employee share
    return min(w,SS_BASE)*0.062 + w*0.0145
def fica_er(w):
    return min(w,SS_BASE)*0.062 + w*0.0145

def personal(wages_owner, wages_wife, k1_b, health_in_w2, se_health_ded, extra_agi=0, qbi_extra=0, label=''):
    wages = wages_owner + wages_wife
    agi = wages + health_in_w2 + OTHER + k1_b + extra_agi - se_health_ded
    ca_ti_pre = agi + CA_ADJ - (MORT+CHAR+PROP)
    ca = max(0, br(max(0,ca_ti_pre), CA) - CA_EXEMPT)
    salt = min(SALT_CAP, PROP + ca)
    itemized = max(STD_MFJ, salt + MORT + CHAR)
    ti_pre = agi - itemized
    qbi = 0.20*max(0,k1_b) + 0.20*VC_K1 + qbi_extra
    qbi = min(qbi, 0.20*max(0,ti_pre))
    ti = max(0, ti_pre - qbi)
    fed = br(ti, FED)
    energy = min(ENERGY_CF, fed); f2 = fed - energy
    gbc = min(GBC_CF, max(0, f2 - 0.25*max(0, f2-25000))); f2 -= gbc
    all_wages = wages + 36000
    add_med = 0.009*max(0, all_wages-250000)
    niit = 0.038*min(INV_INC, max(0, agi-250000))
    fed_total = f2 + add_med + niit
    emp_fica = fica_emp(wages_owner) + fica_emp(wages_wife) + fica_emp(36000)   # V C LLC wages too
    return dict(label=label, agi=round(agi), itemized=round(itemized), salt=round(salt), qbi=round(qbi), ti=round(ti),
                fed_gross=round(fed), energy=round(energy), gbc=round(gbc), fed=round(fed_total), add_med=round(add_med), niit=round(niit),
                marginal=marg(ti,FED), ca=round(ca), ca_ti=round(max(0,ca_ti_pre)), emp_fica=round(emp_fica))

def s_corp(wages_owner, wages_wife, sep_rate, health, extra_fee=0, other_payroll=1000):
    er = fica_er(wages_owner) + fica_er(wages_wife) + (other_payroll if (wages_owner+wages_wife)>0 else 0)
    sep = sep_rate*(wages_owner+wages_wife)
    sep = min(sep, SEP_MAX*2)
    k1 = POOL - wages_owner - wages_wife - er - sep - health - extra_fee
    ca_corp = max(800, round(0.015*max(0, k1-23732)))
    return dict(wages_owner=wages_owner, wages_wife=wages_wife, er_payroll=round(er), sep=round(sep), sep_owner=round(sep_rate*wages_owner), sep_wife=round(sep_rate*wages_wife), health=health, fee=extra_fee, k1=round(k1), ca_corp=ca_corp)


PREMIUM = 24000; DEATH_BENEFIT = 1500000; OLD_LOAN = 125100; LOAN_REPAY_S1 = 25000
out = {}
# ---- Baseline, married, no changes ----
b = s_corp(13700, 0, 0, 0, other_payroll=0)
p = personal(13700, 0, b['k1'], 0, 0, label='Baseline, married, no changes')
out['baseline'] = dict(corp=b, p=p, name='Married baseline, no changes')

# ---- Scenario 1: S corp wages, spouse $12K, SEP 25%, health via S corp, personal life policy, note repayment ----
def scen1(wo, name):
    c = s_corp(wo, 12000, 0.25, 18000)
    p = personal(wo, 12000, c['k1'], 18000, 18000, label=name)
    return dict(corp=c, p=p, name=name, premium=PREMIUM, loan_repay=LOAN_REPAY_S1, loan_interest=round(OLD_LOAN*AFR))
out['s1'] = [scen1(180000,'Owner $180K'), scen1(140000,'Owner $140K'), scen1(100000,'Owner $100K')]

# ---- Scenario 2: sibling C corp, owner $120K + spouse $12K, SEP 25%, health fringe ----
FEE=300000; CW=120000; SW=12000; C_HEALTH=18000; C_ADMIN=6000
c_er = fica_er(CW)+fica_er(SW)+1000
c_sep = 0.25*(CW+SW)
c_pre = FEE-CW-SW-c_er-c_sep-C_HEALTH-C_ADMIN
c_ca = max(800, 0.0884*c_pre); c_fed = 0.21*(c_pre-c_ca); c_after = c_pre-c_ca-c_fed
b2 = s_corp(0,0,0,0, extra_fee=FEE, other_payroll=0)
p2 = personal(CW, SW, b2['k1'], 0, 0, label='Scenario 2')
# year-1 allocation of retained earnings: premium loan first, remainder lent to owner to repay B LLC
prem_loan = PREMIUM; repay_loan = c_after - prem_loan
yrs=[]; bal=OLD_LOAN; owes_c=0
for y in range(1,6):
    repay = min(bal, repay_loan if bal>0 else 0)
    bal -= repay
    expansion = c_after - prem_loan - repay
    owes_c += prem_loan + repay
    yrs.append(dict(year=2025+y, retained=round(c_after), premium=prem_loan, repay=round(repay), b_balance=round(bal), expansion=round(expansion), owes_c=round(owes_c), interest=round(owes_c*AFR)))
out['s2'] = dict(fee=FEE, c_wages=CW, c_wages_wife=SW, c_er=round(c_er), c_sep=round(c_sep), c_health=C_HEALTH, c_admin=C_ADMIN, c_pre=round(c_pre), c_ca=round(c_ca), c_fed=round(c_fed), c_after=round(c_after),
    corp=b2, p=p2, name='Scenario 2: sibling C corp', premium=PREMIUM, prem_loan=prem_loan, repay_loan=round(repay_loan), years=yrs, death_benefit=DEATH_BENEFIT,
    interest_saved=round(0.21*OLD_LOAN))   # B LLC retires ~21%-cost debt with the repaid cash

def econ(entry, retained=0, corp_tax=0, savings=None, health=None, premium=0, loan_repay=0, loan_interest=0, er=None):
    c,p = entry['corp'], entry['p']
    er = c['er_payroll'] if er is None else er
    taxes = p['fed']+p['ca']+c['ca_corp']+p['emp_fica']+er+corp_tax
    savings = c['sep'] if savings is None else savings
    health = c['health'] if health is None else health
    spend = POOL+OTHER-taxes-savings-health-retained-premium-loan_repay-loan_interest
    return dict(taxes=round(taxes), savings=round(savings), health=health, retained=round(retained), premium=premium, loan_repay=loan_repay, loan_interest=loan_interest, spend=round(spend), pool=POOL+OTHER)
out['baseline']['econ'] = econ(out['baseline'])
for s_ in out['s1']: s_['econ'] = econ(s_, premium=PREMIUM, loan_repay=LOAN_REPAY_S1, loan_interest=s_['loan_interest'])
y1 = yrs[0]
out['s2']['econ'] = econ(out['s2'], retained=c_after, corp_tax=c_fed+c_ca, savings=c_sep, health=C_HEALTH, er=c_er, loan_interest=y1['interest'])
# in scenario 2 the premium and the old-loan repayment are funded by the C corp loan (inside 'retained'), so they do not reduce spendable again
json.dump(out, open(os.path.join(os.path.dirname(__file__),'calc3.json'),'w'), indent=1)
for k in ['baseline','s2']:
    e=out[k]; print(k,'K-1',e['corp']['k1'],'AGI',e['p']['agi'],'TI',e['p']['ti'],'fed',e['p']['fed'],'ca',e['p']['ca'],'fica',e['p']['emp_fica'],'econ',e['econ'])
for s_ in out['s1']: print(s_['name'],'K-1',s_['corp']['k1'],'SEP',s_['corp']['sep'],s_['corp']['sep_owner'],s_['corp']['sep_wife'],'AGI',s_['p']['agi'],'fed',s_['p']['fed'],'ca',s_['p']['ca'],'fica',s_['p']['emp_fica'],'er',s_['corp']['er_payroll'],'econ',s_['econ'])
print('C corp', {k:v for k,v in out['s2'].items() if k.startswith('c_')}, 'years', yrs)
