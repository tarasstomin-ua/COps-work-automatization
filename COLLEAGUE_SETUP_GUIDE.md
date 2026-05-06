# UA Weather Dashboard — Setup Guide

## What this does
This sets up the **Courier Ops Weather Dashboard** on your computer. It's a shared dashboard — all 3 of us (Taras, Anna, Nataliia) see the same live status for all 37 cities in real time. When anyone changes a city's weather, everyone's dashboard updates within 30 seconds.

The dashboard posts messages to **#delivery-city-settings-automation** on your behalf, and **@Delivery Courier Automation Bot** applies the settings automatically.

---

## Setup — paste this into Cursor

Open **Cursor** → press **Cmd+I** → make sure you're in **Agent** mode → paste this:

```
Please set up the UA Weather Dashboard on my machine. Follow ALL steps exactly:

1. Clone the repo (if folder exists, pull latest instead):
   git clone https://github.com/tarasstomin-ua/COps-work-automatization.git ~/Documents/Cursor/Bad\ weather\ settings
   OR if folder exists:
   cd ~/Documents/Cursor/Bad\ weather\ settings && git pull

2. Install Python dependencies:
   pip3 install flask requests
   If that fails try: python3 -m pip install flask requests

3. Create the local config file. Write this JSON to ~/Documents/Cursor/Bad weather settings/.cops_config.json :
   {
     "pat": "ASK_TARAS_FOR_GITHUB_TOKEN",
     "slack_client_id": "2894167688.10943458704292",
     "slack_client_secret": "5d92724dd7a2cf21499d95877ff89cf9"
   }
   IMPORTANT: Replace ASK_TARAS_FOR_GITHUB_TOKEN with the actual GitHub token Taras sends you.

4. Set up auto-start so the dashboard survives restarts. Add this to crontab:
   @reboot sleep 10 && cd "/Users/$(whoami)/Documents/Cursor/Bad weather settings" && /usr/bin/python3 dashboard_v2.py >> /tmp/courier-ops-dashboard.log 2>&1
   Use: echo '@reboot sleep 10 && cd "$HOME/Documents/Cursor/Bad weather settings" && /usr/bin/python3 dashboard_v2.py >> /tmp/courier-ops-dashboard.log 2>&1' | crontab -

5. Start the dashboard now:
   Kill anything on port 5050 first: lsof -ti :5050 | xargs kill 2>/dev/null
   Then: cd ~/Documents/Cursor/Bad\ weather\ settings && python3 dashboard_v2.py

6. Once running, open http://localhost:5050 in the browser.

7. Tell me I need to do ONE manual step in the dashboard:
   - Click the purple "Connect Slack" button in the header → it will open Slack → I authorize → done
   - Then select my name from the dropdown

That's it. The dashboard auto-starts on reboot and stays running 24/7.
```

---

## After setup

- **Dashboard URL:** http://localhost:5050
- **Auto-starts** on Mac login (via crontab)
- **Shared status:** All team members see the same city statuses in real time (synced via GitHub every 30 seconds)
- **How it works:** Click a weather button → message posted to Slack on your behalf → bot applies settings → status updates for everyone

---

## If dashboard goes down

Open **Cursor** → paste:

```
My dashboard is down. Kill anything on port 5050, then start it:
lsof -ti :5050 | xargs kill
cd ~/Documents/Cursor/Bad\ weather\ settings && python3 dashboard_v2.py
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `pip3 install` fails | Try `python3 -m pip install flask requests` |
| Port 5050 already in use | `lsof -ti :5050 \| xargs kill` then start again |
| "Connect Slack" needed after restart | Click the purple button again — one-time per machine |
| Dashboard won't open | Make sure `python3 dashboard_v2.py` is running |
| Don't see teammate's changes | Refresh the page — auto-updates every 30 seconds |
