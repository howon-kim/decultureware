# Design Culture Software website

A static app showroom in English, Korean and Japanese, hosted on Cloudflare Pages.

| Directory | Contents |
| --- | --- |
| `public/` | Website HTML, stylesheets, browser scripts, fonts, per-app images and `_headers` |
| `content/` | The app catalog in `apps.json`, saved App Store image URLs in `app-store-screenshots.js`, and translations in `locales/` |
| `scripts/` | Python scripts for page generation, localization, screenshot refreshes and the deployment build |
| `dist/` | Generated Cloudflare Pages deployment output |

## Edit and preview

Edit app descriptions, platforms and store links in `content/apps.json`. Run these commands from the repository root and open [the local preview](http://127.0.0.1:18766/).

```sh
python3 scripts/build-showroom.py
python3 -m http.server 18766 --bind 127.0.0.1 --directory public
```

The generator writes the English homepage to `public/index.html`, its translations to `public/ko/` and `public/ja/`, and product pages to each language's `apps/` directory. The public URLs remain `/`, `/ko/` and `/ja/`. Commit changes to the content and regenerated public pages together.

## Languages and support

Korean showroom copy lives in `content/locales/ko.json`. Japanese showroom, support and policy translations live in `content/locales/ja.json`, `content/locales/ja-contact.json` and `content/locales/ja-policies.json`. Rebuild the showroom after editing translations to update the pages and language links.

English support and policy pages live under `public/<app>/`. The localizer uses the English sources to generate the Japanese pages under `public/ja/<app>/`. `scripts/build-feedback.py` generates BananaCal's English and Korean contact pages. Contact links open the visitor's email app with `feedback@decultureware.com` and the product name in the subject.

## Refresh App Store screenshots

```sh
python3 scripts/update-app-store-screenshots.py
```

The refresh saves public App Store image URLs in `content/app-store-screenshots.js` and rebuilds the showroom. The default storefront is the US. Pass `--country kr` for South Korea. Unavailable apps keep their saved URLs. BananaSnap's local fallback screenshots live in `public/bananasnap/images/`.

## Cloudflare Pages deployment

| Setting | Value |
| --- | --- |
| Repository | `howon-kim/decultureware` |
| Production branch | `main` |
| Framework preset | None |
| Build command | `python3 scripts/build-cloudflare.py` |
| Build output directory | `dist` |
| Root directory | Repository root |

Pushing to `main` triggers a production deployment. The build regenerates the localized pages and packages the public site in `dist/`. To preview the deployment output locally, run the following commands.

```sh
python3 scripts/build-cloudflare.py
python3 -m http.server 18766 --bind 127.0.0.1 --directory dist
```

`public/404.html` handles missing URLs. `public/_headers` sets the Content Security Policy, HTTPS and browser permission policies, cache rules, and search indexing restrictions for Cloudflare deployment URLs. The site serves scripts and fonts locally and loads App Store images from Apple's CDN.

Stylesheet and script URLs include content hashes so returning visitors receive updated assets. The self-hosted SUIT font has a versioned filename and a one-year cache lifetime. When updating it, update its references and keep its SIL Open Font License in `public/assets/fonts/`. [Official SUIT distribution](https://github.com/sun-typeface/SUIT/tree/2.0.5)

`dist/` is regenerated on each build and ignored by Git.
