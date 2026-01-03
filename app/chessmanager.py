import logging
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Union

from app.models import Player, Tournament, Group
from app.soup import get_soup

page_url = "https://www.chessmanager.com/pl-pl/tournaments/now"


def relative_to_absolute_url(url: str) -> str:
    return url if "https://www.chessmanager.com" in url else f"https://www.chessmanager.com{url}"


def create_player(soup: BeautifulSoup, header_positions: Dict[str, int]) -> Player:
    place = int(soup.select_one('td:nth-of-type(1)').get_text(strip=True).rstrip('.'))

    title_span = soup.select_one('td:nth-of-type(4) span')
    title = title_span.get_text(strip=True) if title_span else None

    name_tag = soup.select_one('td > a')
    name = name_tag.get_text(strip=True)
    player_link = relative_to_absolute_url(name_tag['href'])

    elo_td = soup.select_one(f'td:nth-of-type({header_positions["elo"]})')
    elo = int(elo_td.contents[0].strip()) if elo_td.small is None and elo_td.contents[0].strip() else 0
    elo_chg = int(elo_td.span.get_text(strip=True)) if elo_td.span else 0

    points = float(soup.select_one(f'td:nth-of-type({header_positions["points"]})').get_text(strip=True))
    return Player(place, title, name, player_link, elo, elo_chg, points)


def get_players(link: str, searched_club: str) -> List[Player]:
    try:
        results_soup = get_soup(link + "/results")
    except Exception:
        logging.error(f"Cannot get results page: {link}")
        return []

    rows = results_soup.find_all("tr")

    players_from_club = []
    header_positions = {}
    for row in rows:
        if row.find("th"):
            headers = [th.get_text(strip=True) for th in row.find_all('th')]
            header_positions = retrieve_header_positions(headers, {"elo": "Ranking", "points": "Pkt"})

        if row.find("em", string=searched_club):
            try:
                players_from_club.append(create_player(row, header_positions))
            except Exception as e:
                logging.error(f"Error parsing row: {row}\nError: {e}")

    return players_from_club


def retrieve_header_positions(headers: List[str], header_keys: Dict[str, str]) -> Dict[str, int]:
    header_positions = {}
    for key, header in header_keys.items():
        header_positions[key] = headers.index(header) + 1 if header in headers else -1
    return header_positions


def get_tournament(link: str, searched_club: str) -> Union[Tournament, None]:
    try:
        tournament_soup = get_soup(link)
    except Exception:
        logging.error(f"Cannot get tournament page: {link}")
        return None

    year = 0
    site = ""
    played_rounds = 0

    name = tournament_soup.find("h1", class_="ui inverted header").text.strip()
    for statistic in tournament_soup.find_all("div", class_="statistic"):
        label = statistic.find("div", class_="label")
        if "Miasto" in label.text:
            site = statistic.find("div", class_="text value").text.strip().split("\n")[0]
        elif "Data" in label.text:
            dates_text = statistic.find("div", class_="text value").text
            year_match = re.search(r"\b(20\d{2})\b", dates_text)
            year = int(year_match.group(1)) if year_match else 0
        elif "Rundy" in label.text:
            rounds_text = statistic.find("div", class_="value").text.strip()
            rounds_match = re.match(r"(\d+)/(\d+)", rounds_text)
            current_round = int(rounds_match.group(1)) if rounds_match and int(rounds_match.group(1)) > 0 else 0
            number_of_rounds_in_tournament = int(rounds_match.group(2)) if rounds_match and int(rounds_match.group(2)) > 0 else 0
            played_rounds = current_round - 1 if current_round != number_of_rounds_in_tournament else number_of_rounds_in_tournament

    if played_rounds == 0:
        return None  # Tournament has no results yet

    return Tournament(name, year, site, [get_group(link, searched_club, name, played_rounds)])


def get_group(link: str, searched_club: str, tournament_name: str, played_rounds: int) -> Union[Group, None]:
    try:
        players_soup = get_soup(f"{link}/players")
    except Exception:
        logging.error(f"Cannot get players page: {link}")
        return None

    rows = players_soup.find_all("tr")
    how_many_players = len(rows) - 1

    how_many_women = 0
    for statistic in players_soup.find_all("div", class_="statistic"):
        label = statistic.find("div", class_="label")
        if label and "kobiety" in label.text:
            how_many_women = int(statistic.find("div", class_="value").text.strip().split("\n")[0])

    return Group(
        f"{link}/results",
        how_many_players,
        played_rounds,
        tournament_name,
        how_many_players == how_many_women,
        get_players(link, searched_club)
    )


def get_tournaments_with_players_of_club(searched_club: str) -> List[Tournament]:
    initial_soup = get_soup(page_url)
    last_page_number = get_max_pagination_number(initial_soup)

    results = []
    for i in range(last_page_number):
        soup = initial_soup if i == 0 else get_soup(f"{page_url}?offset={50 * i}")
        results.extend(one_page_processing(soup, searched_club))

    return results


def get_max_pagination_number(soup: BeautifulSoup) -> int:
    pagination_links = soup.select('.ui.centered.pagination.menu a')
    return int(pagination_links[-1].get_text(strip=True)) if pagination_links else 1


def one_page_processing(page_soup, searched_club):
    menu_div = page_soup.find("div", class_="ui centered fluid secondary pointing massive menu")
    tournaments = menu_div.find_next_siblings()

    results = []
    for tournament in tournaments:
        classes = tournament["class"]
        if "red" in classes or "yellow" in classes:
            href = relative_to_absolute_url(tournament["href"])
            result = get_tournament(href, searched_club)
            if result and result.groups[0] and len(result.groups[0].players) > 0:
                results.append(result)
    return results