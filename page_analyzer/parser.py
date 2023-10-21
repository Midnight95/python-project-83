import requests
from bs4 import BeautifulSoup


def make_check(url, id):
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
    }
