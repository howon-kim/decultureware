"""Shared build inputs and URL helpers; never required by the web server."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "app-store-screenshots.js"
SCREENSHOT_PREFIX = "window.appStoreScreenshots = "


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_apps():
    return read_json(ROOT / "apps.json")


def load_screenshots():
    if not SCREENSHOTS.exists():
        return {}
    return json.loads(SCREENSHOTS.read_text(encoding="utf-8")
                      .removeprefix(SCREENSHOT_PREFIX).strip().rstrip(";"))


def save_screenshots(data):
    SCREENSHOTS.write_text(SCREENSHOT_PREFIX + json.dumps(data, indent=2) + ";\n", encoding="utf-8")


def screenshot_urls(app, data, device="iphone"):
    urls = data.get(app["slug"], {}).get(device, [])
    if not urls and device == "iphone" and app.get("preview"):
        urls = [app["preview"]]
    if not urls and device == "iphone" and app["slug"] == "bananasnap":
        urls = ["bananasnap/images/" + name + "-2880x1800.png"
                for name in ["02-snapshot", "03-preview", "04-library"]]
    return urls


def relative(target, source):
    return Path(os.path.relpath(target, source.parent)).as_posix()
