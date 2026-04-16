#!/usr/bin/env python3
"""
Courier Ops Dashboard — Weather Settings Control Panel — Ukraine

Run:   python3 dashboard.py
Open:  http://127.0.0.1:5050

IMPORTANT: This dashboard does NOT kill or close the user's Chrome.
It opens a separate Selenium-managed Chrome window and cleans it up after.
"""

import json
import subprocess
import threading
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "usage_log.json"

# ── City & profile configuration ─────────────────────────────────────────────

CITIES = {
    "Kyiv": {
        "group": "TOP cities", "group_order": 0,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kyiv (2).csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/158",
        "base_path": "Kyiv", "profiles": ["good", "bad", "harsh"],
    },
    "Lviv": {
        "group": "TOP cities", "group_order": 0,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Lviv (1).csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/496",
        "base_path": "Lviv", "profiles": ["good", "bad", "harsh"],
    },
    "Dnipro": {
        "group": "TOP cities", "group_order": 0,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Dnipro (1).csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/499",
        "base_path": "Dnipro", "profiles": ["good", "bad", "harsh"],
    },
    "Kharkiv": {
        "group": "TOP cities", "group_order": 0,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kharkiv (1).csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/491",
        "base_path": "Kharkiv", "profiles": ["good", "bad", "harsh"],
    },
    "Vinnytsia": {
        "group": "TOP cities", "group_order": 0,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Vinnytsia.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/501",
        "base_path": "Vinnytsia", "profiles": ["good", "bad", "harsh"],
    },
    "Odesa": {
        "group": "Tier 2", "group_order": 1,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/498",
        "base_path": "Secondary cities/Tier2 cities/Odesa", "profiles": ["good", "harsh"],
    },
    "Kryvyi Rih": {
        "group": "Tier 2", "group_order": 1,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/504",
        "base_path": "Secondary cities/Tier2 cities/Kryvyi Rih", "profiles": ["good", "harsh"],
    },
    "Poltava": {
        "group": "Tier 2", "group_order": 1,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/506",
        "base_path": "Secondary cities/Tier2 cities/Poltava", "profiles": ["good", "harsh"],
    },
    "Ivano-Frankivsk": {
        "group": "Tier 2", "group_order": 1,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/990",
        "base_path": "Secondary cities/Tier2 cities/Ivano-Frankivsk", "profiles": ["good", "harsh"],
    },
    "Chernivtsi": {
        "group": "Tier 2", "group_order": 1,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1084",
        "base_path": "Secondary cities/Tier2 cities/Chernivtsi", "profiles": ["good", "harsh"],
    },
    "Irpin": {
        "group": "Tier 2", "group_order": 1,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1261",
        "base_path": "Secondary cities/Tier2 cities/Irpin", "profiles": ["good", "harsh"],
    },
    "Cherkasy": {
        "group": "Tier 2", "group_order": 1,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1087",
        "base_path": "Secondary cities/Tier2 cities/Cherkasy", "profiles": ["good", "harsh"],
    },
    "Zaporizhia": {
        "group": "Tier 3", "group_order": 2,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/500",
        "base_path": "Secondary cities/Tier3 cities/Zaporizhia", "profiles": ["good", "harsh"],
    },
    "Bila Tserkva": {
        "group": "Tier 3", "group_order": 2,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1079",
        "base_path": "Secondary cities/Tier3 cities/Bila Tserkva", "profiles": ["good", "harsh"],
    },
    "Khmelnytskyi": {
        "group": "Tier 3", "group_order": 2,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1081",
        "base_path": "Secondary cities/Tier3 cities/Khmelnytskyi", "profiles": ["good", "harsh"],
    },
    "Rivne": {
        "group": "Tier 3", "group_order": 2,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1086",
        "base_path": "Secondary cities/Tier3 cities/Rivne", "profiles": ["good", "harsh"],
    },
    "Uzhhorod": {
        "group": "Tier 3", "group_order": 2,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1131",
        "base_path": "Secondary cities/Tier3 cities/Uzhhorod", "profiles": ["good", "harsh"],
    },
    "Brovary": {
        "group": "Tier 3", "group_order": 2,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1259",
        "base_path": "Secondary cities/Tier3 cities/Brovary", "profiles": ["good", "harsh"],
    },
    "Zhytomyr": {
        "group": "Tier 3", "group_order": 2,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1083",
        "base_path": "Secondary cities/Tier3 cities/Zhytomyr", "profiles": ["good", "harsh"],
    },
    "Mykolaiv": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/503",
        "base_path": "Secondary cities/Rest of the cities/Mykolaiv", "profiles": ["good", "harsh"],
    },
    "Chernihiv": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1076",
        "base_path": "Secondary cities/Rest of the cities/Chenihiv", "profiles": ["good", "harsh"],
    },
    "Sumy": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1078",
        "base_path": "Secondary cities/Rest of the cities/Sumy", "profiles": ["good", "harsh"],
    },
    "Ternopil": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1080",
        "base_path": "Secondary cities/Rest of the cities/Ternopil", "profiles": ["good", "harsh"],
    },
    "Lutsk": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1082",
        "base_path": "Secondary cities/Rest of the cities/Lutsk", "profiles": ["good", "harsh"],
    },
    "Kropyvnytskyi": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1085",
        "base_path": "Secondary cities/Rest of the cities/Kropyvnytskyi", "profiles": ["good", "harsh"],
    },
    "Kremenchuk": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1088",
        "base_path": "Secondary cities/Rest of the cities/Kremenchuk", "profiles": ["good", "harsh"],
    },
    "Kamianets-Podilskyi": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1132",
        "base_path": "Secondary cities/Rest of the cities/Kamianets-Podilskyi", "profiles": ["good", "harsh"],
    },
    "Pavlohrad": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1176",
        "base_path": "Secondary cities/Rest of the cities/Pavlohrad", "profiles": ["good", "harsh"],
    },
    "Kamianske": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1178",
        "base_path": "Secondary cities/Rest of the cities/Kamianske", "profiles": ["good", "harsh"],
    },
    "Mukachevo": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1179",
        "base_path": "Secondary cities/Rest of the cities/Mukachevo", "profiles": ["good", "harsh"],
    },
    "Boryspil": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1220",
        "base_path": "Secondary cities/Rest of the cities/Boryspil", "profiles": ["good", "harsh"],
    },
    "Vyshhorod": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1262",
        "base_path": "Secondary cities/Rest of the cities/Vyshhorod", "profiles": ["good", "harsh"],
    },
    "Drohobych": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1348",
        "base_path": "Secondary cities/Rest of the cities/Drohobych", "profiles": ["good", "harsh"],
    },
    "Truskavets": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/1357",
        "base_path": "Secondary cities/Rest of the cities/Truskavets", "profiles": ["good", "harsh"],
    },
    "Kovel": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2170",
        "base_path": "Secondary cities/Rest of the cities/Kovel", "profiles": ["good", "harsh"],
    },
    "Oleksandriia": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2171",
        "base_path": "Secondary cities/Rest of the cities/Oleksandriia", "profiles": ["good", "harsh"],
    },
    "Kolomyia": {
        "group": "Rest of cities", "group_order": 3,
        "csv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv",
        "mode": "url", "url": "https://admin-panel.bolt.eu/delivery-courier/settings/city/2499",
        "base_path": "Secondary cities/Rest of the cities/Kolomyia", "profiles": ["good", "harsh"],
    },
}

