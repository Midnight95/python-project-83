import psycopg2
from psycopg2.extras import NamedTupleCursor, RealDictCursor


class DatabaseException(Exception):
    def __init__(self, message):
        self.message = message


def connect(config):
    try:
        conn = psycopg2.connect(config['DATABASE_URL'])
        return conn
    except psycopg2.Error as e:
        message = f'Can\'t connect to the database! Error: {e}'
        raise DatabaseException(message)


def get_urls_with_last_checks(connection):
    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute('SELECT id, name FROM urls ORDER BY id DESC')
                urls = cursor.fetchall()
                cursor.execute(
                    '''
                    SELECT DISTINCT ON (url_id)
                    url_id, created_at, status_code
                    FROM urls_checks ORDER BY url_id DESC
                    '''
                )
                checks = cursor.fetchall()
    except psycopg2.Error as e:
        message = f'\nError has occurred!\nError message: {e}'
        raise DatabaseException(message)
    if checks:
        for url in urls:
            check = [c for c in checks if c['url_id'] == url['id']]
            if check:
                url['status_code'] = check[0]['status_code']
                url['created_at'] = check[0]['created_at']
    return urls


def get_url_checks(connection, url_check_id: int):
    try:
        with connection:
            with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(
                    'SELECT * FROM urls_checks WHERE url_id = (%s)',
                    (url_check_id,))
                url_checks = cursor.fetchall()
    except psycopg2.Error as e:
        message = f'\nError has occurred!\nError message: {e}'
        raise DatabaseException(message)
    return url_checks


def get_url_by_id(connection, url_id: int):
    try:
        with connection:
            with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(
                    'SELECT * FROM urls WHERE id = (%s)',
                    (url_id,))
                result = cursor.fetchone()
    except psycopg2.Error as e:
        message = f'\nError has occurred!\nError message: {e}'
        raise DatabaseException(message)
    return result


def get_url_by_name(connection, url: str):
    try:
        with connection:
            with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(
                    'SELECT * FROM urls WHERE name = (%s)',
                    (url,))
                result = cursor.fetchone()
    except psycopg2.Error as e:
        message = f'\nError has occurred!\nError message: {e}'
        raise DatabaseException(message)
    return result


def add_url(connection, url: str):
    try:
        with connection:
            with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(
                    'INSERT INTO urls (name) VALUES (%s) RETURNING id',
                    (url,))
                result = cursor.fetchone()
    except psycopg2.Error as e:
        message = f'\nError has occurred!\nError message: {e}'
        raise DatabaseException(message)
    return result.id


def add_url_check(connection, check: dict, url_id: int):
    check['url_id'] = url_id
    try:
        with connection:
            with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(
                    '''
                    INSERT INTO urls_checks (url_id, status_code,
                    h1, title, description)
                    VALUES (%(url_id)s, %(status_code)s, %(h1)s,
                    %(title)s, %(description)s)
                    ''',
                    check
                )
    except psycopg2.Error as e:
        message = f'\nError has occurred!\nError message: {e}'
        raise DatabaseException(message)
