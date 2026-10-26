import time

import pytest

from fantasy_hoops_dash import auth
from fantasy_hoops_dash.config import YahooCredentials

CREDS = YahooCredentials("id", "secret", "https://localhost:8080")


def test_token_expiry():
    assert auth.Token("a", "r", time.time() - 1).expired
    assert not auth.Token("a", "r", time.time() + 3600).expired


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "token.json"
    token = auth.Token("access", "refresh", 123.0)
    auth.save_token(token, path)
    assert auth.load_token(path) == token


def test_get_valid_token_requires_login(tmp_path):
    with pytest.raises(auth.AuthError):
        auth.get_valid_token(CREDS, tmp_path / "missing.json")


def test_get_valid_token_refreshes_expired(tmp_path, monkeypatch):
    path = tmp_path / "token.json"
    auth.save_token(auth.Token("old", "refresh", 0.0), path)
    monkeypatch.setattr(
        auth, "_request_token", lambda creds, **p: {"access_token": "new", "expires_in": 3600}
    )

    token = auth.get_valid_token(CREDS, path)

    assert token.access_token == "new"
    assert token.refresh_token == "refresh"
    assert auth.load_token(path) == token


def test_authorization_url_contains_client_and_redirect():
    url = auth.authorization_url(CREDS)
    assert "client_id=id" in url
    assert "redirect_uri=https%3A%2F%2Flocalhost%3A8080" in url
