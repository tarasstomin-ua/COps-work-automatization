#!/usr/bin/env python3
"""
Apply weather settings to Bolt Admin Panel.
Runs inside GitHub Actions.

Approach:
  1. Try direct API (fast, no browser) — needs BOLT_JWT secret
  2. Fall back to Playwright browser automation — needs BOLT_COOKIES secret

Usage:
  python apply.py <city> <profile> <user>
"""

import json
import os
import re
import sys
import base64
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

REPO_RAW = "https://raw.githubusercontent.com/tarasstomin-ua/COps-work-automatization/main/Bad%20weather%20settings"
STATUS_FILE = Path("status.json")
API_BASE = "https://admin-panel.bolt.eu/backend/delivery-courier-settings/adminPanel"

CITIES = {
    "Kyiv": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/158", "city_id": 158, "base": "Kyiv", "jsonName": "Kyiv"},
    "Lviv": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/496", "city_id": 496, "base": "Lviv", "jsonName": "Lviv"},
    "Dnipro": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/499", "city_id": 499, "base": "Dnipro", "jsonName": "Dnipro"},
    "Kharkiv": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/491", "city_id": 491, "base": "Kharkiv", "jsonName": "Kharkiv"},
    "Vinnytsia": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/501", "city_id": 501, "base": "Vinnytsia", "jsonName": "Vinnytsia"},
    "Odesa": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/498", "city_id": 498, "base": "Secondary cities/Tier2 cities/Odesa", "jsonName": "Odesa"},
    "Kryvyi Rih": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/504", "city_id": 504, "base": "Secondary cities/Tier2 cities/Kryvyi Rih", "jsonName": "Kryvyi Rih"},
    "Poltava": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/506", "city_id": 506, "base": "Secondary cities/Tier2 cities/Poltava", "jsonName": "Poltava"},
    "Ivano-Frankivsk": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/990", "city_id": 990, "base": "Secondary cities/Tier2 cities/Ivano-Frankivsk", "jsonName": "Ivano-Frankivsk"},
    "Chernivtsi": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1084", "city_id": 1084, "base": "Secondary cities/Tier2 cities/Chernivtsi", "jsonName": "Chernivtsi"},
    "Irpin": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1261", "city_id": 1261, "base": "Secondary cities/Tier2 cities/Irpin", "jsonName": "Irpin"},
    "Cherkasy": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1087", "city_id": 1087, "base": "Secondary cities/Tier2 cities/Cherkasy", "jsonName": "Cherkasy"},
    "Zaporizhia": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/500", "city_id": 500, "base": "Secondary cities/Tier3 cities/Zaporizhia", "jsonName": "Zaporizhia"},
    "Bila Tserkva": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1079", "city_id": 1079, "base": "Secondary cities/Tier3 cities/Bila Tserkva", "jsonName": "Bila Tserkva"},
    "Khmelnytskyi": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1081", "city_id": 1081, "base": "Secondary cities/Tier3 cities/Khmelnytskyi", "jsonName": "Khmelnytskyi"},
    "Rivne": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1086", "city_id": 1086, "base": "Secondary cities/Tier3 cities/Rivne", "jsonName": "Rivne"},
    "Uzhhorod": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1131", "city_id": 1131, "base": "Secondary cities/Tier3 cities/Uzhhorod", "jsonName": "Uzhhorod"},
    "Brovary": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1259", "city_id": 1259, "base": "Secondary cities/Tier3 cities/Brovary", "jsonName": "Brovary"},
    "Zhytomyr": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1083", "city_id": 1083, "base": "Secondary cities/Tier3 cities/Zhytomyr", "jsonName": "Zhytomyr"},
    "Mykolaiv": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/503", "city_id": 503, "base": "Secondary cities/Rest of the cities/Mykolaiv", "jsonName": "Mykolaiv"},
    "Chernihiv": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1076", "city_id": 1076, "base": "Secondary cities/Rest of the cities/Chenihiv", "jsonName": "Chernihiv"},
    "Sumy": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1078", "city_id": 1078, "base": "Secondary cities/Rest of the cities/Sumy", "jsonName": "Sumy"},
    "Ternopil": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1080", "city_id": 1080, "base": "Secondary cities/Rest of the cities/Ternopil", "jsonName": "Ternopil"},
    "Lutsk": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1082", "city_id": 1082, "base": "Secondary cities/Rest of the cities/Lutsk", "jsonName": "Lutsk"},
    "Kropyvnytskyi": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1085", "city_id": 1085, "base": "Secondary cities/Rest of the cities/Kropyvnytskyi", "jsonName": "Kropyvnytskyi"},
    "Kremenchuk": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1088", "city_id": 1088, "base": "Secondary cities/Rest of the cities/Kremenchuk", "jsonName": "Kremenchuk"},
    "Kamianets-Podilskyi": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1132", "city_id": 1132, "base": "Secondary cities/Rest of the cities/Kamianets-Podilskyi", "jsonName": "Kamianets-Podilskyi"},
    "Pavlohrad": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1176", "city_id": 1176, "base": "Secondary cities/Rest of the cities/Pavlohrad", "jsonName": "Pavlohrad"},
    "Kamianske": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1178", "city_id": 1178, "base": "Secondary cities/Rest of the cities/Kamianske", "jsonName": "Kamianske"},
    "Mukachevo": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1179", "city_id": 1179, "base": "Secondary cities/Rest of the cities/Mukachevo", "jsonName": "Mukachevo"},
    "Boryspil": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1220", "city_id": 1220, "base": "Secondary cities/Rest of the cities/Boryspil", "jsonName": "Boryspil"},
    "Vyshhorod": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1262", "city_id": 1262, "base": "Secondary cities/Rest of the cities/Vyshhorod", "jsonName": "Vyshhorod"},
    "Drohobych": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1348", "city_id": 1348, "base": "Secondary cities/Rest of the cities/Drohobych", "jsonName": "Drohobych"},
    "Truskavets": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1357", "city_id": 1357, "base": "Secondary cities/Rest of the cities/Truskavets", "jsonName": "Truskavets"},
    "Kovel": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2170", "city_id": 2170, "base": "Secondary cities/Rest of the cities/Kovel", "jsonName": "Kovel"},
    "Oleksandriia": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2171", "city_id": 2171, "base": "Secondary cities/Rest of the cities/Oleksandriia", "jsonName": "Oleksandriia"},
    "Kolomyia": {"url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2499", "city_id": 2499, "base": "Secondary cities/Rest of the cities/Kolomyia", "jsonName": "Kolomyia"},
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


# ── Approach 1: Direct API (fast, no browser) ───────────────────────────────

def try_api_approach(city_name: str, target: dict, jwt: str, cookies_str: str) -> bool:
    """GET current settings, merge, POST back. Returns True on success."""
    city_id = CITIES[city_name]["city_id"]

    headers = {
        "Authorization": f"Bearer {jwt}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://admin-panel.bolt.eu",
        "Referer": f"https://admin-panel.bolt.eu/delivery-courier/settings/city/{city_id}",
    }
    if cookies_str:
        headers["Cookie"] = cookies_str

    get_url = f"{API_BASE}/city/get?city_id={city_id}"
    print(f"  API GET {get_url}")
    req = urllib.request.Request(get_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  API GET failed: HTTP {e.code} — {e.read().decode()[:200]}")
        return False

    if "data" in body and "settings" in body["data"]:
        current = body["data"]["settings"]
    elif "data" in body:
        current = body["data"]
    else:
        current = body
    print(f"  Current settings: {len(current)} top-level keys")

    deep_merge(current, target)

    update_url = f"{API_BASE}/city/update"
    payload = json.dumps({"city_id": city_id, "settings": current}).encode()
    print(f"  API POST {update_url}")
    req = urllib.request.Request(update_url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = resp.read().decode()[:200]
            print(f"  API POST response: {result}")
            return True
    except urllib.error.HTTPError as e:
        print(f"  API POST failed: HTTP {e.code} — {e.read().decode()[:200]}")
        return False


# ── Approach 2: Playwright browser automation ────────────────────────────────

def try_playwright_approach(city_name: str, target: dict, cookies: list) -> bool:
    """Open admin panel in Playwright, merge JSON in editor, click Update."""
    from playwright.sync_api import sync_playwright

    admin_url = CITIES[city_name]["url"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
        )
        context.add_cookies(cookies)
        page = context.new_page()

        captured_jwt = None

        def on_request(request):
            nonlocal captured_jwt
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer ") and not captured_jwt:
                captured_jwt = auth[7:]
                print(f"  Captured fresh JWT from browser request")

        page.on("request", on_request)

        print(f"  Navigating to {admin_url}")
        try:
            page.goto(admin_url, wait_until="networkidle", timeout=60_000)
        except Exception as e:
            print(f"  Navigation failed: {e}")
            page.screenshot(path="debug_navigation.png")
            browser.close()
            return False

        current_url = page.url
        print(f"  Current URL after load: {current_url}")

        if "login" in current_url.lower() or "auth" in current_url.lower() or "sso" in current_url.lower():
            print("  Login page detected — session cookies are not sufficient")
            page.screenshot(path="debug_login_page.png")
            browser.close()
            return False

        print("  Waiting for JSON editor...")
        try:
            page.wait_for_selector(".jsoneditor", timeout=30_000)
        except Exception:
            print("  JSON editor not found")
            page.screenshot(path="debug_no_editor.png")
            title = page.title()
            body_text = page.evaluate("document.body?.innerText?.substring(0, 500) || ''")
            print(f"  Page title: {title}")
            print(f"  Page content: {body_text[:300]}")

            if captured_jwt:
                print("  But we captured a JWT — trying API approach with fresh token")
                browser.close()
                cookies_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
                return try_api_approach(city_name, target, captured_jwt, cookies_str)

            browser.close()
            return False

        page.wait_for_timeout(1500)

        print("  Switching to Code mode...")
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

        print("  Reading current settings from editor...")
        raw = page.evaluate(
            "ace.edit(document.querySelector('.ace_editor')).getValue()"
        )
        current = json.loads(raw)
        print(f"  Current settings: {len(current)} top-level keys")

        deep_merge(current, target)

        print("  Writing merged settings...")
        page.evaluate(
            "ace.edit(document.querySelector('.ace_editor')).setValue(arguments[0], -1)",
            json.dumps(current, indent=2),
        )
        page.wait_for_timeout(500)

        print("  Clicking Update...")
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
            print(f"  Update clicked!")
        else:
            print("  WARNING: Update button not found")
            page.screenshot(path="debug_no_update_btn.png")

        browser.close()
        return clicked


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    city_name = sys.argv[1]
    profile = sys.argv[2]
    user = sys.argv[3]

    if city_name not in CITIES:
        sys.exit(f"Unknown city: {city_name}")
    if profile not in PROFILE_META:
        sys.exit(f"Unknown profile: {profile}")

    print(f"=== Applying {profile} weather to {city_name} ===")

    target = fetch_target(city_name, profile)
    print(f"Target settings fetched ({len(target)} top-level keys)")

    cookies_b64 = os.environ.get("BOLT_COOKIES", "")
    jwt = os.environ.get("BOLT_JWT", "")
    cookies = json.loads(base64.b64decode(cookies_b64)) if cookies_b64 else []
    cookies_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

    success = False

    if jwt:
        print("\n[1] Trying direct API approach (JWT available)...")
        success = try_api_approach(city_name, target, jwt, cookies_str)
        if success:
            print("API approach succeeded!")

    if not success and cookies:
        print("\n[2] Trying Playwright browser approach...")
        success = try_playwright_approach(city_name, target, cookies)
        if success:
            print("Playwright approach succeeded!")

    if not success:
        print("\n=== FAILED ===")
        print("Neither API nor Playwright approach worked.")
        print("This likely means the auth tokens have expired.")
        print("")
        print("To fix this:")
        print("1. Log in to admin-panel.bolt.eu in your browser")
        print("2. F12 → Network → Fetch/XHR → Copy as cURL")
        print("3. Run: python automation/parse_curl.py")
        print("4. Update the BOLT_COOKIES secret in GitHub repo settings")
        print("5. If you see a Bearer token, also set BOLT_JWT secret")
        sys.exit(1)

    update_status(city_name, profile, user)
    print(f"\n=== SUCCESS: {city_name} → {profile} weather applied by {user} ===")


if __name__ == "__main__":
    main()
