#!/usr/bin/env python3
"""Check generated links and repeatable builds in a temporary copy, without SMTP/network."""
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit, unquote, parse_qs
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.lang = None
        self.alternates = []
        self.page_links = []
        self.language_links = []
        self.named_link = None
        self.in_nav = False
        self.switch_tag = None
        self.switch_depth = 0
        self.in_head = False
        self.redirect = False
        self.head_assets = {'script': [], 'stylesheet': []}

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'html':
            self.lang = values.get('lang')
        if tag == 'nav':
            self.in_nav = True
        if self.in_nav and 'language-switch' in values.get('class', '').split():
            self.switch_tag = tag
        if tag == self.switch_tag:
            self.switch_depth += 1
        if tag == 'a' and values.get('href'):
            if self.switch_depth:
                self.language_links.append(values)
            else:
                self.page_links.append(values)
                if values.get('lang'):
                    self.named_link = values
                    self.named_link['text'] = ''
        if tag == 'head':
            self.in_head = True
        if self.in_head:
            if tag == 'script' and values.get('src'):
                self.head_assets['script'].append(urlsplit(values['src']))
            if tag == 'link' and values.get('rel') == 'stylesheet':
                self.head_assets['stylesheet'].append(urlsplit(values['href']))
            if tag == 'link' and values.get('rel') == 'alternate' and 'hreflang' in values:
                self.alternates.append(values)
            if tag == 'meta' and values.get('http-equiv', '').lower() == 'refresh':
                self.redirect = True
        if values.get('id'):
            self.ids.add(values['id'])
        for key in ('href', 'src', 'action'):
            if values.get(key):
                self.links.append(values[key])

    def handle_data(self, text):
        if self.named_link is not None:
            self.named_link['text'] += text

    def handle_endtag(self, tag):
        if tag == 'a':
            self.named_link = None
        if tag == self.switch_tag:
            self.switch_depth -= 1
            if not self.switch_depth:
                self.switch_tag = None
        if tag == 'nav':
            self.in_nav = False
        if tag == 'head':
            self.in_head = False


class HomeHero(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self.in_heading = False
        self.in_hero = False
        self.in_main_nav = False
        self.nav_app_link = False
        self.filters = {'platform': [], 'purpose': []}
        self.cards = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        classes = values.get('class', '').split()
        if 'type-hero' in classes:
            self.in_hero = True
        if tag == 'nav':
            self.in_main_nav = values.get('aria-label') in ('Main navigation', '주 메뉴', 'メインナビゲーション')
        if tag == 'button':
            for kind, items in self.filters.items():
                value = values.get('data-filter-' + kind)
                if value is not None:
                    items.append(value)
                    assert values.get('aria-pressed') == ('true' if value == 'all' else 'false')
        if 'app-card' in classes:
            self.cards.append((values.get('id'), values.get('data-platform'), values.get('data-category')))
        if tag == 'a' and urlsplit(values.get('href', '')).fragment == 'apps':
            assert not self.in_hero, 'Unexpected app collection CTA in the hero'
            if self.in_main_nav:
                self.nav_app_link = True
        if tag == 'h1':
            assert self.in_hero and values.get('role', 'heading') == 'heading'
            assert values.get('lang') == 'en', 'Brand wordmark must be pronounced in English'
            self.headings.append([])
            self.in_heading = True
        if self.in_heading or 'type-lens' in classes or 'type-hero' in classes:
            assert values.get('aria-hidden') != 'true' and 'hidden' not in values
        if 'type-lens-alternate' in classes:
            assert values.get('aria-hidden') == 'true', 'Screen readers must skip duplicate lens text'
            assert values.get('lang') == 'en'
        if self.in_hero:
            assert tag != 'figcaption', 'Unexpected lens caption'

    def handle_data(self, data):
        if self.in_heading:
            self.headings[-1].extend(data.split())

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_heading = False
        if tag == 'section':
            self.in_hero = False
        if tag == 'nav':
            self.in_main_nav = False


class PublicPolicy(HTMLParser):
    """Catch new markup that would be blocked by the deployed security policy."""
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        assert not any(key.startswith('on') for key in values), 'Inline event handler'
        if tag == 'script':
            assert values.get('src'), 'Inline script blocked by CSP'
            assert not urlsplit(values['src']).scheme and not urlsplit(values['src']).netloc
        if tag == 'form':
            raise AssertionError('Public forms are disabled; use email support')
        if tag == 'img' and values.get('src'):
            url = urlsplit(values['src'])
            if url.scheme or url.netloc:
                assert url.scheme == 'https' and url.hostname.endswith('.mzstatic.com')
        if tag == 'link' and values.get('rel') in ('stylesheet', 'preload'):
            url = urlsplit(values.get('href', ''))
            assert not url.scheme and not url.netloc, 'Style/font must be self-hosted'
        for key in ('href', 'src', 'action'):
            assert not values.get(key, '').lower().startswith(('javascript:', 'http:'))


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*.html')}


def local_target(root, page, url):
    if not url.path:
        return page
    path = unquote(url.path)
    target = ((root if path.startswith('/') else page.parent) / path.lstrip('/')).resolve()
    return target / 'index.html' if target.is_dir() else target


def check_links(root):
    pages = {}
    for path in root.rglob('*.html'):
        parser = Links()
        parser.feed(path.read_text(encoding='utf-8'))
        pages[path.resolve()] = parser
    errors = []
    for page, parser in pages.items():
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = local_target(root, page, url)
            if not target.exists():
                errors.append(f'{page.relative_to(root)} -> {link}')
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f'{page.relative_to(root)} -> missing anchor {link}')
    assert not errors, '\n'.join(errors)
    return pages


