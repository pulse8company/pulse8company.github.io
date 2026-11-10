#!/usr/bin/env python3
"""Build static language editions. Translations are cached and editable in locales/*.json."""
import json,re,html,subprocess,time,concurrent.futures
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
PAGES=['index','aso','support','privacy-policy','terms','data-deletion']
LANGS={'en':'English','fr':'Français','it':'Italiano','de':'Deutsch','es':'Español','ru':'Русский'}
PROTECTED={'Pulse8','pulse8.','Red Hunt','Drag Battle','Blade of Shadows','Zombie Warriors','Tiny Island','AIrtist','App Store','Google Play','iPhone','iPhone / iPad','Android','1M+','15M+','Pulse8 LLC - FZ','Pulse8 L.L.C-FZ'}
ATTRS={'aria-label','placeholder','alt','title'}
strings=set()
def eligible(s):
    return bool(re.search('[A-Za-z]',s)) and s not in PROTECTED and not re.match(r'^(https?://|mailto:|[^ ]+@)',s)
def collect(s):
    s=html.unescape(s).strip()
    if eligible(s):strings.add(s)
class Collector(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
        for k,v in attrs:
            if k in ATTRS and v:collect(v)
            if tag=='meta' and k=='content' and dict(attrs).get('name')=='description':collect(v)
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip-=1
    def handle_data(self,s):
        if not self.skip:collect(s)
for p in PAGES:Collector().feed((ROOT/'templates/en'/(p+'.html')).read_text())
s=(ROOT/'games.js').read_text();games=json.loads(re.search(r'const games=(.*?);\n',s).group(1))
for g in games:
    for k in ('description','subtitle'):collect(g[k])
    for x in g['genres']:collect(x)
    collect(g['title']+' — concept illustration');collect('Show '+g['title'])
    for platform in g['platforms']:collect(g['title']+' on '+platform['name'])
    for i in range(1,len(games)+1):
        collect(f'{i} of {len(games)}: {g["title"]}');collect(f'{g["title"]}, game {i} of {len(games)}')
for v in ['EXPLORE OUR GAMES','OUR GAMES','Available on','Coming soon','In development','Other platforms · Coming soon','installs','All platforms','Your draft is ready. Open it below, then review and send from your email app. Nothing has been sent yet.','Your email request is ready. Open it below, then review and send it. Nothing has been sent yet.']:collect(v)
a=(ROOT/'aso.js').read_text().split('function drawChart')[0]
for v in re.findall(r"'([^']+)'",a):collect(v)
for stages in ['Research, Position, Optimize, Review','Map intent, Localize, Refine, Monitor','Audit, Create, Test, Iterate']:collect('Conceptual service journey: '+stages+'. This diagram contains no performance data.')
# Avoid translating brands inside longer sentences.
BRANDS=['Pulse8 L.L.C-FZ','Pulse8 LLC - FZ','Blade of Shadows','Zombie Warriors','Tiny Island','Red Hunt','Drag Battle','AIrtist','Google Play','App Store','Pulse8']
def translate_batch(items,lang):
    raw='\n'.join(f'ZXQ{i:04d}QXZ\n{s}' for i,s in enumerate(items))
    for i,brand in enumerate(BRANDS):raw=raw.replace(brand,f'BRANDTOKEN{i:02d}')
    url='https://translate.googleapis.com/translate_a/single'
    for attempt in range(4):
        r=subprocess.run(['curl','-fsSLG',url,'--max-time','40','--data-urlencode','client=gtx','--data-urlencode','sl=en','--data-urlencode','tl='+lang,'--data-urlencode','dt=t','--data-urlencode','q='+raw],capture_output=True,text=True)
        try:
            data=json.loads(r.stdout);out=''.join(x[0] for x in data[0] if x and x[0])
            for i,brand in enumerate(BRANDS):out=re.sub(f'BRANDTOKEN\\s*{i:02d}',lambda m:brand,out,flags=re.I)
            parts=re.split(r'ZXQ\s*(\d{4})\s*QXZ',out,flags=re.I)
            result={int(parts[i]):parts[i+1].strip() for i in range(1,len(parts),2)}
            assert set(result)==set(range(len(items)))
            assert all(result.values())
            assert not any(re.search('BRANDTOKEN|ZXQ|QXZ',v,re.I) for v in result.values())
            return [result[i] for i in range(len(items))]
        except Exception:
            if attempt==3:raise RuntimeError('Translation failed '+lang+' '+r.stdout[:200])
            time.sleep(2*(attempt+1))
def run(lang):
    path=ROOT/'locales'/f'{lang}.json';d=json.loads(path.read_text()) if path.exists() else {}
    todo=[s for s in sorted(strings) if s not in d];batches=[];batch=[];size=0
    for s in todo:
        if size+len(s)>3200 and batch:batches.append(batch);batch=[];size=0
        batch.append(s);size+=len(s)+16
    if batch:batches.append(batch)
    for n,b in enumerate(batches):
        d.update(zip(b,translate_batch(b,lang)));path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
        print(f'{lang}: {n+1}/{len(batches)}',flush=True)
    return lang,len(d)
if __name__=='__main__':
    (ROOT/'locales/source.json').write_text(json.dumps(sorted(strings),ensure_ascii=False,indent=2)+'\n')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(run,[x for x in LANGS if x!='en']):print(result,flush=True)
