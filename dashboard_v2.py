#!/usr/bin/env python3
"""
Courier Ops Dashboard v2 — Weather Settings Control Panel — Ukraine

Self-contained Flask dashboard.
Posts weather-change commands to Slack; @Delivery Courier Automation Bot
applies the settings in the admin panel.
Shared status tracking via GitHub API (status.json in the repo).
Slack config (channel, templates) fetched from GitHub; bot token stored locally.

Run:   python3 dashboard_v2.py
Open:  http://127.0.0.1:5050
"""

import base64
import json
import subprocess
import threading
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import requests
from flask import Flask, jsonify, request

# ── GitHub constants ──────────────────────────────────────────────────────────

OWNER = "tarasstomin-ua"
REPO = "COps-work-automatization"
GH_API = "https://api.github.com"

# ── Users ─────────────────────────────────────────────────────────────────────

USERS = [
    {"email": "taras.stomin@bolt.eu", "name": "Taras Stomin"},
    {"email": "anna.tiurina@bolt.eu", "name": "Anna Tiurina"},
    {"email": "nataliia.malakova@bolt.eu", "name": "Nataliia Malakova"},
]

# ── City & profile configuration ─────────────────────────────────────────────

CITIES = {
    "Kyiv": {"group": "TOP cities", "group_order": 0, "id": 158, "base": "Kyiv", "jn": "Kyiv", "profiles": ["good", "bad", "harsh"]},
    "Lviv": {"group": "TOP cities", "group_order": 0, "id": 496, "base": "Lviv", "jn": "Lviv", "profiles": ["good", "bad", "harsh"]},
    "Dnipro": {"group": "TOP cities", "group_order": 0, "id": 499, "base": "Dnipro", "jn": "Dnipro", "profiles": ["good", "bad", "harsh"]},
    "Kharkiv": {"group": "TOP cities", "group_order": 0, "id": 491, "base": "Kharkiv", "jn": "Kharkiv", "profiles": ["good", "bad", "harsh"]},
    "Vinnytsia": {"group": "TOP cities", "group_order": 0, "id": 501, "base": "Vinnytsia", "jn": "Vinnytsia", "profiles": ["good", "bad", "harsh"]},
    "Odesa": {"group": "Tier 2", "group_order": 1, "id": 498, "base": "Secondary cities/Tier2 cities/Odesa", "jn": "Odesa", "profiles": ["good", "harsh"]},
    "Kryvyi Rih": {"group": "Tier 2", "group_order": 1, "id": 504, "base": "Secondary cities/Tier2 cities/Kryvyi Rih", "jn": "Kryvyi Rih", "profiles": ["good", "harsh"]},
    "Poltava": {"group": "Tier 2", "group_order": 1, "id": 506, "base": "Secondary cities/Tier2 cities/Poltava", "jn": "Poltava", "profiles": ["good", "harsh"]},
    "Ivano-Frankivsk": {"group": "Tier 2", "group_order": 1, "id": 990, "base": "Secondary cities/Tier2 cities/Ivano-Frankivsk", "jn": "Ivano-Frankivsk", "profiles": ["good", "harsh"]},
    "Chernivtsi": {"group": "Tier 2", "group_order": 1, "id": 1084, "base": "Secondary cities/Tier2 cities/Chernivtsi", "jn": "Chernivtsi", "profiles": ["good", "harsh"]},
    "Irpin": {"group": "Tier 2", "group_order": 1, "id": 1261, "base": "Secondary cities/Tier2 cities/Irpin", "jn": "Irpin", "profiles": ["good", "harsh"]},
    "Cherkasy": {"group": "Tier 2", "group_order": 1, "id": 1087, "base": "Secondary cities/Tier2 cities/Cherkasy", "jn": "Cherkasy", "profiles": ["good", "harsh"]},
    "Zaporizhia": {"group": "Tier 3", "group_order": 2, "id": 500, "base": "Secondary cities/Tier3 cities/Zaporizhia", "jn": "Zaporizhia", "profiles": ["good", "harsh"]},
    "Bila Tserkva": {"group": "Tier 3", "group_order": 2, "id": 1079, "base": "Secondary cities/Tier3 cities/Bila Tserkva", "jn": "Bila Tserkva", "profiles": ["good", "harsh"]},
    "Khmelnytskyi": {"group": "Tier 3", "group_order": 2, "id": 1081, "base": "Secondary cities/Tier3 cities/Khmelnytskyi", "jn": "Khmelnytskyi", "profiles": ["good", "harsh"]},
    "Rivne": {"group": "Tier 3", "group_order": 2, "id": 1086, "base": "Secondary cities/Tier3 cities/Rivne", "jn": "Rivne", "profiles": ["good", "harsh"]},
    "Uzhhorod": {"group": "Tier 3", "group_order": 2, "id": 1131, "base": "Secondary cities/Tier3 cities/Uzhhorod", "jn": "Uzhhorod", "profiles": ["good", "harsh"]},
    "Brovary": {"group": "Tier 3", "group_order": 2, "id": 1259, "base": "Secondary cities/Tier3 cities/Brovary", "jn": "Brovary", "profiles": ["good", "harsh"]},
    "Zhytomyr": {"group": "Tier 3", "group_order": 2, "id": 1083, "base": "Secondary cities/Tier3 cities/Zhytomyr", "jn": "Zhytomyr", "profiles": ["good", "harsh"]},
    "Mykolaiv": {"group": "Rest of cities", "group_order": 3, "id": 503, "base": "Secondary cities/Rest of the cities/Mykolaiv", "jn": "Mykolaiv", "profiles": ["good", "harsh"]},
    "Chernihiv": {"group": "Rest of cities", "group_order": 3, "id": 1076, "base": "Secondary cities/Rest of the cities/Chenihiv", "jn": "Chernihiv", "profiles": ["good", "harsh"]},
    "Sumy": {"group": "Rest of cities", "group_order": 3, "id": 1078, "base": "Secondary cities/Rest of the cities/Sumy", "jn": "Sumy", "profiles": ["good", "harsh"]},
    "Ternopil": {"group": "Rest of cities", "group_order": 3, "id": 1080, "base": "Secondary cities/Rest of the cities/Ternopil", "jn": "Ternopil", "profiles": ["good", "harsh"]},
    "Lutsk": {"group": "Rest of cities", "group_order": 3, "id": 1082, "base": "Secondary cities/Rest of the cities/Lutsk", "jn": "Lutsk", "profiles": ["good", "harsh"]},
    "Kropyvnytskyi": {"group": "Rest of cities", "group_order": 3, "id": 1085, "base": "Secondary cities/Rest of the cities/Kropyvnytskyi", "jn": "Kropyvnytskyi", "profiles": ["good", "harsh"]},
    "Kremenchuk": {"group": "Rest of cities", "group_order": 3, "id": 1088, "base": "Secondary cities/Rest of the cities/Kremenchuk", "jn": "Kremenchuk", "profiles": ["good", "harsh"]},
    "Kamianets-Podilskyi": {"group": "Rest of cities", "group_order": 3, "id": 1132, "base": "Secondary cities/Rest of the cities/Kamianets-Podilskyi", "jn": "Kamianets-Podilskyi", "profiles": ["good", "harsh"]},
    "Pavlohrad": {"group": "Rest of cities", "group_order": 3, "id": 1176, "base": "Secondary cities/Rest of the cities/Pavlohrad", "jn": "Pavlohrad", "profiles": ["good", "harsh"]},
    "Kamianske": {"group": "Rest of cities", "group_order": 3, "id": 1178, "base": "Secondary cities/Rest of the cities/Kamianske", "jn": "Kamianske", "profiles": ["good", "harsh"]},
    "Mukachevo": {"group": "Rest of cities", "group_order": 3, "id": 1179, "base": "Secondary cities/Rest of the cities/Mukachevo", "jn": "Mukachevo", "profiles": ["good", "harsh"]},
    "Boryspil": {"group": "Rest of cities", "group_order": 3, "id": 1220, "base": "Secondary cities/Rest of the cities/Boryspil", "jn": "Boryspil", "profiles": ["good", "harsh"]},
    "Vyshhorod": {"group": "Rest of cities", "group_order": 3, "id": 1262, "base": "Secondary cities/Rest of the cities/Vyshhorod", "jn": "Vyshhorod", "profiles": ["good", "harsh"]},
    "Drohobych": {"group": "Rest of cities", "group_order": 3, "id": 1348, "base": "Secondary cities/Rest of the cities/Drohobych", "jn": "Drohobych", "profiles": ["good", "harsh"]},
    "Truskavets": {"group": "Rest of cities", "group_order": 3, "id": 1357, "base": "Secondary cities/Rest of the cities/Truskavets", "jn": "Truskavets", "profiles": ["good", "harsh"]},
    "Kovel": {"group": "Rest of cities", "group_order": 3, "id": 2170, "base": "Secondary cities/Rest of the cities/Kovel", "jn": "Kovel", "profiles": ["good", "harsh"]},
    "Oleksandriia": {"group": "Rest of cities", "group_order": 3, "id": 2171, "base": "Secondary cities/Rest of the cities/Oleksandriia", "jn": "Oleksandriia", "profiles": ["good", "harsh"]},
    "Kolomyia": {"group": "Rest of cities", "group_order": 3, "id": 2499, "base": "Secondary cities/Rest of the cities/Kolomyia", "jn": "Kolomyia", "profiles": ["good", "harsh"]},
}

