#!/usr/bin/env python3
"""
Bolt Admin Panel — Harsh Weather Settings Automation — Kharkiv

Applies Harsh Weather settings to Kharkiv's courier config.

Admin panel route:
  City list:  https://admin-panel.bolt.eu/delivery-courier/settings/city
  City name:  Kharkiv (find in city list → click to open settings)

Two modes:
  1. Offline:  reads CSV + current JSON file → outputs modified JSON file
  2. Browser:  reads CSV, opens admin panel via Selenium, applies changes, clicks Update

Usage examples:
  # Offline — generate a JSON file with harsh weather values
  python apply_harsh_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kharkiv.csv" \
      --json "Harsh Weather Settings Kharkiv.json"

  # Browser automation — navigate to city list, find Kharkiv, apply harsh weather
  python apply_harsh_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kharkiv.csv" --browser
"""

import csv
import json
import sys
import time
import argparse
from pathlib import Path

# ── City config ───────────────────────────────────────────────────────────────
CITY_NAME = "Kharkiv"
CITY_LIST_URL = "https://admin-panel.bolt.eu/delivery-courier/settings/city"

# ── CSV column indices (0-based) ─────────────────────────────────────────────
COL_PATH = 2
COL_CURRENT = 5
COL_PROPOSED = 6
COL_HARSH_WEATHER = 10

PROFILE = "harsh"

COURIER_SURGE_OVERRIDES = {
    "batching/disable_second_batched_order_auto_acceptance": True,
    "dynamic_multiplier/courier_earning/is_enabled": False,
    "dynamic_multiplier/courier_earning/is_generation_enabled": False,
    "dynamic_multiplier/courier_earning/notification_settings/is_enabled": False,
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 30000000,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 30000000,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 40000000,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 40000000,
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
            "harsh": row[COL_HARSH_WEATHER].strip(),
        })
    return settings


def coerce(value_str: str):
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


def apply_weather(json_data: dict, settings: list[dict]):
    changes, skipped = [], []

    for s in settings:
        target_str = s[PROFILE]
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


def print_report(changes, skipped):
    print(f"\n{'='*60}")
    print(f"  Harsh Weather Settings ({CITY_NAME}) — {len(changes)} change(s) applied")
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
def offline(csv_path, json_path, output_path):
    settings = parse_csv(csv_path)
    with open(json_path) as f:
        data = json.load(f)

    changes, skipped = apply_weather(data, settings)
    print_report(changes, skipped)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved to: {output_path}\n")


# ── Browser automation mode ──────────────────────────────────────────────────
def _make_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    tmp_profile = Path.home() / ".chrome_selenium_profile"
    tmp_profile.mkdir(exist_ok=True)
    opts = Options()
    opts.add_argument(f"--user-data-dir={tmp_profile}")
    opts.add_argument("--profile-directory=AutomationProfile")
    return webdriver.Chrome(options=opts)


def _navigate_to_city(driver, city_name):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    print(f"  Opening city list: {CITY_LIST_URL} ...")
    driver.get(CITY_LIST_URL)
    print(f"  Waiting for city list to load ...")

    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table, .MuiTable-root, [class*='table'], a[href*='/city/']"))
    )
    time.sleep(2)

    city_link = None
    for a in driver.find_elements(By.CSS_SELECTOR, "a"):
        if city_name.lower() in a.text.lower() and "/city/" in (a.get_attribute("href") or ""):
            city_link = a
            break

    if not city_link:
        for el in driver.find_elements(By.XPATH, f"//*[contains(text(), '{city_name}')]"):
            el.click()
            time.sleep(2)
            if "/city/" in driver.current_url:
                print(f"  Navigated to {city_name}: {driver.current_url}")
                return
        sys.exit(f"  ERROR: Could not find '{city_name}' in the city list.")

    href = city_link.get_attribute("href")
    print(f"  Found {city_name}: {href}")
    city_link.click()
    time.sleep(2)


def browser(csv_path, url=None):
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        sys.exit("Selenium is required for browser mode.  pip install selenium")

    settings = parse_csv(csv_path)
    driver = _make_driver()

    if url:
        print(f"  Opening {url} ...")
        driver.get(url)
        print("  Waiting for the page to load ...")
    else:
        _navigate_to_city(driver, CITY_NAME)

    WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".jsoneditor"))
    )
    time.sleep(2)

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

    changes, skipped = apply_weather(data, settings)
    print_report(changes, skipped)

    if not changes:
        print("  Nothing to update — closing browser.")
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
    input("  Press Enter to close the browser...")
    driver.quit()


# ── CLI ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description=f"Apply Harsh Weather settings to Bolt courier config — {CITY_NAME}"
    )
    ap.add_argument("csv", help="CSV settings proposal file")
    ap.add_argument("--json", "-j", help="Current settings JSON (offline mode)")
    ap.add_argument("--output", "-o", help="Output JSON path (offline mode)")
    ap.add_argument("--url", "-u", help="Direct city settings URL (skips city list navigation)")
    ap.add_argument("--browser", "-b", action="store_true",
                    help="Browser mode: navigate to city list, find city, apply settings")

    args = ap.parse_args()

    if args.url:
        browser(args.csv, args.url)
    elif args.browser:
        browser(args.csv)
    elif args.json:
        out = args.output or str(
            Path(args.json).with_stem(Path(args.json).stem + "_applied")
        )
        offline(args.csv, args.json, out)
    else:
        ap.error("Provide --browser (city list navigation), --url (direct URL), or --json (offline mode)")


if __name__ == "__main__":
    main()
