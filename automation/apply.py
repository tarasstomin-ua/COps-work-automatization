#!/usr/bin/env python3
"""
Apply weather settings to Bolt Admin Panel via Playwright.
Runs inside GitHub Actions with BOLT_COOKIES secret.

Usage:
  python apply.py <city> <profile> <user>
"""

import json
import os
import sys
import base64
import urllib.request
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_RAW = "https://raw.githubusercontent.com/tarasstomin-ua/COps-work-automatization/main/Bad%20weather%20settings"
STATUS_FILE = Path("status.json")

CITIES = {
    "Kyiv": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/158", "base": "Kyiv", "jsonName": "Kyiv"},
    "Lviv": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/496", "base": "Lviv", "jsonName": "Lviv"},
    "Dnipro": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/499", "base": "Dnipro", "jsonName": "Dnipro"},
    "Kharkiv": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/491", "base": "Kharkiv", "jsonName": "Kharkiv"},
    "Vinnytsia": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/501", "base": "Vinnytsia", "jsonName": "Vinnytsia"},
    "Odesa": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/498", "base": "Secondary cities/Tier2 cities/Odesa", "jsonName": "Odesa"},
    "Kryvyi Rih": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/504", "base": "Secondary cities/Tier2 cities/Kryvyi Rih", "jsonName": "Kryvyi Rih"},
    "Poltava": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/506", "base": "Secondary cities/Tier2 cities/Poltava", "jsonName": "Poltava"},
    "Ivano-Frankivsk": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/990", "base": "Secondary cities/Tier2 cities/Ivano-Frankivsk", "jsonName": "Ivano-Frankivsk"},
    "Chernivtsi": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1084", "base": "Secondary cities/Tier2 cities/Chernivtsi", "jsonName": "Chernivtsi"},
    "Irpin": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1261", "base": "Secondary cities/Tier2 cities/Irpin", "jsonName": "Irpin"},
    "Cherkasy": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1087", "base": "Secondary cities/Tier2 cities/Cherkasy", "jsonName": "Cherkasy"},
    "Zaporizhia": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/500", "base": "Secondary cities/Tier3 cities/Zaporizhia", "jsonName": "Zaporizhia"},
    "Bila Tserkva": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1079", "base": "Secondary cities/Tier3 cities/Bila Tserkva", "jsonName": "Bila Tserkva"},
    "Khmelnytskyi": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1081", "base": "Secondary cities/Tier3 cities/Khmelnytskyi", "jsonName": "Khmelnytskyi"},
    "Rivne": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1086", "base": "Secondary cities/Tier3 cities/Rivne", "jsonName": "Rivne"},
    "Uzhhorod": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1131", "base": "Secondary cities/Tier3 cities/Uzhhorod", "jsonName": "Uzhhorod"},
    "Brovary": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1259", "base": "Secondary cities/Tier3 cities/Brovary", "jsonName": "Brovary"},
    "Zhytomyr": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1083", "base": "Secondary cities/Tier3 cities/Zhytomyr", "jsonName": "Zhytomyr"},
    "Mykolaiv": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/503", "base": "Secondary cities/Rest of the cities/Mykolaiv", "jsonName": "Mykolaiv"},
    "Chernihiv": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1076", "base": "Secondary cities/Rest of the cities/Chenihiv", "jsonName": "Chernihiv"},
    "Sumy": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1078", "base": "Secondary cities/Rest of the cities/Sumy", "jsonName": "Sumy"},
    "Ternopil": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1080", "base": "Secondary cities/Rest of the cities/Ternopil", "jsonName": "Ternopil"},
    "Lutsk": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1082", "base": "Secondary cities/Rest of the cities/Lutsk", "jsonName": "Lutsk"},
    "Kropyvnytskyi": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1085", "base": "Secondary cities/Rest of the cities/Kropyvnytskyi", "jsonName": "Kropyvnytskyi"},
    "Kremenchuk": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1088", "base": "Secondary cities/Rest of the cities/Kremenchuk", "jsonName": "Kremenchuk"},
    "Kamianets-Podilskyi": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1132", "base": "Secondary cities/Rest of the cities/Kamianets-Podilskyi", "jsonName": "Kamianets-Podilskyi"},
    "Pavlohrad": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1176", "base": "Secondary cities/Rest of the cities/Pavlohrad", "jsonName": "Pavlohrad"},
    "Kamianske": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1178", "base": "Secondary cities/Rest of the cities/Kamianske", "jsonName": "Kamianske"},
    "Mukachevo": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1179", "base": "Secondary cities/Rest of the cities/Mukachevo", "jsonName": "Mukachevo"},
    "Boryspil": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1220", "base": "Secondary cities/Rest of the cities/Boryspil", "jsonName": "Boryspil"},
    "Vyshhorod": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1262", "base": "Secondary cities/Rest of the cities/Vyshhorod", "jsonName": "Vyshhorod"},
    "Drohobych": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1348", "base": "Secondary cities/Rest of the cities/Drohobych", "jsonName": "Drohobych"},
    "Truskavets": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1357", "base": "Secondary cities/Rest of the cities/Truskavets", "jsonName": "Truskavets"},
    "Kovel": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2170", "base": "Secondary cities/Rest of the cities/Kovel", "jsonName": "Kovel"},
    "Oleksandriia": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2171", "base": "Secondary cities/Rest of the cities/Oleksandriia", "jsonName": "Oleksandriia"},
    "Kolomyia": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2499", "base": "Secondary cities/Rest of the cities/Kolomyia", "jsonName": "Kolomyia"},
}