VALID_PROFILES = {"good", "bad", "harsh"}

# ── Flask app ─────────────────────────────────────────────────────────────────

app = Flask(__name__)
tasks: dict = {}
log_lock = threading.Lock()

LOG_FILE = Path(__file__).parent / ".cops_log.json"
CONFIG_FILE = Path(__file__).parent / ".cops_config.json"

# ── Config helpers ────────────────────────────────────────────────────────────

def _get_gh_token():
    """Try to get token from gh CLI, fall back to config file."""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    home_gh = Path.home() / "bin" / "gh"
    if home_gh.exists():
        try:
            result = subprocess.run(
                [str(home_gh), "auth", "token"], capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
    return ""


def _load_config():
    try:
        cfg = json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else {}
    except Exception:
        cfg = {}
    if not cfg.get("pat"):
        gh_token = _get_gh_token()
        if gh_token:
            cfg["pat"] = gh_token
    return cfg


def _save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

# ── Log helpers ───────────────────────────────────────────────────────────────

def _load_log() -> list:
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_log(entries: list):
    with open(LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def _log_action(city: str, profile: str, status: str, duration: float = 0, user: str = ""):
    with log_lock:
        entries = _load_log()
        entries.append({
            "city": city, "profile": profile, "status": status,
            "user": user,
            "duration_seconds": round(duration, 1),
            "timestamp": datetime.now().isoformat(),
        })
        _save_log(entries)


def _get_active_profiles() -> dict:
    log = _load_log()
    active: dict = {}
    for entry in reversed(log):
        if entry["status"] == "success" and entry["city"] not in active:
            active[entry["city"]] = {
                "profile": entry["profile"],
                "since": entry["timestamp"],
                "user": entry.get("user", ""),
            }
    return active


def _compute_durations(cutoff: datetime) -> tuple:
    now = datetime.now()
    log = _load_log()
    city_events: dict = {}
    for e in log:
        if e["status"] != "success":
            continue
        city_events.setdefault(e["city"], []).append(e)
    for city in city_events:
        city_events[city].sort(key=lambda x: x["timestamp"])

    city_breakdown: dict = {}
    profile_hours = {"good": 0.0, "bad": 0.0, "harsh": 0.0}

    for city, events in city_events.items():
        durations = {"good": 0.0, "bad": 0.0, "harsh": 0.0}
        for i, evt in enumerate(events):
            start = datetime.fromisoformat(evt["timestamp"])
            end = datetime.fromisoformat(events[i + 1]["timestamp"]) if i + 1 < len(events) else now
            cs, ce = max(start, cutoff), min(end, now)
            if ce > cs:
                hours = (ce - cs).total_seconds() / 3600
                p = evt["profile"]
                if p in durations:
                    durations[p] += hours
                    profile_hours[p] += hours
        city_breakdown[city] = {k: round(v, 2) for k, v in durations.items()}

    return city_breakdown, {k: round(v, 2) for k, v in profile_hours.items()}

# ── Slack config fetcher ──────────────────────────────────────────────────────

_slack_cache: dict = {"data": None, "ts": 0}

def _fetch_slack_config() -> dict:
    now = time.time()
    if _slack_cache["data"] and now - _slack_cache["ts"] < 300:
        return _slack_cache["data"]
    cfg = _load_config()
    pat = cfg.get("pat", "")
    if pat:
        try:
            headers = {"Authorization": f"Bearer {pat}", "Accept": "application/vnd.github+json"}
            r = requests.get(
                f"{GH_API}/repos/{OWNER}/{REPO}/contents/slack_config.json",
                headers=headers, timeout=10,
            )
            if r.ok:
                content = base64.b64decode(r.json()["content"]).decode()
                _slack_cache["data"] = json.loads(content)
                _slack_cache["ts"] = now
                return _slack_cache["data"]
        except Exception:
            pass
    url = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/slack_config.json?t={now}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    _slack_cache["data"] = r.json()
    _slack_cache["ts"] = now
    return _slack_cache["data"]


def _post_to_slack(city: str, profile: str, user: str) -> tuple:
    cfg = _load_config()
    token = cfg.get("slack_token", "")
    if not token:
        return False, "No Slack token configured. Paste it in the dashboard header."

    slack_cfg = _fetch_slack_config()
    channel = slack_cfg["channel_id"]
    templates = slack_cfg.get("templates", {})

    city_templates = templates.get(city)
    if not city_templates:
        return False, f"No Slack template found for city: {city}"
    message = city_templates.get(profile)
    if not message:
        return False, f"No Slack template for {city}/{profile}"

    text = message.replace("@Delivery Courier Automation Bot", "<@U0AEPHE0CHH>")

    r = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"channel": channel, "text": text},
        timeout=15,
    )
    body = r.json()
    if not body.get("ok"):
        return False, f"Slack API error: {body.get('error', 'unknown')}"
    return True, "Message posted to Slack successfully!"

# ── GitHub shared status ──────────────────────────────────────────────────────

def _pull_github_status():
    cfg = _load_config()
    pat = cfg.get("pat", "")
    try:
        if pat:
            headers = {"Authorization": f"Bearer {pat}", "Accept": "application/vnd.github+json"}
            r = requests.get(
                f"{GH_API}/repos/{OWNER}/{REPO}/contents/status.json",
                headers=headers, timeout=10,
            )
            if r.ok:
                content = base64.b64decode(r.json()["content"]).decode()
                return json.loads(content)
        r = requests.get(
            f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/status.json?t={time.time()}",
            timeout=10,
        )
        return r.json() if r.ok else {}
    except Exception:
        return {}


def _push_github_status(city, profile, user):
    cfg = _load_config()
    pat = cfg.get("pat", "")
    if not pat:
        return
    try:
        headers = {"Authorization": f"Bearer {pat}", "Accept": "application/vnd.github+json"}
        fr = requests.get(
            f"{GH_API}/repos/{OWNER}/{REPO}/contents/status.json",
            headers=headers, timeout=10,
        )
        sha = None
        remote = {"cities": {}, "history": [], "last_updated": None}
        if fr.ok:
            d = fr.json()
            sha = d["sha"]
            remote = json.loads(base64.b64decode(d["content"]).decode())

        ts = datetime.now().isoformat()
        remote["cities"][city] = {"profile": profile, "user": user, "timestamp": ts}
        remote.setdefault("history", []).insert(0, {
            "city": city, "profile": profile, "user": user, "timestamp": ts,
        })
        remote["history"] = remote["history"][:300]
        remote["last_updated"] = ts

        body = {
            "message": f"Status: {city} -> {profile} by {user}",
            "content": base64.b64encode(json.dumps(remote, indent=2).encode()).decode(),
        }
        if sha:
            body["sha"] = sha
        requests.put(
            f"{GH_API}/repos/{OWNER}/{REPO}/contents/status.json",
            headers=headers, json=body, timeout=10,
        )
    except Exception as e:
        print(f"  Push status error: {e}")

