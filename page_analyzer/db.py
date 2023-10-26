import psycopg2
from psycopg2.extras import NamedTupleCursor, RealDictCursor


def connect(db_url):
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except psycopg2.Error as e:
        print('Can\'t connect to the database!')
        raise e


def get_urls(connection):
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT id, name FROM urls ORDER BY id DESC')
            urls = cursor.fetchall()
    return urls


def get_last_checks(connection):
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                '''
                SELECT DISTINCT ON (url_id)
                url_id, created_at, status_code
                FROM urls_checks ORDER BY url_id DESC
                '''
            )
            last_checks = cursor.fetchall()
    return last_checks


def get_urls_with_last_checks(connection):
    urls = get_urls(connection)
    checks = get_last_checks(connection)
    if checks:
        for url in urls:
            check = [c for c in checks if c['url_id'] == url['id']]
            if check:
                url['status_code'] = check[0]['status_code']
                url['created_at'] = check[0]['created_at']
    return urls


def get_url_checks(connection, url_check_id: int):
    with connection:
        with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(
                'SELECT * FROM urls_checks WHERE url_id = (%s)',
                (url_check_id,))
            url_checks = cursor.fetchall()
    return url_checks


def get_url_by_id(connection, url_id: int):
    with connection:
        with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(
                'SELECT * FROM urls WHERE id = (%s)',
                (url_id,))
            result = cursor.fetchone()
    return result


def get_url_by_name(connection, url: str):
    with connection:
        with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute(
                'SELECT * FROM urls WHERE name = (%s)',
                (url,))
            result = cursor.fetchone()
    return result


def add_url(connection, url: str):
    with connection:
        with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute('INSERT INTO urls (name) VALUES (%s) RETURNING id',
                           (url,))
            result = cursor.fetchone()
    return result.id


def add_url_check(connection, check: dict, url_id: int):
    check['url_id'] = url_id
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
