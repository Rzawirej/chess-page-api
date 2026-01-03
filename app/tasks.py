from datetime import datetime

from app.helpers import search_today, generate_html
from app.database import save_tournaments, load_tournaments, save_html_content


def update_data_task():
    """
    Orchestrates the data update process:
    1. Scrapes today's tournaments
    2. Saves them to DB
    3. Reloads all data
    4. Regenerates and saves HTML
    """
    print("Running background task: update_data_task", datetime.utcnow().isoformat())

    # 1. Fetch new data
    today_tournaments = search_today()

    # 2. Store to DB
    if today_tournaments:
        save_tournaments(today_tournaments)

    # 3. Load all for HTML generation
    stored_tournaments = load_tournaments()

    # 4. Generate and save HTML
    html = generate_html(stored_tournaments)
    save_html_content(html)
    print("Background task complete: update_data_task", datetime.utcnow().isoformat())