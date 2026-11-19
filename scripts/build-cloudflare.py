#!/usr/bin/env python3
"""Build public files only for Cloudflare Pages (Python standard library only)."""
import shutil
import subprocess
import sys

from site_common import PUBLIC_DIR, ROOT, load_apps

OUTPUT = ROOT / 'dist'
PUBLIC_FILES = ('index.html', '404.html', 'showroom.css', 'showroom.js', 'subpage.css',
                'theme.css', 'theme.js',
                'type-lens.css', 'type-lens.js', 'assets/fonts/DCW-Pixel-v1.woff2',
                'assets/type/culture-dancheong.webp',
                '_headers', 'assets/fonts/SUIT-Variable-v2.0.5.woff2',
                'assets/fonts/SUIT-LICENSE.txt')
PUBLIC_EXTENSIONS = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.webp', '.avif',
                     '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf'}


def build():
    subprocess.run([sys.executable, str(ROOT / 'scripts/build-showroom.py')], check=True)
    if OUTPUT.is_symlink():
        raise RuntimeError('dist must not be a symbolic link')
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()
    for name in PUBLIC_FILES:
        (OUTPUT / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PUBLIC_DIR / name, OUTPUT / name)
    for directory in ['apps', 'ko', 'ja', *(app['slug'] for app in load_apps())]:
        for source in (PUBLIC_DIR / directory).rglob('*'):
            relative = source.relative_to(PUBLIC_DIR)
            if (not source.is_file() or source.is_symlink()
                    or source.suffix.lower() not in PUBLIC_EXTENSIONS
                    or any(part.startswith('.') for part in relative.parts)):
                continue
            if source.stat().st_size > 25 * 1024 * 1024:
                raise RuntimeError(f'Cloudflare file size limit exceeded: {relative}')
            target = OUTPUT / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    files = [path for path in OUTPUT.rglob('*') if path.is_file()]
    if len(files) > 20_000:
        raise RuntimeError('Cloudflare file count limit exceeded')
    print(f'Built {len(files)} public files in dist; PHP, configuration and development files excluded.')


if __name__ == '__main__':
    build()
