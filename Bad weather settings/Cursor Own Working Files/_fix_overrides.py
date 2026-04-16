#!/usr/bin/env python3
"""
Fix all city settings:
  - Courier surge: ALWAYS FALSE (is_enabled, is_generation_enabled, notification_settings/is_enabled)
  - Arrival thresholds: 300/300/400/400 for all cities EXCEPT Kharkiv (30000000/30000000/40000000/40000000)
  - All other settings: from CSV Proposed Settings column (eater surge, batching, etc.)
"""

import csv
import json
from pathlib import Path

BASE = Path("/Users/taras.stomin/Documents/Cursor/Bad weather settings")

COURIER_SURGE_FALSE = {
    "dynamic_multiplier/courier_earning/is_enabled": False,
    "dynamic_multiplier/courier_earning/is_generation_enabled": False,
    "dynamic_multiplier/courier_earning/notification_settings/is_enabled": False,
}

THRESHOLDS_STD = {
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 400,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 400,
}

THRESHOLDS_KH = {
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 30000000,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 30000000,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 40000000,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 40000000,
}


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


def fix_json(json_path, is_kharkiv):
    with open(json_path) as f:
        data = json.load(f)

    overrides = {**COURIER_SURGE_FALSE, **(THRESHOLDS_KH if is_kharkiv else THRESHOLDS_STD)}
    changes = []

    for path, val in overrides.items():
        keys = path.split("/")
        old = get_nested(data, keys)
        if old is None:
            continue
        if old != val:
            set_nested(data, keys, val)
            changes.append((path, old, val))

    if changes:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)

    return changes


# ── PY override blocks ───────────────────────────────────────────────────────

# What's currently in TOP city PY files (just set by previous script)
CUR_TOP = '''COURIER_SURGE_OVERRIDES = {
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 100,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 100,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 200,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 200,
}'''

NEW_TOP_STD = '''COURIER_SURGE_OVERRIDES = {
    "dynamic_multiplier/courier_earning/is_enabled": False,
    "dynamic_multiplier/courier_earning/is_generation_enabled": False,
    "dynamic_multiplier/courier_earning/notification_settings/is_enabled": False,
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 400,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 400,
}'''

NEW_TOP_KH = '''COURIER_SURGE_OVERRIDES = {
    "dynamic_multiplier/courier_earning/is_enabled": False,
    "dynamic_multiplier/courier_earning/is_generation_enabled": False,
    "dynamic_multiplier/courier_earning/notification_settings/is_enabled": False,
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 30000000,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 30000000,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 40000000,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 40000000,
}'''

CUR_SEC = '''SETTING_OVERRIDES = {
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 100,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 100,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 200,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 200,
}'''

NEW_SEC = '''SETTING_OVERRIDES = {
    "dynamic_multiplier/courier_earning/is_enabled": False,
    "dynamic_multiplier/courier_earning/is_generation_enabled": False,
    "dynamic_multiplier/courier_earning/notification_settings/is_enabled": False,
    "order_settings/arrival_distance_threshold_in_meters/provider_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/eater_warning": 300,
    "order_settings/arrival_distance_threshold_in_meters/provider_error": 400,
    "order_settings/arrival_distance_threshold_in_meters/eater_error": 400,
}'''


def fix_py_top(py_path, is_kharkiv):
    content = py_path.read_text()
    target = NEW_TOP_KH if is_kharkiv else NEW_TOP_STD
    if CUR_TOP in content:
        content = content.replace(CUR_TOP, target)
        py_path.write_text(content)
        return True
    return False


def fix_py_sec(py_path):
    content = py_path.read_text()
    if CUR_SEC in content:
        content = content.replace(CUR_SEC, NEW_SEC)
        py_path.write_text(content)
        return True
    return False


# ── Main ─────────────────────────────────────────────────────────────────────

TOP_CITIES = ["Kyiv", "Lviv", "Dnipro", "Kharkiv", "Vinnytsia"]
TOP_PROFILES = ["Good weather", "Bad weather", "Harsh weather"]

stats = {"py": 0, "json": 0, "json_changes": 0}


def process_top():
    print("=" * 70)
    print("  FIXING TOP CITIES")
    print("=" * 70)

    for city in TOP_CITIES:
        is_kh = city == "Kharkiv"
        print(f"\n  [{city}] {'(special thresholds)' if is_kh else ''}")
        city_dir = BASE / city

        for prof in TOP_PROFILES:
            subfolder = city_dir / prof

            for py in subfolder.glob("apply_*.py"):
                if fix_py_top(py, is_kh):
                    stats["py"] += 1
                    print(f"    PY fixed: {prof}/{py.name}")

            for jf in subfolder.glob("*.json"):
                if jf.name.endswith(".json"):
                    changes = fix_json(jf, is_kh)
                    stats["json"] += 1
                    stats["json_changes"] += len(changes)
                    if changes:
                        print(f"    JSON fixed ({len(changes)} changes): {prof}/{jf.name}")
                        for p, o, n in changes:
                            print(f"      {p}: {o} -> {n}")


def process_secondary():
    print("\n" + "=" * 70)
    print("  FIXING SECONDARY CITIES")
    print("=" * 70)

    sec_base = BASE / "Secondary cities"
    for tier_dir in sorted(sec_base.iterdir()):
        if not tier_dir.is_dir() or tier_dir.name.startswith("."):
            continue
        for city_dir in sorted(tier_dir.iterdir()):
            if not city_dir.is_dir() or city_dir.name.startswith("."):
                continue

            city = city_dir.name
            changed = False

            for prof in ["Good weather", "Harsh weather"]:
                subfolder = city_dir / prof
                if not subfolder.exists():
                    continue

                for py in subfolder.glob("apply_*.py"):
                    if fix_py_sec(py):
                        stats["py"] += 1
                        changed = True

                for jf in subfolder.glob("*.json"):
                    changes = fix_json(jf, False)
                    stats["json"] += 1
                    stats["json_changes"] += len(changes)
                    if changes:
                        changed = True

            if changed:
                print(f"    Fixed: {city}")


if __name__ == "__main__":
    process_top()
    process_secondary()

    print("\n" + "=" * 70)
    print(f"  DONE: {stats['py']} PY files, {stats['json']} JSON files fixed, "
          f"{stats['json_changes']} JSON value corrections")
    print("=" * 70)
