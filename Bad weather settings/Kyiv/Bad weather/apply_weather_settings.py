#!/usr/bin/env python3
"""
Bolt Admin Panel — Weather Settings Automation

Applies Bad Weather or Harsh Weather settings to a city's courier config.

Two modes:
  1. Offline:  reads CSV + current JSON file → outputs modified JSON file
  2. Browser:  reads CSV, opens admin panel via Selenium, applies changes, clicks Update

Usage examples:
  # Offline — generate a JSON file with bad weather values
  python apply_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kyiv (1).csv" \
      --json "Bad Weather Settings Kyiv.json" --weather bad

  # Offline — harsh weather
  python apply_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kyiv (1).csv" \
      --json "Bad Weather Settings Kyiv.json" --weather harsh

  # Browser automation — opens a fresh Chrome, apply bad weather to admin panel
  python apply_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kyiv (1).csv" \
      --url https://admin-panel.bolt.eu/delivery-courier/settings/city/158 --weather bad

  # Attach to your already-running Chrome (keeps SSL certs & session):
  #   1. Quit Chrome, relaunch with:
  #        /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
  #   2. Then run:
  python apply_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kyiv (1).csv" \
      --url https://admin-panel.bolt.eu/delivery-courier/settings/city/158 --weather bad --debug-port 9222
"""

import csv
import json
import sys
import time
import argparse
from pathlib import Path

# ── CSV column indices (0-based) ─────────────────────────────────────────────
COL_PATH = 2            # full setting path, e.g. "batching/food/max_delay_seconds"
COL_CURRENT = 5         # current value in the admin panel
COL_PROPOSED = 6        # proposed "normal" value
COL_BAD_WEATHER = 8     # bad weather value
COL_HARSH_WEATHER = 10  # harsh weather value

WEATHER_COL = {
    "bad": COL_BAD_WEATHER,
    "harsh": COL_HARSH_WEATHER,
    "proposed": COL_PROPOSED,
}


# ── CSV parsing ──────────────────────────────────────────────────────────────
def parse_csv(csv_path: str) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    settings = []
    for row in rows:
        if len(row) <= COL_HARSH_WEATHER:
            continue
        path = row[COL_PATH].strip()
        if not path or "/" not in path:
            continue

        settings.append({
            "path": path,
            "current": row[COL_CURRENT].strip(),
            "proposed": row[COL_PROPOSED].strip(),
            "bad": row[COL_BAD_WEATHER].strip(),
            "harsh": row[COL_HARSH_WEATHER].strip(),
        })
    return settings


def coerce(value_str: str):
    """Convert a CSV string to the matching Python/JSON type."""
    if not value_str or value_str.startswith("default"):
        return None
    s = value_str.strip()
    if s.upper() == "TRUE":
        return True
    if s.upper() == "FALSE":
        return False
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


# ── JSON manipulation ────────────────────────────────────────────────────────
def set_nested(obj: dict, keys: list[str], value) -> bool:
    for k in keys[:-1]:
        if k not in obj or not isinstance(obj[k], dict):
            return False
        obj = obj[k]
    if keys[-1] in obj:
        obj[keys[-1]] = value
        return True
    return False


def get_nested(obj: dict, keys: list[str]):
    for k in keys:
        if not isinstance(obj, dict) or k not in obj:
            return "<missing>"
        obj = obj[k]
    return obj


COURIER_SURGE_OVERRIDES = {
    "batching/disable_second_batched_order_auto_acceptance": True,
    "dynamic_multiplier/courier_earning/is_enabled": False,
    "dynamic_multiplier/courier_earning/is_generation_enabled": False,
    "dynamic_multiplier/courier_earning/notification_settings/is_enabled": False,
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 400,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 400,
}


def apply_weather(json_data: dict, settings: list[dict], profile: str):
    """Apply a weather profile to json_data in-place. Returns (changes, skipped)."""
    changes, skipped = [], []

    for s in settings:
        target_str = s[profile]
        target = coerce(target_str)
        if target is None:
            skipped.append((s["path"], "default / empty"))
            continue

        if s["path"] in COURIER_SURGE_OVERRIDES:
            target = COURIER_SURGE_OVERRIDES[s["path"]]

        keys = s["path"].split("/")
        old = get_nested(json_data, keys)

        if old == "<missing>":
            skipped.append((s["path"], "not found in JSON"))
            continue
        if old == target:
            skipped.append((s["path"], f"already {target}"))
            continue

        set_nested(json_data, keys, target)
        changes.append((s["path"], old, target))

    return changes, skipped