def check_locale_families(root, pages, catalog):
    showroom = {Path('index.html'), *(Path('apps') / (app['slug'] + '.html') for app in catalog)}
    supports = {Path(app['slug']) / (kind + '.html') for app in catalog
                for kind in ('contact', 'privacy', 'terms')}
    korean = showroom | {Path('bananacal/contact.html')}
    families = {}
    for path in showroom | supports:
        family = {'en': root / path, 'ja': root / 'ja' / path}
        if path in korean:
            family['ko'] = root / 'ko' / path
        for lang, page in family.items():
            assert page in pages, f'Missing deployed {lang} translation of {path}'
            families[page] = (lang, family)

    for page, (lang, family) in families.items():
        html = pages[page]
        assert html.lang == lang, f'Wrong html lang on {page}'
        alternates = {**family, 'x-default': family['en']}
        for links, expected in ((html.alternates, alternates), (html.language_links, family)):
            found = {}
            for link in links:
                code = link.get('hreflang')
                assert code not in found, f'Duplicate hreflang={code} on {page}'
                url = urlsplit(link['href'])
                assert not (url.scheme or url.netloc or url.query or url.fragment), link
                found[code] = local_target(root, page, url)
            assert found == expected, f'Wrong language counterparts on {page}: {found} != {expected}'
        for link in html.language_links:
            current = link.get('aria-current')
            if link['hreflang'] == lang:
                assert current == 'page', f'Current language missing on {page}'
            else:
                assert current in (None, 'false'), f'Incorrect current language on {page}'
        for link in html.page_links:
            href = link['href']
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            target = local_target(root, page, url)
            if target in families:
                target_lang, target_family = families[target]
                if link.get('lang') == target_lang and (link.get('aria-label') or link.get('text', '')).strip():
                    continue
                assert target == target_family.get(lang, target_family['en']), f'{page} changes language at {href}'

    not_found = pages[root / '404.html']
    links = not_found.page_links + not_found.language_links
    assert any(link['href'] in ('/ja/', '/ja/index.html') for link in links), (
        '404 must link to the Japanese home from arbitrary missing URLs')


