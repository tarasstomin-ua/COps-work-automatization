# UA Weather Dashboard — Setup Guide

## What this does
This sets up the **Courier Ops Weather Dashboard** on your computer. Once done, you'll have a local web dashboard where you can switch weather settings for all 37 Ukrainian cities by clicking a button. Changes are posted to the **#delivery-city-settings-automation** Slack channel on your behalf.

---

## Instructions for Cursor AI

> **Copy everything below this line and paste it as a message to Cursor Agent (Cmd+I → Agent mode):**

---

### Prompt to paste into Cursor:

```
Please set up the UA Weather Dashboard on my machine. Follow these steps exactly:

1. Clone the repo:
   git clone https://github.com/tarasstomin-ua/COps-work-automatization.git ~/Documents/Cursor/Bad\ weather\ settings

   If the folder already exists, just pull the latest:
   cd ~/Documents/Cursor/Bad\ weather\ settings && git pull

2. Install Python dependencies:
   pip3 install flask requests

3. Create the local config file at ~/Documents/Cursor/Bad weather settings/.cops_config.json with this content:
   {
     "slack_client_id": "2894167688.10943458704292",
     "slack_client_secret": "5d92724dd7a2cf21499d95877ff89cf9"
   }

4. Start the dashboard:
   cd ~/Documents/Cursor/Bad\ weather\ settings && python3 dashboard_v2.py

5. Once the server is running, open http://localhost:5050 in my browser.

6. Tell me to do these two things manually in the dashboard:
   a) Paste my GitHub Personal Access Token in the header (I can create one at https://github.com/settings/tokens → "Generate new token (classic)" → select "repo" scope → Generate → copy the token)
   b) Click the purple "Connect Slack" button in the header → authorize in Slack when prompted
   c) Select my name from the dropdown

That's it — the dashboard is ready to use.
```

---

## What happens after setup

- **Dashboard URL:** http://localhost:5050
- **How to start it next time:** Open Terminal, run:
  ```
  cd ~/Documents/Cursor/Bad\ weather\ settings && python3 dashboard_v2.py
  ```
  Then open http://localhost:5050

- **What each button does:** Clicking a weather button (Good/Bad/Harsh) for any city posts a message to Slack on your behalf. The @Delivery Courier Automation Bot picks it up and applies the settings automatically.

- **Live status:** The dashboard shows which weather is active in every city, who changed it, and when — shared across the whole team in real time.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `pip3 install` fails | Try `python3 -m pip install flask requests` |
| Port 5050 already in use | Run `lsof -ti :5050 \| xargs kill` then start again |
| "No Slack token" after restart | Click "Connect Slack" again — it's a one-time auth per machine |
| Dashboard won't open | Make sure `python3 dashboard_v2.py` is running in a terminal |