def print_report(changes, skipped, profile):
    label = {"bad": "Bad Weather", "harsh": "Harsh Weather", "proposed": "Proposed"}[profile]
    print(f"\n{'='*60}")
    print(f"  {label} Settings — {len(changes)} change(s) applied")
    print(f"{'='*60}")
    if changes:
        path_w = max(len(c[0]) for c in changes)
        for path, old, new in changes:
            print(f"  {path:<{path_w}}  {old} -> {new}")
    if skipped:
        print(f"\n  Skipped ({len(skipped)}):")
        for path, reason in skipped:
            print(f"    {path}: {reason}")
    print()


# ── Offline mode ─────────────────────────────────────────────────────────────
def offline(csv_path, json_path, output_path, profile):
    settings = parse_csv(csv_path)
    with open(json_path) as f:
        data = json.load(f)

    changes, skipped = apply_weather(data, settings, profile)
    print_report(changes, skipped, profile)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved to: {output_path}\n")


# ── Browser automation mode ──────────────────────────────────────────────────
def _make_driver(debug_port):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    # Strategy 1: attach to an already-running Chrome via remote debugging
    if debug_port:
        opts = Options()
        opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        return webdriver.Chrome(options=opts)

    # Strategy 2: launch a fresh Chrome (separate profile so it won't
    # conflict with the user's main Chrome that is already running)
    tmp_profile = Path.home() / ".chrome_selenium_profile"
    tmp_profile.mkdir(exist_ok=True)
    opts = Options()
    opts.add_argument(f"--user-data-dir={tmp_profile}")
    opts.add_argument("--profile-directory=AutomationProfile")
    return webdriver.Chrome(options=opts)


def browser(csv_path, url, profile, debug_port=None):
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        sys.exit("Selenium is required for browser mode.  pip install selenium")

    settings = parse_csv(csv_path)

    print(f"  Opening {url} ...")
    driver = _make_driver(debug_port)

    if not debug_port:
        driver.get(url)
        print("  Waiting for the page to load (log in if prompted) ...")
    else:
        driver.get(url)

    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".jsoneditor"))
    )
    time.sleep(2)

    # Switch to Code view
    driver.find_element(By.CSS_SELECTOR, "button.jsoneditor-modes").click()
    time.sleep(0.5)
    for el in driver.find_elements(By.CSS_SELECTOR, ".jsoneditor-type-modes div"):
        if el.text.strip() == "Code":
            el.click()
            break
    time.sleep(1)

    raw = driver.execute_script(
        "return ace.edit(document.querySelector('.ace_editor')).getValue();"
    )
    data = json.loads(raw)

    changes, skipped = apply_weather(data, settings, profile)
    print_report(changes, skipped, profile)

    if not changes:
        print("  Nothing to update — closing browser.")
        if not debug_port:
            driver.quit()
        return

    driver.execute_script(
        "ace.edit(document.querySelector('.ace_editor')).setValue(arguments[0], -1);",
        json.dumps(data, indent=2),
    )
    time.sleep(1)

    driver.execute_script("""
        Array.from(document.querySelectorAll('button'))
             .find(b => b.textContent.trim() === 'Update')
             ?.click();
    """)
    time.sleep(3)

    print("  Update clicked — settings saved.")
    if not debug_port:
        input("  Press Enter to close the browser...")
        driver.quit()


# ── CLI ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description="Apply weather settings to Bolt courier city config"
    )
    ap.add_argument("csv", help="CSV settings proposal file")
    ap.add_argument(
        "--weather", "-w",
        choices=["bad", "harsh", "proposed"],
        default="bad",
        help="Weather profile to apply (default: bad)",
    )
    ap.add_argument("--json", "-j", help="Current settings JSON (offline mode)")
    ap.add_argument("--output", "-o", help="Output JSON path (offline mode)")
    ap.add_argument("--url", "-u", help="Admin panel URL (browser mode)")
    ap.add_argument(
        "--debug-port", "-d", type=int, default=None,
        help="Connect to running Chrome on this debug port (e.g. 9222)",
    )

    args = ap.parse_args()

    if args.url:
        browser(args.csv, args.url, args.weather, args.debug_port)
    elif args.json:
        out = args.output or str(
            Path(args.json).with_stem(Path(args.json).stem + f"_{args.weather}")
        )
        offline(args.csv, args.json, out, args.weather)
    else:
        ap.error("Provide --url (browser mode) or --json (offline mode)")


if __name__ == "__main__":
    main()
