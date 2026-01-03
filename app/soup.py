import requests
from bs4 import BeautifulSoup


def get_soup(url):
    response = requests.get(url)
    try:
        response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.RequestException):
        raise
    return BeautifulSoup(response.text, "html.parser")