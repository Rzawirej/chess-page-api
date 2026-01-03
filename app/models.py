from dataclasses import dataclass, field
from typing import List

PlayersList = List['Player']
GroupsList = List['Group']

@dataclass(frozen=True)
class Player:
    place: int
    title: str
    name: str
    url: str
    elo: int
    elo_chg: int
    points: float

@dataclass()
class Group:
    url: str
    players_number: int
    played_rounds: int
    name: str
    is_only_female: bool = False
    players: PlayersList = field(default_factory=list)

@dataclass()
class Tournament:
    name: str
    year: int
    site: str
    groups: GroupsList = field(default_factory=list)


def dict_to_tournament(d: dict) -> Tournament:
    return Tournament(
        name=d["name"],
        year=d["year"],
        site=d["site"],
        groups=[
            Group(
                url=g["url"],
                players_number=g["players_number"],
                played_rounds=g["played_rounds"],
                name=g["name"],
                is_only_female=g.get("is_only_female", False),
                players=[
                    Player(
                        place=p["place"],
                        title=p["title"],
                        name=p["name"],
                        url=p["url"],
                        elo=p["elo"],
                        elo_chg=p["elo_chg"],
                        points=p["points"],
                    )
                    for p in g.get("players", [])
                ],
            )
            for g in d.get("groups", [])
        ],
    )


def tournament_to_dict(t: Tournament) -> dict:
    return {
        "name": t.name,
        "year": t.year,
        "site": t.site,
        "groups": [
            {
                "url": g.url,
                "players_number": g.players_number,
                "played_rounds": g.played_rounds,
                "name": g.name,
                "is_only_female": g.is_only_female,
                "players": [
                    {
                        "place": p.place,
                        "title": p.title,
                        "name": p.name,
                        "url": p.url,
                        "elo": p.elo,
                        "elo_chg": p.elo_chg,
                        "points": p.points,
                    }
                    for p in g.players
                ],
            }
            for g in t.groups
        ],
    }