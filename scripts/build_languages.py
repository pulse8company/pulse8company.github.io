#!/usr/bin/env python3
"""Generate static language pages and the small runtime dictionary for interactive UI."""
import json,re,html
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
PAGES=['index','aso','support','privacy-policy','terms','data-deletion']
LANGS={'en':'English','fr':'Français','it':'Italiano','de':'Deutsch','es':'Español','ru':'Русский'}
LABELS={'en':'Language','fr':'Langue','it':'Lingua','de':'Sprache','es':'Idioma','ru':'Язык'}
VERSION='20261110a'
def target(page,lang):return page+('' if lang=='en' else '-'+lang)+'.html'
def local_link(url,lang):
    m=re.fullmatch(r'('+ '|'.join(PAGES)+r')\.html([?#].*)?',url)
    return target(m[1],lang)+(m[2] or '') if m else url
class Localizer(HTMLParser):
    def __init__(self,d,lang):super().__init__(convert_charrefs=True);self.d=d;self.lang=lang;self.out=[];self.skip=0
    def tr(self,s):
        t=s.strip();return s[:len(s)-len(s.lstrip())]+self.d.get(t,t)+s[len(s.rstrip()):] if t else s
    def handle_decl(self,x):self.out.append('<!'+x+'>')
    def handle_comment(self,x):self.out.append('<!--'+x+'-->')
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
        original=dict(attrs);new=[]
        for k,v in attrs:
            if k=='lang' and tag=='html':v=self.lang
            elif k=='href':v=local_link(v,self.lang)
            elif k in ('aria-label','placeholder','alt','title') and v:v=self.tr(v)
            elif tag=='meta' and k=='content' and original.get('name')=='description':v=self.tr(v)
            new.append(k if v is None else k+'="'+html.escape(v,quote=True)+'"')
        self.out.append('<'+tag+(' '+' '.join(new) if new else '')+'>')
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs);self.out[-1]=self.out[-1][:-1]+'/>'
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip-=1
        self.out.append('</'+tag+'>')
    def handle_data(self,x):self.out.append(x if self.skip else html.escape(self.tr(x),quote=False))

def build():
    for page in PAGES:
        source=(ROOT/'templates'/'en'/(page+'.html')).read_text()
        # Rebuild safely on repeated runs.
        source=re.sub(r'<!-- languages:start -->.*?<!-- languages:end -->','',source,flags=re.S)
        source=re.sub(r'<link rel="stylesheet" href="i18n.css[^\"]*">','',source)
        source=re.sub(r'<script src="(?:locales/[^\"]+|i18n.js[^\"]*)"></script>','',source)
        for lang in LANGS:
            d={} if lang=='en' else json.loads((ROOT/'locales'/f'{lang}.json').read_text())
            parser=Localizer(d,lang);parser.feed(source);s=''.join(parser.out)
            alternates=''.join(f'<link rel="alternate" hreflang="{code}" href="https://pulse8company.github.io/{target(page,code)}">' for code in LANGS)
            alternates+=f'<link rel="alternate" hreflang="x-default" href="https://pulse8company.github.io/{page}.html"><link rel="canonical" href="https://pulse8company.github.io/{target(page,lang)}">'
            s=s.replace('</head>',f'<!-- languages:start -->{alternates}<!-- languages:end --><link rel="stylesheet" href="i18n.css?v={VERSION}"></head>')
            links=''.join(f'<a href="{target(page,code)}" lang="{code}" hreflang="{code}" title="{name}" aria-label="{name}"'+(' aria-current="page"' if lang==code else '')+f'>{code.upper()}</a>' for code,name in LANGS.items())
            switch=f'<!-- languages:start --><nav class="language-switch" aria-label="{LABELS[lang]}"><span aria-hidden="true">{LABELS[lang]}</span>{links}</nav><!-- languages:end -->'
            s=s.replace('</header>',switch+'</header>') if '</header>' in s else s.replace('</nav>','</nav>'+switch,1)
            runtime=(f'<script src="locales/{lang}.js?v={VERSION}"></script>' if lang!='en' else '')+f'<script src="i18n.js?v={VERSION}"></script>'
            # Start before the interactive scripts so their changes are localized too.
            pos=s.find('<script',s.find('</footer>'))
            s=s[:pos]+runtime+s[pos:] if pos!=-1 else s.replace('</body>',runtime+'</body>')
            (ROOT/target(page,lang)).write_text(s+'\n')
    for lang in LANGS:
        if lang=='en':continue
        d=json.loads((ROOT/'locales'/f'{lang}.json').read_text())
        # Only interactive strings need client-side translation. Static policy stays readable without JavaScript.
        runtime={k:v for k,v in d.items() if len(k)<700}
        (ROOT/'locales'/f'{lang}.js').write_text('window.PULSE8_TRANSLATIONS='+json.dumps(runtime,ensure_ascii=False)+';\n')
    (ROOT/'ru.html').write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=index-ru.html"><title>Pulse8</title></head><body><a href="index-ru.html">Открыть сайт Pulse8 на русском</a></body></html>\n')
if __name__=='__main__':build()