# ── Task runner ───────────────────────────────────────────────────────────────

def _run_task(task_id: str, city_name: str, profile: str, user: str):
    start = time.time()
    try:
        tasks[task_id]["status"] = "running"
        tasks[task_id]["message"] = f"Posting to Slack: {city_name} → {profile}..."

        success, message = _post_to_slack(city_name, profile, user)
        elapsed = time.time() - start

        tasks[task_id].update(
            status="success" if success else "error",
            finished_at=datetime.now().isoformat(),
            duration=round(elapsed, 1),
            message=message,
        )
        _log_action(city_name, profile, "success" if success else "error", elapsed, user)

        if success:
            _push_github_status(city_name, profile, user)

    except Exception as exc:
        elapsed = time.time() - start
        tasks[task_id].update(
            status="error", message=str(exc), finished_at=datetime.now().isoformat(),
        )
        _log_action(city_name, profile, "error", elapsed, user)

# ── API routes ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return HTML_PAGE


@app.route("/api/cities")
def api_cities():
    group_map: dict = {}
    for name, cfg in CITIES.items():
        g = cfg["group"]
        if g not in group_map:
            group_map[g] = {"order": cfg["group_order"], "cities": []}
        group_map[g]["cities"].append({"name": name, "profiles": cfg["profiles"]})
    groups = sorted(group_map.items(), key=lambda x: x[1]["order"])

    gh = _pull_github_status()
    active = {}
    for city, info in gh.get("cities", {}).items():
        active[city] = {
            "profile": info["profile"],
            "since": info["timestamp"],
            "user": info.get("user", ""),
        }

    return jsonify({
        "groups": [{"name": k, "count": len(v["cities"]), "cities": v["cities"]} for k, v in groups],
        "active_profiles": active,
    })


@app.route("/api/apply", methods=["POST"])
def api_apply():
    data = request.json or {}
    city = data.get("city", "")
    profile = data.get("profile", "")
    user = data.get("user", "")
    if not user:
        return jsonify({"error": "Select your name first"}), 400
    if city not in CITIES:
        return jsonify({"error": f"Unknown city: {city}"}), 400
    if profile not in VALID_PROFILES:
        return jsonify({"error": f"Unknown profile: {profile}"}), 400
    avail = CITIES[city]["profiles"]
    if profile not in avail:
        return jsonify({"error": f"Profile '{profile}' not available for {city}"}), 400

    task_id = str(uuid.uuid4())[:8]
    tasks[task_id] = {
        "id": task_id, "city": city, "profile": profile, "user": user,
        "status": "queued", "message": "Starting...",
        "created_at": datetime.now().isoformat(),
        "finished_at": None, "duration": None,
    }
    threading.Thread(target=_run_task, args=(task_id, city, profile, user), daemon=True).start()
    return jsonify({"task_id": task_id})


@app.route("/api/tasks/<task_id>")
def api_task(task_id):
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(tasks[task_id])


@app.route("/api/stats")
def api_stats():
    period = request.args.get("period", "all")
    now = datetime.now()
    cutoffs = {
        "hour": now - timedelta(hours=1),
        "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
        "week": now - timedelta(weeks=1),
        "month": now - timedelta(days=30),
        "year": now - timedelta(days=365),
        "all": datetime.min,
    }
    cutoff = cutoffs.get(period, datetime.min)
    city_breakdown, profile_hours = _compute_durations(cutoff)
    total_hours = sum(profile_hours.values())
    most_used = max(profile_hours, key=profile_hours.get) if total_hours > 0 else None
    log = _load_log()
    applies = len([e for e in log if e["status"] == "success" and datetime.fromisoformat(e["timestamp"]) >= cutoff])
    return jsonify({
        "period": period, "total_hours": round(total_hours, 2),
        "profile_hours": profile_hours, "city_breakdown": city_breakdown,
        "total_applies": applies, "most_used_profile": most_used,
    })


@app.route("/api/history")
def api_history():
    return jsonify(_load_log()[-50:])


@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "GET":
        cfg = _load_config()
        has_pat = bool(cfg.get("pat", ""))
        pat_source = "gh CLI" if (has_pat and not CONFIG_FILE.exists()) or (has_pat and "pat" not in (json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else {})) else ("saved" if has_pat else "none")
        has_slack = bool(cfg.get("slack_token", ""))
        return jsonify({
            "user": cfg.get("user", ""),
            "has_pat": has_pat, "pat_source": pat_source,
            "has_slack": has_slack,
        })
    data = request.json or {}
    cfg = _load_config()
    if "user" in data:
        cfg["user"] = data["user"]
    if "pat" in data:
        cfg["pat"] = data["pat"]
    if "slack_token" in data:
        cfg["slack_token"] = data["slack_token"]
    _save_config(cfg)
    return jsonify({"ok": True})


@app.route("/api/shared-status")
def api_shared_status():
    return jsonify(_pull_github_status())

# ── Slack OAuth flow ──────────────────────────────────────────────────────────

SLACK_OAUTH_REDIRECT = "http://localhost:5050/slack/callback"

@app.route("/slack/authorize")
def slack_authorize():
    cfg = _load_config()
    cid = cfg.get("slack_client_id", "")
    if not cid:
        return "Slack client_id not configured in .cops_config.json", 400
    url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={cid}"
        f"&user_scope=chat:write"
        f"&redirect_uri={SLACK_OAUTH_REDIRECT}"
    )
    return f'<html><head><meta http-equiv="refresh" content="0;url={url}"></head></html>'


@app.route("/slack/callback")
def slack_callback():
    code = request.args.get("code")
    error = request.args.get("error")
    if error:
        return f"""<html><body style="background:#0f0f1a;color:#ef4444;font-family:Inter,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;text-align:center">
        <div><h2>Slack Authorization Failed</h2><p>{error}</p><a href="/" style="color:#8b5cf6">Back to Dashboard</a></div></body></html>"""
    if not code:
        return "Missing code parameter", 400

    cfg = _load_config()
    cid = cfg.get("slack_client_id", "")
    csecret = cfg.get("slack_client_secret", "")
    if not cid or not csecret:
        return "Slack OAuth credentials not configured", 400

    r = requests.post("https://slack.com/api/oauth.v2.access", data={
        "client_id": cid,
        "client_secret": csecret,
        "code": code,
        "redirect_uri": SLACK_OAUTH_REDIRECT,
    }, timeout=15)
    body = r.json()

    if not body.get("ok"):
        err = body.get("error", "unknown")
        return f"""<html><body style="background:#0f0f1a;color:#ef4444;font-family:Inter,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;text-align:center">
        <div><h2>Token Exchange Failed</h2><p>{err}</p><a href="/" style="color:#8b5cf6">Back to Dashboard</a></div></body></html>"""

    user_token = body.get("authed_user", {}).get("access_token", "")
    if not user_token:
        return "No user token received from Slack", 400

    cfg["slack_token"] = user_token
    _save_config(cfg)

    return """<html><body style="background:#0f0f1a;color:#10b981;font-family:Inter,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;text-align:center">
    <div><h2>Slack Connected!</h2><p style="color:#c8cad0">Your Slack account is now linked. Messages will be sent on your behalf.</p>
    <a href="/" style="color:#8b5cf6;font-size:16px;text-decoration:none">&#8592; Back to Dashboard</a></div></body></html>"""

# ── City timeline API ──────────────────────────────────────────────────────────