PROFILES = {
    "good": {"folder": "Good weather", "script": "apply_good_weather_settings.py", "extra_args": []},
    "bad": {"folder": "Bad weather", "script": "apply_weather_settings.py", "extra_args": ["--weather", "bad"]},
    "harsh": {"folder": "Harsh weather", "script": "apply_harsh_weather_settings.py", "extra_args": []},
}

# ── Flask app ─────────────────────────────────────────────────────────────────

app = Flask(__name__)
tasks: dict = {}
log_lock = threading.Lock()
run_lock = threading.Lock()

# ── Log helpers ───────────────────────────────────────────────────────────────

def _load_log() -> list:
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            return json.load(f)
    return []


def _save_log(entries: list):
    with open(LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def _log_action(city: str, profile: str, status: str, duration: float = 0):
    with log_lock:
        entries = _load_log()
        entries.append({
            "city": city, "profile": profile, "status": status,
            "duration_seconds": round(duration, 1),
            "timestamp": datetime.now().isoformat(),
        })
        _save_log(entries)


def _get_active_profiles() -> dict:
    log = _load_log()
    active: dict = {}
    for entry in reversed(log):
        if entry["status"] == "success" and entry["city"] not in active:
            active[entry["city"]] = {"profile": entry["profile"], "since": entry["timestamp"]}
    return active


def _compute_durations(cutoff: datetime) -> tuple[dict, dict]:
    now = datetime.now()
    log = _load_log()
    city_events: dict[str, list] = {}
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

# ── Command builder & runner ──────────────────────────────────────────────────

def _build_command(city_name: str, profile: str):
    city = CITIES[city_name]
    prof = PROFILES[profile]
    base = city.get("base_path", city_name)
    work_dir = BASE_DIR / base / prof["folder"]
    csv_path = f"../{city['csv']}"
    cmd = ["python3", prof["script"], csv_path]
    if city["mode"] == "url":
        cmd.extend(["--url", city["url"]])
    else:
        cmd.append("--browser")
    cmd.extend(prof["extra_args"])
    return cmd, work_dir


def _cleanup_selenium_chrome():
    subprocess.run(["pkill", "-f", "chrome_selenium_profile"], capture_output=True, timeout=5)


def _run_task(task_id: str, city_name: str, profile: str):
    start = time.time()
    try:
        with run_lock:
            tasks[task_id]["status"] = "running"
            tasks[task_id]["message"] = f"Applying {profile} weather to {city_name}..."
            _cleanup_selenium_chrome()
            time.sleep(1)

            cmd, work_dir = _build_command(city_name, profile)
            result = subprocess.run(
                cmd, cwd=str(work_dir), capture_output=True, text=True,
                timeout=180, stdin=subprocess.DEVNULL,
            )
            output = (result.stdout or "") + "\n" + (result.stderr or "")
            elapsed = time.time() - start
            success = "Update clicked" in output or "settings saved" in output

            time.sleep(1)
            _cleanup_selenium_chrome()

            tasks[task_id].update(
                status="success" if success else "error",
                output=output.strip(),
                finished_at=datetime.now().isoformat(),
                duration=round(elapsed, 1),
                message="Settings applied!" if success else "Failed — check output",
            )
            _log_action(city_name, profile, "success" if success else "error", elapsed)

    except subprocess.TimeoutExpired:
        _cleanup_selenium_chrome()
        elapsed = time.time() - start
        tasks[task_id].update(status="error", message="Script timed out (180 s)", finished_at=datetime.now().isoformat())
        _log_action(city_name, profile, "timeout", elapsed)
    except Exception as exc:
        _cleanup_selenium_chrome()
        elapsed = time.time() - start
        tasks[task_id].update(status="error", message=str(exc), finished_at=datetime.now().isoformat())
        _log_action(city_name, profile, "error", elapsed)

# ── API routes ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return HTML_PAGE


@app.route("/api/cities")
def get_cities():
    group_map: dict = {}
    for name, cfg in CITIES.items():
        g = cfg["group"]
        if g not in group_map:
            group_map[g] = {"order": cfg["group_order"], "cities": []}
        group_map[g]["cities"].append({
            "name": name, "profiles": cfg.get("profiles", ["good", "bad", "harsh"]),
        })
    groups = sorted(group_map.items(), key=lambda x: x[1]["order"])
    return jsonify({
        "groups": [{"name": k, "count": len(v["cities"]), "cities": v["cities"]} for k, v in groups],
        "active_profiles": _get_active_profiles(),
    })


@app.route("/api/apply", methods=["POST"])
def apply_settings():
    data = request.json or {}
    city, profile = data.get("city", ""), data.get("profile", "")
    if city not in CITIES:
        return jsonify({"error": f"Unknown city: {city}"}), 400
    if profile not in PROFILES:
        return jsonify({"error": f"Unknown profile: {profile}"}), 400
    avail = CITIES[city].get("profiles", ["good", "bad", "harsh"])
    if profile not in avail:
        return jsonify({"error": f"Profile '{profile}' not available for {city}"}), 400
    for t in tasks.values():
        if t["status"] == "running":
            return jsonify({"error": "Another task is already running"}), 409

    task_id = str(uuid.uuid4())[:8]
    tasks[task_id] = {
        "id": task_id, "city": city, "profile": profile,
        "status": "queued", "message": "Starting...",
        "output": "", "created_at": datetime.now().isoformat(),
        "finished_at": None, "duration": None,
    }
    threading.Thread(target=_run_task, args=(task_id, city, profile), daemon=True).start()
    return jsonify({"task_id": task_id})


@app.route("/api/tasks/<task_id>")
def get_task(task_id):
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(tasks[task_id])


@app.route("/api/stats")
def get_stats():
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
def get_history():
    return jsonify(_load_log()[-50:])

# ── Embedded HTML ─────────────────────────────────────────────────────────────

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Courier Ops — Ukraine</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#080a0f;--sf:#0f1218;--sf2:#151a22;--bd:#1c2230;--bd2:#252d3b;
  --tx:#d1d5db;--txb:#f0f2f5;--mu:#5c6370;--mu2:#3d4452;
  --good:#10b981;--goodH:#34d399;--goodBg:rgba(16,185,129,.08);
  --bad:#f59e0b;--badH:#fbbf24;--badBg:rgba(245,158,11,.08);
  --harsh:#ef4444;--harshH:#f87171;--harshBg:rgba(239,68,68,.08);
  --acc:#3b82f6;--accH:#60a5fa;--accBg:rgba(59,130,246,.06);
  --r:8px;--r2:12px;
}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;font-size:13px}

