import logging
import os
from typing import List, Optional
from dotenv import load_dotenv
from app.chessmanager import get_tournaments_with_players_of_club, get_tournament
from app.decorators import log_execution_time
from app.generate_html import generate_table
from app.models import Tournament

load_dotenv()
searched_club = os.getenv('SEARCHED_CLUB')
logging.basicConfig(level=logging.INFO)
if not searched_club:
    raise ValueError("SEARCHED_CLUB environment variable is not set! Add SEARCHED_CLUB in .env file")

@log_execution_time
def search_today() -> List[Tournament]:
    tournaments = get_tournaments_with_players_of_club(searched_club)
    return tournaments

def search_specific_tournaments(tournaments_urls: List[str]) -> list[Optional[Tournament]]:
    return [get_tournament(url, searched_club) for url in tournaments_urls]

def generate_html(tournaments: List[Tournament]) -> str:
    tables = "\n".join(generate_table(t) for t in tournaments)
    return f"<html><body>\n{tables}\n</body></html>"