@app.route("/api/city-timeline")
def api_city_timeline():
    city = request.args.get("city", "")
    period = request.args.get("period", "day")
    now = datetime.now()
    cutoffs = {"day": now - timedelta(days=1), "week": now - timedelta(weeks=1), "month": now - timedelta(days=30)}
    cutoff = cutoffs.get(period, now - timedelta(days=1))
    log = _load_log()
    events = sorted(
        [e for e in log if e["city"] == city and e["status"] == "success" and datetime.fromisoformat(e["timestamp"]) >= cutoff],
        key=lambda x: x["timestamp"],
    )
    hours = {}
    total_h = max((now - cutoff).total_seconds() / 3600, 1)
    for i, evt in enumerate(events):
        start = max(datetime.fromisoformat(evt["timestamp"]), cutoff)
        end = datetime.fromisoformat(events[i + 1]["timestamp"]) if i + 1 < len(events) else now
        cs, ce = max(start, cutoff), min(end, now)
        if ce > cs:
            cur = cs
            while cur < ce:
                h_key = cur.strftime("%Y-%m-%d %H:00")
                bucket = hours.setdefault(h_key, {"good": 0, "bad": 0, "harsh": 0})
                next_h = (cur + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                seg_end = min(next_h, ce)
                minutes = (seg_end - cur).total_seconds() / 60
                bucket[evt["profile"]] = bucket.get(evt["profile"], 0) + minutes
                cur = seg_end
    timeline = []
    t = cutoff.replace(minute=0, second=0, microsecond=0)
    while t <= now:
        h_key = t.strftime("%Y-%m-%d %H:00")
        h_data = hours.get(h_key, {"good": 0, "bad": 0, "harsh": 0})
        dominant = max(h_data, key=h_data.get) if sum(h_data.values()) > 0 else "none"
        intensity = min(sum(h_data.values()) / 60, 1.0)
        timeline.append({"hour": h_key, "dominant": dominant, "intensity": round(intensity, 2), "minutes": h_data})
        t += timedelta(hours=1)
    profile_totals = {"good": 0.0, "bad": 0.0, "harsh": 0.0}
    for evt_i, evt in enumerate(events):
        start = max(datetime.fromisoformat(evt["timestamp"]), cutoff)
        end = datetime.fromisoformat(events[evt_i + 1]["timestamp"]) if evt_i + 1 < len(events) else now
        cs2, ce2 = max(start, cutoff), min(end, now)
        if ce2 > cs2:
            profile_totals[evt["profile"]] += (ce2 - cs2).total_seconds() / 3600
    return jsonify({
        "city": city, "period": period,
        "timeline": timeline,
        "totals": {k: round(v, 2) for k, v in profile_totals.items()},
        "total_hours": round(total_h, 2),
    })

# ── Embedded HTML ─────────────────────────────────────────────────────────────

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Courier Ops — Ukraine Weather Control</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0f0f1a;--card:#1a1a2e;--card2:#1f1f36;--bd:#2a2a40;--bd2:#353550;
  --tx:#c8cad0;--txb:#f0f1f4;--mu:#6b6b80;--mu2:#45455a;
  --good:#10b981;--goodH:#34d399;--goodBg:rgba(16,185,129,.1);
  --bad:#f59e0b;--badH:#fbbf24;--badBg:rgba(245,158,11,.1);
  --harsh:#ef4444;--harshH:#f87171;--harshBg:rgba(239,68,68,.1);
  --accent:#8b5cf6;--accentH:#a78bfa;--accentBg:rgba(139,92,246,.08);
  --r:8px;--r2:12px;
}
body{font-family:'Inter',system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;font-size:13px;-webkit-font-smoothing:antialiased}
::selection{background:var(--accent);color:#fff}

.hdr{border-bottom:1px solid var(--bd);padding:0 28px;height:56px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:50;backdrop-filter:blur(16px);background:rgba(26,26,46,.88)}
.hdr-l{display:flex;align-items:center;gap:14px}
.logo{font-size:17px;font-weight:800;color:var(--txb);letter-spacing:-.4px}
.logo em{font-style:normal;color:var(--accent)}
.hdr .pipe{width:1px;height:22px;background:var(--bd2)}
.hdr .sub{font-size:10px;color:var(--mu);text-transform:uppercase;letter-spacing:1px;font-weight:600}
.hdr-r{display:flex;align-items:center;gap:12px}
.hdr select{background:var(--bg);border:1px solid var(--bd);color:var(--txb);padding:6px 12px;border-radius:var(--r);font-size:12px;font-weight:500;font-family:inherit;cursor:pointer;outline:none;transition:border-color .15s}
.hdr select:hover,.hdr select:focus{border-color:var(--accent)}
.pat-badge{font-size:10px;color:var(--mu);padding:5px 12px;background:var(--bg);border:1px solid var(--bd);border-radius:var(--r);font-weight:500;white-space:nowrap}
.pat-input{background:var(--bg);border:1px solid var(--bd);color:var(--txb);padding:6px 12px;border-radius:var(--r);font-size:11px;width:180px;font-family:'SF Mono',SFMono-Regular,Menlo,monospace;outline:none;transition:border-color .15s}
.pat-input:focus{border-color:var(--accent)}
.hdr-stat{text-align:center;padding:0 6px}
.hdr-stat-v{font-size:18px;font-weight:800;color:var(--txb);line-height:1.1}
.hdr-stat-l{font-size:8px;color:var(--mu);text-transform:uppercase;letter-spacing:.8px;font-weight:600;margin-top:2px}
.live{display:flex;align-items:center;gap:6px;font-size:11px;font-weight:600;color:var(--good);padding:5px 14px;background:var(--goodBg);border-radius:20px;border:1px solid rgba(16,185,129,.18)}
.live-dot{width:7px;height:7px;border-radius:50%;background:var(--good);animation:lp 2s ease-in-out infinite}
@keyframes lp{0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,.35)}50%{box-shadow:0 0 0 6px rgba(16,185,129,0)}}
.live.busy{color:var(--accent);background:var(--accentBg);border-color:rgba(139,92,246,.2)}
.live.busy .live-dot{background:var(--accent);animation:lp2 1.4s ease-in-out infinite}
@keyframes lp2{0%,100%{box-shadow:0 0 0 0 rgba(139,92,246,.35)}50%{box-shadow:0 0 0 6px rgba(139,92,246,0)}}

.main{max-width:1480px;margin:0 auto;padding:20px 28px 60px}

.sec{margin-bottom:16px;background:var(--card);border:1px solid var(--bd);border-radius:var(--r2);overflow:hidden}
.sec-h{display:flex;align-items:center;gap:10px;padding:14px 20px;cursor:pointer;user-select:none;transition:background .15s}
.sec-h:hover{background:var(--card2)}
.chv{font-size:11px;color:var(--mu);transition:transform .25s;width:16px;text-align:center}
.sec.closed .chv{transform:rotate(-90deg)}
.sec-h h2{font-size:12px;font-weight:700;color:var(--txb);text-transform:uppercase;letter-spacing:.7px}
.cnt{font-size:10px;color:var(--mu);background:var(--bg);padding:3px 10px;border-radius:10px;font-weight:600;margin-left:auto}
.sec-b{transition:max-height .35s ease,padding .2s ease;overflow:hidden;padding:0 20px 18px}
.sec.closed .sec-b{max-height:0!important;padding-top:0;padding-bottom:0}

