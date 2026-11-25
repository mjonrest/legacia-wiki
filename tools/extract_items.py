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
 'db/import/item_db_other.yml','db/import/item_db_costume.yml','db/import/item_headgear.yml','db/import/item_db_legacia.yml']
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
# PvP shop (Ladder)
for p in re.search(r'^-\tpointshop\tPvP_Cash_Shop#cash\t-1,#PvpPoints,(.*)$',L('npc/miracle/s_pvp_rank.txt'),re.M).group(1).strip().split(','):
    i,pr=map(int,p.split(':')); add(i,'PvP Shop','Ladder, prontera 166,198 (PvP Shops)','%d PvP Points'%pr)
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
# Town shops: every loaded zeny shop with a map position (Pet Groomers included)
def loaded_npc_files():
    out=[]; seen=set()
    def walk(conf):
        try: lines=L(conf).splitlines()
        except Exception: return
        for line in lines:
            line=line.split('//')[0].strip()
            m=re.match(r'(npc|import|delnpc):\s*(.+)',line)
            if not m: continue
            k,v=m.group(1),m.group(2).strip()
            if k=='import': walk(v)
            elif k=='npc' and v not in seen: seen.add(v); out.append(v)
            elif k=='delnpc' and v in seen: out.remove(v); seen.discard(v)
    walk('npc/pre-re/scripts_main.conf'); walk('npc/scripts_custom.conf')
    return out
LOADED=loaded_npc_files()
TOWN=[('prt_church','Prontera'),('prt_in','Prontera'),('prt_monk','Prontera'),('prt_fild','Prontera field'),('prontera','Prontera'),('izlude','Izlude'),('alb2trea','Alberta'),('alberta','Alberta'),('aldeba','Al De Baran'),('alde_alche','Al De Baran'),('aldebaran','Al De Baran'),('ama','Amatsu'),('que_ng','Amatsu'),('ayo','Ayothaya'),('cmd_fild','Comodo field'),('cmd','Comodo'),('comodo','Comodo'),('ein','Einbroch'),('geffen','Geffen'),('gonryun','Kunlun'),('hu_in','Hugel'),('hugel','Hugel'),('jawaii','Jawaii'),('yuno','Juno'),('lighthalzen','Lighthalzen'),('lhz','Lighthalzen'),('lou','Louyang'),('xmas','Lutie'),('in_moc','Morroc'),('moc_ruins','Morroc'),('morocc','Morroc'),('mosk','Moscovia'),('moscovia','Moscovia'),('nif','Niflheim'),('niflheim','Niflheim'),('payon','Payon'),('ra_in','Rachel'),('rachel','Rachel'),('tur_dun','Turtle Island'),('um','Umbala'),('umbala','Umbala'),('ve_in','Veins'),('cave','Morroc')]
HIDDEN_SHOP={'Weapon Dealer#prt20':'prt_in,172,130','Armor Dealer#prt20':'prt_in,172,132'}
for f in LOADED:
    if not (f.endswith('merchants/shops.txt') or f.endswith('quests/quests_morocc.txt')): continue
    for m in re.finditer(r'^([^/\t\n][^\t\n]*)\tshop\t([^\t\n]+)\t([^\n]*)$',L(f),re.M):
        loc,name,body=m.groups()
        if loc=='-':
            if name not in HIDDEN_SHOP: continue
            loc=HIDDEN_SHOP[name]
        mp,x,y=loc.split(',')[:3]
        if mp.startswith('brasilis'): continue   # city not loaded, warper blocks it
        town=next((tw for pre,tw in TOWN if mp.startswith(pre)),mp)
        npc=name.split('#')[0]
        src='Pet Groomer' if npc=='Pet Groomer' else 'Town Shop'
        body=re.split(r'\s*//',body)[0].split('\t')[0]
        for part in body.split(',')[1:]:
            part=part.strip()
            if not part: continue
            i,pr=map(int,part.split(':')[:2])
            if pr==-1: pr=buy(i)
            add(i,src,'%s, %s %s,%s (%s)'%(npc,mp,x,y,town),'{:,}z'.format(pr))
