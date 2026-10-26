# Fantasy NBA Dashboard

A personal analytics dashboard for my own team in a single private Yahoo Fantasy Basketball (NBA) league.

> **Status:** In development. Waiting for approval of Yahoo Fantasy Sports API access.

## What it is

This is a private, non-commercial tool that runs locally on my own machine. It is not a published website or app, and I am its only user.

It reads data from my league through the official [Yahoo Fantasy Sports API](https://sports.yahoo.com/developer/docs/) and turns it into a dashboard that helps me manage my team over the season.

## Planned features

- **League overview:** standings, weekly scoreboard and head-to-head matchups
- **Category tracking:** how my team performs in each scoring category over time
- **Roster analysis:** daily rosters for all teams in the league, with player stats
- **Waiver wire:** available free agents ranked against my team's weak categories
- **Transaction log:** adds, drops and trades across the league
- **Recommendations:** suggested lineup and waiver moves

## How it works

1. A Python script authenticates with OAuth 2.0 as my own Yahoo account.
2. It reads league data a few times per day at most. Access is read-only.
3. Responses are parsed and stored locally.
4. The dashboard is built from the stored data.

## Yahoo Fantasy Sports data used (read-only)

| Data | Endpoint |
|---|---|
| League metadata and settings | `league/{league_key}/settings` |
| Standings | `league/{league_key}/standings` |
| Scoreboard and matchups | `league/{league_key}/scoreboard` |
| Team rosters by date | `team/{team_key}/roster;date=YYYY-MM-DD` |
| Player stats and free agents | `league/{league_key}/players` |
| Transactions | `league/{league_key}/transactions` |

## Scope and data use

- **Users:** 1 (myself)
- **Leagues:** 1 private league that I am a member of
- **Access needed:** read-only; write access is not needed
- **Data handling:** stored locally only; not redistributed, shared, sold or made public

## Tech stack

- Python
- OAuth 2.0 for Yahoo authentication
- pandas for data processing
- Local storage
- Dashboard layer (to be decided)

## Project structure

```
src/fantasy_hoops_dash/
    config.py    paths and credentials (.env)
    auth.py      Yahoo OAuth 2.0 login, token storage and refresh
    client.py    read-only Yahoo Fantasy API client
    cli.py       command line entry point
tests/           unit tests
```

## Setup

Requires Python 3.12+.

```bash
python -m venv .venv            # or any venv location
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
copy .env.example .env          # then fill in your Yahoo app credentials
```

## Usage

```bash
python -m fantasy_hoops_dash login     # one time: approve in the browser, paste the code
python -m fantasy_hoops_dash leagues   # list your NBA leagues
pytest                                 # run tests
```

The login token is saved in `.secrets/` and refreshed automatically.

## Security

API credentials, tokens and `.env` files are never committed to this repository.

## Disclaimer

This is a personal project. It is not affiliated with, endorsed by or sponsored by Yahoo.