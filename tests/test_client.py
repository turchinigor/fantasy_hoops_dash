from fantasy_hoops_dash.client import League, parse_user_leagues


def _response(games: dict) -> dict:
    return {"fantasy_content": {"users": {"0": {"user": [{"guid": "x"}, {"games": games}]}}}}


def test_parse_user_leagues():
    games = {
        "count": 2,
        "0": {"game": [{"season": "2025"}]},  # season with no leagues
        "1": {
            "game": [
                {"season": "2026"},
                {
                    "leagues": {
                        "count": 1,
                        "0": {"league": [{"name": "Hoops", "league_key": "466.l.123"}]},
                    }
                },
            ]
        },
    }
    assert parse_user_leagues(_response(games)) == [League("2026", "Hoops", "466.l.123")]


def test_parse_user_leagues_empty():
    assert parse_user_leagues(_response({"count": 0})) == []
