import requests

from datetime import date
from bs4 import BeautifulSoup


def get_urls(url) -> dict:
    """
    Creates a dictionary with the provided url and current date
    for the purpose of providing it to 'urls' table.
    """
    return {
        'name': url,
        'created_at': date.today()
    }


def get_urls_checks(url, id):
    """
    Parses the page object from requests using BeautifulSoup and
    creates dict with information from it
    for the purpose of providing it to 'urls_checks' table
    """
    try:
        request = requests.get(url, timeout=5)
        request.raise_for_status()
    except requests.RequestException:
        return

    soup = BeautifulSoup(request.text, 'html.parser')

    h1 = soup.h1.string if soup.h1 else None
    title = soup.title.string if soup.title else None
    description = soup.find('meta', attrs={'name': 'description'})
    if description:
        description = description['content']

    return {
        'url_id': id,
        'status_code': request.status_code,
        'h1': h1,
        'title': title,
        'description': description,
        'created_at': date.today()
    }


def get_last_status_codes(checks) -> dict:
    """
    Returns entries dict with last status codes for each URL
    in the provided psycopg2 'dict' object.
    """
    result = {}

    for item in checks:
        id = item['id']
        url_id = item['url_id']

        if url_id not in result or result.get(url_id, {}).get('id', -1) < id:
            result[url_id] = {
                'id': id,
                'status_code': item['status_code'],
                'created_at': item['created_at']
            }

    return result