with TemporaryDirectory(prefix='dcw-build-') as temp:
    root = Path(temp).resolve() / 'site'
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(
        '.git', '.claude', '__pycache__', '.DS_Store', 'deploy', 'dist', '.env*', 'feedback.local.php'))
    def run(script):
        subprocess.run([sys.executable, str(root / 'scripts' / script)], check=True)
    run('build-showroom.py')
    first = snapshot(root)
    run('build-showroom.py')
    assert snapshot(root) == first, 'Full build must be repeatable'
    run('localize-showroom.py')
    assert snapshot(root) == first, 'Standalone localization must be repeatable'
    count = len(check_links(root))
    print(f'PASS: {count} HTML pages, local links/anchors, repeated build and localization.')
    run('build-cloudflare.py')
    output = root / 'dist'
    pages = check_links(output)
    catalog = json.loads((root / 'apps.json').read_text())
    check_locale_families(output, pages, catalog)
    for private in ('api', 'config', 'scripts', 'tests', 'docs', '.git', '.htaccess', 'README.md'):
        assert not (output / private).exists(), f'Private file deployed: {private}'
    assert not list(output.rglob('*.php')), 'PHP source must never be deployed as a static asset'
    for contact in output.rglob('contact.html'):
        content = contact.read_text()
        assert 'mailto:feedback@decultureware.com' in content
        assert '<form' not in content and 'contactForm' not in content and 'api/feedback' not in content
    for page, parser in pages.items():
        content = page.read_text()
        PublicPolicy().feed(content)
        if page.relative_to(output).as_posix() in ('index.html', 'ko/index.html', 'ja/index.html'):
            hero = HomeHero()
            hero.feed(content)
            assert hero.headings == [['DESIGN', 'CULTURE', 'SOFTWARE']], f'Unexpected homepage title: {page}'
            assert hero.nav_app_link and 'apps' in parser.ids, f'Missing main navigation link to apps: {page}'
            assert all(text not in content for text in ('type-lens-hint', 'Drag the lens', '렌즈를 끌거나'))
            assert sorted(hero.cards) == sorted((app['slug'], app['platform'], app['category']) for app in catalog), (
                f'App filter data must match the catalog on {page}')
            for kind, key in [('platform', 'platform'), ('purpose', 'category')]:
                expected = {'all', *(app[key] for app in catalog)}
                assert sorted(hero.filters[kind]) == sorted(expected), f'Invalid {kind} filters on {page}'
        if not parser.redirect:
            for kind, name in [('stylesheet', 'theme.css'), ('script', 'theme.js')]:
                matches = [url for url in parser.head_assets[kind] if Path(url.path).name == name]
                assert len(matches) == 1, f'Expected one {name} in the head of {page}'
                if page == output / '404.html':
                    assert matches[0].path == '/' + name, f'404 needs root-relative {name}'
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme == 'mailto':
                assert url.path == 'feedback@decultureware.com', f'Old support address in {page}'
            if not url.scheme and not url.netloc and Path(url.path).name in ('showroom.css', 'subpage.css', 'showroom.js', 'type-lens.css', 'type-lens.js', 'theme.css', 'theme.js'):
                target = ((output if url.path.startswith('/') else page.parent) / url.path.lstrip('/')).resolve()
                version = hashlib.sha256(target.read_bytes()).hexdigest()[:12]
                assert parse_qs(url.query).get('v') == [version], f'Stale asset URL in {page}'
    assert (output / '404.html').exists(), 'Missing URLs must return a real 404'
    headers = (output / '_headers').read_text()
    assert "script-src 'self'" in headers and "frame-ancestors 'none'" in headers
    assert "form-action 'none'" in headers and 'X-Content-Type-Options: nosniff' in headers
    for css in output.rglob('*.css'):
        assert '@import' not in css.read_text(), 'Avoid serial stylesheet loading'
    font = output / 'assets/fonts/SUIT-Variable-v2.0.5.woff2'
    assert font.read_bytes()[:4] == b'wOF2', 'Missing or invalid local font'
    assert (font.parent / 'SUIT-LICENSE.txt').is_file(), 'Font license must ship with font'
    assert (font.parent / 'DCW-Pixel-v1.woff2').read_bytes()[:4] == b'wOF2', 'Missing type lens pixel font'
    lens_css = (output / 'type-lens.css').read_text()
    urls = [urlsplit(value) for value in re.findall(r"""url\(\s*['"]?([^'")\s]+)""", lens_css)]
    local_assets = {Path(url.path.lstrip('/')) for url in urls if not url.scheme and not url.netloc}
    artwork = Path('assets/type/culture-dancheong.webp')
    assert artwork in local_assets, f'Lens CSS must reference {artwork}'
    data = (output / artwork).read_bytes()
    assert data[:4] == b'RIFF' and data[8:12] == b'WEBP' and data[12:16] in (b'VP8 ', b'VP8L', b'VP8X'), f'Invalid WebP header: {artwork}'
    assert int.from_bytes(data[4:8], 'little') == len(data) - 8, f'Incomplete WebP: {artwork}'
    print(f'PASS: {len(pages)} deployable HTML pages, email contacts and private-file exclusions.')
    print('PASS: EN/KO/JA locale counterparts, localized navigation, homepage wordmarks and filter identifiers.')
    print('PASS: CSP-compatible markup, direct stylesheets and licensed local font.')
