#!/usr/bin/env python3
"""
Bulk update all city settings files:
  - Remove courier surge FALSE overrides from all PY scripts
  - Update arrival distance thresholds to 100/100/200/200
  - Regenerate JSON files from new CSVs
  - Copy new CSVs to subfolders
"""

import csv
import json
import shutil
from pathlib import Path

BASE = Path("/Users/taras.stomin/Documents/Cursor/Bad weather settings")

# ── Helpers ──────────────────────────────────────────────────────────────────

def coerce(value_str):
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


def set_nested(obj, keys, value):
    for k in keys[:-1]:
        if k not in obj or not isinstance(obj[k], dict):
            return False
        obj = obj[k]
    if keys[-1] in obj:
        obj[keys[-1]] = value
        return True
    return False


def get_nested(obj, keys):
    for k in keys:
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj


def parse_csv_column(csv_path, col_target):
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    settings = []
    for row in rows:
        if len(row) <= col_target:
            continue
        path = row[2].strip()
        if not path or "/" not in path:
            continue
        settings.append({"path": path, "value": row[col_target].strip()})
    return settings


THRESHOLD_OVERRIDES = {
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 100,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 100,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 200,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 200,
}


def update_json_from_csv(json_path, csv_path, col_target):
    settings = parse_csv_column(csv_path, col_target)
    with open(json_path) as f:
        data = json.load(f)

    changes = []
    for s in settings:
        val = coerce(s["value"])
        if val is None:
            continue
        if s["path"] in THRESHOLD_OVERRIDES:
            val = THRESHOLD_OVERRIDES[s["path"]]
        keys = s["path"].split("/")
        old = get_nested(data, keys)
        if old is None:
            continue
        if old != val:
            changes.append((s["path"], old, val))
            set_nested(data, keys, val)

    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    f_name = json_path.name
    return changes


# ── PY Override Replacement ──────────────────────────────────────────────────

OLD_TOP_STD = '''COURIER_SURGE_OVERRIDES = {
    "dynamic_multiplier/courier_earning/is_enabled": False,
    "dynamic_multiplier/courier_earning/is_generation_enabled": False,
    "dynamic_multiplier/courier_earning/notification_settings/is_enabled": False,
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 400,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 400,
}'''

OLD_TOP_KH = '''COURIER_SURGE_OVERRIDES = {
    "dynamic_multiplier/courier_earning/is_enabled": False,
    "dynamic_multiplier/courier_earning/is_generation_enabled": False,
    "dynamic_multiplier/courier_earning/notification_settings/is_enabled": False,
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 50000000,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 50000000,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 60000000,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 60000000,
}'''

NEW_TOP = '''COURIER_SURGE_OVERRIDES = {
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 100,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 100,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 200,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 200,
}'''

OLD_SEC = '''SETTING_OVERRIDES = {
    "dynamic_multiplier/courier_earning/is_enabled": False,
    "dynamic_multiplier/courier_earning/is_generation_enabled": False,
    "dynamic_multiplier/courier_earning/notification_settings/is_enabled": False,
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 400,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 400,
}'''

NEW_SEC = '''SETTING_OVERRIDES = {
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 100,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 100,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 200,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 200,
}'''


def replace_overrides_top(py_path):
    content = py_path.read_text()
    for old in [OLD_TOP_KH, OLD_TOP_STD]:
        if old in content:
            content = content.replace(old, NEW_TOP)
            py_path.write_text(content)
            return True
    return False


def replace_overrides_sec(py_path):
    content = py_path.read_text()
    if OLD_SEC in content:
        content = content.replace(OLD_SEC, NEW_SEC)
        py_path.write_text(content)
        return True
    return False


# ── TOP cities ───────────────────────────────────────────────────────────────

TOP_CITIES = {
    "Kyiv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kyiv (2).csv",
    "Lviv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Lviv (1).csv",
    "Dnipro": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Dnipro (1).csv",
    "Kharkiv": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kharkiv (1).csv",
    "Vinnytsia": "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Vinnytsia.csv",
}

TOP_PROFILES = {
    "Good weather":  {"col": 6, "json": "Good Weather Settings {}.json"},
    "Bad weather":   {"col": 8, "json": "Bad Weather Settings {}.json"},
    "Harsh weather": {"col": 10, "json": "Harsh Weather Settings {}.json"},
}

stats = {"py": 0, "json": 0, "csv": 0, "json_changes": 0}


def process_top_cities():
    print("=" * 70)
    print("  UPDATING TOP CITIES (5 cities x 3 profiles)")
    print("=" * 70)

    for city, new_csv_name in TOP_CITIES.items():
        print(f"\n  [{city}]")
        city_dir = BASE / city
        new_csv = city_dir / new_csv_name

        if not new_csv.exists():
            print(f"    WARNING: CSV not found: {new_csv}")
            continue

        for prof_name, prof_cfg in TOP_PROFILES.items():
            subfolder = city_dir / prof_name
            if not subfolder.exists():
                continue

            # Copy CSV to subfolder
            dest = subfolder / new_csv_name
            shutil.copy2(new_csv, dest)
            stats["csv"] += 1

            # Update PY overrides
            for py in subfolder.glob("apply_*.py"):
                if replace_overrides_top(py):
                    stats["py"] += 1
                    print(f"    PY overrides updated: {prof_name}/{py.name}")

            # Update JSON
            json_name = prof_cfg["json"].format(city)
            json_path = subfolder / json_name
            if json_path.exists():
                changes = update_json_from_csv(json_path, new_csv, prof_cfg["col"])
                stats["json"] += 1
                stats["json_changes"] += len(changes)
                if changes:
                    print(f"    JSON updated ({len(changes)} changes): {prof_name}/{json_name}")
                    for path, old, new in changes:
                        print(f"      {path}: {old} -> {new}")
                else:
                    print(f"    JSON unchanged: {prof_name}/{json_name}")


# ── Secondary cities ─────────────────────────────────────────────────────────

SEC_CSV = BASE / "Secondary cities" / "COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv"

SEC_PROFILES = {
    "Good weather":  {"col": 4},
    "Harsh weather": {"col": 5},
}


def process_secondary_cities():
    print("\n" + "=" * 70)
    print("  UPDATING SECONDARY CITIES (32 cities x 2 profiles)")
    print("=" * 70)

    sec_base = BASE / "Secondary cities"
    if not sec_base.exists():
        print("  Secondary cities folder not found!")
        return

    for tier_dir in sorted(sec_base.iterdir()):
        if not tier_dir.is_dir() or tier_dir.name.startswith(".") or tier_dir.name.endswith(".csv"):
            continue

        for city_dir in sorted(tier_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name.startswith("."):
                continue

            city = city_dir.name
            city_changed = False

            for prof_name, prof_cfg in SEC_PROFILES.items():
                subfolder = city_dir / prof_name
                if not subfolder.exists():
                    continue

                # Update PY overrides
                for py in subfolder.glob("apply_*.py"):
                    if replace_overrides_sec(py):
                        stats["py"] += 1
                        city_changed = True

                # Update JSON
                for json_file in subfolder.glob("*.json"):
                    changes = update_json_from_csv(json_file, SEC_CSV, prof_cfg["col"])
                    stats["json"] += 1
                    stats["json_changes"] += len(changes)
                    if changes:
                        city_changed = True

            if city_changed:
                print(f"    Updated: {city}")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    process_top_cities()
    process_secondary_cities()

    print("\n" + "=" * 70)
    print(f"  DONE: {stats['py']} PY files, {stats['json']} JSON files, "
          f"{stats['csv']} CSV copies, {stats['json_changes']} total JSON value changes")
    print("=" * 70)
