"""Structural checks for all six editions; run after build_languages.py."""
import json,re
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from build_languages import PAGES,LANGS,target
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self,text):super().__init__(convert_charrefs=True);self.tags=Counter();self.attrs=[];self.data=[];self.feed(text)
 def handle_starttag(self,tag,attrs):self.tags[tag]+=1;self.attrs.append((tag,dict(attrs)))
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
 def handle_data(self,s):
  if s.strip():self.data.append(s.strip())
for page in PAGES:
 original=Page((ROOT/'templates/en'/f'{page}.html').read_text())
 ext=lambda p:Counter(a['href'] for t,a in p.attrs if t=='a' and a.get('href','').startswith(('https:','http:','mailto:')))
 for lang in LANGS:
  path=ROOT/target(page,lang);text=path.read_text();p=Page(text)
  assert next(a['lang'] for t,a in p.attrs if t=='html')==lang,path
  assert ext(p)==ext(original),(path,'External links changed')
  for tag in ['p','h1','h2','h3','h4','li','input','select','textarea','svg','path']:
   assert p.tags[tag]==original.tags[tag],(path,tag,'Missing content/structure')
  active=[a for t,a in p.attrs if a.get('aria-current')=='page' and 'hreflang' in a]
  assert len(active)==1 and active[0]['href']==path.name,path
  assert sum(1 for t,a in p.attrs if t=='link' and a.get('rel')=='alternate')==7,path
  for t,a in p.attrs:
   for attr in (['href'] if t in ('a','link') else ['src'] if t in ('script','img') else []):
    url=a.get(attr,'').split('#')[0].split('?')[0]
    if url and not re.match(r'^[a-z]+:',url):assert (ROOT/url).exists(),(path,url)
  assert not re.search(r'(BRANDTOKEN|MARQUETOKEN|MARCATOKEN|БР[АЕ]НДТОКЕН|ZXQ\d|QXZ)',text),path
  if lang=='en':
   for s in original.data:assert s in p.data,('English content changed',page,s)
for lang in LANGS:
 if lang=='en':continue
 d=json.loads((ROOT/'locales'/f'{lang}.json').read_text())
 assert all(isinstance(v,str) and v.strip() for v in d.values())
 assert all(s in d for s in json.loads((ROOT/'locales/source.json').read_text()))
print('PASS: 36 pages, complete structure, unchanged external links, six-way navigation, assets and translation coverage.')
