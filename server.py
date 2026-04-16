#!/usr/bin/env python3
"""
COps Weather Control — Server Edition
Render.com deployment with Playwright for fully automatic admin panel automation.

ENV VARS (set in Render dashboard):
  SECRET_KEY          – Flask session secret (required)
  DASHBOARD_PASSWORD  – Shared password for the 3 allowed users (required)
  BOLT_COOKIES        – Base64-encoded JSON array of Bolt admin cookies (set via /auth page)
"""

import json, os, re, threading, time, uuid, base64, urllib.request
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request, session, redirect

# ── Config ────────────────────────────────────────────────────────────────────

ALLOWED_EMAILS = [
    "anna.tiurina@bolt.eu",
    "nataliia.malakova@bolt.eu",
    "taras.stomin@bolt.eu",
]

SECRET_KEY = os.environ.get("SECRET_KEY", "cops-change-me-in-production")
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "cops2026")
PORT = int(os.environ.get("PORT", 10000))

REPO_RAW = "https://raw.githubusercontent.com/tarasstomin-ua/COps-work-automatization/main/Bad%20weather%20settings"

# ── City config ───────────────────────────────────────────────────────────────

CITIES = {
    "Kyiv": {"group": "TOP cities", "order": 0, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/158", "base": "Kyiv", "profiles": ["good","bad","harsh"], "jsonName": "Kyiv"},
    "Lviv": {"group": "TOP cities", "order": 0, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/496", "base": "Lviv", "profiles": ["good","bad","harsh"], "jsonName": "Lviv"},
    "Dnipro": {"group": "TOP cities", "order": 0, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/499", "base": "Dnipro", "profiles": ["good","bad","harsh"], "jsonName": "Dnipro"},
    "Kharkiv": {"group": "TOP cities", "order": 0, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/491", "base": "Kharkiv", "profiles": ["good","bad","harsh"], "jsonName": "Kharkiv"},
    "Vinnytsia": {"group": "TOP cities", "order": 0, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/501", "base": "Vinnytsia", "profiles": ["good","bad","harsh"], "jsonName": "Vinnytsia"},
    "Odesa": {"group": "Tier 2", "order": 1, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/498", "base": "Secondary cities/Tier2 cities/Odesa", "profiles": ["good","harsh"], "jsonName": "Odesa"},
    "Kryvyi Rih": {"group": "Tier 2", "order": 1, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/504", "base": "Secondary cities/Tier2 cities/Kryvyi Rih", "profiles": ["good","harsh"], "jsonName": "Kryvyi Rih"},
    "Poltava": {"group": "Tier 2", "order": 1, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/506", "base": "Secondary cities/Tier2 cities/Poltava", "profiles": ["good","harsh"], "jsonName": "Poltava"},
    "Ivano-Frankivsk": {"group": "Tier 2", "order": 1, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/990", "base": "Secondary cities/Tier2 cities/Ivano-Frankivsk", "profiles": ["good","harsh"], "jsonName": "Ivano-Frankivsk"},
    "Chernivtsi": {"group": "Tier 2", "order": 1, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1084", "base": "Secondary cities/Tier2 cities/Chernivtsi", "profiles": ["good","harsh"], "jsonName": "Chernivtsi"},
    "Irpin": {"group": "Tier 2", "order": 1, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1261", "base": "Secondary cities/Tier2 cities/Irpin", "profiles": ["good","harsh"], "jsonName": "Irpin"},
    "Cherkasy": {"group": "Tier 2", "order": 1, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1087", "base": "Secondary cities/Tier2 cities/Cherkasy", "profiles": ["good","harsh"], "jsonName": "Cherkasy"},
    "Zaporizhia": {"group": "Tier 3", "order": 2, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/500", "base": "Secondary cities/Tier3 cities/Zaporizhia", "profiles": ["good","harsh"], "jsonName": "Zaporizhia"},
    "Bila Tserkva": {"group": "Tier 3", "order": 2, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1079", "base": "Secondary cities/Tier3 cities/Bila Tserkva", "profiles": ["good","harsh"], "jsonName": "Bila Tserkva"},
    "Khmelnytskyi": {"group": "Tier 3", "order": 2, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1081", "base": "Secondary cities/Tier3 cities/Khmelnytskyi", "profiles": ["good","harsh"], "jsonName": "Khmelnytskyi"},
    "Rivne": {"group": "Tier 3", "order": 2, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1086", "base": "Secondary cities/Tier3 cities/Rivne", "profiles": ["good","harsh"], "jsonName": "Rivne"},
    "Uzhhorod": {"group": "Tier 3", "order": 2, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1131", "base": "Secondary cities/Tier3 cities/Uzhhorod", "profiles": ["good","harsh"], "jsonName": "Uzhhorod"},
    "Brovary": {"group": "Tier 3", "order": 2, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1259", "base": "Secondary cities/Tier3 cities/Brovary", "profiles": ["good","harsh"], "jsonName": "Brovary"},
    "Zhytomyr": {"group": "Tier 3", "order": 2, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1083", "base": "Secondary cities/Tier3 cities/Zhytomyr", "profiles": ["good","harsh"], "jsonName": "Zhytomyr"},
    "Mykolaiv": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/503", "base": "Secondary cities/Rest of the cities/Mykolaiv", "profiles": ["good","harsh"], "jsonName": "Mykolaiv"},
    "Chernihiv": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1076", "base": "Secondary cities/Rest of the cities/Chenihiv", "profiles": ["good","harsh"], "jsonName": "Chernihiv"},
    "Sumy": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1078", "base": "Secondary cities/Rest of the cities/Sumy", "profiles": ["good","harsh"], "jsonName": "Sumy"},
    "Ternopil": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1080", "base": "Secondary cities/Rest of the cities/Ternopil", "profiles": ["good","harsh"], "jsonName": "Ternopil"},
    "Lutsk": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1082", "base": "Secondary cities/Rest of the cities/Lutsk", "profiles": ["good","harsh"], "jsonName": "Lutsk"},
    "Kropyvnytskyi": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1085", "base": "Secondary cities/Rest of the cities/Kropyvnytskyi", "profiles": ["good","harsh"], "jsonName": "Kropyvnytskyi"},
    "Kremenchuk": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1088", "base": "Secondary cities/Rest of the cities/Kremenchuk", "profiles": ["good","harsh"], "jsonName": "Kremenchuk"},
    "Kamianets-Podilskyi": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1132", "base": "Secondary cities/Rest of the cities/Kamianets-Podilskyi", "profiles": ["good","harsh"], "jsonName": "Kamianets-Podilskyi"},
    "Pavlohrad": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1176", "base": "Secondary cities/Rest of the cities/Pavlohrad", "profiles": ["good","harsh"], "jsonName": "Pavlohrad"},
    "Kamianske": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1178", "base": "Secondary cities/Rest of the cities/Kamianske", "profiles": ["good","harsh"], "jsonName": "Kamianske"},
    "Mukachevo": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1179", "base": "Secondary cities/Rest of the cities/Mukachevo", "profiles": ["good","harsh"], "jsonName": "Mukachevo"},
    "Boryspil": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1220", "base": "Secondary cities/Rest of the cities/Boryspil", "profiles": ["good","harsh"], "jsonName": "Boryspil"},
    "Vyshhorod": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1262", "base": "Secondary cities/Rest of the cities/Vyshhorod", "profiles": ["good","harsh"], "jsonName": "Vyshhorod"},
    "Drohobych": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1348", "base": "Secondary cities/Rest of the cities/Drohobych", "profiles": ["good","harsh"], "jsonName": "Drohobych"},
    "Truskavets": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1357", "base": "Secondary cities/Rest of the cities/Truskavets", "profiles": ["good","harsh"], "jsonName": "Truskavets"},
    "Kovel": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2170", "base": "Secondary cities/Rest of the cities/Kovel", "profiles": ["good","harsh"], "jsonName": "Kovel"},
    "Oleksandriia": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2171", "base": "Secondary cities/Rest of the cities/Oleksandriia", "profiles": ["good","harsh"], "jsonName": "Oleksandriia"},
    "Kolomyia": {"group": "Rest of cities", "order": 3, "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2499", "base": "Secondary cities/Rest of the cities/Kolomyia", "profiles": ["good","harsh"], "jsonName": "Kolomyia"},
}

PROFILE_META = {
    "good":  {"folder": "Good weather",  "prefix": "Good Weather Settings"},
    "bad":   {"folder": "Bad weather",   "prefix": "Bad Weather Settings"},
    "harsh": {"folder": "Harsh weather", "prefix": "Harsh Weather Settings"},
}
P_FULL = {"good": "Good Weather", "bad": "Bad Weather", "harsh": "Harsh Weather"}

# ── Flask app ─────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

tasks: dict = {}
status_data: dict = {"cities": {}, "history": []}
bolt_cookies: list = []
run_lock = threading.Lock()
status_lock = threading.Lock()

STATUS_FILE = Path("status_data.json")


def _load_status():
    global status_data
    if STATUS_FILE.exists():
        with open(STATUS_FILE) as f:
            status_data = json.load(f)


def _save_status():
    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, indent=2)


def _load_bolt_cookies():
    global bolt_cookies
    raw = os.environ.get("BOLT_COOKIES", "")
    if raw:
        try:
            bolt_cookies = json.loads(base64.b64decode(raw))
        except Exception:
            bolt_cookies = []


def _save_bolt_cookies_to_env():
    """Encode current cookies for display (user sets env var manually on Render)."""
    return base64.b64encode(json.dumps(bolt_cookies).encode()).decode()


def _set_status(city, profile, user):
    with status_lock:
        status_data["cities"][city] = {
            "profile": profile, "user": user,
            "timestamp": datetime.now().isoformat(),
        }
        status_data.setdefault("history", []).insert(0, {
            "city": city, "profile": profile, "user": user,
            "timestamp": datetime.now().isoformat(),
        })
        status_data["history"] = status_data["history"][:300]
        _save_status()


# ── Auth helpers ──────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "email" not in session or session["email"] not in ALLOWED_EMAILS:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapped


# ── Cookie parsing from cURL ──────────────────────────────────────────────────

def parse_curl_cookies(curl_text: str) -> list[dict]:
    match = re.search(r"""(?:-[hH]|--header)\s+['"]Cookie:\s*([^'"]+)['"]""", curl_text)
    if not match:
        match = re.search(r"Cookie:\s*(.+?)(?:\r?\n|$)", curl_text)
    if not match:
        return []
    cookies = []
    for part in match.group(1).split("; "):
        eq = part.find("=")
        if eq < 1:
            continue
        cookies.append({
            "name": part[:eq].strip(),
            "value": part[eq + 1:].strip(),
            "domain": ".bolt.eu",
            "path": "/",
            "secure": True,
            "httpOnly": True,
            "sameSite": "Lax",
        })
    return cookies


# ── JSON URL builder ──────────────────────────────────────────────────────────

def _json_url(city_name: str, profile: str) -> str:
    c = CITIES[city_name]
    m = PROFILE_META[profile]
    base = c["base"].replace(" ", "%20")
    folder = m["folder"].replace(" ", "%20")
    prefix = m["prefix"].replace(" ", "%20")
    name = c["jsonName"].replace(" ", "%20")
    return f"{REPO_RAW}/{base}/{folder}/{prefix}%20{name}.json"


def _fetch_target_json(city_name: str, profile: str) -> dict:
    url = _json_url(city_name, profile)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read())


def _deep_merge(dst: dict, src: dict):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v


# ── Playwright automation ─────────────────────────────────────────────────────

_pw = None
_browser = None
_browser_lock = threading.Lock()


def _get_browser():
    global _pw, _browser
    with _browser_lock:
        if _browser is None:
            from playwright.sync_api import sync_playwright
            _pw = sync_playwright().start()
            _browser = _pw.chromium.launch(headless=True)
        return _browser


def _run_apply(task_id: str, city_name: str, profile: str, user: str):
    start = time.time()
    page = None
    try:
        tasks[task_id]["status"] = "running"
        tasks[task_id]["message"] = f"Opening admin panel for {city_name}..."

        browser = _get_browser()
        context = browser.new_context()

        if bolt_cookies:
            context.add_cookies(bolt_cookies)

        page = context.new_page()
        admin_url = CITIES[city_name]["url"]

        tasks[task_id]["message"] = f"Navigating to {city_name} settings..."
        page.goto(admin_url, wait_until="networkidle", timeout=60_000)

        tasks[task_id]["message"] = "Waiting for JSON editor to load..."
        page.wait_for_selector(".jsoneditor", timeout=90_000)
        page.wait_for_timeout(1500)

        tasks[task_id]["message"] = "Switching to Code mode..."
        modes_btn = page.query_selector("button.jsoneditor-modes")
        if modes_btn:
            modes_btn.click()
            page.wait_for_timeout(400)
            for item in page.query_selector_all(".jsoneditor-type-modes div, .jsoneditor-type-modes button"):
                if item.inner_text().strip() == "Code":
                    item.click()
                    break
            page.wait_for_timeout(800)

        tasks[task_id]["message"] = "Reading current settings..."
        raw_json = page.evaluate(
            "ace.edit(document.querySelector('.ace_editor')).getValue()"
        )
        current = json.loads(raw_json)

        tasks[task_id]["message"] = "Fetching target settings from GitHub..."
        target = _fetch_target_json(city_name, profile)

        tasks[task_id]["message"] = "Merging settings..."
        _deep_merge(current, target)

        tasks[task_id]["message"] = "Writing merged settings to editor..."
        page.evaluate(
            "ace.edit(document.querySelector('.ace_editor')).setValue(arguments[0], -1)",
            json.dumps(current, indent=2),
        )
        page.wait_for_timeout(500)

        tasks[task_id]["message"] = "Clicking Update..."
        page.evaluate("""
            (() => {
                const btn = Array.from(document.querySelectorAll('button'))
                    .find(b => b.textContent.trim() === 'Update');
                if (btn) btn.click();
                return !!btn;
            })()
        """)
        page.wait_for_timeout(3000)

        elapsed = round(time.time() - start, 1)
        tasks[task_id].update(
            status="success",
            message=f"Settings applied! ({elapsed}s)",
            finished_at=datetime.now().isoformat(),
            duration=elapsed,
        )
        _set_status(city_name, profile, user)

    except Exception as exc:
        elapsed = round(time.time() - start, 1)
        msg = str(exc)
        if "jsoneditor" in msg.lower() or "timeout" in msg.lower():
            msg = "JSON editor not found — Bolt auth cookies may be expired. Go to Auth Setup to update them."
        tasks[task_id].update(
            status="error",
            message=msg,
            finished_at=datetime.now().isoformat(),
            duration=elapsed,
        )
    finally:
        try:
            if page:
                page.close()
        except Exception:
            pass


# ── API Routes ────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form if request.form else (request.json or {})
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        if email not in ALLOWED_EMAILS:
            return LOGIN_PAGE.replace("{{error}}", "Email not authorized"), 403
        if password != DASHBOARD_PASSWORD:
            return LOGIN_PAGE.replace("{{error}}", "Wrong password"), 403
        session["email"] = email
        return redirect("/")
    return LOGIN_PAGE.replace("{{error}}", "")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
@login_required
def index():
    return DASHBOARD_PAGE


@app.route("/api/cities")
@login_required
def api_cities():
    groups = {}
    for name, cfg in CITIES.items():
        g = cfg["group"]
        if g not in groups:
            groups[g] = {"order": cfg["order"], "cities": []}
        groups[g]["cities"].append({"name": name, "profiles": cfg["profiles"]})
    sorted_groups = sorted(groups.items(), key=lambda x: x[1]["order"])
    return jsonify({
        "groups": [{"name": k, "count": len(v["cities"]), "cities": v["cities"]} for k, v in sorted_groups],
        "status": status_data.get("cities", {}),
    })


@app.route("/api/apply", methods=["POST"])
@login_required
def api_apply():
    data = request.json or {}
    city = data.get("city", "")
    profile = data.get("profile", "")
    if city not in CITIES:
        return jsonify({"error": f"Unknown city: {city}"}), 400
    if profile not in PROFILE_META:
        return jsonify({"error": f"Unknown profile: {profile}"}), 400
    if profile not in CITIES[city]["profiles"]:
        return jsonify({"error": f"Profile '{profile}' not available for {city}"}), 400
    if not bolt_cookies:
        return jsonify({"error": "Bolt admin cookies not configured. Go to Auth Setup."}), 400
    for t in tasks.values():
        if t["status"] == "running":
            return jsonify({"error": "Another task is already running. Please wait."}), 409

    task_id = str(uuid.uuid4())[:8]
    user = session.get("email", "unknown")
    tasks[task_id] = {
        "id": task_id, "city": city, "profile": profile, "user": user,
        "status": "queued", "message": "Starting...",
        "created_at": datetime.now().isoformat(),
        "finished_at": None, "duration": None,
    }
    threading.Thread(target=_run_apply, args=(task_id, city, profile, user), daemon=True).start()
    return jsonify({"task_id": task_id})


@app.route("/api/tasks/<task_id>")
@login_required
def api_task(task_id):
    if task_id not in tasks:
        return jsonify({"error": "Not found"}), 404
    return jsonify(tasks[task_id])


@app.route("/api/status")
@login_required
def api_status():
    return jsonify(status_data)


@app.route("/api/history")
@login_required
def api_history():
    return jsonify(status_data.get("history", [])[:50])


@app.route("/api/auth/bolt", methods=["GET"])
@login_required
def api_bolt_auth_get():
    return jsonify({
        "has_cookies": len(bolt_cookies) > 0,
        "cookie_count": len(bolt_cookies),
        "cookie_names": [c["name"] for c in bolt_cookies[:20]],
    })


@app.route("/api/auth/bolt", methods=["POST"])
@login_required
def api_bolt_auth_post():
    global bolt_cookies
    data = request.json or {}
    curl_text = data.get("curl", "")
    raw_cookies = data.get("cookies", "")

    if curl_text:
        parsed = parse_curl_cookies(curl_text)
        if not parsed:
            return jsonify({"error": "Could not parse cookies from cURL command"}), 400
        bolt_cookies = parsed
    elif raw_cookies:
        try:
            bolt_cookies = json.loads(raw_cookies) if isinstance(raw_cookies, str) else raw_cookies
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON"}), 400
    else:
        return jsonify({"error": "Provide 'curl' or 'cookies' field"}), 400

    env_val = _save_bolt_cookies_to_env()
    return jsonify({
        "success": True,
        "cookie_count": len(bolt_cookies),
        "env_value": env_val,
        "hint": "Set BOLT_COOKIES env var on Render to this value for persistence across deploys",
    })


# ── HTML Pages ────────────────────────────────────────────────────────────────

LOGIN_PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>COps — Login</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#080a0f;color:#d1d5db;min-height:100vh;display:flex;justify-content:center;align-items:center}
.box{background:#0f1218;border:1px solid #1c2230;border-radius:12px;padding:32px;width:360px;text-align:center}
h1{font-size:18px;color:#f0f2f5;margin-bottom:4px}
.sub{font-size:11px;color:#5c6370;text-transform:uppercase;letter-spacing:.8px;margin-bottom:24px}
input{width:100%;padding:10px 14px;margin-bottom:12px;background:#080a0f;border:1px solid #1c2230;border-radius:8px;color:#f0f2f5;font-size:13px;outline:none}
input:focus{border-color:#3b82f6}
button{width:100%;padding:10px;background:#3b82f6;color:#fff;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer}
button:hover{background:#60a5fa}
.err{color:#ef4444;font-size:12px;margin-bottom:12px}
</style></head><body>
<div class="box">
<h1>Courier Ops</h1>
<div class="sub">Ukraine Weather Control</div>
<div class="err">{{error}}</div>
<form method="POST" action="/login">
<input name="email" type="email" placeholder="your.name@bolt.eu" required>
<input name="password" type="password" placeholder="Password" required>
<button type="submit">Sign In</button>
</form>
</div>
</body></html>"""

DASHBOARD_PAGE = r"""<!DOCTYPE html>
<html lang="uk"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Courier Ops — Ukraine Weather Control</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#080a0f;--sf:#0f1218;--sf2:#151a22;--bd:#1c2230;--bd2:#252d3b;--tx:#d1d5db;--txb:#f0f2f5;--mu:#5c6370;--mu2:#3d4452;--good:#10b981;--goodH:#34d399;--goodBg:rgba(16,185,129,.08);--bad:#f59e0b;--badH:#fbbf24;--badBg:rgba(245,158,11,.08);--harsh:#ef4444;--harshH:#f87171;--harshBg:rgba(239,68,68,.08);--acc:#3b82f6;--accH:#60a5fa;--accBg:rgba(59,130,246,.06);--r:8px;--r2:12px}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;font-size:13px}
.hdr{background:var(--sf);border-bottom:1px solid var(--bd);padding:14px 28px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:50;flex-wrap:wrap;gap:10px}
.hdr-l{display:flex;align-items:center;gap:14px}
.hdr h1{font-size:16px;font-weight:700;color:var(--txb)}
.pipe{width:1px;height:20px;background:var(--bd2)}
.hdr .sub{font-size:11px;color:var(--mu);text-transform:uppercase;letter-spacing:.8px}
.hdr-r{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.user-badge{font-size:11px;color:var(--acc);background:var(--accBg);padding:4px 12px;border-radius:20px;border:1px solid rgba(59,130,246,.15)}
.hdr-btn{font-size:11px;padding:5px 12px;border-radius:20px;border:1px solid var(--bd);background:transparent;color:var(--mu);cursor:pointer;text-decoration:none;transition:all .15s}
.hdr-btn:hover{border-color:var(--bd2);color:var(--tx)}
.metric{text-align:center}.metric-v{font-size:18px;font-weight:700;color:var(--txb)}.metric-l{font-size:9px;color:var(--mu);text-transform:uppercase;letter-spacing:.6px}
.main{max-width:1500px;margin:0 auto;padding:20px 28px 40px}
.sec{margin-bottom:16px;background:var(--sf);border:1px solid var(--bd);border-radius:var(--r2);overflow:hidden}
.sec-h{display:flex;align-items:center;gap:10px;padding:12px 18px;cursor:pointer;user-select:none;transition:background .15s}
.sec-h:hover{background:var(--sf2)}
.chv{font-size:11px;color:var(--mu);transition:transform .2s;width:16px;text-align:center}
.sec.closed .chv{transform:rotate(-90deg)}
.sec-h h2{font-size:13px;font-weight:600;color:var(--txb);text-transform:uppercase;letter-spacing:.5px}
.cnt{font-size:10px;color:var(--mu);background:var(--bg);padding:2px 8px;border-radius:10px;font-weight:600;margin-left:auto}
.sec-b{overflow:hidden;padding:0 18px 16px}.sec.closed .sec-b{max-height:0!important;padding:0 18px}
.ov-group{margin-bottom:12px}.ov-group:last-child{margin-bottom:0}
.ov-group-h{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;color:var(--mu);margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid var(--bd)}
.ov-pills{display:flex;flex-wrap:wrap;gap:5px}
.pill{display:inline-flex;align-items:center;gap:6px;padding:5px 10px;border-radius:6px;background:var(--bg);border:1px solid var(--bd);font-size:11px}
.pill .dot{width:7px;height:7px;border-radius:50%}
.pill .dot.good{background:var(--good);box-shadow:0 0 6px rgba(16,185,129,.4)}.pill .dot.bad{background:var(--bad);box-shadow:0 0 6px rgba(245,158,11,.4)}.pill .dot.harsh{background:var(--harsh);box-shadow:0 0 6px rgba(239,68,68,.4)}.pill .dot.none{background:var(--mu2)}
.pill .pn{font-weight:600;color:var(--txb)}.pill .pp{font-weight:500}.pill .pp.good{color:var(--good)}.pill .pp.bad{color:var(--bad)}.pill .pp.harsh{color:var(--harsh)}.pill .pp.none{color:var(--mu)}
.pill .pmeta{font-size:10px;color:var(--mu)}.pill .puser{color:var(--acc);font-weight:500}
.auth-banner{padding:10px 18px;border-radius:var(--r);margin-bottom:16px;font-size:12px;display:flex;align-items:center;gap:10px}
.auth-banner.ok{background:var(--goodBg);border:1px solid rgba(16,185,129,.2);color:var(--good)}
.auth-banner.warn{background:var(--harshBg);border:1px solid rgba(239,68,68,.2);color:var(--harsh)}
.auth-banner a{color:inherit;font-weight:600;text-decoration:underline;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
.card{background:var(--bg);border:1px solid var(--bd);border-radius:var(--r);padding:14px;transition:border-color .15s}
.card:hover{border-color:var(--bd2)}
.card.applying{border-color:var(--acc)}
.card-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px}
.city-name{font-size:14px;font-weight:600;color:var(--txb)}
.card-status{display:flex;align-items:center;gap:6px;font-size:10px;color:var(--mu);margin-bottom:10px;min-height:18px}
.card-status .cs-profile{font-weight:500}.card-status .cs-profile.good{color:var(--good)}.card-status .cs-profile.bad{color:var(--bad)}.card-status .cs-profile.harsh{color:var(--harsh)}
.card-status .cs-user{color:var(--acc)}
.btns{display:flex;gap:6px}
.b{flex:1;padding:9px 0;border:none;border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;transition:all .12s;color:#fff}
.b:disabled{opacity:.35;cursor:not-allowed}
.b.good{background:var(--good)}.b.good:hover:not(:disabled){background:var(--goodH)}
.b.bad{background:var(--bad);color:#1a1a2e}.b.bad:hover:not(:disabled){background:var(--badH)}
.b.harsh{background:var(--harsh)}.b.harsh:hover:not(:disabled){background:var(--harshH)}
.b.active-prof{box-shadow:0 0 0 2px var(--txb);transform:scale(1.02)}
.b .sp{display:none;width:12px;height:12px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite;margin:0 auto}
.b.ld .lb{display:none}.b.ld .sp{display:block}
@keyframes spin{to{transform:rotate(360deg)}}
.card-progress{display:none;margin-top:8px;padding:8px;background:var(--accBg);border:1px solid rgba(59,130,246,.2);border-radius:6px;font-size:11px;color:var(--acc);text-align:center}
.card-progress.show{display:flex;align-items:center;justify-content:center;gap:8px}
.card-progress .cp-sp{width:14px;height:14px;border:2px solid rgba(59,130,246,.2);border-top-color:var(--acc);border-radius:50%;animation:spin .7s linear infinite;flex-shrink:0}
.search-bar{display:flex;align-items:center;gap:10px;margin-bottom:16px;background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:8px 14px}
.search-bar input{flex:1;background:none;border:none;color:var(--txb);font-size:13px;outline:none}
.search-bar input::placeholder{color:var(--mu2)}
/* Auth setup */
.auth-box{background:var(--bg);border:1px solid var(--bd);border-radius:var(--r);padding:16px;margin-bottom:12px}
.auth-box h3{font-size:12px;color:var(--txb);margin-bottom:8px}
.auth-box p{font-size:12px;color:var(--tx);line-height:1.7;margin-bottom:8px}
.auth-box code{background:var(--sf2);padding:1px 5px;border-radius:3px;font-size:11px;color:var(--accH)}
.auth-box textarea{width:100%;height:100px;background:var(--sf);border:1px solid var(--bd);border-radius:6px;color:var(--tx);padding:8px;font-size:11px;font-family:monospace;resize:vertical;outline:none}
.auth-box textarea:focus{border-color:var(--acc)}
.auth-box button{padding:8px 20px;background:var(--acc);color:#fff;border:none;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;margin-top:8px}
.auth-box button:hover{background:var(--accH)}
.toasts{position:fixed;bottom:16px;right:16px;z-index:200;display:flex;flex-direction:column;gap:6px}
.toast{padding:10px 16px;border-radius:8px;font-size:12px;font-weight:500;animation:si .2s ease;max-width:400px;box-shadow:0 4px 20px rgba(0,0,0,.4)}
.toast.success{background:var(--good);color:#fff}.toast.error{background:var(--harsh);color:#fff}.toast.info{background:var(--acc);color:#fff}
@keyframes si{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
@media(max-width:640px){.hdr{padding:10px 16px}.main{padding:12px 16px 30px}.grid{grid-template-columns:1fr}}
</style></head><body>
<div class="hdr">
  <div class="hdr-l"><h1>Courier Ops</h1><div class="pipe"></div><span class="sub">Ukraine Weather Control</span></div>
  <div class="hdr-r">
    <div class="metric"><div class="metric-v" id="hCities">37</div><div class="metric-l">Cities</div></div>
    <div class="metric"><div class="metric-v" id="hTracked">0</div><div class="metric-l">Tracked</div></div>
    <span class="user-badge" id="userBadge"></span>
    <a class="hdr-btn" href="/logout">Logout</a>
  </div>
</div>
<div class="main">
  <div id="authBanner"></div>
  <div class="sec" id="sec-overview"><div class="sec-h" onclick="toggleSec('sec-overview')"><span class="chv">&#9662;</span><h2>Active Weather Status</h2><span class="cnt" id="ov-cnt">0</span></div><div class="sec-b" style="max-height:800px" id="overview-body"></div></div>
  <div class="sec closed" id="sec-auth"><div class="sec-h" onclick="toggleSec('sec-auth')"><span class="chv">&#9662;</span><h2>Bolt Auth Setup</h2></div><div class="sec-b" style="max-height:1200px" id="auth-body">
    <div class="auth-box"><h3>How to set up Bolt Admin authentication</h3>
    <p>1. Open <a href="https://admin-panel.bolt.eu" target="_blank">admin-panel.bolt.eu</a> in your browser and log in<br>
    2. Press <code>F12</code> → <code>Network</code> tab → click on any request to bolt.eu<br>
    3. Right-click the request → <strong>Copy → Copy as cURL</strong><br>
    4. Paste the cURL command below and click Save</p>
    <textarea id="curlInput" placeholder="Paste cURL command here..."></textarea>
    <button onclick="saveBoltAuth()">Save Bolt Cookies</button>
    <div id="authResult" style="margin-top:8px;font-size:11px"></div>
    </div>
  </div></div>
  <div class="search-bar"><span style="color:var(--mu);font-size:14px">&#128269;</span><input type="text" id="searchInput" placeholder="Search cities..." oninput="filterCities(this.value)"></div>
  <div id="city-sections"></div>
</div>
<div class="toasts" id="ts"></div>
<script>
const P={good:'Good Weather',bad:'Bad Weather',harsh:'Harsh Weather'};
const PL={good:'Good',bad:'Bad',harsh:'Harsh'};
let allGroups=[],allStatus={},applyingTask=null;

function toggleSec(id){document.getElementById(id).classList.toggle('closed')}
function toast(m,t='info',d=5000){const c=document.getElementById('ts'),e=document.createElement('div');e.className='toast '+t;e.textContent=m;c.appendChild(e);setTimeout(()=>e.remove(),d)}
function timeAgo(iso){if(!iso)return'';const ms=Date.now()-new Date(iso).getTime(),m=Math.floor(ms/60000),h=Math.floor(m/60),d=Math.floor(h/24);if(m<1)return'just now';if(m<60)return m+'m ago';if(h<24)return h+'h '+m%60+'m ago';return d+'d '+h%24+'h ago'}
function cardId(n){return'card-'+n.replace(/[^a-zA-Z0-9]/g,'_')}

async function loadData(){
  const r=await fetch('/api/cities');const d=await r.json();
  allGroups=d.groups;allStatus=d.status;
  renderOverview();renderSections(document.getElementById('searchInput').value);
  document.getElementById('hCities').textContent=allGroups.reduce((s,g)=>s+g.count,0);
  document.getElementById('hTracked').textContent=Object.keys(allStatus).length;
  document.getElementById('ov-cnt').textContent=Object.keys(allStatus).length+' tracked';
}

function renderOverview(){
  document.getElementById('overview-body').innerHTML=allGroups.map(g=>{
    const pills=g.cities.map(c=>{
      const s=allStatus[c.name];const prof=s?.profile||'none';const lbl=s?PL[prof]:'—';
      const meta=s?'<span class="pmeta"><span class="puser">'+s.user.split('@')[0]+'</span> · '+timeAgo(s.timestamp)+'</span>':'';
      return'<span class="pill"><span class="dot '+prof+'"></span><span class="pn">'+c.name+'</span><span class="pp '+prof+'">'+lbl+'</span>'+meta+'</span>';
    }).join('');
    return'<div class="ov-group"><div class="ov-group-h">'+g.name+' · '+g.count+'</div><div class="ov-pills">'+pills+'</div></div>';
  }).join('');
}

function renderSections(filter){
  const fl=(filter||'').toLowerCase();
  const wrap=document.getElementById('city-sections');
  const saved={};wrap.querySelectorAll('.sec').forEach(s=>{saved[s.id]=s.classList.contains('closed')});
  let html='';
  allGroups.forEach((g,i)=>{
    const cities=fl?g.cities.filter(c=>c.name.toLowerCase().includes(fl)):g.cities;
    if(!cities.length)return;
    const id='sec-g-'+i;const closed=id in saved?saved[id]:(i>0&&!fl);
    const cards=cities.map(c=>{
      const s=allStatus[c.name];const cid=cardId(c.name);
      let st='<div class="card-status" style="color:var(--mu2)">No profile set</div>';
      if(s)st='<div class="card-status"><span class="dot '+s.profile+'" style="width:6px;height:6px;border-radius:50%"></span><span class="cs-profile '+s.profile+'">'+P[s.profile]+'</span><span>·</span><span class="cs-user">'+s.user.split('@')[0]+'</span><span>·</span><span style="font-size:9px">'+timeAgo(s.timestamp)+'</span></div>';
      const btns=c.profiles.map(p=>{const act=s?.profile===p;return'<button class="b '+p+(act?' active-prof':'')+'" onclick="apply(\''+c.name+'\',\''+p+'\')"><span class="lb">'+(p.charAt(0).toUpperCase()+p.slice(1))+'</span><div class="sp"></div></button>'}).join('');
      return'<div class="card" id="'+cid+'"><div class="card-top"><span class="city-name">'+c.name+'</span></div>'+st+'<div class="btns">'+btns+'</div><div class="card-progress"><div class="cp-sp"></div><span class="cp-msg"></span></div></div>';
    }).join('');
    html+='<div class="sec '+(closed?'closed':'')+'" id="'+id+'"><div class="sec-h" onclick="toggleSec(\''+id+'\')"><span class="chv">&#9662;</span><h2>'+g.name+'</h2><span class="cnt">'+cities.length+' cities</span></div><div class="sec-b" style="max-height:8000px"><div class="grid">'+cards+'</div></div></div>';
  });
  wrap.innerHTML=html;
}

function filterCities(v){renderSections(v)}

async function apply(city,profile){
  if(applyingTask){toast('Another task is running — please wait','error');return}
  const card=document.getElementById(cardId(city));
  card?.classList.add('applying');
  card?.querySelectorAll('.b').forEach(b=>b.disabled=true);
  const prog=card?.querySelector('.card-progress');
  if(prog){prog.classList.add('show');prog.querySelector('.cp-msg').textContent='Starting...';}

  try{
    const r=await fetch('/api/apply',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({city,profile})});
    const d=await r.json();
    if(!r.ok){toast(d.error||'Error','error');resetCard(city);return}
    applyingTask=d.task_id;
    pollTask(d.task_id,city);
  }catch(e){toast('Network error: '+e.message,'error');resetCard(city)}
}

async function pollTask(taskId,city){
  const card=document.getElementById(cardId(city));
  const prog=card?.querySelector('.card-progress');
  while(true){
    await new Promise(r=>setTimeout(r,2000));
    try{
      const r=await fetch('/api/tasks/'+taskId);const t=await r.json();
      if(prog)prog.querySelector('.cp-msg').textContent=t.message||'Running...';
      if(t.status==='success'){toast(city+' — '+t.message,'success',6000);resetCard(city);applyingTask=null;loadData();return}
      if(t.status==='error'){toast(city+' — '+t.message,'error',8000);resetCard(city);applyingTask=null;return}
    }catch(e){toast('Poll error','error');resetCard(city);applyingTask=null;return}
  }
}

function resetCard(city){
  const card=document.getElementById(cardId(city));
  card?.classList.remove('applying');
  card?.querySelectorAll('.b').forEach(b=>b.disabled=false);
  const prog=card?.querySelector('.card-progress');
  if(prog)prog.classList.remove('show');
}

async function checkBoltAuth(){
  const r=await fetch('/api/auth/bolt');const d=await r.json();
  const el=document.getElementById('authBanner');
  if(d.has_cookies){
    el.innerHTML='<div class="auth-banner ok">Bolt admin auth configured ('+d.cookie_count+' cookies). Apply buttons are fully automatic.</div>';
  }else{
    el.innerHTML='<div class="auth-banner warn">Bolt admin cookies not set. <a onclick="toggleSec(\'sec-auth\');document.getElementById(\'sec-auth\').scrollIntoView({behavior:\'smooth\'})">Set up auth</a> to enable one-click automation.</div>';
  }
}

async function saveBoltAuth(){
  const curl=document.getElementById('curlInput').value;
  if(!curl.trim()){toast('Paste a cURL command first','error');return}
  const r=await fetch('/api/auth/bolt',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({curl})});
  const d=await r.json();const el=document.getElementById('authResult');
  if(d.success){
    el.innerHTML='<span style="color:var(--good)">Saved '+d.cookie_count+' cookies! For persistence, set BOLT_COOKIES env var on Render to:<br><code style="word-break:break-all">'+d.env_value+'</code></span>';
    toast('Bolt auth cookies saved!','success');checkBoltAuth();
  }else{
    el.innerHTML='<span style="color:var(--harsh)">Error: '+d.error+'</span>';
  }
}

const email=document.cookie.split(';').map(c=>c.trim()).find(c=>c.startsWith('session='));
document.getElementById('userBadge').textContent='Loading...';
fetch('/api/status').then(r=>r.json()).then(()=>{
  document.getElementById('userBadge').textContent=document.cookie?'Logged in':'';
});

loadData();checkBoltAuth();
setInterval(loadData,30000);
</script></body></html>"""

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    _load_status()
    _load_bolt_cookies()
    print(f"\n  COps Weather Control — Server Edition")
    print(f"  http://0.0.0.0:{PORT}")
    print(f"  {len(CITIES)} cities | {len(ALLOWED_EMAILS)} users\n")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
