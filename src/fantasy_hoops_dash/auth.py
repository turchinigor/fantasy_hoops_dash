"""Yahoo OAuth 2.0: one-time login, then token storage and automatic refresh."""

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlencode

import requests

from fantasy_hoops_dash.config import TOKEN_FILE, YahooCredentials

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
EXPIRY_MARGIN_SECONDS = 60


class AuthError(RuntimeError):
    pass


@dataclass
class Token:
    access_token: str
    refresh_token: str
    expires_at: float

    @property
    def expired(self) -> bool:
        return time.time() >= self.expires_at - EXPIRY_MARGIN_SECONDS


def authorization_url(creds: YahooCredentials) -> str:
    params = {
        "client_id": creds.client_id,
        "redirect_uri": creds.redirect_uri,
        "response_type": "code",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def _request_token(creds: YahooCredentials, **params: str) -> dict:
    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "redirect_uri": creds.redirect_uri,
            **params,
        },
        timeout=30,
    )
    if not resp.ok:
        raise AuthError(f"Yahoo token request failed ({resp.status_code}): {resp.text}")
    return resp.json()


def exchange_code(creds: YahooCredentials, code: str) -> Token:
    data = _request_token(creds, grant_type="authorization_code", code=code)
    return Token(data["access_token"], data["refresh_token"], time.time() + data["expires_in"])


def refresh(creds: YahooCredentials, token: Token) -> Token:
    data = _request_token(creds, grant_type="refresh_token", refresh_token=token.refresh_token)
    return Token(
        data["access_token"],
        data.get("refresh_token", token.refresh_token),
        time.time() + data["expires_in"],
    )


def load_token(path: Path = TOKEN_FILE) -> Token | None:
    if not path.exists():
        return None
    return Token(**json.loads(path.read_text()))


def save_token(token: Token, path: Path = TOKEN_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(token), indent=2))


def get_valid_token(creds: YahooCredentials, path: Path = TOKEN_FILE) -> Token:
    """Return a usable access token, refreshing and saving it if it has expired."""
    token = load_token(path)
    if token is None:
        raise AuthError("Not logged in. Run: python -m fantasy_hoops_dash login")
    if token.expired:
        token = refresh(creds, token)
        save_token(token, path)
    return token