/* ─ Header ─ */
.hdr{background:var(--sf);border-bottom:1px solid var(--bd);padding:14px 28px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:50}
.hdr-l{display:flex;align-items:center;gap:14px}
.hdr h1{font-size:16px;font-weight:700;color:var(--txb);letter-spacing:-.3px}
.hdr .pipe{width:1px;height:20px;background:var(--bd2)}
.hdr .sub{font-size:11px;color:var(--mu);text-transform:uppercase;letter-spacing:.8px;font-weight:500}
.hdr-r{display:flex;align-items:center;gap:16px}
.metric{text-align:center}
.metric-v{font-size:18px;font-weight:700;color:var(--txb)}
.metric-l{font-size:9px;color:var(--mu);text-transform:uppercase;letter-spacing:.6px;margin-top:1px}
.live{display:flex;align-items:center;gap:6px;font-size:11px;font-weight:500;color:var(--good);padding:5px 12px;background:var(--goodBg);border-radius:20px;border:1px solid rgba(16,185,129,.15)}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--good);animation:lp 2s infinite}
@keyframes lp{0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,.3)}50%{box-shadow:0 0 0 5px rgba(16,185,129,0)}}
.live.busy{color:var(--acc);background:var(--accBg);border-color:rgba(59,130,246,.15)}
.live.busy .live-dot{background:var(--acc);animation:lp2 1.5s infinite}
@keyframes lp2{0%,100%{box-shadow:0 0 0 0 rgba(59,130,246,.3)}50%{box-shadow:0 0 0 5px rgba(59,130,246,0)}}

