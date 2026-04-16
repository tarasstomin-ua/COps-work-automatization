# Agent Context & Backlog

> **Purpose:** Persistent context file for any new Cursor agent session. Read this FIRST before doing anything. It contains proven workflows, hard-won lessons, and operational context so you don't re-invent or delay anything.

---

## Who is the user

- **Role:** Courier Ops Manager at Bolt (Delivery)
- **Country:** Ukraine
- **Cities managed:** 37 cities total — 5 TOP + 7 Tier 2 + 7 Tier 3 + 18 Rest
- **Admin panel auth:** SSL client certificate (stored in macOS Keychain — no manual login needed when using Selenium with a temp profile)

### Ukraine-specific operational factors
- **Air alarms:** Frequent air-raid alerts disrupt courier availability and demand. May require rapid profile switching (treat like harsh weather).
- **Weather volatility:** Continental climate — sharp shifts possible within hours. Winters (Nov–Mar) bring heavy snow/ice; summers get sudden storms.
- **Core workflow:** Monitor forecasts + busy ratios → switch city between Good / Bad / Harsh weather profiles to keep service levels stable.

---

## City registry

| City | Tier | CDT Group | Admin panel route | City ID | Delivery radius |
|------|------|-----------|-------------------|---------|-----------------|
| **Kyiv** | Tier 1 | Group 3 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/158` | 158 | 9 km |
| **Lviv** | Tier 2 | Group 3 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/496` | 496 | 9 km |
| **Dnipro** | Tier 3 | Group 3 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/499` | 499 | 9 km |
| **Kharkiv** | Tier 4 | Group 3 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/491` | 491 | 9 km |
| **Vinnytsia** | TOP | Group 3 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/501` | 501 | 9 km |

### Secondary cities (Tier 2) — 7 cities

| City | ID | Admin URL |
|------|----|-----------|
| Odesa | 498 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/498` |
| Kryvyi Rih | 504 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/504` |
| Poltava | 506 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/506` |
| Ivano-Frankivsk | 990 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/990` |
| Chernivtsi | 1084 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1084` |
| Irpin | 1261 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1261` |
| Cherkasy | 1087 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1087` |

### Secondary cities (Tier 3) — 7 cities

| City | ID | Admin URL |
|------|----|-----------|
| Zaporizhia | 500 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/500` |
| Bila Tserkva | 1079 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1079` |
| Khmelnytskyi | 1081 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1081` |
| Rivne | 1086 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1086` |
| Uzhhorod | 1131 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1131` |
| Brovary | 1259 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1259` |
| Zhytomyr | 1083 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1083` |

### Secondary cities (Rest) — 18 cities

| City | ID | Admin URL |
|------|----|-----------|
| Mykolaiv | 503 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/503` |
| Chernihiv | 1076 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1076` |
| Sumy | 1078 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1078` |
| Ternopil | 1080 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1080` |
| Lutsk | 1082 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1082` |
| Kropyvnytskyi | 1085 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1085` |
| Kremenchuk | 1088 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1088` |
| Kamianets-Podilskyi | 1132 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1132` |
| Pavlohrad | 1176 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1176` |
| Kamianske | 1178 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1178` |
| Mukachevo | 1179 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1179` |
| Boryspil | 1220 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1220` |
| Vyshhorod | 1262 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1262` |
| Drohobych | 1348 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1348` |
| Truskavets | 1357 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/1357` |
| Kovel | 2170 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/2170` |
| Oleksandriia | 2171 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/2171` |
| Kolomyia | 2499 | `https://admin-panel.bolt.eu/delivery-courier/settings/city/2499` |

**Note:** Chernihiv folder is named "Chenihiv" (typo in original creation). The dashboard maps display name "Chernihiv" to folder "Chenihiv".

---

## How to apply city settings to admin (PROVEN METHOD)

**This is the only method that works reliably. Do NOT try alternatives.**

### Step-by-step

1. **Do NOT kill Chrome.** Selenium opens its own separate Chrome window with a temp profile — it does not interfere with the user's running Chrome.

2. **Run the profile's Python script** with the appropriate flag:

   **For cities with known ID (e.g., Kyiv):** use `--url`
   ```bash
   python3 <script>.py "<csv_file>" --url https://admin-panel.bolt.eu/delivery-courier/settings/city/<ID> 2>&1
   ```

   **All cities now have known IDs:** use `--url` with the direct city URL
   ```bash
   python3 <script>.py "<csv_file>" --url https://admin-panel.bolt.eu/delivery-courier/settings/city/<ID> 2>&1
   ```