PROFILE_META = {
    "good":  {"folder": "Good weather",  "prefix": "Good Weather Settings"},
    "bad":   {"folder": "Bad weather",   "prefix": "Bad Weather Settings"},
    "harsh": {"folder": "Harsh weather", "prefix": "Harsh Weather Settings"},
}


def fetch_target(city_name: str, profile: str) -> dict:
    c = CITIES[city_name]
    m = PROFILE_META[profile]
    base = c["base"].replace(" ", "%20")
    folder = m["folder"].replace(" ", "%20")
    prefix = m["prefix"].replace(" ", "%20")
    name = c["jsonName"].replace(" ", "%20")
    url = f"{REPO_RAW}/{base}/{folder}/{prefix}%20{name}.json"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read())


def deep_merge(dst: dict, src: dict):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_merge(dst[k], v)
        else:
            dst[k] = v


def update_status(city_name: str, profile: str, user: str):
    status = json.loads(STATUS_FILE.read_text()) if STATUS_FILE.exists() else {"cities": {}}
    status.setdefault("cities", {})[city_name] = {
        "profile": profile,
        "user": user,
        "timestamp": datetime.now().isoformat(),
    }
    status.setdefault("history", []).insert(0, {
        "city": city_name, "profile": profile, "user": user,
        "timestamp": datetime.now().isoformat(),
    })
    status["history"] = status["history"][:300]
    status["last_updated"] = datetime.now().isoformat()
    STATUS_FILE.write_text(json.dumps(status, indent=2))


def main():
    city_name = sys.argv[1]
    profile = sys.argv[2]
    user = sys.argv[3]

    if city_name not in CITIES:
        sys.exit(f"Unknown city: {city_name}")
    if profile not in PROFILE_META:
        sys.exit(f"Unknown profile: {profile}")

    cookies_b64 = os.environ.get("BOLT_COOKIES", "")
    if not cookies_b64:
        sys.exit("BOLT_COOKIES secret is not set. Go to repo Settings → Secrets → Actions to set it.")

    cookies = json.loads(base64.b64decode(cookies_b64))
    admin_url = CITIES[city_name]["url"]

    print(f"Applying {profile} weather to {city_name}...")
    print(f"Admin URL: {admin_url}")

    target = fetch_target(city_name, profile)
    print(f"Target settings fetched ({len(target)} top-level keys)")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()

        print("Navigating to admin panel...")
        page.goto(admin_url, wait_until="networkidle", timeout=60_000)

        print("Waiting for JSON editor...")
        page.wait_for_selector(".jsoneditor", timeout=90_000)
        page.wait_for_timeout(1500)

        print("Switching to Code mode...")
        modes_btn = page.query_selector("button.jsoneditor-modes")
        if modes_btn:
            modes_btn.click()
            page.wait_for_timeout(400)
            for item in page.query_selector_all(
                ".jsoneditor-type-modes div, .jsoneditor-type-modes button"
            ):
                if item.inner_text().strip() == "Code":
                    item.click()
                    break
            page.wait_for_timeout(800)

        print("Reading current settings from editor...")
        raw = page.evaluate(
            "ace.edit(document.querySelector('.ace_editor')).getValue()"
        )
        current = json.loads(raw)
        print(f"Current settings: {len(current)} top-level keys")

        print("Merging target into current...")
        deep_merge(current, target)

        print("Writing merged settings to editor...")
        page.evaluate(
            "ace.edit(document.querySelector('.ace_editor')).setValue(arguments[0], -1)",
            json.dumps(current, indent=2),
        )
        page.wait_for_timeout(500)

        print("Clicking Update...")
        clicked = page.evaluate("""
            (() => {
                const btn = Array.from(document.querySelectorAll('button'))
                    .find(b => b.textContent.trim() === 'Update');
                if (btn) { btn.click(); return true; }
                return false;
            })()
        """)

        if clicked:
            page.wait_for_timeout(3000)
            print(f"Update clicked — {city_name} {profile} weather applied!")
        else:
            print("WARNING: Update button not found")

        browser.close()

    update_status(city_name, profile, user)
    print("Status updated in status.json")


if __name__ == "__main__":
    main()
