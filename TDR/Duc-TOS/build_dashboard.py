import csv,collections,datetime as dt,json,sys
"""Build Trading-Dashboard.html from a Schwab Order Status CSV export.

Usage:  python build_dashboard.py <OrderStatus.csv> [output.html]
Default output: Trading-Dashboard.html next to this script.
"""
import os
src=sys.argv[1]
rows=list(csv.DictReader(open(src,encoding='utf-8-sig')))
def ts(s): return dt.datetime.strptime(s,'%I:%M %p %m/%d/%Y')
LAST=max(ts(r['Time and Date(ET)']) for r in rows if r['Time and Date(ET)'])
def otype(p):
    p=p.strip()
    if p.startswith('Stop market'): return 'Stop market'
    if p.startswith('Trailing'): return 'Trailing stop'
    if p.startswith('Limit'): return 'Limit'
    if p.startswith('Market'): return 'Market'
    if p.startswith('Stop'): return 'Stop limit'
    return p or 'Unknown'
opt=[r for r in rows if len(r['Symbol'].split())==4 and r['Time and Date(ET)']]
fills=[r for r in opt if r['Status'] in('Filled','Closed partial fill')]
fills.sort(key=lambda r:(ts(r['Time and Date(ET)']),int(r['Order Number'])))
open_lots=collections.defaultdict(list);trades=[];unmatched=[]
def parse(sym):
    u,exp,strike,cp=sym.split();return u,dt.datetime.strptime(exp,'%m/%d/%Y').date(),float(strike),('Call' if cp=='C' else 'Put')
for r in fills:
    sym=r['Symbol'];q=int(r['Quantity|Face Value'].split()[0]);p=float(r['Fill Price'].strip('$'));t=ts(r['Time and Date(ET)'])
    if r['Action']=='Buy to open':
        # averaging flag: existing lots
        ex=open_lots[sym]
        add='first' if not ex else ('add_down' if p<min(l[1] for l in ex) else 'add_up')
        open_lots[sym].append([q,p,t,otype(r['Price']),add,q])
    elif r['Action']=='Sell to close':
        rem=q
        while rem>0 and open_lots[sym]:
            lot=open_lots[sym][0];take=min(rem,lot[0])
            u,exp,strike,cp=parse(sym)
            trades.append(dict(sym=sym,u=u,cp=cp,strike=strike,exp=exp.isoformat(),qty=take,entry=lot[1],exit=p,et=lot[2].isoformat(),xt=t.isoformat(),
                pnl=round((p-lot[1])*100*take,2),exitType=otype(r['Price']),entryType=lot[3],add=lot[4],orderQty=lot[5],
                dte=(exp-lot[2].date()).days,holdMin=round((t-lot[2]).total_seconds()/60,1),expired=False))
            lot[0]-=take;rem-=take
            if lot[0]==0: open_lots[sym].pop(0)
        if rem>0: unmatched.append(dict(sym=sym,qty=rem,t=t.isoformat(),price=p))
stillOpen=[]
for sym,ls in open_lots.items():
    u,exp,strike,cp=parse(sym)
    for lot in ls:
        if exp<LAST.date():
            xt=dt.datetime.combine(exp,dt.time(16,0)) if u!='SPXW' else dt.datetime.combine(exp,dt.time(16,15))
            trades.append(dict(sym=sym,u=u,cp=cp,strike=strike,exp=exp.isoformat(),qty=lot[0],entry=lot[1],exit=0.0,et=lot[2].isoformat(),xt=xt.isoformat(),
                pnl=round(-lot[1]*100*lot[0],2),exitType='Expired',entryType=lot[3],add=lot[4],orderQty=lot[5],dte=(exp-lot[2].date()).days,
                holdMin=round((xt-lot[2]).total_seconds()/60,1),expired=True))
        else:
            stillOpen.append(dict(sym=sym,qty=lot[0],entry=lot[1],et=lot[2].isoformat()))
trades.sort(key=lambda t:t['xt'])
# orders summary (all option + stock rows)
orders=[]
for r in rows:
    if not r['Time and Date(ET)']: continue
    t=ts(r['Time and Date(ET)'])
    orders.append(dict(sym=r['Symbol'],u=r['Symbol'].split()[0],status=r['Status'],action=r['Action'],qty=r['Quantity|Face Value'],otype=otype(r['Price']),
        price=r['Price'],fill=r['Fill Price'],t=t.isoformat(),isOption=len(r['Symbol'].split())==4))
out=dict(generated=dt.datetime.now().isoformat(timespec='minutes'),source=os.path.basename(src),lastFill=LAST.isoformat(),trades=trades,unmatched=unmatched,stillOpen=stillOpen,orders=orders)
here=os.path.dirname(os.path.abspath(__file__))
tpl=open(os.path.join(here,'dashboard_template.html'),encoding='utf-8').read()
html=tpl.replace('__DATA__',json.dumps(out).replace('</',r'<\/'))
outp=sys.argv[2] if len(sys.argv)>2 else os.path.join(here,'Trading-Dashboard.html')
open(outp,'w',encoding='utf-8').write(html)
print(f'wrote {outp}: {len(trades)} trades, {len(unmatched)} unmatched sells, {len(stillOpen)} still open, net {sum(t["pnl"] for t in trades):,.0f}')