3. **That's it.** Takes ~20-30 seconds. The script launches Selenium-managed Chrome with a temp profile (`~/.chrome_selenium_profile`), reads the current JSON, patches it with CSV values, writes it back, and clicks Update.

### Exact commands — Kyiv

```bash
# Good weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Kyiv/Good weather"
python3 apply_good_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kyiv (1).csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/158 2>&1

# Bad weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Kyiv/Bad weather"
python3 apply_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kyiv (1).csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/158 --weather bad 2>&1

# Harsh weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Kyiv/Harsh weather"
python3 apply_harsh_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kyiv (1).csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/158 2>&1
```

### Exact commands — Lviv

```bash
# Good weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Lviv/Good weather"
python3 apply_good_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Lviv.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/496 2>&1

# Bad weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Lviv/Bad weather"
python3 apply_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Lviv.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/496 --weather bad 2>&1

# Harsh weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Lviv/Harsh weather"
python3 apply_harsh_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Lviv.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/496 2>&1
```

### Exact commands — Dnipro

```bash
# Good weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Dnipro/Good weather"
python3 apply_good_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Dnipro.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/499 2>&1

# Bad weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Dnipro/Bad weather"
python3 apply_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Dnipro.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/499 --weather bad 2>&1

# Harsh weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Dnipro/Harsh weather"
python3 apply_harsh_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Dnipro.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/499 2>&1
```

### Exact commands — Kharkiv

```bash
# Good weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Kharkiv/Good weather"
python3 apply_good_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kharkiv.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/491 2>&1

# Bad weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Kharkiv/Bad weather"
python3 apply_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kharkiv.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/491 --weather bad 2>&1

# Harsh weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Kharkiv/Harsh weather"
python3 apply_harsh_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kharkiv.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/491 2>&1
```

### Exact commands — Vinnytsia

```bash
# Good weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Vinnytsia/Good weather"
python3 apply_good_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Vinnytsia.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/501 2>&1

# Bad weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Vinnytsia/Bad weather"
python3 apply_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Vinnytsia.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/501 --weather bad 2>&1

# Harsh weather
cd "/Users/taras.stomin/Documents/Cursor/Bad weather settings/Vinnytsia/Harsh weather"
python3 apply_harsh_weather_settings.py "../COPS City settings Proposal - Q4'25 & Q1 26' - UA-Vinnytsia.csv" \
    --url https://admin-panel.bolt.eu/delivery-courier/settings/city/501 2>&1
```

