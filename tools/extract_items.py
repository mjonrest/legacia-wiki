import re, json, yaml
R='/home/user/legacia-RO/'
def L(p):
    b=open(R+p,'rb').read()
    try: t=b.decode('utf-8')
    except UnicodeDecodeError: t=b.decode('latin-1')
    return re.sub(r'[\x80-\x9f]','',t)
# item db
items={}
files=['db/pre-re/item_db_usable.yml','db/pre-re/item_db_equip.yml','db/pre-re/item_db_etc.yml',
 'db/import/item_db.yml','db/import/item_db_ex.yml','db/import/item_db_costume_legacy.yml','db/import/item_db_elite.yml',
 'db/import/item_db_other.yml','db/import/item_db_costume.yml','db/import/item_headgear.yml']
for f in files:
    try: d=yaml.safe_load(L(f).replace('\t','  '))
    except Exception as e: print('ERR',f,e); continue
    for it in (d.get('Body') or []):
        o=items.get(it['Id'],{}); o.update(it); items[it['Id']]=o
def nm(i):
    it=items.get(i)
    if not it: return None
    n=it.get('Name',str(i)); s=it.get('Slots')
    if it.get('Type') in ('Weapon','Armor') and s is not None: n+=' [%d]'%s
    return n
def typ(i):
    it=items.get(i,{}); t=it.get('Type','')
    loc=it.get('Locations') or {}
    if any(k.startswith('Costume') for k in loc): return 'Costume'
    if t=='Armor' and any(k.startswith('Head') for k in loc): return 'Headgear'
    return {'Healing':'Consumable','Usable':'Consumable','Delayconsume':'Consumable','Cash':'Consumable','Etc':'Material','Card':'Card','Weapon':'Weapon','Armor':'Armor','Ammo':'Ammo','Petegg':'Pet','Petarmor':'Pet'}.get(t,t or 'Item')
def buy(i):
    it=items.get(i,{}); b=it.get('Buy'); s=it.get('Sell')
    if b is None: b=(s or 0)*2
    return b
rows=[]; missing=set()
def add(i,src,where,cost,detail=''):
    n=nm(i)
    if not n: missing.add(i); return
    rows.append({'id':i,'n':n,'t':typ(i),'s':src,'w':where,'c':cost,'d':detail})
def shopline(name):
    for f in ['npc/miracle/script_oinit.txt','npc/miracle/hatmaker.txt','npc/miracle/devil_square.txt']:
        m=re.search(r'^-\t(?:shop|pointshop)\t'+re.escape(name)+r'\t-1,(.*)$',L(f),re.M)
        if m: return m.group(1).strip()
# Tool dealer
for sh,lab in [('tooldealershop','Normal Tool'),('ninja','Ninja'),('guns','Gunslinger')]:
    for p in shopline(sh).split(','):
        i,pr=map(int,p.split(':'))
        if pr==-1: pr=buy(i)
        add(i,'Tool Dealer','prontera 164,175 ('+lab+')','{:,}z'.format(pr))
# Hourly
for p in shopline('Hourly').split(',')[1:]:
    i,pr=map(int,p.split(':')); add(i,'Hourly Shop','Hourly / Gold PC button','%d Hourly Points'%pr)
# DS
for p in shopline('dsshop').split(',')[1:]:
    i,pr=map(int,p.split(':')); add(i,'Devil Square Shop','prontera 138,176','%d DS Points'%pr)
# Quest shop
t=L('npc/miracle/hatmaker.txt')
for m in re.finditer(r'^\s*Add\(([^)]*)\);',t,re.M):
    a=[int(x) for x in m.group(1).split(',')]
    shop,rid,amt,z,pt=a[:5]; req=a[5:]
    parts=[]
    for k in range(0,len(req),2):
        rn=nm(req[k]) or ('Item %d'%req[k]); parts.append('%d x %s'%(req[k+1],rn))
    if z: parts.append('{:,}z'.format(z))
    if pt: parts.append('%d Cash Points'%pt)
    add(rid,'Quest Shop','prontera 147,166 (Quest %s)'%['I','II','III','IV','V','VI','VII','VIII'][shop-1],'; '.join(parts) or 'free')
# Daily
dc=L('npc/miracle/daily_classic.txt')
add(13534,'Daily Point Shop','@dailyquest','1 Daily Point')
add(13810,'Daily Point Shop','@dailyquest','1 Daily Point')
g=re.search(r'setarray \.@geararray\[0\],(.*?);',dc,re.S).group(1)
g=re.sub(r'//[^\n]*','',g)
for i in sorted(set(int(x) for x in re.findall(r'\d+',g))):
    add(i,'Daily Point Shop','@dailyquest','5 Daily Points','Only on days it is the headgear of the day')
# Gacha
gc=L('npc/miracle/gacha_costume.txt')
for var,lab,cost in [('top','Costume Headgear gacha','10 Activity Points, 10% win'),('mid','Costume Headgear gacha','10 Activity Points, 10% win'),('low','Costume Headgear gacha','10 Activity Points, 10% win'),('garments','Costume Garment gacha','30 Activity Points, 5% win')]:
    m=re.search(r'setarray \.@'+var+r'\[0\],(.*?);',gc,re.S)
    body=re.sub(r'//[^\n]*','',m.group(1))
    for i in dict.fromkeys(int(x) for x in re.findall(r'\d+',body)):
        add(i,'Gacha Machine','prontera 131,216 ('+lab+')',cost,'Random prize, account bound')
# Pet groomer
for p in '14569 14570 14571 14572 14573 14574 12358 12359 12360 12361 12362 12363 12364 12365 12366 12367 12368 12369 12370 12371 12372 12357'.split():
    add(int(p),'Pet Groomer','Prontera, Geffen, Payon, Izlude, Morroc, Juno, Lighthalzen','100,000z')
# Extra mob drops
md=L('npc/miracle/mob_drop.txt')
mob=[int(x) for x in re.search(r'setarray \.@MobID\[0\],([^;]*);',md).group(1).split(',')]
drop=[int(x) for x in re.search(r'setarray \.@DropID\[0\],([^;]*);',md).group(1).split(',')]
mobdb={}
for f in ['db/pre-re/mob_db.yml','db/import/mob_db.yml']:
    try:
        d=yaml.safe_load(L(f))
        for mm in d.get('Body') or []: mobdb[mm['Id']]=mm.get('Name')
    except Exception as e: print('mob',f,e)
for a,b in zip(mob,drop):
    add(b,'Monster drop','%s (bonus drop)'%mobdb.get(a,'Monster %d'%a),'0.3% drop','Server-wide announce when it drops')
# Cash shop
for f in ['db/item_cash.yml','db/import/item_cash.yml']:
    d=yaml.safe_load(L(f)) or {}
    aeg={str(v.get('AegisName')).lower():k for k,v in items.items()}
    for tab in d.get('Body') or []:
        for it in tab.get('Items') or []:
            i=aeg.get(it['Item'].lower())
            if i: add(i,'Cash Shop','Cash Shop button (%s tab)'%tab['Tab'],'%d CP'%it['Price'])
            else: missing.add(it['Item'])
# dedupe
seen=set(); out=[]
for r in rows:
    k=(r['id'],r['s'],r['w'],r['c'])
    if k in seen: continue
    seen.add(k); out.append(r)
json.dump(out,open('/tmp/claude-0/wk/items.json','w'),separators=(',',':'),ensure_ascii=False)
from collections import Counter
print(len(out),Counter(r['s'] for r in out)); print('missing',list(missing)[:30],len(missing))