# Legacy Shard Exchange (Archivist Sera, Legacia story): weapons + guns 50 shards, utility headgears 150
hc=L('npc/miracle/legacia_story/hollow_crown_part1.txt')
pm=re.search(r'setarray \.price\[0\],\s*(\d+),\s*(\d+);',hc)
pw,ph=(int(pm.group(1)),int(pm.group(2))) if pm else (50,150)
exw=list(range(60001,60022))+[int(x) for x in re.findall(r'\d+',(re.search(r'setarray \.ex_weapons\[getarraysize\(\.ex_weapons\)\],([^;]*);',hc) or re.search('()','')).group(1))]
exh=[int(x) for x in re.findall(r'\d+',(re.search(r'setarray \.ex_heads\[0\],([^;]*);',hc) or re.search('()','')).group(1))]
for i in exw: add(i,'Shard Exchange','Archivist Sera, prt_castle 125,51 (Legacia story)','%d Legacy Shards'%pw)
for i in exh: add(i,'Shard Exchange','Archivist Sera, prt_castle 125,51 (Legacia story)','%d Legacy Shards'%ph)
# Monster drops: every monster that spawns on a loaded map, with server drop rates (conf/battle/drops.conf)
def conf_val(k,default):
    m=re.search(r'^'+k+r':\s*(\d+)',L('conf/battle/drops.conf'),re.M)
    return int(m.group(1)) if m else default
spawn={}
for f in LOADED:
    try: t=L(f)
    except Exception: continue
    for m in re.finditer(r'^([a-z0-9_@]+),[^\t\n]*\t(?:boss_)?monster\t[^\t\n]*\t(\d+),(\d+)',t,re.M):
        c=spawn.setdefault(int(m.group(2)),{})
        c[m.group(1)]=c.get(m.group(1),0)+int(m.group(3))
spawn={k:sorted(v,key=lambda mp:-v[mp]) for k,v in spawn.items()}   # maps with the most of this monster first
mobfull={}
for f in ['db/pre-re/mob_db.yml','db/import/mob_db.yml']:
    try:
        d=yaml.safe_load(L(f))
        for mm in d.get('Body') or []: mobfull.setdefault(mm['Id'],{}).update(mm)
    except Exception as e: print('mob',f,e)
aeg_all={str(v.get('AegisName')).lower():k for k,v in items.items()}
def kind(i):
    t=items.get(i,{}).get('Type','')
    if t=='Healing': return 'heal'
    if t in ('Usable','Delayconsume','Cash'): return 'use'
    if t in ('Weapon','Armor','Petarmor','Shadowgear'): return 'equip'
    if t=='Card': return 'card'
    return 'common'
cap=conf_val('drop_rate_cap',9000)
for mid,maps in spawn.items():
    mm=mobfull.get(mid)
    if not mm: continue
    mvp=bool(mm.get('MvpExp')); boss=mvp or mm.get('Class')=='Boss'
    where='%s (Lv %s), %s'%(mm.get('Name'),mm.get('Level',1),', '.join(maps[:3])+(' +%d more'%(len(maps)-3) if len(maps)>3 else ''))
    for dr in mm.get('Drops') or []:
        i=aeg_all.get(str(dr['Item']).lower())
        if not i: continue
        k=kind(i); suf='_mvp' if mvp else '_boss' if boss else ''
        r=dr['Rate']*conf_val('item_rate_'+k+suf,100)//100
        r=max(conf_val('item_drop_'+k+'_min',1),min(conf_val('item_drop_'+k+'_max',10000),r))
        r=min(r,cap)
        add(i,'Monster drop',where,('%.2f'%(r/100)).rstrip('0').rstrip('.')+'% drop')
    for dr in mm.get('MvpDrops') or []:
        i=aeg_all.get(str(dr['Item']).lower())
        if not i: continue
        r=max(1,min(10000,dr['Rate']*conf_val('item_rate_mvp',100)//100))
        add(i,'Monster drop',where,('%.2f'%(r/100)).rstrip('0').rstrip('.')+'% MVP reward')
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
