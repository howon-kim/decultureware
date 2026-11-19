#!/usr/bin/env python3
"""Build translated pages and link each page to its available language editions."""
import os
import re
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlencode, urlsplit

from site_common import ROOT, load_apps, read_json, relative

APPS = [app['slug'] for app in load_apps()]
SHOWROOM = [Path('index.html'), *(Path('apps', slug + '.html') for slug in APPS)]
FEEDBACK = Path('bananacal/contact.html')
SUPPORT = [Path(slug, name + '.html') for slug in APPS for name in ('contact', 'privacy', 'terms')]
PAGES = SHOWROOM + SUPPORT
EDITIONS = {'en': set(PAGES), 'ko': set(SHOWROOM + [FEEDBACK]), 'ja': set(PAGES)}
LANGUAGE_NAMES = {'en': 'EN', 'ko': '한국어', 'ja': '日本語'}
LANGUAGE_LABELS = {'en': 'Language', 'ko': '언어 선택', 'ja': '言語を選択'}

# Match complete generated labels so product names and placeholders keep their meaning.
LABELS = (
    'Enlarge {name} screenshot {number}', '{name} screenshot {number}', 'Explore {name}',
    'Get {name} on the App Store', 'Download {name} from GitHub',
    '{name} app preview', '{name} preview', '{name} support',
)
PATTERNS = {
    key: re.compile(re.escape(key).replace(r'\{name\}', '(?P<name>.+)')
                    .replace(r'\{number\}', r'(?P<number>\d+)')) for key in LABELS
}


def translated(text, catalog):
    if text in catalog:
        return catalog[text]
    stripped = text.strip()
    if stripped and stripped in catalog:
        return text.replace(stripped, catalog[stripped], 1)
    title, separator, brand = text.partition(' · ')
    if separator and brand == 'Design Culture Software':
        return catalog.get(title, title) + separator + brand
    category, separator, platform = text.partition(' / ')
    if separator and category in catalog:
        return catalog[category] + separator + platform
    for template, pattern in PATTERNS.items():
        match = pattern.fullmatch(text)
        if match:
            return catalog[template].format(**match.groupdict())
    return text


def location(page, lang):
    return page if lang == 'en' else Path(lang) / page


def strip_languages(document):
    document = re.sub(r'<span class="language-switch"[^>]*>.*?</span>(?=\s*</nav>)',
                      '', document, count=1, flags=re.S)
    return re.sub(r'<link rel="alternate" hreflang="(?:en|ko|ja|x-default)" href="[^"]*">', '', document)


def add_languages(document, page, lang):
    dest = location(page, lang)
    urls = {code: relative(location(page, code), dest)
            for code, pages in EDITIONS.items() if page in pages}
    anchors = []
    for code, url in urls.items():
        current = ' aria-current="page"' if code == lang else ''
        anchors.append(f'<a href="{url}" lang="{code}" hreflang="{code}"{current}>{LANGUAGE_NAMES[code]}</a>')
    links = '<span aria-hidden="true">/</span>'.join(anchors)
    switch = f'<span class="language-switch" role="group" aria-label="{LANGUAGE_LABELS[lang]}">{links}</span>'
    document = document.replace('</nav></header>', switch + '</nav></header>', 1)
    urls['x-default'] = urls['en']
    alternates = ''.join(f'<link rel="alternate" hreflang="{code}" href="{url}">' for code, url in urls.items())
    return document.replace('</head>', alternates + '</head>', 1)


class LocalizedHTML(HTMLParser):
    def __init__(self, page, lang, catalog):
        super().__init__()
        self.page = page
        self.lang = lang
        self.catalog = catalog
        self.output = []

    def url(self, value):
        url = urlsplit(value)
        if self.lang == 'ja' and url.scheme == 'mailto' and url.query:
            query = [(key, self.catalog.get(val, val) if key == 'subject' else val)
                     for key, val in parse_qsl(url.query, keep_blank_values=True)]
            return url._replace(query=urlencode(query, quote_via=quote)).geturl()
        if self.lang == 'ja' and url.netloc == 'apps.apple.com' and url.path.startswith('/us/'):
            return url._replace(path='/jp/' + url.path[4:]).geturl()
        if url.scheme or url.netloc or not url.path or url.path.startswith('/'):
            return value
        target = Path(os.path.normpath(self.page.parent / url.path))
        if target in EDITIONS[self.lang]:
            target = location(target, self.lang)
        return url._replace(path=relative(target, location(self.page, self.lang))).geturl()

    def handle_starttag(self, tag, attrs):
        values = []
        for key, value in attrs:
            if value is None:
                values.append(key)
                continue
            if key == 'lang' and tag == 'html':
                value = self.lang
            elif key in ('href', 'src'):
                value = self.url(value)
            elif key in ('alt', 'aria-label') or (key == 'content' and dict(attrs).get('name') == 'description'):
                value = translated(value, self.catalog)
            values.append(f'{key}="{escape(value, quote=True)}"')
        self.output.append('<' + ' '.join([tag, *values]) + '>')

    def handle_endtag(self, tag):
        self.output.append(f'</{tag}>')

    def handle_data(self, data):
        self.output.append(escape(translated(data, self.catalog), quote=False))

    def handle_decl(self, decl):
        self.output.append(f'<!{decl}>')

    def handle_comment(self, comment):
        self.output.append(f'<!--{comment}-->')


def build():
    korean = read_json(ROOT / 'locales/ko.json')
    japanese = read_json(ROOT / 'locales/ja.json')
    contact = japanese | read_json(ROOT / 'locales/ja-contact.json')
    policies = japanese | read_json(ROOT / 'locales/ja-policies.json')
    for page in PAGES:
        original = strip_languages((ROOT / page).read_text())
        for lang, pages in EDITIONS.items():
            if page not in pages:
                continue
            dest = ROOT / location(page, lang)
            if lang == 'en':
                document = original
            elif lang == 'ko' and page == FEEDBACK:
                # The Korean contact page has its own copy in build-feedback.py.
                document = strip_languages(dest.read_text())
            else:
                catalog = korean if lang == 'ko' else japanese
                if lang == 'ja' and page in SUPPORT:
                    catalog = contact if page.name == 'contact.html' else policies
                parser = LocalizedHTML(page, lang, catalog)
                parser.feed(original)
                parser.close()
                document = ''.join(parser.output)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(add_languages(document, page, lang))


if __name__ == '__main__':
    build()
