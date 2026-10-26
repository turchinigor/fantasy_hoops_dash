"""
First Yahoo Fantasy API call: authenticate once, then list your NBA leagues.

Setup:
    pip install yahoo_oauth python-dotenv

.env (same folder as this script):
    YAHOO_CLIENT_ID=your_client_id
    YAHOO_CLIENT_SECRET=your_client_secret
    YAHOO_REDIRECT_URI=oob        # or https://localhost:8080 - must match what you entered on Yahoo

Run:
    python yahoo_auth_test.py
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from yahoo_oauth import OAuth2

load_dotenv()

TOKEN_FILE = Path("oauth2.json")  # holds your keys + tokens; add it to .gitignore

# yahoo_oauth reads keys from a JSON file and writes tokens back into it.
if not TOKEN_FILE.exists():
    TOKEN_FILE.write_text(json.dumps({
        "consumer_key": os.environ["YAHOO_CLIENT_ID"],
        "consumer_secret": os.environ["YAHOO_CLIENT_SECRET"],
    }, indent=2))

# First run: a browser opens -> approve -> paste the code into this terminal.
# Later runs: reuses / refreshes the saved token, no browser.
oauth = OAuth2(
    None, None,
    from_file=str(TOKEN_FILE),
    callback_uri=os.getenv("YAHOO_REDIRECT_URI", "oob"),
)
if not oauth.token_is_valid():
    oauth.refresh_access_token()

url = ("https://fantasysports.yahooapis.com/fantasy/v2/"
       "users;use_login=1/games;game_codes=nba/leagues?format=json")
resp = oauth.session.get(url)
resp.raise_for_status()
data = resp.json()

# Dig out league name + key from Yahoo's nested JSON.
user = data["fantasy_content"]["users"]["0"]["user"]
games = user[1]["games"]
found = False
for gi in range(games["count"]):
    game = games[str(gi)]["game"]
    if len(game) < 2 or "leagues" not in game[1]:
        continue
    season = game[0].get("season")
    leagues = game[1]["leagues"]
    for li in range(leagues["count"]):
        lg = leagues[str(li)]["league"][0]
        print(f"{season}  {lg['name']:<30}  league_key = {lg['league_key']}")
        found = True

if not found:
    print("Authenticated OK, but no NBA leagues found on this Yahoo account.")
    print(json.dumps(data, indent=2)[:2000])