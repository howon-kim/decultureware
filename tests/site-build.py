#!/usr/bin/env python3
"""Check generated links and repeatable builds in a temporary copy, without SMTP/network."""
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit, unquote
import hashlib
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get('id'):
            self.ids.add(values['id'])
        for key in ('href', 'src', 'action'):
            if values.get(key):
                self.links.append(values[key])


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
            target = ((root if url.path.startswith('/') else page.parent) /
                      unquote(url.path).lstrip('/')).resolve() if url.path else page
            if target.is_dir():
                target = target / 'index.html'
            if not target.exists():
                errors.append(f'{page.relative_to(root)} -> {link}')
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f'{page.relative_to(root)} -> missing anchor {link}')
    assert not errors, '\n'.join(errors)
    return len(pages)


with TemporaryDirectory(prefix='dcw-build-') as temp:
    root = Path(temp) / 'site'
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
    count = check_links(root)
    print(f'PASS: {count} HTML pages, local links/anchors, repeated build and localization.')
    run('build-cloudflare.py')
    output = root / 'dist'
    deployed_count = check_links(output)
    for private in ('api', 'config', 'scripts', 'tests', 'docs', '.git', '.htaccess', 'README.md'):
        assert not (output / private).exists(), f'Private file deployed: {private}'
    assert not list(output.rglob('*.php')), 'PHP source must never be deployed as a static asset'
    for contact in output.rglob('contact.html'):
        content = contact.read_text()
        assert 'mailto:feedback@decultureware.com' in content
        assert '<form' not in content and 'contactForm' not in content and 'api/feedback' not in content
    for page in output.rglob('*.html'):
        PublicPolicy().feed(page.read_text())
        parser = Links()
        parser.feed(page.read_text())
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme == 'mailto':
                assert url.path == 'feedback@decultureware.com', f'Old support address in {page}'
    assert (output / '404.html').exists(), 'Missing URLs must return a real 404'
    headers = (output / '_headers').read_text()
    assert "script-src 'self'" in headers and "frame-ancestors 'none'" in headers
    assert "form-action 'none'" in headers and 'X-Content-Type-Options: nosniff' in headers
    for css in output.rglob('*.css'):
        assert '@import' not in css.read_text(), 'Avoid serial stylesheet loading'
    font = output / 'assets/fonts/SUIT-Variable-v2.0.5.woff2'
    assert font.read_bytes()[:4] == b'wOF2', 'Missing or invalid local font'
    assert (font.parent / 'SUIT-LICENSE.txt').is_file(), 'Font license must ship with font'
    print(f'PASS: {deployed_count} deployable HTML pages, email contacts and private-file exclusions.')
    print('PASS: CSP-compatible markup, direct stylesheets and licensed local font.')