### What NOT to do
- **Do NOT kill Chrome.** The user forbids killing/closing their Chrome. Selenium uses a separate temp profile (`~/.chrome_selenium_profile`) and opens its own window.
- **After the script finishes,** clean up only the Selenium Chrome with `pkill -f chrome_selenium_profile` (does NOT touch the user's browser).
- **Do NOT use `--debug-port 9222`** — macOS Chrome does not reliably expose the debug port. Tested & failed multiple times.
- **Do NOT worry about the `EOFError` at the end** — the `input("Press Enter...")` line fails in non-interactive shells, but the settings are already saved.
- **Set `block_until_ms: 0`** when running from Cursor Shell tool — background the command and poll the terminal file.

---

## Weather Profiles — Kyiv

| Profile | Folder | JSON file | Script | When to use |
|---------|--------|-----------|--------|-------------|
| **Good** | `Kyiv/Good weather/` | `Good Weather Settings Kyiv.json` | `apply_good_weather_settings.py` | Clear/mild weather |
| **Bad** | `Kyiv/Bad weather/` | `Bad Weather Settings Kyiv.json` | `apply_weather_settings.py --weather bad` | Rain, moderate snow, wind |
| **Harsh** | `Kyiv/Harsh weather/` | `Harsh Weather Settings Kyiv.json` | `apply_harsh_weather_settings.py` | Blizzard, ice, extreme cold, air alarms |

### Kyiv key settings

| Setting | Good | Bad | Harsh |
|---|---|---|---|
| Batching (min/max/bag/wait) | 300/800/700/700 | 360/920/820/820 | 360/920/820/820 |
| Per-provider needed_couriers | 0.7 | 1.2 | 1.5 |
| Per-provider max_courier_delay_s | 900 | 740 | 600 |
| Shrinkage (max/min ratio) | 1.4 / 2.2 | 1.2 / 2.0 | 1.1 / 1.85 |
| Eater surge busy ratio (min/max) | 1.2 / 2.2 | 1.1 / 2.0 | 1.1 / 1.8 |
| Eater surge multiplier (min/max) | 1.1 / 2.2 | 1.3 / 2.4 | 1.2 / 2.4 |
| Campaigns bypass threshold | 1.2 | 1.15 | 1.10 |
| ETA dynamic_radius_max | 6500 | 3000 | 2500 |
| ETA base_radius | 2000 | 1000 | 0 |
| ETA busy_ratio_min | 0.9 | 0.9 | 0.9 |
| ETA eta_multiplier_min | 1.1 | 1.3 | 1.3 |
| Matching bicycle/ped km | 4 / 2 | 4 / 2 | 7 / 4 |
| Max flight car/moto/bike | 6/6/4 | 5/5/3 | 5/5/3 |
| is_surcharge_applicable_only | true | true | false |
| PPC is_future_orders_verification | false | true | false |
| PPC min_flight car/moto | 3/2 | 3/2 | 2/1 |

---

## Weather Profiles — Lviv

| Profile | Folder | JSON file | Script | When to use |
|---------|--------|-----------|--------|-------------|
| **Good** | `Lviv/Good weather/` | `Good Weather Settings Lviv.json` | `apply_good_weather_settings.py` | Clear/mild weather |
| **Bad** | `Lviv/Bad weather/` | `Bad Weather Settings Lviv.json` | `apply_weather_settings.py --weather bad` | Rain, moderate snow, wind |
| **Harsh** | `Lviv/Harsh weather/` | `Harsh Weather Settings Lviv.json` | `apply_harsh_weather_settings.py` | Blizzard, ice, extreme cold, air alarms |

### Lviv key settings

| Setting | Good | Bad | Harsh |
|---|---|---|---|
| Batching (min/max/bag/wait) | 420/980/900/900 | 420/980/900/900 | 720/1080/960/960 |
| Per-provider needed_couriers | 0.7 | 0.7 | 0.9 |
| Per-provider max_courier_delay_s | 900 | 900 | 900 |
| Shrinkage (max/min ratio) | 1.4 / 2.2 | 1.3 / 2.1 | 1.2 / 2.0 |
| Eater surge busy ratio (min/max) | 1.2 / 2.2 | 1.1 / 2.2 | 1.1 / 2.0 |
| Eater surge multiplier (min/max) | 1.1 / 2.2 | 1.1 / 2.2 | 1.1 / 2.4 |
| Campaigns bypass threshold | 1.2 | 1.2 | 1.10 |
| ETA dynamic_radius_max | 6500 | 4500 | 3000 |
| ETA base_radius | 2000 | 2000 | 1000 |
| ETA busy_ratio_min | 0.6 | 0.5 | 0.9 |
| ETA eta_multiplier_min | 1.1 | 1.1 | 1.3 |
| Matching bicycle/ped km | 4 / 2 | 4 / 2 | 4 / 2 |
| Max flight car/moto/bike | 6/6/4 | 6/6/4 | 6/6/4 |
| is_surcharge_applicable_only | true | true | false |
| PPC is_future_orders_verification | false | false | false |

---

## Weather Profiles — Dnipro

| Profile | Folder | JSON file | Script | When to use |
|---------|--------|-----------|--------|-------------|
| **Good** | `Dnipro/Good weather/` | `Good Weather Settings Dnipro.json` | `apply_good_weather_settings.py` | Clear/mild weather |
| **Bad** | `Dnipro/Bad weather/` | `Bad Weather Settings Dnipro.json` | `apply_weather_settings.py --weather bad` | Rain, moderate snow, wind |
| **Harsh** | `Dnipro/Harsh weather/` | `Harsh Weather Settings Dnipro.json` | `apply_harsh_weather_settings.py` | Blizzard, ice, extreme cold, air alarms |

### Dnipro key settings

| Setting | Good | Bad | Harsh |
|---|---|---|---|
| Batching (min/max/bag/wait) | 540/1020/960/960 | 540/1020/960/960 | 480/1020/960/960 |
| Per-provider needed_couriers | 0.7 | 0.7 | 0.9 |
| Per-provider max_courier_delay_s | 900 | 900 | 900 |
| Shrinkage (max/min ratio) | 1.2 / 2.2 | 1.2 / 2.1 | 1.1 / 2.0 |
| Eater surge busy ratio (min/max) | 1.2 / 2.2 | 1.1 / 2.2 | 1.1 / 2.0 |
| Eater surge multiplier (min/max) | 1.1 / 2.2 | 1.1 / 2.2 | 1.1 / 2.4 |
| Campaigns bypass threshold | 1.2 | 1.2 | 1.10 |
| ETA dynamic_radius_max | 4000 | 3500 | 3000 |
| ETA base_radius | 2000 | 2000 | 1000 |
| ETA busy_ratio_min | 0.9 | 0.8 | 0.7 |
| ETA eta_multiplier_min | 1.1 | 1.1 | 1.3 |
| Matching bicycle/ped km | 4 / 2 | 4 / 2 | 4 / 2 |
| Max flight car/moto/bike | 6/6/4 | 6/6/4 | 6/6/4 |
| is_surcharge_applicable_only | true | true | false |
| PPC is_future_orders_verification | false | false | false |

---

## Weather Profiles — Kharkiv

| Profile | Folder | JSON file | Script | When to use |
|---------|--------|-----------|--------|-------------|
| **Good** | `Kharkiv/Good weather/` | `Good Weather Settings Kharkiv.json` | `apply_good_weather_settings.py` | Clear/mild weather |
| **Bad** | `Kharkiv/Bad weather/` | `Bad Weather Settings Kharkiv.json` | `apply_weather_settings.py --weather bad` | Rain, moderate snow, wind |
| **Harsh** | `Kharkiv/Harsh weather/` | `Harsh Weather Settings Kharkiv.json` | `apply_harsh_weather_settings.py` | Blizzard, ice, extreme cold, air alarms |

### Kharkiv key settings

| Setting | Good | Bad | Harsh |
|---|---|---|---|
| Batching (min/max/bag/wait) | 390/960/870/870 | 390/960/870/870 | 480/1020/960/960 |
| Per-provider needed_couriers | 0.7 | 0.7 | 0.9 |
| Per-provider max_courier_delay_s | 900 | 900 | 900 |
| Shrinkage (max/min ratio) | 1.2 / 2.2 | 1.2 / 2.1 | 1.1 / 2.1 |
| Eater surge busy ratio (min/max) | 1.2 / 2.2 | 1.2 / 2.1 | 1.1 / 2.0 |
| Eater surge multiplier (min/max) | 1.1 / 2.2 | 1.1 / 2.2 | 1.1 / 2.4 |
| Campaigns bypass threshold | 1.2 | 1.2 | 1.10 |
| ETA dynamic_radius_max | 4000 | 3500 | 3000 |
| ETA base_radius | 2000 | 2000 | 1000 |
| ETA busy_ratio_min | 0.9 | 0.8 | 0.7 |
| ETA eta_multiplier_min | 1.1 | 1.1 | 1.3 |
| Matching bicycle/ped km | 4 / 2 | 4 / 2 | 4 / 2 |
| Max flight car/moto/bike | 6/6/4 | 6/6/4 | 6/6/4 |
| is_surcharge_applicable_only | true | true | false |
| PPC is_future_orders_verification | false | false | false |

---

## Weather Profiles — Vinnytsia

| Profile | Folder | JSON file | Script | When to use |
|---------|--------|-----------|--------|-------------|
| **Good** | `Vinnytsia/Good weather/` | `Good Weather Settings Vinnytsia.json` | `apply_good_weather_settings.py` | Clear/mild weather |
| **Bad** | `Vinnytsia/Bad weather/` | `Bad Weather Settings Vinnytsia.json` | `apply_weather_settings.py --weather bad` | Rain, moderate snow, wind |
| **Harsh** | `Vinnytsia/Harsh weather/` | `Harsh Weather Settings Vinnytsia.json` | `apply_harsh_weather_settings.py` | Blizzard, ice, extreme cold, air alarms |

### Vinnytsia key settings

| Setting | Good | Bad | Harsh |
|---|---|---|---|
| Batching (min/max/bag/wait) | 300/760/660/660 | 300/760/660/660 | 480/1020/960/960 |
| Batching min_delay_ratio | 0.6 | 0.6 | 0.5 |
| Per-provider needed_couriers | 0.7 | 0.7 | 0.9 |
| Per-provider max_courier_delay_s | 900 | 900 | 900 |
| Shrinkage (max/min ratio) | 1.2 / 2.2 | 1.2 / 2.1 | 1.1 / 2.0 |
| Eater surge busy ratio (min/max) | 1.2 / 2.2 | 1.2 / 2.1 | 1.1 / 2.0 |
| Eater surge multiplier (min/max) | 1.1 / 2.2 | 1.1 / 2.2 | 1.1 / 2.4 |
| Campaigns bypass threshold | 1.2 | 1.15 | 1.10 |
| ETA dynamic_radius_max | 4000 | 3500 | 3000 |
| ETA base_radius | 2000 | 2000 | 1000 |
| ETA busy_ratio_min | 0.9 | 0.9 | 0.9 |
| ETA eta_multiplier_min | 1.1 | 1.1 | 1.3 |
| Matching bicycle/ped km | 4 / 2 | 4 / 2 | 4 / 2 |
| Max flight car/moto/bike | 6/6/4 | 6/6/4 | 6/6/4 |
| is_surcharge_applicable_only | true | true | false |
| PPC is_future_orders_verification | false | false | false |

---

## Hard overrides (ALWAYS enforce, ALL cities)
- **Courier Surge `is_enabled`: FALSE** — in ALL profiles, regardless of CSV.
- **Courier Surge `is_generation_enabled`: FALSE** — in ALL profiles.
- **Courier Surge notification `is_enabled`: FALSE** — in ALL profiles.
- **Arrival distance thresholds** — overridden in ALL cities, ALL profiles:
  - `provider_warning`: 300 (CSV says 100)
  - `eater_warning`: 300 (CSV says 100)
  - `provider_error`: 400 (CSV says 200)
  - `eater_error`: 400 (CSV says 200)
- Enforced via `COURIER_SURGE_OVERRIDES` (TOP cities) or `SETTING_OVERRIDES` (secondary cities) dict in every Python script.

---

## Source of truth

| City | Master CSV |
|------|-----------|
| Kyiv | `Bad weather settings/Kyiv/COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kyiv (1).csv` |
| Lviv | `Bad weather settings/Lviv/COPS City settings Proposal - Q4'25 & Q1 26' - UA-Lviv.csv` |
| Dnipro | `Bad weather settings/Dnipro/COPS City settings Proposal - Q4'25 & Q1 26' - UA-Dnipro.csv` |
| Kharkiv | `Bad weather settings/Kharkiv/COPS City settings Proposal - Q4'25 & Q1 26' - UA-Kharkiv.csv` |
| Vinnytsia | `Bad weather settings/Vinnytsia/COPS City settings Proposal - Q4'25 & Q1 26' - UA-Vinnytsia.csv` |
| **All 32 secondary cities** | `Bad weather settings/Secondary cities/COPS City settings Proposal - Q4'25 & Q1 26' - UA-Rest of cities.csv` |

- Copies live in each subfolder for script convenience.
- **TOP cities CSV column layout:** col 2 = setting path, col 5 = current value, col 6 = proposed (good weather), col 8 = bad weather, col 10 = harsh weather.
- **Secondary cities CSV column layout:** col 2 = setting path, col 4 = proposed (good weather), col 5 = harsh weather. (No bad weather profile for secondary cities.)

### When user provides a new CSV
1. Read the new CSV and diff against profiles.
2. Update all three JSON files with the correct values per profile.
3. Copy the new CSV into each subfolder (replacing old copies).
4. Always enforce Courier Surge overrides (FALSE).
5. Update the PY script docstrings if the CSV filename changed.

### When adding a new city
1. User creates a city folder under `Bad weather settings/` and puts the CSV there.
2. Create Good/Bad/Harsh subfolders with JSON + PY files (use existing city as template).
3. PY scripts should have `CITY_NAME` and `CITY_LIST_URL` constants.
4. Use `--browser` flag for cities without a known admin panel city ID.
5. Once city ID is discovered (visible in URL after first navigation), update the backlog city registry and optionally switch to `--url` for speed.

---

## Dashboard

**Location:** `Bad weather settings/dashboard.py`
**Run:** `python3 dashboard.py` → open `http://127.0.0.1:5050`
**Dependency:** Flask (`pip3 install flask`, see `requirements.txt`)

### Features (v3 — rebuilt Apr 7 2026)
- **37 cities** across 4 tiers: TOP (5), Tier 2 (7), Tier 3 (7), Rest (18)
- **Active Weather Status** overview at the top — compact pills for every city, grouped by tier, each sub-tier collapsible
- **Collapsible tier sections** — TOP cities expanded by default, Tier 2/3/Rest collapsed. Click to toggle.
- **TOP cities** have Good / Bad / Harsh buttons; **secondary cities** have Good / Harsh only (no Bad weather profile)
- **One-click apply** opens a separate Selenium Chrome window, applies to admin, then cleans up (does NOT touch user's Chrome)
- **Active profile + live timer** per city card
- **Strategic/dark design** — mission-control aesthetic, information-dense, professional
- **Time-based analytics** with granularity (hour / day / week / month / year / all):
  - Total tracked time, most used profile, total profile switches
  - Time distribution bar, per-city breakdown table (scrollable for 37 cities)
- **Confirmation dialog** before every apply action
- **Task status** with real-time polling and toast notifications
- **Usage log:** stored in `usage_log.json` (auto-created)

### Adding a new city to the dashboard
1. Add city entry to `CITIES` dict in `dashboard.py`
2. Specify `group`, `group_order`, `profiles` (list), `base_path`, `csv`, `url`
3. For secondary cities, `base_path` = `"Secondary cities/{tier_folder}/{city_folder}"`
4. Restart the dashboard

---

## General agent instructions

- **Read this file at the start of every session.** It's the source of truth for how things work.
- **Don't invent new approaches.** If a proven method is documented above, use it exactly.
- **Be fast.** The user manages live operations — delays cost real money.
- **When asked to apply settings to admin:** follow the "How to apply city settings" section above verbatim. Kill Chrome → run script → done. No experiments.
- **When asked to update JSON/PY files from a new CSV:** follow the "When user provides a new CSV" checklist.
- **Workspace root:** `/Users/taras.stomin/Documents/Cursor`

---

## Change log

| Date | Action | Details |
|------|--------|---------|
| 2026-04-07 | Harsh weather applied to Kyiv admin | Ran `apply_harsh_weather_settings.py` via Selenium (no debug-port). Kill Chrome → run script → 29 changes applied → Update clicked → done in ~22s. |
| 2026-04-07 | All Kyiv profiles revised | Updated 3 JSONs + 3 PY scripts per new CSV. Courier Surge forced FALSE everywhere. CSV copied to subfolders. |
| 2026-04-07 | Lviv city added | Created 3 profile folders with JSON + PY + CSV. Scripts use `--browser` flag to navigate via city list (city ID TBD). Courier Surge forced FALSE. |
| 2026-04-07 | Dnipro city added | Created 3 profile folders with JSON + PY + CSV. Same pattern as Lviv — `--browser` flag, city ID TBD. Courier Surge forced FALSE. |
| 2026-04-07 | Kharkiv city added | Created 3 profile folders with JSON + PY + CSV. Tier 4, Group 3. Same pattern — `--browser` flag, city ID TBD. Courier Surge forced FALSE. |
| 2026-04-07 | Vinnytsia city added | Created 3 profile folders with JSON + PY + CSV. Tier 5, Group 3. Same pattern — `--browser` flag, city ID TBD. Courier Surge forced FALSE. |
| 2026-04-07 | Dashboard created | Flask-based web dashboard at `dashboard.py`. One-click weather profile apply for all 5 cities. Usage analytics with time granularity. Groups cities under "TOP cities". |
| 2026-04-07 | All city IDs discovered | Lviv=496, Dnipro=499, Kharkiv=491, Vinnytsia=501. All cities now use `--url` direct links. Dashboard and BACKLOG updated. |
| 2026-04-07 | 32 secondary cities added | Created Good/Harsh weather folders, JSONs, PY scripts for all secondary cities across Tier 2 (7), Tier 3 (7), Rest (18). All use shared CSV (UA-Rest of cities). Courier Surge forced FALSE. |
| 2026-04-07 | Arrival distance thresholds updated | ALL cities (TOP + secondary): provider_warning=300, eater_warning=300, provider_error=400, eater_error=400. Updated 15 TOP city JSONs + 15 PY scripts + all 64 secondary city JSONs. |
| 2026-04-07 | Dashboard v3 rebuilt | Collapsible tier sections, active weather overview at top, 37 cities, strategic dark design. Secondary cities have Good/Harsh only (no Bad). |