.ov-tier{margin-bottom:14px}
.ov-tier:last-child{margin-bottom:0}
.ov-tier-h{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:var(--mu);margin-bottom:8px;padding-bottom:5px;border-bottom:1px solid var(--bd);cursor:pointer;display:flex;align-items:center;gap:6px}
.ov-tier-h .chv2{font-size:9px;transition:transform .2s}
.ov-tier.cl .ov-tier-h .chv2{transform:rotate(-90deg)}
.ov-tier.cl .ov-pills{display:none}
.ov-pills{display:flex;flex-wrap:wrap;gap:5px}
.pill{display:inline-flex;align-items:center;gap:6px;padding:5px 12px 5px 9px;border-radius:var(--r);background:var(--bg);border:1px solid var(--bd);font-size:11px;transition:all .15s}
.pill:hover{border-color:var(--bd2);background:var(--card2)}
.pill .d{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.pill .d.good{background:var(--good);box-shadow:0 0 6px rgba(16,185,129,.45)}
.pill .d.bad{background:var(--bad);box-shadow:0 0 6px rgba(245,158,11,.45)}
.pill .d.harsh{background:var(--harsh);box-shadow:0 0 6px rgba(239,68,68,.45)}
.pill .d.none{background:var(--mu2)}
.pill .pn{font-weight:600;color:var(--txb)}
.pill .pp{font-weight:500}
.pill .pp.good{color:var(--good)}.pill .pp.bad{color:var(--bad)}.pill .pp.harsh{color:var(--harsh)}.pill .pp.none{color:var(--mu)}
.pill .pt{font-size:10px;color:var(--mu);margin-left:2px;font-weight:500}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(275px,1fr));gap:10px}
.card{background:var(--bg);border:1px solid var(--bd);border-radius:var(--r2);padding:16px;transition:all .15s}
.card:hover{border-color:var(--bd2);box-shadow:0 2px 16px rgba(0,0,0,.2)}
.card-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px}
.city{font-size:14px;font-weight:700;color:var(--txb)}
.ap{font-size:11px;color:var(--mu);display:flex;align-items:center;gap:6px;min-height:18px;margin-bottom:12px;flex-wrap:wrap}
.ap .pname{color:var(--tx);font-weight:600}
.ap .since{font-size:10px;color:var(--accent);font-weight:500;margin-left:auto}
.btns{display:flex;gap:6px}
.b{flex:1;padding:9px 0;border:none;border-radius:var(--r);font-size:11px;font-weight:700;cursor:pointer;transition:all .12s;color:#fff;letter-spacing:.3px;font-family:inherit}
.b:disabled{opacity:.3;cursor:not-allowed}
.b.good{background:var(--good)}.b.good:hover:not(:disabled){background:var(--goodH);transform:translateY(-1px)}
.b.bad{background:var(--bad);color:#1a1a2e}.b.bad:hover:not(:disabled){background:var(--badH);transform:translateY(-1px)}
.b.harsh{background:var(--harsh)}.b.harsh:hover:not(:disabled){background:var(--harshH);transform:translateY(-1px)}
.b .sp{display:none;width:12px;height:12px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite;margin:0 auto}
.b.ld .lb{display:none}.b.ld .sp{display:block}
@keyframes spin{to{transform:rotate(360deg)}}

.an-sum{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px}
.sc{background:var(--bg);border-radius:var(--r2);padding:16px;text-align:center;border:1px solid var(--bd)}
.sv{font-size:22px;font-weight:800;color:var(--txb);margin-bottom:3px}
.sl{font-size:9px;color:var(--mu);text-transform:uppercase;letter-spacing:.7px;font-weight:600}
.tabs{display:flex;gap:2px;margin-bottom:16px;background:var(--bg);padding:3px;border-radius:var(--r);width:fit-content;border:1px solid var(--bd)}
.tab{padding:6px 16px;border:none;border-radius:6px;background:transparent;color:var(--mu);font-size:12px;cursor:pointer;transition:all .15s;font-weight:600;font-family:inherit}
.tab:hover{color:var(--tx)}.tab.on{background:var(--accent);color:#fff}
.bar{display:flex;height:22px;border-radius:11px;overflow:hidden;background:var(--bg);border:1px solid var(--bd);margin-bottom:6px}
.seg{display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;color:#fff;transition:width .4s ease;min-width:0}
.seg.good{background:var(--good)}.seg.bad{background:var(--bad);color:#1a1a2e}.seg.harsh{background:var(--harsh)}
.legend{display:flex;gap:18px;margin-bottom:16px;font-size:11px;color:var(--mu);font-weight:500}
.legend i{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:5px;vertical-align:middle}
.tbl-wrap{max-height:450px;overflow-y:auto;border:1px solid var(--bd);border-radius:var(--r2)}
.tbl-wrap::-webkit-scrollbar{width:5px}.tbl-wrap::-webkit-scrollbar-track{background:var(--bg)}.tbl-wrap::-webkit-scrollbar-thumb{background:var(--bd2);border-radius:3px}
table{width:100%;border-collapse:separate;border-spacing:0}
th{text-align:left;font-size:9px;color:var(--mu);text-transform:uppercase;letter-spacing:.6px;padding:8px 12px;border-bottom:1px solid var(--bd);background:var(--card);position:sticky;top:0;z-index:1;font-weight:700}
td{padding:8px 12px;font-size:12px;border-bottom:1px solid var(--bd)}
tr:last-child td{border-bottom:none}
tr.city-row{cursor:pointer;transition:background .12s}
tr.city-row:hover{background:var(--card2)}
.ct{font-weight:600;font-size:11px}
.ct.good{color:var(--good)}.ct.bad{color:var(--bad)}.ct.harsh{color:var(--harsh)}
.mini-bar{display:flex;height:4px;border-radius:2px;overflow:hidden;background:var(--bd);width:100%;max-width:120px;margin-top:2px}
.mini-seg{height:100%;transition:width .3s}
.mini-seg.good{background:var(--good)}.mini-seg.bad{background:var(--bad)}.mini-seg.harsh{background:var(--harsh)}

.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:100;justify-content:center;align-items:center;backdrop-filter:blur(6px)}
.overlay.open{display:flex}
.modal{background:var(--card);border:1px solid var(--bd2);border-radius:var(--r2);padding:28px;max-width:380px;width:92%;text-align:center}
.modal h3{font-size:16px;font-weight:700;margin-bottom:6px;color:var(--txb)}
.modal p{color:var(--mu);margin-bottom:20px;font-size:12px;line-height:1.5}
.ma{display:flex;gap:10px;justify-content:center}
.mb{padding:9px 24px;border-radius:var(--r);border:none;font-size:12px;font-weight:700;cursor:pointer;font-family:inherit;transition:all .12s}
.mb.cn{background:var(--bg);color:var(--tx);border:1px solid var(--bd)}.mb.cn:hover{border-color:var(--bd2)}
.mb.ok{background:var(--accent);color:#fff}.mb.ok:hover{background:var(--accentH)}

.detail-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:110;justify-content:center;align-items:center;backdrop-filter:blur(6px)}
.detail-overlay.open{display:flex}
.detail-modal{background:var(--card);border:1px solid var(--bd2);border-radius:var(--r2);padding:28px 32px;max-width:660px;width:94%;max-height:85vh;overflow-y:auto}
.detail-modal::-webkit-scrollbar{width:5px}.detail-modal::-webkit-scrollbar-thumb{background:var(--bd2);border-radius:3px}
.dm-header{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:20px}
.dm-header h3{font-size:18px;font-weight:800;color:var(--txb);margin-bottom:4px}
.dm-period{font-size:11px;color:var(--mu);font-weight:600;text-transform:uppercase;letter-spacing:.5px;display:inline-block;background:var(--bg);padding:4px 10px;border-radius:6px}
.dm-close{background:var(--bg);border:1px solid var(--bd);color:var(--mu);width:32px;height:32px;border-radius:8px;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;transition:all .12s;flex-shrink:0}
.dm-close:hover{color:var(--txb);border-color:var(--bd2)}
.dm-totals{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:24px}
.dm-total{background:var(--bg);border:1px solid var(--bd);border-radius:var(--r);padding:14px;text-align:center}
.dm-total-v{font-size:20px;font-weight:800;margin-bottom:2px}
.dm-total-l{font-size:9px;color:var(--mu);text-transform:uppercase;letter-spacing:.5px;font-weight:600}
.dm-total.good .dm-total-v{color:var(--good)}.dm-total.bad .dm-total-v{color:var(--bad)}.dm-total.harsh .dm-total-v{color:var(--harsh)}
.heatmap-label{font-size:11px;font-weight:700;color:var(--txb);margin-bottom:10px;text-transform:uppercase;letter-spacing:.5px}
.heatmap-wrap{margin-bottom:10px}
.heatmap{display:flex;flex-wrap:wrap;gap:2px}
.hm-cell{width:22px;height:22px;border-radius:4px;position:relative;transition:transform .1s,box-shadow .1s}
.hm-cell:hover{transform:scale(1.35);z-index:2;box-shadow:0 0 8px rgba(0,0,0,.4)}
.hm-tip{display:none;position:absolute;bottom:calc(100% + 8px);left:50%;transform:translateX(-50%);background:var(--card);border:1px solid var(--bd2);border-radius:6px;padding:6px 10px;font-size:10px;white-space:nowrap;z-index:10;color:var(--txb);box-shadow:0 4px 16px rgba(0,0,0,.5);pointer-events:none;font-weight:500}
.hm-cell:hover .hm-tip{display:block}
.hm-times{display:flex;justify-content:space-between;font-size:9px;color:var(--mu);font-weight:600;margin-top:4px;padding:0 2px}
.hm-day-label{font-size:10px;color:var(--mu);font-weight:600;margin-bottom:4px;margin-top:12px}
.hm-legend{display:flex;gap:16px;font-size:10px;color:var(--mu);font-weight:500;margin-top:16px;padding-top:12px;border-top:1px solid var(--bd)}
.hm-legend span{display:flex;align-items:center;gap:4px}
.hm-legend i{width:10px;height:10px;border-radius:3px;display:inline-block}

.toasts{position:fixed;bottom:20px;right:20px;z-index:200;display:flex;flex-direction:column;gap:8px}
.toast{padding:12px 18px;border-radius:var(--r);font-size:12px;font-weight:600;animation:si .25s ease;max-width:380px;box-shadow:0 6px 24px rgba(0,0,0,.5);font-family:inherit}
.toast.success{background:var(--good);color:#fff}
.toast.error{background:var(--harsh);color:#fff}
.toast.info{background:var(--accent);color:#fff}
@keyframes si{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
</style>
</head>
<body>

<div class="hdr">
  <div class="hdr-l">
    <span class="logo">Courier<em>Ops</em></span>
    <div class="pipe"></div>
    <span class="sub">Ukraine Weather Control</span>
  </div>
  <div class="hdr-r">
    <select id="userSel">
      <option value="">-- Select user --</option>
      <option value="taras.stomin@bolt.eu">Taras Stomin</option>
      <option value="anna.tiurina@bolt.eu">Anna Tiurina</option>
      <option value="nataliia.malakova@bolt.eu">Nataliia Malakova</option>
    </select>
    <span class="pat-badge" id="patStatus"></span>
    <input class="pat-input" id="patIn" type="password" placeholder="Paste GitHub PAT" style="display:none" />
    <span class="pat-badge" id="slackStatus"></span>
    <a id="slackConnect" href="/slack/authorize" class="pat-badge" style="display:none;text-decoration:none;color:var(--accent);border-color:var(--accent);cursor:pointer">Connect Slack</a>
    <div class="hdr-stat"><div class="hdr-stat-v" id="hCities">37</div><div class="hdr-stat-l">Cities</div></div>
    <div class="hdr-stat"><div class="hdr-stat-v" id="hActive">0</div><div class="hdr-stat-l">Active</div></div>
    <div class="live" id="liveStatus"><span class="live-dot"></span><span id="liveText">Live</span></div>
  </div>
</div>

<div class="main">
  <div class="sec" id="sec-overview">
    <div class="sec-h" onclick="toggleSec('sec-overview')"><span class="chv">&#9662;</span><h2>Active Weather Status</h2><span class="cnt" id="ov-cnt"></span></div>
    <div class="sec-b" id="overview-body" style="max-height:800px"></div>
  </div>

  <div id="city-sections"></div>

  <div class="sec" id="sec-analytics">
    <div class="sec-h" onclick="toggleSec('sec-analytics')"><span class="chv">&#9662;</span><h2>Usage Analytics</h2></div>
    <div class="sec-b" style="max-height:6000px">
      <div class="tabs" id="tabs">
        <button class="tab on" data-p="day">Day</button>
        <button class="tab" data-p="week">Week</button>
        <button class="tab" data-p="month">Month</button>
      </div>
      <div class="an-sum" id="sum"></div>
      <div id="dist"></div>
      <div class="tbl-wrap"><table><thead><tr><th>City</th><th>Good</th><th>Bad</th><th>Harsh</th><th>Distribution</th><th>Active</th></tr></thead><tbody id="tb"></tbody></table></div>
    </div>
  </div>
</div>

<div class="overlay" id="ov">
  <div class="modal">
    <h3 id="mt"></h3><p id="md"></p>
    <div class="ma">
      <button class="mb cn" id="mcn">Cancel</button>
      <button class="mb ok" id="mc">Apply</button>
    </div>
  </div>
</div>

<div class="detail-overlay" id="detailOv">
  <div class="detail-modal" id="detailModal"></div>
</div>

<div class="toasts" id="ts"></div>

<script>
const MONTHS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const periodMap={day:'today',week:'week',month:'month'};
let period='day',pending=null,activeData={},allGroups=[];
const cap=s=>s.charAt(0).toUpperCase()+s.slice(1);
const labels={good:'Good',bad:'Bad',harsh:'Harsh'};
const labelsF={good:'Good Weather',bad:'Bad Weather',harsh:'Harsh Weather'};

function fmtDate(iso){
  if(!iso)return '\u2014';
  const d=new Date(iso);
  if(isNaN(d.getTime()))return '\u2014';
  return d.getDate()+' '+MONTHS[d.getMonth()]+', '+String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');
}

function fmtH(h){
  if(!h||h===0)return '0m';
  if(h<1)return Math.round(h*60)+'m';
  if(h<24){const hr=Math.floor(h),mn=Math.round((h-hr)*60);return hr+'h'+(mn>0?' '+mn+'m':'');}
  const d=Math.floor(h/24),hr=Math.floor(h%24);return d+'d '+hr+'h';
}

function toggleSec(id){document.getElementById(id).classList.toggle('closed')}
function toggleOvTier(el){el.closest('.ov-tier').classList.toggle('cl')}

async function loadConfig(){
  const r=await fetch('/api/config');const d=await r.json();
  if(d.user)document.getElementById('userSel').value=d.user;
  const ps=document.getElementById('patStatus'),pi=document.getElementById('patIn');
  if(d.has_pat){ps.textContent='\u2713 GitHub: '+d.pat_source;ps.style.color='var(--good)';pi.style.display='none';}
  else{ps.textContent='\u2717 No PAT';ps.style.color='var(--harsh)';pi.style.display='';}
  const ss=document.getElementById('slackStatus'),sc=document.getElementById('slackConnect');
  if(d.has_slack){ss.textContent='\u2713 Slack';ss.style.color='var(--good)';sc.style.display='none';}
  else{ss.textContent='';sc.style.display='';}
}
document.getElementById('userSel').onchange=function(){
  fetch('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user:this.value})});
};
document.getElementById('patIn').onchange=async function(){
  if(!this.value)return;
  await fetch('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pat:this.value})});
  this.value='';loadConfig();toast('GitHub token saved!','success');
};
loadConfig();

async function loadCities(){
  const r=await fetch('/api/cities');const d=await r.json();
  activeData=d.active_profiles;allGroups=d.groups;
  renderOverview(d.groups,d.active_profiles);
  renderSections(d.groups,d.active_profiles);
  const ac=Object.keys(d.active_profiles).length;
  document.getElementById('hActive').textContent=ac;
  document.getElementById('ov-cnt').textContent=ac+' active';
}

function renderOverview(groups,active){
  const el=document.getElementById('overview-body');
  el.innerHTML=groups.map(g=>{
    const pills=g.cities.map(c=>{
      const ap=active[c.name];
      const prof=ap?ap.profile:'none';
      const lbl=ap?labels[prof]:'\u2014';
      const ts=ap?fmtDate(ap.since):'';
      const u=ap?((ap.user||'').split('@')[0]||''):'';
      const extra=ts?(ts+(u?' \u00b7 '+u:'')):(u||'');
      return '<span class="pill"><span class="d '+prof+'"></span><span class="pn">'+c.name+'</span><span class="pp '+prof+'">'+lbl+'</span>'+(extra?'<span class="pt">'+extra+'</span>':'')+'</span>';
    }).join('');
    return '<div class="ov-tier"><div class="ov-tier-h" onclick="toggleOvTier(this)"><span class="chv2">&#9662;</span>'+g.name+' <span style="color:var(--mu2)">'+g.count+'</span></div><div class="ov-pills">'+pills+'</div></div>';
  }).join('');
}

let firstRender=true;
function renderSections(groups,active){
  const wrap=document.getElementById('city-sections');
  const saved={};
  wrap.querySelectorAll('.sec').forEach(s=>{saved[s.id]=s.classList.contains('closed')});
  wrap.innerHTML='';
  groups.forEach((g,i)=>{
    const id='sec-g-'+i;
    const closed=id in saved?saved[id]:(firstRender&&i>0);
    const cards=g.cities.map(c=>card(c,active[c.name])).join('');
    wrap.innerHTML+='<div class="sec '+(closed?'closed':'')+'" id="'+id+'"><div class="sec-h" onclick="toggleSec(\''+id+'\')"><span class="chv">&#9662;</span><h2>'+g.name+'</h2><span class="cnt">'+g.count+' cities</span></div><div class="sec-b" style="max-height:6000px"><div class="grid">'+cards+'</div></div></div>';
  });
  firstRender=false;
}

function card(c,ap){
  let ah='<div class="ap" style="color:var(--mu2)">No profile set</div>';
  if(ap){
    const p=ap.profile;
    const u=ap.user?(' \u00b7 '+ap.user.split('@')[0]):'';
    ah='<div class="ap"><span class="d '+p+'" style="width:7px;height:7px;border-radius:50%;display:inline-block"></span><span class="pname">'+labelsF[p]+'</span><span class="since">Since '+fmtDate(ap.since)+u+'</span></div>';
  }
  const btns=c.profiles.map(p=>'<button class="b '+p+'" data-city="'+c.name+'" data-prof="'+p+'"><span class="lb">'+cap(p)+'</span><div class="sp"></div></button>').join('');
  return '<div class="card" id="c-'+c.name+'"><div class="card-top"><span class="city">'+c.name+'</span></div>'+ah+'<div class="btns">'+btns+'</div></div>';
}

document.addEventListener('click',function(e){
  var btn=e.target.closest('.b[data-city]');
  if(btn&&!btn.disabled)ask(btn.dataset.city,btn.dataset.prof);
});

setInterval(()=>{loadCities();loadStats()},30000);

function ask(city,prof){
  const user=document.getElementById('userSel').value;
  if(!user){toast('Select your name first!','error');return;}
  pending={city,profile:prof};
  document.getElementById('mt').textContent='Apply '+labelsF[prof]+'?';
  document.getElementById('md').textContent=user.split('@')[0]+' \u2192 Post '+city+' '+labelsF[prof]+' to Slack channel.';
  document.getElementById('ov').classList.add('open');
}
function closeM(){document.getElementById('ov').classList.remove('open');pending=null}
document.getElementById('mcn').onclick=closeM;
document.getElementById('mc').onclick=async()=>{
  if(!pending)return;const{city,profile}=pending;closeM();await apply(city,profile);
};

async function apply(city,prof){
  const user=document.getElementById('userSel').value;
  if(!user){toast('Select your name first!','error');return;}
  const crd=document.getElementById('c-'+city);
  const btn=crd?crd.querySelector('.b.'+prof):null;
  const all=document.querySelectorAll('.b');
  all.forEach(b=>b.disabled=true);if(btn)btn.classList.add('ld');
  const ls=document.getElementById('liveStatus'),lt=document.getElementById('liveText');
  ls.classList.add('busy');lt.textContent='Slack: '+cap(prof)+' \u2192 '+city+'...';
  try{
    const r=await fetch('/api/apply',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({city,profile:prof,user})});
    if(!r.ok){const e=await r.json();toast(e.error||'Request failed','error');return}
    const{task_id}=await r.json();
    while(true){
      await new Promise(r=>setTimeout(r,2000));
      const tr=await fetch('/api/tasks/'+task_id);const t=await tr.json();
      if(t.status==='success'){toast(city+' \u2192 '+labelsF[prof]+' ('+t.duration+'s)','success');break}
      if(t.status==='error'){toast('Failed: '+t.message,'error');break}
      lt.textContent=t.message||'Running...';
    }
  }catch(e){toast('Error: '+e.message,'error')}
  finally{
    all.forEach(b=>b.disabled=false);if(btn)btn.classList.remove('ld');
    ls.classList.remove('busy');lt.textContent='Live';loadCities();loadStats();
  }
}

function toast(msg,type='info'){
  const c=document.getElementById('ts'),t=document.createElement('div');
  t.className='toast '+type;t.textContent=msg;c.appendChild(t);setTimeout(()=>t.remove(),5000);
}

async function loadStats(){
  const apiP=periodMap[period]||period;
  const r=await fetch('/api/stats?period='+apiP);const d=await r.json();renderStats(d);
}

function renderStats(d){
  const th=d.total_hours,mu=d.most_used_profile;
  document.getElementById('sum').innerHTML=
    '<div class="sc"><div class="sv">'+fmtH(th)+'</div><div class="sl">Total Tracked Time</div></div>'+
    '<div class="sc"><div class="sv" style="color:var(--'+(mu||'mu')+')">'+
    (mu?cap(mu):'\u2014')+'</div><div class="sl">Most Used Profile</div></div>'+
    '<div class="sc"><div class="sv">'+d.total_applies+'</div><div class="sl">Profile Switches</div></div>';

  const tot=th||1,g=d.profile_hours.good,b=d.profile_hours.bad,h=d.profile_hours.harsh;
  const dist=document.getElementById('dist');
  if(th>0){
    dist.innerHTML='<div class="bar">'+
      (g?'<div class="seg good" style="width:'+(g/tot*100).toFixed(1)+'%">'+(g/tot>.08?fmtH(g):'')+'</div>':'')+
      (b?'<div class="seg bad" style="width:'+(b/tot*100).toFixed(1)+'%">'+(b/tot>.08?fmtH(b):'')+'</div>':'')+
      (h?'<div class="seg harsh" style="width:'+(h/tot*100).toFixed(1)+'%">'+(h/tot>.08?fmtH(h):'')+'</div>':'')+
      '</div><div class="legend"><span><i style="background:var(--good)"></i>Good '+fmtH(g)+'</span><span><i style="background:var(--bad)"></i>Bad '+fmtH(b)+'</span><span><i style="background:var(--harsh)"></i>Harsh '+fmtH(h)+'</span></div>';
  }else{
    dist.innerHTML='<div style="color:var(--mu);font-size:12px;padding:10px 0;margin-bottom:14px">No data for this period</div>';
  }

  const tb=document.getElementById('tb'),cities=Object.keys(d.city_breakdown);
  if(cities.length){
    tb.innerHTML=cities.map(c=>{
      const x=d.city_breakdown[c];
      const ap=activeData[c];
      const al=ap?'<span class="d '+ap.profile+'" style="width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:4px"></span>'+cap(ap.profile):'\u2014';
      const rowTotal=(x.good||0)+(x.bad||0)+(x.harsh||0);
      const rt=rowTotal||1;
      const miniBar='<div class="mini-bar">'+
        (x.good?'<div class="mini-seg good" style="width:'+(x.good/rt*100).toFixed(1)+'%"></div>':'')+
        (x.bad?'<div class="mini-seg bad" style="width:'+(x.bad/rt*100).toFixed(1)+'%"></div>':'')+
        (x.harsh?'<div class="mini-seg harsh" style="width:'+(x.harsh/rt*100).toFixed(1)+'%"></div>':'')+
        '</div>';
      return '<tr class="city-row" data-city="'+c+'"><td><strong>'+c+'</strong></td><td><span class="ct good">'+fmtH(x.good)+'</span></td><td><span class="ct bad">'+fmtH(x.bad)+'</span></td><td><span class="ct harsh">'+fmtH(x.harsh)+'</span></td><td>'+miniBar+'</td><td>'+al+'</td></tr>';
    }).join('');
  }else{
    tb.innerHTML='<tr><td colspan="6" style="text-align:center;color:var(--mu);padding:20px">No data for this period</td></tr>';
  }
}

document.addEventListener('click',function(e){
  const row=e.target.closest('tr.city-row');
  if(row)openCityDetail(row.dataset.city);
});

async function openCityDetail(city){
  const modal=document.getElementById('detailModal');
  modal.innerHTML='<div style="text-align:center;padding:40px;color:var(--mu)">Loading timeline for '+city+'...</div>';
  document.getElementById('detailOv').classList.add('open');
  try{
    const r=await fetch('/api/city-timeline?city='+encodeURIComponent(city)+'&period='+period);
    const d=await r.json();
    renderCityDetail(d,city);
  }catch(err){
    modal.innerHTML='<div style="text-align:center;padding:40px;color:var(--harsh)">Failed to load: '+err.message+'</div>';
  }
}

function closeCityDetail(){document.getElementById('detailOv').classList.remove('open')}
document.getElementById('detailOv').addEventListener('click',function(e){
  if(e.target===this)closeCityDetail();
});

function hmColor(dominant,intensity){
  if(dominant==='none'||intensity<=0)return '#1e1e30';
  const base={good:[160,84,39],bad:[38,92,50],harsh:[0,84,60]};
  const b=base[dominant]||base.good;
  const minL=15,maxL=b[2];
  const lightness=minL+(maxL-minL)*intensity;
  return 'hsl('+b[0]+','+b[1]+'%,'+Math.round(lightness)+'%)';
}

function renderCityDetail(d,city){
  const modal=document.getElementById('detailModal');
  const periodLabel={day:'Last 24 Hours',week:'Last 7 Days',month:'Last 30 Days'}[d.period]||d.period;
  const totG=d.totals.good,totB=d.totals.bad,totH=d.totals.harsh;
  const tl=d.timeline;

  let html='<div class="dm-header"><div><h3>'+city+'</h3><span class="dm-period">'+periodLabel+' &middot; '+d.total_hours+'h</span></div><button class="dm-close" onclick="closeCityDetail()">&times;</button></div>';

  html+='<div class="dm-totals">';
  html+='<div class="dm-total good"><div class="dm-total-v">'+fmtH(totG)+'</div><div class="dm-total-l">Good Weather</div></div>';
  html+='<div class="dm-total bad"><div class="dm-total-v">'+fmtH(totB)+'</div><div class="dm-total-l">Bad Weather</div></div>';
  html+='<div class="dm-total harsh"><div class="dm-total-v">'+fmtH(totH)+'</div><div class="dm-total-l">Harsh Weather</div></div>';
  html+='</div>';

  if(d.period==='day'){
    html+='<div class="heatmap-label">Hourly Activity</div>';
    html+='<div class="heatmap-wrap"><div class="heatmap">';
    tl.forEach(function(h){
      const color=hmColor(h.dominant,h.intensity);
      const hourLabel=h.hour.split(' ')[1]||h.hour;
      html+='<div class="hm-cell" style="background:'+color+'"><div class="hm-tip">'+hourLabel+'<br>Good: '+Math.round(h.minutes.good)+'m &middot; Bad: '+Math.round(h.minutes.bad)+'m &middot; Harsh: '+Math.round(h.minutes.harsh)+'m</div></div>';
    });
    html+='</div>';
    if(tl.length>0){
      const first=tl[0].hour.split(' ')[1]||'';
      const last=tl[tl.length-1].hour.split(' ')[1]||'';
      const q1=tl[Math.floor(tl.length/4)]?tl[Math.floor(tl.length/4)].hour.split(' ')[1]:'';
      const q2=tl[Math.floor(tl.length/2)]?tl[Math.floor(tl.length/2)].hour.split(' ')[1]:'';
      const q3=tl[Math.floor(tl.length*3/4)]?tl[Math.floor(tl.length*3/4)].hour.split(' ')[1]:'';
      html+='<div class="hm-times"><span>'+first+'</span><span>'+q1+'</span><span>'+q2+'</span><span>'+q3+'</span><span>'+last+'</span></div>';
    }
    html+='</div>';
  }else{
    var dayBuckets={};
    tl.forEach(function(h){
      var dayKey=h.hour.split(' ')[0];
      var hourIdx=parseInt((h.hour.split(' ')[1]||'0').split(':')[0],10);
      if(!dayBuckets[dayKey])dayBuckets[dayKey]=[];
      while(dayBuckets[dayKey].length<=hourIdx)dayBuckets[dayKey].push({dominant:'none',intensity:0,minutes:{good:0,bad:0,harsh:0}});
      dayBuckets[dayKey][hourIdx]={dominant:h.dominant,intensity:h.intensity,minutes:h.minutes};
    });
    var days=Object.keys(dayBuckets).sort();
    if(days.length>0){
      html+='<div class="heatmap-label">Daily Pattern</div>';
      days.forEach(function(day){
        var dObj=new Date(day);
        var dayLabel=dObj.getDate()+' '+MONTHS[dObj.getMonth()];
        html+='<div class="hm-day-label">'+dayLabel+'</div><div class="heatmap-wrap"><div class="heatmap">';
        for(var idx=0;idx<24;idx++){
          var cell=dayBuckets[day][idx]||{dominant:'none',intensity:0,minutes:{good:0,bad:0,harsh:0}};
          var color=hmColor(cell.dominant,cell.intensity);
          var m=cell.minutes||{good:0,bad:0,harsh:0};
          html+='<div class="hm-cell" style="background:'+color+'"><div class="hm-tip">'+String(idx).padStart(2,'0')+':00<br>Good: '+Math.round(m.good||0)+'m &middot; Bad: '+Math.round(m.bad||0)+'m &middot; Harsh: '+Math.round(m.harsh||0)+'m</div></div>';
        }
        html+='</div>';
        html+='<div class="hm-times"><span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>23:00</span></div></div>';
      });
    }else{
      html+='<div style="color:var(--mu);font-size:12px;padding:12px 0">No timeline data available</div>';
    }
  }

  html+='<div class="hm-legend"><span><i style="background:var(--good)"></i>Good</span><span><i style="background:var(--bad)"></i>Bad</span><span><i style="background:var(--harsh)"></i>Harsh</span><span><i style="background:#1e1e30"></i>No data</span></div>';

  modal.innerHTML=html;
}

document.querySelectorAll('.tab').forEach(function(t){
  t.addEventListener('click',function(){
    document.querySelectorAll('.tab').forEach(function(x){x.classList.remove('on')});
    t.classList.add('on');period=t.dataset.p;loadStats();
  });
});

document.addEventListener('keydown',function(e){
  if(e.key==='Escape'){closeM();closeCityDetail();}
});

loadCities();loadStats();
</script>
</body>
</html>"""

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  \u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557")
    print("  \u2551  Courier Ops Weather Dashboard v2    \u2551")
    print("  \u2551  http://127.0.0.1:5050               \u2551")
    print(f"  \u2551  {len(CITIES)} cities \u00b7 Settings from GitHub    \u2551")
    print("  \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d\n")
    app.run(host="127.0.0.1", port=5050, debug=False)