/* ─ Main layout ─ */
.main{max-width:1440px;margin:0 auto;padding:20px 28px 40px}

/* ─ Section (collapsible) ─ */
.sec{margin-bottom:16px;background:var(--sf);border:1px solid var(--bd);border-radius:var(--r2);overflow:hidden}
.sec-h{display:flex;align-items:center;gap:10px;padding:12px 18px;cursor:pointer;user-select:none;transition:background .15s}
.sec-h:hover{background:var(--sf2)}
.chv{font-size:11px;color:var(--mu);transition:transform .2s;width:16px;text-align:center}
.sec.closed .chv{transform:rotate(-90deg)}
.sec-h h2{font-size:13px;font-weight:600;color:var(--txb);text-transform:uppercase;letter-spacing:.5px}
.cnt{font-size:10px;color:var(--mu);background:var(--bg);padding:2px 8px;border-radius:10px;font-weight:600;margin-left:auto}
.sec-b{transition:max-height .35s ease,padding .2s ease;overflow:hidden;padding:0 18px 16px}
.sec.closed .sec-b{max-height:0!important;padding-top:0;padding-bottom:0}

/* ─ Overview ─ */
.ov-tier{margin-bottom:12px}
.ov-tier:last-child{margin-bottom:0}
.ov-tier-h{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;color:var(--mu);margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid var(--bd);cursor:pointer;display:flex;align-items:center;gap:6px}
.ov-tier-h .chv2{font-size:9px;transition:transform .2s}
.ov-tier.cl .ov-tier-h .chv2{transform:rotate(-90deg)}
.ov-tier.cl .ov-pills{display:none}
.ov-pills{display:flex;flex-wrap:wrap;gap:4px}
.pill{display:inline-flex;align-items:center;gap:5px;padding:4px 10px 4px 8px;border-radius:6px;background:var(--bg);border:1px solid var(--bd);font-size:11px;transition:border-color .15s}
.pill:hover{border-color:var(--bd2)}
.pill .d{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.pill .d.good{background:var(--good);box-shadow:0 0 5px rgba(16,185,129,.4)}
.pill .d.bad{background:var(--bad);box-shadow:0 0 5px rgba(245,158,11,.4)}
.pill .d.harsh{background:var(--harsh);box-shadow:0 0 5px rgba(239,68,68,.4)}
.pill .d.none{background:var(--mu2)}
.pill .pn{font-weight:600;color:var(--txb)}
.pill .pp{font-weight:500}
.pill .pp.good{color:var(--good)}.pill .pp.bad{color:var(--bad)}.pill .pp.harsh{color:var(--harsh)}.pill .pp.none{color:var(--mu)}
.pill .pt{font-family:"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;font-size:10px;color:var(--mu);margin-left:2px}

/* ─ City cards grid ─ */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}
.card{background:var(--bg);border:1px solid var(--bd);border-radius:var(--r);padding:14px;transition:border-color .15s}
.card:hover{border-color:var(--bd2)}
.card-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px}
.city{font-size:14px;font-weight:600;color:var(--txb)}
.ap{font-size:10px;color:var(--mu);display:flex;align-items:center;gap:5px;min-height:16px;margin-bottom:10px}
.ap .pname{color:var(--tx);font-weight:500}
.timer{font-family:"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;font-size:10px;color:var(--acc);margin-left:auto}

.btns{display:flex;gap:6px}
.b{flex:1;padding:8px 0;border:none;border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;transition:all .12s;color:#fff;letter-spacing:.2px}
.b:disabled{opacity:.35;cursor:not-allowed}
.b.good{background:var(--good)}.b.good:hover:not(:disabled){background:var(--goodH)}
.b.bad{background:var(--bad);color:#1a1a2e}.b.bad:hover:not(:disabled){background:var(--badH)}
.b.harsh{background:var(--harsh)}.b.harsh:hover:not(:disabled){background:var(--harshH)}
.b .sp{display:none;width:12px;height:12px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite;margin:0 auto}
.b.ld .lb{display:none}.b.ld .sp{display:block}
@keyframes spin{to{transform:rotate(360deg)}}

/* ─ Analytics ─ */
.an-sum{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px}
.sc{background:var(--bg);border-radius:var(--r);padding:12px;text-align:center;border:1px solid var(--bd)}
.sv{font-size:20px;font-weight:700;color:var(--txb);margin-bottom:2px}
.sl{font-size:9px;color:var(--mu);text-transform:uppercase;letter-spacing:.5px}
.tabs{display:flex;gap:2px;margin-bottom:14px;background:var(--bg);padding:2px;border-radius:6px;width:fit-content;border:1px solid var(--bd)}
.tab{padding:5px 12px;border:none;border-radius:5px;background:transparent;color:var(--mu);font-size:11px;cursor:pointer;transition:all .12s;font-weight:500}
.tab:hover{color:var(--tx)}.tab.on{background:var(--sf2);color:var(--txb)}
.bar{display:flex;height:18px;border-radius:9px;overflow:hidden;background:var(--bg);border:1px solid var(--bd);margin-bottom:4px}
.seg{display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;color:#fff;transition:width .4s ease;min-width:0}
.seg.good{background:var(--good)}.seg.bad{background:var(--bad);color:#1a1a2e}.seg.harsh{background:var(--harsh)}
.legend{display:flex;gap:16px;margin-bottom:14px;font-size:10px;color:var(--mu)}
.legend i{display:inline-block;width:8px;height:8px;border-radius:3px;margin-right:4px;vertical-align:middle}
.tbl-wrap{max-height:400px;overflow-y:auto;border:1px solid var(--bd);border-radius:var(--r)}
.tbl-wrap::-webkit-scrollbar{width:5px}.tbl-wrap::-webkit-scrollbar-track{background:var(--bg)}.tbl-wrap::-webkit-scrollbar-thumb{background:var(--bd2);border-radius:3px}
table{width:100%;border-collapse:separate;border-spacing:0}
th{text-align:left;font-size:9px;color:var(--mu);text-transform:uppercase;letter-spacing:.5px;padding:6px 10px;border-bottom:1px solid var(--bd);background:var(--sf);position:sticky;top:0;z-index:1}
td{padding:6px 10px;font-size:12px;border-bottom:1px solid var(--bd)}
tr:last-child td{border-bottom:none}
.ct{font-family:"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;font-size:11px}
.ct.good{color:var(--good)}.ct.bad{color:var(--bad)}.ct.harsh{color:var(--harsh)}

/* ─ Modal ─ */
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:100;justify-content:center;align-items:center;backdrop-filter:blur(4px)}
.overlay.open{display:flex}
.modal{background:var(--sf);border:1px solid var(--bd2);border-radius:var(--r2);padding:24px;max-width:360px;width:90%;text-align:center}
.modal h3{font-size:15px;margin-bottom:4px;color:var(--txb)}
.modal p{color:var(--mu);margin-bottom:18px;font-size:12px}
.ma{display:flex;gap:8px;justify-content:center}
.mb{padding:8px 20px;border-radius:6px;border:none;font-size:12px;font-weight:600;cursor:pointer}
.mb.cn{background:var(--bg);color:var(--tx);border:1px solid var(--bd)}
.mb.ok{background:var(--acc);color:#fff}.mb.ok:hover{background:var(--accH)}

/* ─ Toasts ─ */
.toasts{position:fixed;bottom:16px;right:16px;z-index:200;display:flex;flex-direction:column;gap:6px}
.toast{padding:10px 16px;border-radius:8px;font-size:12px;font-weight:500;animation:si .2s ease;max-width:360px;box-shadow:0 4px 20px rgba(0,0,0,.4)}
.toast.success{background:var(--good);color:#fff}
.toast.error{background:var(--harsh);color:#fff}
.toast.info{background:var(--acc);color:#fff}
@keyframes si{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
</style>
</head>
<body>

<div class="hdr">
  <div class="hdr-l">
    <h1>Courier Ops</h1>
    <div class="pipe"></div>
    <span class="sub">Ukraine Weather Control</span>
  </div>
  <div class="hdr-r">
    <div class="metric"><div class="metric-v" id="hCities">37</div><div class="metric-l">Cities</div></div>
    <div class="metric"><div class="metric-v" id="hActive">0</div><div class="metric-l">Active</div></div>
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
    <div class="sec-b" style="max-height:2000px">
      <div class="tabs" id="tabs">
        <button class="tab" data-p="hour">Hour</button>
        <button class="tab" data-p="today">Today</button>
        <button class="tab on" data-p="week">Week</button>
        <button class="tab" data-p="month">Month</button>
        <button class="tab" data-p="year">Year</button>
        <button class="tab" data-p="all">All</button>
      </div>
      <div class="an-sum" id="sum"></div>
      <div id="dist"></div>
      <div class="tbl-wrap"><table><thead><tr><th>City</th><th>Good</th><th>Bad</th><th>Harsh</th><th>Active</th></tr></thead><tbody id="tb"></tbody></table></div>
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
<div class="toasts" id="ts"></div>

<script>
let period='week',pending=null,activeData={},allGroups=[];
const cap=s=>s.charAt(0).toUpperCase()+s.slice(1);
const labels={good:'Good',bad:'Bad',harsh:'Harsh'};
const labelsF={good:'Good Weather',bad:'Bad Weather',harsh:'Harsh Weather'};

function fmtH(h){
  if(!h||h===0)return '0m';
  if(h<1)return Math.round(h*60)+'m';
  if(h<24){const hr=Math.floor(h),mn=Math.round((h-hr)*60);return hr+'h'+(mn>0?' '+mn+'m':'');}
  const d=Math.floor(h/24),hr=Math.floor(h%24);return d+'d '+hr+'h';
}
function fmtLive(iso){
  const ms=Date.now()-new Date(iso).getTime();
  if(ms<0)return '0:00:00';
  const s=Math.floor(ms/1000),h=Math.floor(s/3600),m=Math.floor((s%3600)/60),sc=s%60;
  return h+':'+String(m).padStart(2,'0')+':'+String(sc).padStart(2,'0');
}

function toggleSec(id){document.getElementById(id).classList.toggle('closed')}
function toggleOvTier(el){el.closest('.ov-tier').classList.toggle('cl')}

/* ── Load cities ── */
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
      const lbl=ap?labels[prof]:'—';
      return '<span class="pill"><span class="d '+prof+'"></span><span class="pn">'+c.name+'</span><span class="pp '+prof+'">'+lbl+'</span></span>';
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
    wrap.innerHTML+='<div class="sec '+(closed?'closed':'')+'" id="'+id+'"><div class="sec-h" onclick="toggleSec(\''+id+'\')"><span class="chv">&#9662;</span><h2>'+g.name+'</h2><span class="cnt">'+g.count+' cities</span></div><div class="sec-b" style="max-height:4000px"><div class="grid">'+cards+'</div></div></div>';
  });
  firstRender=false;
}

function card(c,ap){
  let ah='<div class="ap" style="color:var(--mu2)">Not set</div>';
  if(ap){
    const p=ap.profile;
    ah='<div class="ap"><span class="d '+p+'" style="width:6px;height:6px;border-radius:50;display:inline-block"></span><span class="pname">'+labelsF[p]+'</span><span class="timer" data-since="'+ap.since+'">'+fmtLive(ap.since)+'</span></div>';
  }
  const btns=c.profiles.map(p=>'<button class="b '+p+'" data-city="'+c.name+'" data-prof="'+p+'"><span class="lb">'+cap(p)+'</span><div class="sp"></div></button>').join('');
  return '<div class="card" id="c-'+c.name+'"><div class="card-top"><span class="city">'+c.name+'</span></div>'+ah+'<div class="btns">'+btns+'</div></div>';
}

document.addEventListener('click',function(e){
  var btn=e.target.closest('.b[data-city]');
  if(btn&&!btn.disabled)ask(btn.dataset.city,btn.dataset.prof);
});

setInterval(()=>{document.querySelectorAll('.timer[data-since]').forEach(el=>{el.textContent=fmtLive(el.dataset.since)})},1000);
setInterval(()=>{loadCities();loadStats()},60000);

/* ── Confirm + Apply ── */
function ask(city,prof){
  pending={city,profile:prof};
  document.getElementById('mt').textContent='Apply '+labelsF[prof]+'?';
  document.getElementById('md').textContent='Update '+city+' admin panel to '+labelsF[prof]+' via Selenium.';
  document.getElementById('ov').classList.add('open');
}
function closeM(){document.getElementById('ov').classList.remove('open');pending=null}
document.getElementById('mcn').onclick=closeM;

document.getElementById('mc').onclick=async()=>{
  if(!pending)return;const{city,profile}=pending;closeM();await apply(city,profile);
};

async function apply(city,prof){
  const card=document.getElementById('c-'+city);
  const btn=card?card.querySelector('.b.'+prof):null;
  const all=document.querySelectorAll('.b');
  all.forEach(b=>b.disabled=true);if(btn)btn.classList.add('ld');
  const ls=document.getElementById('liveStatus'),lt=document.getElementById('liveText');
  ls.classList.add('busy');lt.textContent=cap(prof)+' \u2192 '+city+'...';
  try{
    const r=await fetch('/api/apply',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({city,profile:prof})});
    if(r.status===409){toast('Another task is running','error');return}
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

/* ── Stats ── */
async function loadStats(){
  const r=await fetch('/api/stats?period='+period);const d=await r.json();renderStats(d);
}
function renderStats(d){
  const th=d.total_hours,mu=d.most_used_profile;
  document.getElementById('sum').innerHTML=
    '<div class="sc"><div class="sv">'+fmtH(th)+'</div><div class="sl">Total Tracked Time</div></div>'+
    '<div class="sc"><div class="sv" style="color:var(--'+(mu||'mu')+')">'+
    (mu?cap(mu):'—')+'</div><div class="sl">Most Used Profile</div></div>'+
    '<div class="sc"><div class="sv">'+d.total_applies+'</div><div class="sl">Profile Switches</div></div>';

  const tot=th||1,g=d.profile_hours.good,b=d.profile_hours.bad,h=d.profile_hours.harsh;
  const dist=document.getElementById('dist');
  if(th>0){
    dist.innerHTML='<div class="bar">'+
      (g?'<div class="seg good" style="width:'+(g/tot*100).toFixed(1)+'%">'+fmtH(g)+'</div>':'')+
      (b?'<div class="seg bad" style="width:'+(b/tot*100).toFixed(1)+'%">'+fmtH(b)+'</div>':'')+
      (h?'<div class="seg harsh" style="width:'+(h/tot*100).toFixed(1)+'%">'+fmtH(h)+'</div>':'')+
      '</div><div class="legend"><span><i style="background:var(--good)"></i>Good ('+fmtH(g)+')</span><span><i style="background:var(--bad)"></i>Bad ('+fmtH(b)+')</span><span><i style="background:var(--harsh)"></i>Harsh ('+fmtH(h)+')</span></div>';
  }else{dist.innerHTML='<div style="color:var(--mu);font-size:12px;padding:8px 0;margin-bottom:12px">No data for this period</div>'}

  const tb=document.getElementById('tb'),cities=Object.keys(d.city_breakdown);
  if(cities.length){
    tb.innerHTML=cities.map(c=>{
      const x=d.city_breakdown[c];
      const ap=activeData[c];
      const al=ap?'<span class="d '+ap.profile+'" style="width:5px;height:5px;border-radius:50%;display:inline-block;margin-right:3px"></span>'+cap(ap.profile):'—';
      return '<tr><td><strong>'+c+'</strong></td><td><span class="ct good">'+fmtH(x.good)+'</span></td><td><span class="ct bad">'+fmtH(x.bad)+'</span></td><td><span class="ct harsh">'+fmtH(x.harsh)+'</span></td><td>'+al+'</td></tr>';
    }).join('');
  }else{tb.innerHTML='<tr><td colspan="5" style="text-align:center;color:var(--mu)">No data</td></tr>'}
}

document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click',()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
    t.classList.add('on');period=t.dataset.p;loadStats();
  });
});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeM()});

loadCities();loadStats();
</script>
</body>
</html>"""

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Courier Ops Dashboard")
    print(f"  http://127.0.0.1:5050")
    print(f"  {len(CITIES)} cities configured\n")
    app.run(host="127.0.0.1", port=5050, debug=False)
