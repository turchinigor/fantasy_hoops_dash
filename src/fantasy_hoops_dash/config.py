"""Paths and credentials, read from the environment and the project's .env file."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SECRETS_DIR = PROJECT_ROOT / ".secrets"
DATA_DIR = PROJECT_ROOT / "data"
TOKEN_FILE = SECRETS_DIR / "yahoo_token.json"


@dataclass(frozen=True)
class YahooCredentials:
    client_id: str
    client_secret: str
    redirect_uri: str


def load_credentials() -> YahooCredentials:
    load_dotenv(PROJECT_ROOT / ".env")
    try:
        return YahooCredentials(
            client_id=os.environ["YAHOO_CLIENT_ID"],
            client_secret=os.environ["YAHOO_CLIENT_SECRET"],
            redirect_uri=os.getenv("YAHOO_REDIRECT_URI", "oob"),
        )
    except KeyError as e:
        raise RuntimeError(
            f"{e.args[0]} is not set. Copy .env.example to .env and fill it in."
        ) from None
