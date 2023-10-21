import psycopg2
from psycopg2.extras import DictCursor
from flask import current_app


def connect():
    db_url = current_app.config.get('DATABASE_URL')
    if not db_url:
        raise ValueError('$DATABASE_URL is not found')
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except psycopg2.Error as e:
        print('Can\'t connect to the database!')
        raise e


def execute(connection, query: str, data=None, fetch: str = None):
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query, data)
        result = None
        match fetch:
            case 'all':
                result = cursor.fetchall()
            case 'one':
                result = cursor.fetchone()
        return result


def get_urls(connection):
    query = "SELECT * FROM urls"
    urls = execute(connection, query, fetch='all')
    return urls


def get_urls_with_last_checks(connection):
    query = """
            SELECT DISTINCT
            ON (urls.id)
            urls.id AS id,
            urls.name AS name,
            urls_checks.created_at AS created_at,
            urls_checks.status_code AS status_code
            FROM urls LEFT JOIN urls_checks ON urls.id = urls_checks.url_id
            ORDER BY urls.id, urls_checks.id DESC
            """
    checks = execute(connection, query, fetch='all')
    return checks


def get_url_checks(url_check_id, connection):
    query = "SELECT * FROM urls_checks WHERE url_id = (%s)"
    checks = execute(connection, query, (url_check_id,), fetch='all')
    return checks


def get_url_by_id(url_id: int, connection):
    query = "SELECT * FROM urls WHERE id = (%s)"
    result = execute(connection, query, (url_id,), fetch='one')
    return result


def get_url_by_name(url: str, connection):
    query = "SELECT * FROM urls WHERE name = (%s)"
    result = execute(connection, query, (url,), fetch='one')
    return result


def insert_url(url: str, connection):
    query = "INSERT INTO urls (name) VALUES (%s) RETURNING id"
    data = (url,)
    result = execute(connection, query, data, fetch='one')
    return result.get('id')


def insert_url_check(check: dict, connection):
    query = """
    INSERT INTO urls_checks (url_id, status_code,
    h1, title, description)
    VALUES (%(url_id)s, %(status_code)s, %(h1)s,
    %(title)s, %(description)s)
    """
    execute(connection, query, check)
