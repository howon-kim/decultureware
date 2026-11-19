"""Shared build inputs and URL helpers; never required by the web server."""
import json
import os
import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
CONTENT_DIR = ROOT / "content"
SCREENSHOTS = CONTENT_DIR / "app-store-screenshots.js"
SCREENSHOT_PREFIX = "window.appStoreScreenshots = "


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_apps():
    return read_json(CONTENT_DIR / "apps.json")


def load_screenshots():
    if not SCREENSHOTS.exists():
        return {}
    return json.loads(SCREENSHOTS.read_text(encoding="utf-8")
                      .removeprefix(SCREENSHOT_PREFIX).strip().rstrip(";"))


def save_screenshots(data):
    SCREENSHOTS.write_text(SCREENSHOT_PREFIX + json.dumps(data, indent=2) + ";\n", encoding="utf-8")


def screenshot_urls(app, data, device="iphone"):
    urls = data.get(app["slug"], {}).get(device, [])
    if not urls and device == "iphone" and app.get("screenshots"):
        # Apps outside the App Store ship their own images with known sizes.
        urls = [shot["src"] for shot in app["screenshots"]]
    if not urls and device == "iphone" and app.get("preview"):
        urls = [app["preview"]]
    if not urls and device == "iphone" and app["slug"] == "bananasnap":
        urls = ["bananasnap/images/" + name + "-2880x1800.png"
                for name in ["02-snapshot", "03-preview", "04-library"]]
    return urls


def relative(target, source):
    return Path(os.path.relpath(target, source.parent)).as_posix()


def theme_head(base):
    return ('<meta name="color-scheme" content="light dark">'
            '<meta name="theme-color" media="(prefers-color-scheme: light)" content="#f7f6f2">'
            '<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#191c19">'
            f'<script src="{base}theme.js"></script><link rel="stylesheet" href="{base}theme.css">')


def version_public_assets():
    """Changing CSS/JS changes its URL, including for browsers with an old cache."""
    versions = {name: hashlib.sha256((PUBLIC_DIR / name).read_bytes()).hexdigest()[:12]
                for name in ('showroom.css', 'subpage.css', 'showroom.js', 'type-lens.css', 'type-lens.js',
                             'theme.css', 'theme.js')}

    def replace(match):
        attr, value = match.groups()
        url = urlsplit(value)
        name = Path(url.path).name
        if url.scheme or url.netloc or name not in versions:
            return match.group()
        value = urlunsplit(('', '', url.path, 'v=' + versions[name], url.fragment))
        return f'{attr}="{value}"'

    pages = [PUBLIC_DIR / 'index.html', PUBLIC_DIR / '404.html']
    for directory in ['apps', 'ko', 'ja', *(app['slug'] for app in load_apps())]:
        pages.extend((PUBLIC_DIR / directory).rglob('*.html'))
    for page in pages:
        page.write_text(re.sub(r'(href|src)="([^"]+)"', replace, page.read_text()))
