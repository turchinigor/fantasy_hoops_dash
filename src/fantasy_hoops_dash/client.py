"""Thin client for the Yahoo Fantasy Sports API (read-only)."""

from dataclasses import dataclass
from pathlib import Path

import requests

from fantasy_hoops_dash.auth import get_valid_token
from fantasy_hoops_dash.config import TOKEN_FILE, YahooCredentials, load_credentials

BASE_URL = "https://fantasysports.yahooapis.com/fantasy/v2/"


class YahooAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class League:
    season: str
    name: str
    league_key: str


class YahooFantasyClient:
    def __init__(self, creds: YahooCredentials | None = None, token_file: Path = TOKEN_FILE):
        self._creds = creds or load_credentials()
        self._token_file = token_file
        self._session = requests.Session()

    def get(self, path: str) -> dict:
        """GET a Fantasy API resource, e.g. ``league/{league_key}/standings``."""
        token = get_valid_token(self._creds, self._token_file)
        resp = self._session.get(
            BASE_URL + path,
            params={"format": "json"},
            headers={"Authorization": f"Bearer {token.access_token}"},
            timeout=30,
        )
        if not resp.ok:
            raise YahooAPIError(
                f"GET {path} failed ({resp.status_code}): {_error_description(resp)}"
            )
        return resp.json()

    def nba_leagues(self) -> list[League]:
        """Leagues the logged-in user belongs to, across all NBA seasons."""
        return parse_user_leagues(self.get("users;use_login=1/games;game_codes=nba/leagues"))


def parse_user_leagues(data: dict) -> list[League]:
    user = data["fantasy_content"]["users"]["0"]["user"]
    games = user[1]["games"]
    leagues = []
    for gi in range(games["count"]):
        game = games[str(gi)]["game"]
        if len(game) < 2 or "leagues" not in game[1]:
            continue
        season = game[0].get("season", "")
        game_leagues = game[1]["leagues"]
        for li in range(game_leagues["count"]):
            lg = game_leagues[str(li)]["league"][0]
            leagues.append(League(season, lg["name"], lg["league_key"]))
    return leagues


def _error_description(resp: requests.Response) -> str:
    try:
        return resp.json()["error"]["description"]
    except (ValueError, KeyError, TypeError):
        return resp.text[:500]
