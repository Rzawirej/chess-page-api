import json
import sqlite3

from app.helpers import get_polish_iso_time
from app.models import Tournament, tournament_to_dict, dict_to_tournament

DB_FILE = "data.db"


def get_connection():
    """Creates and returns a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn


def init_db():
    """Initializes database tables."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS html_data (
            id INTEGER PRIMARY KEY,
            html TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tournaments (
            name TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_tournaments(tournaments: list[Tournament]):
    """Saves a list of Tournament objects to the DB."""
    conn = get_connection()
    c = conn.cursor()

    now = get_polish_iso_time()
    for t in tournaments:
        # Convert to dict manually, then to JSON string
        data_dict = tournament_to_dict(t)
        data_json = json.dumps(data_dict)

        c.execute("""
                INSERT INTO tournaments (name, data, updated_at) 
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET 
                    data = excluded.data, 
                    updated_at = excluded.updated_at
            """, (t.name, data_json, now))

    conn.commit()
    conn.close()


def load_tournaments() -> list[Tournament]:
    """Retrieves all tournaments from the DB."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT data FROM tournaments ORDER BY updated_at DESC")
    rows = c.fetchall()
    conn.close()

    tournaments = []
    for row in rows:
        data_dict = json.loads(row["data"])
        tournaments.append(dict_to_tournament(data_dict))  # Convert back to object
    return tournaments


def save_html_content(html: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO html_data (id, html) VALUES (?, ?)", (1, html))
    conn.commit()
    conn.close()


def get_html_content() -> str:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT html FROM html_data WHERE id = 1")
    row = c.fetchone()
    conn.close()
    return row["html"] if row else None