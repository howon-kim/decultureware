# Design Culture Software website

Static responsive app showroom hosted on Cloudflare Pages. Support uses email links; no PHP or SMTP runtime is required for the website.

- `apps.json`: app copy, platforms, colors, icons, and store links.
- `app-store-screenshots.js`: Apple-hosted screenshot URLs.
- `scripts/build-showroom.py`: generates `index.html` and `apps/*.html`.
- `showroom.css` / `showroom.js`: homepage and product-page styling and interactions.
- Existing app directories retain their privacy, terms, and support pages.

## Edit and preview

After editing app information:

```sh
python3 scripts/build-showroom.py
python3 -m http.server 18766 --bind 127.0.0.1
```

Open http://127.0.0.1:18766.

## Refresh App Store screenshots

```sh
python3 scripts/update-app-store-screenshots.py
```

This fetches public US App Store image URLs and rebuilds the showroom. It does not download images. Unavailable apps keep their saved URLs; local BananaSnap images remain as fallback assets. Use `--country kr` to select another storefront. This command must run before deploying if screenshots need refreshing; it is not a scheduled or visitor-triggered update.

Deploy the generated HTML alongside the CSS, JavaScript, app support directories, and local fallback images. Building and previewing do not publish the site.

## Languages

English pages live at the root and in `apps/`; Korean pages live in `ko/` and `ko/apps/`. The page generator produces both versions, including reciprocal language links. Edit Korean copy in `locales/ko.json`, then run `python3 scripts/build-showroom.py`. Screenshot refreshes also rebuild both languages. Screenshots are shared; policy and support links retain their existing destinations.

## Cloudflare Pages deployment

Connect the GitHub repository `howon-kim/decultureware` with these settings:

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Framework preset | None |
| Build command | `python3 scripts/build-cloudflare.py` |
| Build output directory | `dist` |
| Root directory | Repository root |

The build regenerates the English/Korean pages and copies only public HTML,
styles, browser JavaScript, and images to `dist/`. PHP, configuration, tests,
development scripts, documentation, and Git files are excluded. Do not publish
the repository root: Cloudflare does not apply Apache `.htaccess` rules.
The root `404.html` keeps missing URLs from falling back to the homepage.

`_headers` supplies the Content Security Policy, frame blocking, HTTPS persistence,
and browser permission restrictions. Scripts and fonts load from this site; images
may also load from Apple's image CDN. Inline CSS remains allowed for app colors.
The HTTPS policy applies only to the current hostname, not mail or other subdomains.
Deployment URLs are marked `noindex` so the custom domain is the searchable copy.

SUIT Variable 2.0.5 is self-hosted under `assets/fonts/` with its SIL Open Font
License, from the [official distribution](https://github.com/sun-typeface/SUIT/tree/2.0.5).
Keep the license with the font. The versioned font is preloaded, uses `font-display:
swap`, and has a one-year browser cache; change the filename and references when
updating it. Both common stylesheets are linked directly, without chained imports.
App icons request 160px Apple thumbnails; Mac screenshots reserve their 8:5 space
before loading. Cloudflare's revalidation policy stays in place for HTML/CSS/JS.

Push updates to `main` to trigger a new deployment. The build uses saved App Store
image URLs; run the screenshot refresh locally and commit its output when needed.

To inspect the exact deployable files locally:

```sh
python3 scripts/build-cloudflare.py
python3 -m http.server 18766 --bind 127.0.0.1 --directory dist
```

## Email support

All app contact pages link directly to `feedback@decultureware.com`, with the app
name in the email subject. Visitors write and send the message in their email
app; the website has no contact forms. Navigation, privacy policies, and terms
use the same support address. `scripts/build-feedback.py` generates BananaCal's
English/Korean contact pages; other app contact pages are maintained as HTML.

The earlier PHP feedback implementation and [Synology setup](INSTALL-SYNOLOGY.md)
remain in the repository for reference but are not deployed to Cloudflare.
Website migration does not move the existing email inbox or its mail service.

## Maintenance

- `scripts/site_common.py`: shared app catalog, screenshot data and relative paths.
- `scripts/build-cloudflare.py`: public-file allowlist and Cloudflare output.
- `api/feedback.php`: retained legacy endpoint; `api/feedback/` contains configuration,
  validation, submission limits/idempotency, and SMTP delivery separately.
- `config/feedback.example.php`: placeholder configuration, never real credentials.
- `tests/`: build/link checks and feedback regression tests.
- [Refactoring guide](docs/REFACTORING.md): boundaries and cleanup decisions.

Website validation (no network or email):

```sh
python3 tests/site-build.py
```

Legacy feedback checks are `node tests/feedback-client.mjs` and
`php tests/feedback.php` (PHP 8.2+), only needed when changing that implementation.
Keep generated HTML and existing support URLs in Git. `dist/` is regenerated by
Cloudflare and is ignored locally.
