import json
# ---------- 2025 facts from the returns ----------
REV25=289584; COGS25=18745
DED25={'Officer compensation':13700,'Taxes and licenses':1391,'Interest':30941,'Depreciation':12544,'Advertising':4067,
 'Auto and truck':31663,'Travel':29642,'Meals (50% allowed)':14590,'Office expense':18107,'Outside services':11395,'Printing':7204,
 'Legal and professional':5715,'Permits and fees':5003,'Utilities':3756,'Uniforms':2967,'Equipment rental':2528,'Software':2380,
 'Bank charges':1210,'Commissions':975,'Supplies':868,'Payroll processing':645,'Telephone':316,'Insurance':99}
assert sum(DED25.values())==201706, sum(DED25.values())
K1_25=REV25-COGS25-sum(DED25.values()); assert K1_25==69133
VARIABLE={'Outside services','Permits and fees','Commissions','Supplies','Equipment rental','Payroll processing'}
var25=COGS25+sum(v for k,v in DED25.items() if k in VARIABLE)
fixed25=sum(v for k,v in DED25.items() if k not in VARIABLE)

# personal 2025
P25=dict(wages=49700,interest=7143,dividends=87,ira=455,capgain=-3000,f4797=-4106,rental=-7736,k1_vc=76351,k1_v=-2739,k1_pya=-58496,k1_b=69133)
AGI25=sum(P25.values()); assert AGI25==126792, AGI25
ITEM25=49923; QBI25=14414; TI25=62455; TAX25=8655; CRED25=8655; OTHER25=46
CA25=dict(agi=101976,taxable=55073,tax=1699)

# ---------- 2026 tax functions ----------
FED26=[(12400,.10),(50400,.12),(105700,.22),(201775,.24),(256225,.32),(640600,.35),(10**9,.37)]
CA26=[(10756,.01),(25499,.02),(40245,.04),(55866,.06),(70606,.08),(360659,.093),(432787,.103),(721314,.113),(10**9,.123)]
def bracket(ti,br):
    t=0;lo=0
    for hi,r in br:
        if ti>lo: t+=(min(ti,hi)-lo)*r
        lo=hi
    return t
def marginal(ti,br):
    lo=0
    for hi,r in br:
        if ti<=hi: return r
        lo=hi
    return br[-1][1]

ENERGY_CF=10543; GBC_CF=22385; SALT_CAP=40400
MORT=32075; CHAR=3039; PROP_OTHER=10355+1461
B_W2=13700; B_UBIA=129541; VC_K1=76351

def personal(k1_b, label, note):
    # AGI: 2025 items unchanged except B LLC K-1 and rental loss (special allowance gone above $150K AGI)
    other=AGI25-P25['k1_b']-P25['rental']            # everything except B LLC K-1 and the rental loss
    agi_pre=other+k1_b
    rental=P25['rental'] if agi_pre<=100000 else 0    # fully phased out above $150K
    agi=agi_pre+rental
    # itemized: SALT = property/other taxes + CA income tax paid in-year (assume estimates paid), capped
    ca=california(agi,k1_b)
    salt=min(SALT_CAP,PROP_OTHER+ca['tax'])
    itemized=salt+MORT+CHAR
    # QBI: above threshold, B LLC limited to greater of 50% W-2 or 25% W-2 + 2.5% UBIA
    ti_pre=agi-itemized
    if ti_pre<=201750:
        qbi=0.20*(k1_b+VC_K1-P25['k1_v']*0)  # simple: 20% of positive QBI
        qbi=min(qbi,0.20*ti_pre)
    else:
        cap_b=max(0.5*B_W2,0.25*B_W2+0.025*B_UBIA)
        qbi=min(0.20*k1_b,cap_b)+0.20*VC_K1          # assumes the partnership's own wages support its share
        qbi=min(qbi,0.20*ti_pre)
    ti=max(0,ti_pre-qbi)
    tax=bracket(ti,FED26)
    energy=min(ENERGY_CF,tax); tax_after=tax-energy
    gbc_limit=max(0,tax_after-0.25*max(0,tax_after-25000))
    gbc=min(GBC_CF,gbc_limit); tax_after-=gbc
    fed_other=OTHER25*0
    fica=3802
    total=tax_after+ca['tax']+ca['corp']+fica
    takehome=agi-total   # cash view: AGI less all income and payroll taxes (ignores non-cash items)
    return dict(label=label,note=note,k1_b=k1_b,agi=round(agi),rental=rental,itemized=round(itemized),salt=round(salt),qbi=round(qbi),ti=round(ti),
                fed_gross=round(tax),energy=round(energy),gbc=round(gbc),fed=round(tax_after),marginal=marginal(ti,FED26),
                ca=ca['tax'],ca_ti=ca['ti'],ca_corp=ca['corp'],fica=fica,total=round(total),eff=round(total/agi*100,1),takehome=round(takehome))

def california(agi,k1_b):
    ca_adj=-25557                                   # 2025 CA subtraction (depreciation/other differences) held constant
    ca_item=46903-ITEM25+ (MORT+CHAR+PROP_OTHER)    # CA itemized: no deduction for state income tax; keep other items
    ca_item=MORT+CHAR+PROP_OTHER
    ti=max(0,agi+ca_adj-ca_item)
    tax=bracket(ti,CA26)-153
    corp=max(800,round(0.015*max(0,k1_b-23732)))   # 1.5% S-corp tax on CA net income (2025 depreciation adj held)
    return dict(tax=round(tax),ti=round(ti),corp=corp)

REV26=600000
scen=[]
# A: costs grow with revenue (same 23.9% margin)
m=K1_25/REV25
scen.append(dict(name='Costs scale with revenue',k1=round(REV26*m),cogs=round(COGS25/REV25*REV26),ded=round(sum(DED25.values())/REV25*REV26),
                 note='Every expense line grows in proportion to sales; margin stays at 23.9%.'))
# B: only variable costs grow
v=var25/REV25
scen.append(dict(name='Only variable costs grow',k1=round(REV26-REV26*v-fixed25),cogs=round(COGS25/REV25*REV26),ded=round(fixed25+ (var25-COGS25)/REV25*REV26),
                 note='COGS, outside services, permits, commissions, supplies, equipment rental and payroll processing grow with sales (13.6%); everything else held at 2025 dollars.'))
# C: all costs flat
scen.append(dict(name='All costs held flat',k1=REV26-COGS25-sum(DED25.values()),cogs=COGS25,ded=sum(DED25.values()),
                 note='Every 2025 expense repeats at the same dollar amount; all added revenue is profit.'))
for s in scen: s['personal']=personal(s['k1'],s['name'],s['note'])

out=dict(rev25=REV25,cogs25=COGS25,ded25=DED25,k1_25=K1_25,var25=var25,fixed25=fixed25,p25=P25,agi25=AGI25,scen=scen,
         fed_marg25=0.22)
json.dump(out,open(__file__.replace('calc.py','calc.json'),'w'),indent=1)
for s in scen:
    p=s['personal']; print(s['name'],'K-1',s['k1'],'| AGI',p['agi'],'item',p['itemized'],'qbi',p['qbi'],'TI',p['ti'],'fed gross',p['fed_gross'],'energy',p['energy'],'gbc',p['gbc'],'fed',p['fed'],'CA',p['ca'],'CAcorp',p['ca_corp'],'total',p['total'],'eff',p['eff'],'take',p['takehome'])
print('var25',var25,'fixed25',fixed25, 'fed25 check', bracket(62455,[(11925,.1),(48475,.12),(103350,.22),(197300,.24),(250525,.32),(626350,.35),(10**9,.37)]))
