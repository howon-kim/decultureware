#!/usr/bin/env python3
"""Generate the static home and app pages from apps.json and Apple image URLs."""
from html import escape as e
import re
from site_common import PUBLIC_DIR, ROOT, load_apps, load_screenshots, screenshot_urls, version_public_assets, theme_head


PURPOSES = {
    'Calendar': 'Plan my day',
    'Screen capture': 'Capture my screen',
    'Transit': 'Get around',
    'Fitness': 'Track workouts',
    'Food & habits': 'Plan meals',
    'Terminal': 'Work in a terminal',
    'Work & time': 'Log work hours',
}


def build():
 apps=load_apps()
 data=load_screenshots()
 def shots(a,device='iphone'):
  return screenshot_urls(a,data,device)
 def asset(url,base):return url if url.startswith('https://') else base+url
 def icon(a,base='',eager=False):
  # Apple's thumbnail service keeps small UI icons sharp without the 512px payload.
  url=re.sub(r'/\d+x\d+bb\.(png|jpg)$', r'/160x160bb.\1', a['icon']) if a['icon'].startswith('https://is1-ssl.mzstatic.com/') else a['icon']
  return f'<img class="app-icon" src="{e(asset(url,base))}" alt="" width="52" height="52" loading="{"eager" if eager else "lazy"}" decoding="async">' if a['icon'] else '<span class="app-icon banana-icon" aria-hidden="true">b.</span>'
 def dimensions(a,url=''):
  # Self-hosted screenshots declare their sizes; Mac App Store images are 800x500.
  for shot in a.get('screenshots',[]):
   if shot['src']==url:return f' width="{shot["width"]}" height="{shot["height"]}"'
  return ' width="800" height="500"' if a['platform']=='mac' else ''
 def platform(a):return 'Mac' if a['platform']=='mac' else ('iPhone & iPad' if a['slug']=='baytransit' else 'iPhone')
 def shell(title,description,body,base='',extra_head=''):
  return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(description)}">{theme_head(base)}<title>{e(title)} · Design Culture Software</title><link rel="preload" href="{base}assets/fonts/SUIT-Variable-v2.0.5.woff2" as="font" type="font/woff2" crossorigin><link rel="preconnect" href="https://is1-ssl.mzstatic.com"><link rel="stylesheet" href="{base}showroom.css"><script src="{base}showroom.js" defer></script>{extra_head}</head><body><a class="skip" href="#main">Skip to content</a><header class="header wrap"><a class="brand" href="{base}index.html" aria-label="Design Culture Software home"><span class="brand-mark">dcw.</span><span class="brand-name">Design Culture<br>Software</span></a><nav aria-label="Main navigation"><a href="{base}index.html#apps">The apps</a><a href="{base}index.html#studio">The studio</a><a class="contact-link" href="mailto:feedback@decultureware.com">Say hello <span aria-hidden="true">↗</span></a></nav></header>{body}<footer class="wrap footer"><a class="brand-mark" href="{base}index.html">dcw.</a><p>Small tools. Everyday possibilities.</p><span>© 2026 Design Culture Software</span><a href="https://findnshot.com/" target="_blank" rel="noopener noreferrer">FindnShot ↗</a><a href="https://totowakiki.com/" target="_blank" rel="noopener noreferrer">Toto &amp; Kiki ↗</a><a href="mailto:feedback@decultureware.com">Get in touch ↗</a></footer></body></html>'''
 def card(a):
  image=shots(a)[0]
  store_link=f'<a href="{e(a["url"])}" target="_blank" rel="noopener noreferrer" aria-label="Get {a["name"]} on the App Store">App Store ↗</a>' if a.get('url') else f'<a href="{e(a["download"])}" target="_blank" rel="noopener noreferrer" aria-label="Download {a["name"]} from GitHub">Download ↗</a>' if a.get('download') else '<span class="coming-soon">Coming soon</span>'
  return f'''<article class="app-card" id="{a['slug']}" data-platform="{a['platform']}" data-category="{e(a['category'])}"><a class="card-art {a['platform']}" style="--tint:{a['color']}" href="apps/{a['slug']}.html" aria-label="Explore {a['name']}"><span class="art-label">{a['category']}</span><img src="{e(image)}" alt="{a['name']} preview"{dimensions(a,image)} loading="lazy" decoding="async"><span class="art-arrow" aria-hidden="true">↗</span></a><div class="card-title">{icon(a)}<div><h3><a href="apps/{a['slug']}.html">{a['name']}</a></h3><span>{platform(a)}</span></div></div><p>{a['tagline']}</p><div class="card-links"><a href="apps/{a['slug']}.html">Explore app <span aria-hidden="true">↗</span></a>{store_link}</div></article>'''
 cards=''.join(card(a) for a in apps)
 categories={a['category'] for a in apps}
 purposes=''.join(f'<button type="button" data-filter-purpose="{e(category)}" aria-pressed="false">{label}</button>'
                  for category,label in PURPOSES.items() if category in categories)
 lens_words=' '.join(f'<span class="type-{word.lower()}">{word}</span>'
                     for word in ('DESIGN','CULTURE','SOFTWARE'))
 lens_assets='<link rel="stylesheet" href="type-lens.css"><script src="type-lens.js" defer></script>'
 body=f'''<main id="main">
  <section class="type-hero wrap">
    <div class="type-hero-content">
      <div class="type-lens" role="group" aria-label="Type lens">
        <h1 class="type-lens-words" lang="en">{lens_words}</h1>
        <div class="type-lens-words type-lens-alternate" lang="en" aria-hidden="true">{lens_words}</div>
        <span class="type-lens-rim" aria-hidden="true"></span>
      </div>
      <p>Independent apps for the things you do every day.</p>
    </div>
  </section>
  <section class="collection wrap" id="apps" tabindex="-1">
    <div class="section-heading">
      <div><p class="eyebrow">THE COLLECTION</p><h2>Find your everyday.</h2></div>
      <div class="filters" role="group" aria-label="Filter apps by platform" data-app-filters hidden>
        <button type="button" data-filter-platform="all" aria-pressed="true">All devices</button>
        <button type="button" data-filter-platform="mac" aria-pressed="false">Mac</button>
        <button type="button" data-filter-platform="mobile" aria-pressed="false">iPhone &amp; iPad</button>
      </div>
    </div>
    <div class="purpose-filters" role="group" aria-label="Filter apps by use" data-app-filters hidden>
      <span>I want to</span>
      <button type="button" data-filter-purpose="all" aria-pressed="true">Any use</button>{purposes}
    </div>
    <p class="sr-only" id="filter-status" aria-live="polite"></p>
    <div class="empty-apps" hidden><p>No apps match these filters.</p><button type="button" data-clear-filters>Clear filters</button></div>
    <div class="app-grid">{cards}</div>
  </section>
  <section class="banana-series wrap"><div><p class="eyebrow">THE BANANA SERIES</p><h2>Good company<br>for your Mac.</h2></div><div><p>One keeps your day in view.<br>One keeps the things worth saving.<br>One keeps your work running.</p><div class="series-links"><a href="apps/bananacal.html">BananaCal ↗</a><a href="apps/bananasnap.html">BananaSnap ↗</a><a href="apps/bananashell.html">bananaShell ↗</a></div></div><span class="series-decoration" aria-hidden="true">( b. )</span></section>
  <section class="studio wrap" id="studio"><p class="eyebrow">A NOTE FROM THE STUDIO</p><div><h2>Software that fits<br>into your day.</h2><p>Design Culture Software is an independent collection of apps for everyday life. A clearer calendar. An easier commute. A new way to see where you’ve been.</p><p>Small, focused tools, made with care.</p><a class="text-link" href="mailto:feedback@decultureware.com">Have a thought? Say hello ↗</a></div></section>
</main>'''
 (PUBLIC_DIR/'apps').mkdir(parents=True,exist_ok=True)
 (PUBLIC_DIR/'index.html').write_text(shell('Thoughtful apps for everyday life','Discover independent apps for Mac, iPhone, and iPad from Design Culture Software.',body,extra_head=lens_assets))
 for a in apps:
  gallery=''
  devices=['iphone']+(['ipad'] if shots(a,'ipad') else [])
  toggles=''.join(f'<button data-device="{d}" aria-pressed="{str(i==0).lower()}">{"Mac" if a["platform"]=="mac" else ("iPad" if d=="ipad" else "iPhone")}</button>' for i,d in enumerate(devices)) if len(devices)>1 else ''
  for i,d in enumerate(devices):
   images=''.join(f'<button class="screenshot" aria-label="Enlarge {a["name"]} screenshot {j+1}"><img src="{e(asset(url,"../"))}" alt="{a["name"]} screenshot {j+1}"{dimensions(a,url)} loading="lazy" decoding="async"></button>' for j,url in enumerate(shots(a,d)))
   gallery+=f'<div class="screenshots {a["platform"]}" data-gallery="{d}" {"hidden" if i else ""}>{images}</div>'
  features=''.join(f'<div><span>0{i+1}</span><h3>{e(f)}</h3></div>' for i,f in enumerate(a['features']))
  store_button=f'<a class="button" href="{e(a["url"])}" target="_blank" rel="noopener noreferrer">Download on {"Mac " if a["platform"]=="mac" else ""}App Store ↗</a>' if a.get('url') else f'<a class="button" href="{e(a["download"])}" target="_blank" rel="noopener noreferrer">Download for Mac ↗</a>' if a.get('download') else '<span class="button unavailable">Coming soon</span>'
  if a.get('install'):store_button+=f'<p class="install">Or install with Homebrew<code>{e(a["install"])}</code></p>'
  if a.get('source'):store_button+=f'<p><a class="text-link" href="{e(a["source"])}" target="_blank" rel="noopener noreferrer">Free and open source on GitHub ↗</a></p>'
  if a['slug']=='bananacal':store_button+='<p><a class="text-link" href="../bananacal/contact.html">Share feedback ↗</a></p>'
  body=f'''<main id="main" class="detail"><section class="wrap detail-hero"><a class="back" href="../index.html#apps">← All apps</a><div class="detail-intro"><div>{icon(a,'../',eager=True)}<p class="eyebrow">{a['category']} / {platform(a)}</p><h1>{a['name']}</h1><h2>{a['tagline']}</h2><p>{a['description']}</p>{store_button}</div><div class="detail-art {a['platform']}" style="--tint:{a['color']}"><img src="{e(asset(shots(a)[0],'../'))}" alt="{a['name']} app preview"{dimensions(a,shots(a)[0])} fetchpriority="high" decoding="async"></div></div></section><section class="wrap features">{features}</section><section class="wrap screenshot-section"><div class="section-heading"><h2>A closer look.</h2><div class="filters" role="group" aria-label="Screenshot device">{toggles}</div></div><p class="gallery-hint">Scroll to explore. Select a screenshot to take a closer look.</p>{gallery}</section><nav class="wrap support-links" aria-label="{a['name']} support"><a href="../{a['slug']}/contact.html">Contact & support ↗</a><a href="../{a['slug']}/privacy.html">Privacy policy ↗</a><a href="../{a['slug']}/terms.html">Terms & conditions ↗</a></nav></main><dialog class="lightbox" aria-label="Screenshot viewer"><button class="close" aria-label="Close screenshot">×</button><button class="previous" aria-label="Previous screenshot">←</button><img alt=""><button class="next" aria-label="Next screenshot">→</button><p class="image-count" aria-live="polite"></p></dialog>'''
  (PUBLIC_DIR/'apps'/f'{a["slug"]}.html').write_text(shell(a['name'],a['description'],body,'../'))
if __name__=='__main__':
 build()
 import runpy
 runpy.run_path(str(ROOT/'scripts/build-feedback.py'),run_name='__main__')
 runpy.run_path(str(ROOT/'scripts/localize-showroom.py'),run_name='__main__')
 version_public_assets()
