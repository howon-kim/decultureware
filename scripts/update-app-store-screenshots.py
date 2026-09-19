#!/usr/bin/env python3
"""Refresh Apple-hosted screenshot URLs before deploying this static site.
Run: python3 scripts/update-app-store-screenshots.py
No image files are downloaded. Unavailable apps retain their current galleries.
"""
import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
APPS = {
    "baytransit": (1644622451, "Bay Transit", "software"),
    "habitplate": (6753604162, "HabitPlate", "software"),
    "wyr": (6754036352, "Where You Run", "software"),
    "workone": (6502869186, "WorkOne", "software"),
    "bananacal": (6759227522, "BananaCal", "macSoftware"),
    "bananasnap": (6812689057, "BananaSnap", "macSoftware"),
}

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
    apps = {}
    if args.response:
        payloads = [json.loads(path.read_text()) for path in args.response]
    else:
        payloads = []
        for entity in ("software", "macSoftware"):
            ids = ",".join(str(value[0]) for value in APPS.values() if value[2] == entity)
            url = "https://itunes.apple.com/lookup?" + urlencode(
                {"id": ids, "entity": entity, "country": args.country})
            with urlopen(url, timeout=30) as response:
                payloads.append(json.load(response))
    for payload in payloads:
        for app in payload["results"]:
            if "trackId" in app:
                apps[app["trackId"]] = app

    data_path = ROOT / "app-store-screenshots.js"
    prefix = "window.appStoreScreenshots = "
    data = json.loads(data_path.read_text().removeprefix(prefix).strip().rstrip(";")) if data_path.exists() else {}
    for slug, (app_id, name, entity) in APPS.items():
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
    data_path.write_text(prefix + json.dumps(data, indent=2) + ";\n")

    import runpy
    runpy.run_path(str(ROOT / "scripts/build-showroom.py"), run_name="__main__")

if __name__ == "__main__":
    main()
