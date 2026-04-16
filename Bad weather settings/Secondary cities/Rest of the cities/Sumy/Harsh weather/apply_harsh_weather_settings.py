#!/usr/bin/env python3
"""
Bolt Admin Panel — Harsh Weather Settings Automation — Sumy

Applies Harsh Weather settings to Sumy's courier config.
Source CSV: COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv

Usage:
  python apply_harsh_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv" --url https://admin-panel.bolt.eu/delivery-courier/settings/city/1078
"""

import csv
import json
import sys
import time
import argparse
from pathlib import Path

CITY_NAME = "Sumy"

COL_PATH = 2
COL_TARGET = 5

PROFILE = "harsh"

SETTING_OVERRIDES = {
    "batching/disable_second_batched_order_auto_acceptance": True,
    "dynamic_multiplier/courier_earning/is_enabled": False,
    "dynamic_multiplier/courier_earning/is_generation_enabled": False,
    "dynamic_multiplier/courier_earning/notification_settings/is_enabled": False,
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 400,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 400,
}


def parse_csv(csv_path: str) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    settings = []
    for row in rows:
        if len(row) <= COL_TARGET:
            continue
        path = row[COL_PATH].strip()
        if not path or "/" not in path:
            continue
        settings.append({
            "path": path,
            PROFILE: row[COL_TARGET].strip(),
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
        if s["path"] in SETTING_OVERRIDES:
            target = SETTING_OVERRIDES[s["path"]]
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


def offline(csv_path, json_path, output_path):
    settings = parse_csv(csv_path)
    with open(json_path) as f:
        data = json.load(f)
    changes, skipped = apply_weather(data, settings)
    print_report(changes, skipped)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved to: {output_path}\n")


def _make_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    tmp_profile = Path.home() / ".chrome_selenium_profile"
    tmp_profile.mkdir(exist_ok=True)
    opts = Options()
    opts.add_argument(f"--user-data-dir={tmp_profile}")
    opts.add_argument("--profile-directory=AutomationProfile")
    return webdriver.Chrome(options=opts)


def browser(csv_path, url):
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        sys.exit("Selenium is required.  pip install selenium")

    settings = parse_csv(csv_path)
    driver = _make_driver()

    print(f"  Opening {url} ...")
    driver.get(url)
    print("  Waiting for the page to load ...")

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


def main():
    ap = argparse.ArgumentParser(
        description=f"Apply Harsh Weather settings — {CITY_NAME}"
    )
    ap.add_argument("csv", help="CSV settings proposal file")
    ap.add_argument("--json", "-j", help="Current settings JSON (offline mode)")
    ap.add_argument("--output", "-o", help="Output JSON path (offline mode)")
    ap.add_argument("--url", "-u", help="Direct city settings URL")

    args = ap.parse_args()

    if args.url:
        browser(args.csv, args.url)
    elif args.json:
        out = args.output or str(
            Path(args.json).with_stem(Path(args.json).stem + "_applied")
        )
        offline(args.csv, args.json, out)
    else:
        ap.error("Provide --url (browser mode) or --json (offline mode)")


if __name__ == "__main__":
    main()
