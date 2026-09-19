# De Culture Ware website

Static responsive app showroom. No server-side runtime is required.

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

This fetches public US App Store image URLs and rebuilds the showroom. It does not download images. Unavailable apps keep their saved URLs; BananaSnap uses its existing local screenshots until available. Use `--country kr` to select another storefront. This command must run before deploying if screenshots need refreshing; it is not a scheduled or visitor-triggered update.

Deploy the generated HTML alongside the CSS, JavaScript, app support directories, and local fallback images. Building and previewing do not publish the site.

## Languages

English pages live at the root and in `apps/`; Korean pages live in `ko/` and `ko/apps/`. The page generator produces both versions, including reciprocal language links. Edit Korean copy in `locales/ko.json`, then run `python3 scripts/build-showroom.py`. Screenshot refreshes also rebuild both languages. Screenshots are shared; policy and support links retain their existing destinations.
