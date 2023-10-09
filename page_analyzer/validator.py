from urllib.parse import urlparse
from validators.url import url


def validate(addr: str):
    """
    Checks if valid url is provided.

    :return: Error string or nothing
    """
    if not addr:
        return 'URL обязателен'
    if not url(addr):
        return 'Некорректный URL'
    if len(addr) > 255:
        return 'URL превышает 255 символов'


def normalize(addr: str):
    """
    Normalizes the provided URL by removing any unnecessary components.

    :return: Normalized URL.
    """
    normalized_addr = urlparse(addr)
    return f'{normalized_addr.scheme}://{normalized_addr.netloc}'
