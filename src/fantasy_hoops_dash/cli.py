"""Command line entry point: ``python -m fantasy_hoops_dash <command>``."""

import argparse
import sys
import webbrowser

import requests

from fantasy_hoops_dash import auth
from fantasy_hoops_dash.client import YahooFantasyClient
from fantasy_hoops_dash.config import load_credentials


def cmd_login(args: argparse.Namespace) -> int:
    creds = load_credentials()
    code = args.code
    if code is None:
        url = auth.authorization_url(creds)
        print(f"Open this URL, approve access, then copy the 'code' value:\n\n{url}\n")
        webbrowser.open(url)
        code = input("Code: ").strip()
    auth.save_token(auth.exchange_code(creds, code))
    print("Logged in. Token saved.")
    return 0


def cmd_leagues(args: argparse.Namespace) -> int:
    leagues = YahooFantasyClient().nba_leagues()
    if not leagues:
        print("No NBA leagues found on this Yahoo account.")
    for lg in leagues:
        print(f"{lg.season}  {lg.name:<30}  league_key = {lg.league_key}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fantasy-hoops")
    sub = parser.add_subparsers(dest="command", required=True)

    login = sub.add_parser("login", help="log in to Yahoo (one time)")
    login.add_argument("--code", help="authorization code, if you already have one")
    login.set_defaults(func=cmd_login)

    leagues = sub.add_parser("leagues", help="list your NBA leagues")
    leagues.set_defaults(func=cmd_leagues)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (RuntimeError, requests.RequestException) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
