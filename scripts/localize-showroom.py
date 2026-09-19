#!/usr/bin/env python3
"""Build Korean showroom pages and reciprocal language links from generated English HTML."""
import json, os, re
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit
R=Path(__file__).resolve().parents[1]
T=json.loads((R/'locales/ko.json').read_text())
PAGES=[Path('index.html'),*(p.relative_to(R) for p in sorted((R/'apps').glob('*.html')))]

def translate(text):
 if text in T:return T[text]
 stripped=text.strip()
 if stripped in T:return text.replace(stripped,T[stripped],1)
 if text.endswith(' · Design Culture Software'):return translate(text.removesuffix(' · Design Culture Software'))+' · Design Culture Software'
 if ' / ' in text:
  a,b=text.split(' / ',1)
  if a in T:return T[a]+' / '+b
 match=re.fullmatch(r'Enlarge (.+) screenshot (\d+)',text)
 if match:return f'{match[1]} 스크린샷 {match[2]} 확대'
 match=re.fullmatch(r'(.+) screenshot (\d+)',text)
 if match:return f'{match[1]} 스크린샷 {match[2]}'
 if text.startswith('Explore '):return text[8:]+' 자세히 보기'
 if text.startswith('Get ') and text.endswith(' on the App Store'):return text[4:-17]+' App Store에서 다운로드'
 if text.endswith(' app preview'):return text[:-12]+' 앱 미리보기'
 if text.endswith(' preview'):return text[:-8]+' 미리보기'
 if text.endswith(' support'):return text[:-8]+' 지원'
 return text

def relative(target,source):return Path(os.path.relpath(target,source.parent)).as_posix()

def language_links(page,lang):
 source=page if lang=='en' else Path('ko')/page
 en=relative(page,source);ko=relative(Path('ko')/page,source)
 return f'<span class="language-switch" role="group" aria-label="{"Language" if lang=="en" else "언어 선택"}"><a href="{en}" lang="en" hreflang="en" {"aria-current=\"page\"" if lang=="en" else ""}>EN</a><span aria-hidden="true">/</span><a href="{ko}" lang="ko" hreflang="ko" {"aria-current=\"page\"" if lang=="ko" else ""}>한국어</a></span>'

class KoreanHTML(HTMLParser):
 def __init__(self,page):
  super().__init__(convert_charrefs=True);self.page=page;self.output=[]
 def handle_decl(self,decl):self.output.append('<!'+decl+'>')
 def handle_starttag(self,tag,attrs):
  values=[]
  for key,value in attrs:
   if value is None:values.append(key);continue
   if key=='lang' and tag=='html':value='ko'
   elif key in ('href','src'):
    u=urlsplit(value)
    if not u.scheme and not u.netloc and u.path:
     target=Path(os.path.normpath(self.page.parent/u.path))
     if target in PAGES:target=Path('ko')/target
     value=urlunsplit(('', '', relative(target,Path('ko')/self.page),u.query,u.fragment))
   elif key in ('alt','aria-label','content'):value=translate(value)
   values.append(f'{key}="{escape(value,quote=True)}"')
  self.output.append('<'+tag+(' '+ ' '.join(values) if values else '')+'>')
 def handle_endtag(self,tag):self.output.append('</'+tag+'>')
 def handle_data(self,data):self.output.append(escape(translate(data),quote=False))
 def handle_entityref(self,name):self.output.append('&'+name+';')
 def handle_charref(self,name):self.output.append('&#'+name+';')
 def handle_comment(self,text):self.output.append('<!--'+text+'-->')

def build():
 for page in PAGES:
  original=(R/page).read_text()
  parser=KoreanHTML(page);parser.feed(original)
  korean=''.join(parser.output)
  for lang,document,dest in [('en',original,page),('ko',korean,Path('ko')/page)]:
   document=document.replace('</nav></header>',language_links(page,lang)+'</nav></header>',1)
   links=''.join(f'<link rel="alternate" hreflang="{code}" href="{relative(target,dest)}">' for code,target in [('en',page),('ko',Path('ko')/page),('x-default',page)])
   document=document.replace('</head>',links+'</head>',1)
   (R/dest).parent.mkdir(parents=True,exist_ok=True)
   (R/dest).write_text(document)
if __name__=='__main__':build()
