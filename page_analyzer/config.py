from datetime import date
from bs4 import BeautifulSoup


def get_url_config(name) -> dict:
    return {
        'name': name,
        'created_at': date.today()
    }


def get_urls_checks(page, id) -> dict:
    soup = BeautifulSoup(page.text, 'html.parser')

    h1 = soup.h1.string if soup.h1 else None
    title = soup.title.string if soup.title else None
    description = soup.find('meta', attrs={'name': 'description'})
    if description:
        description = description['content']

    return {
        'url_id': id,
        'status_code': page.status_code,
        'h1': h1,
        'title': title,
        'description': description,
        'created_at': date.today()
    }


def get_last_status_codes(checks):
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
