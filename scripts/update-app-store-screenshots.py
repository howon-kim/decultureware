#!/usr/bin/env python3
"""Refresh Apple-hosted screenshot URLs before deploying this static site.
Run: python3 scripts/update-app-store-screenshots.py
No image files are downloaded. Unavailable apps retain their current galleries.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen

from site_common import ROOT, load_apps, load_screenshots, save_screenshots


def catalog():
    """App Store IDs and platform already belong to apps.json."""
    return {app["slug"]: (app["id"], app["name"],
            "macSoftware" if app["platform"] == "mac" else "software")
            for app in load_apps() if app.get("id")}

def valid_urls(values):
    return [url for url in values if isinstance(url, str)
            and urlparse(url).scheme == "https"
            and (urlparse(url).hostname or "").endswith(".mzstatic.com")]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--country", default="us")
    parser.add_argument("--response", type=Path, action="append",
                        help="Use saved Apple lookup responses instead of network requests")
    args = parser.parse_args()
    app_catalog = catalog()
    apps = {}
    if args.response:
        payloads = [json.loads(path.read_text()) for path in args.response]
    else:
        payloads = []
        for entity in ("software", "macSoftware"):
            ids = ",".join(str(value[0]) for value in app_catalog.values() if value[2] == entity)
            url = "https://itunes.apple.com/lookup?" + urlencode(
                {"id": ids, "entity": entity, "country": args.country})
            with urlopen(url, timeout=30) as response:
                payloads.append(json.load(response))
    for payload in payloads:
        for app in payload["results"]:
            if "trackId" in app:
                apps[app["trackId"]] = app

    data = load_screenshots()
    for slug, (app_id, name, entity) in app_catalog.items():
        app = apps.get(app_id, {})
        urls = valid_urls(app.get("screenshotUrls", []))
        if not urls:
            print(f"{name}: unavailable; keeping existing screenshots")
            continue
        data.setdefault(slug, {})["iphone"] = urls
        ipad = valid_urls(app.get("ipadScreenshotUrls", []))
        if ipad:
            data[slug]["ipad"] = ipad
        print(f"{name}: {len(urls)} Apple-hosted screenshots")
    save_screenshots(data)

    import runpy
    runpy.run_path(str(ROOT / "scripts/build-showroom.py"), run_name="__main__")

if __name__ == "__main__":
    main()
