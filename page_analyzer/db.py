import psycopg2
from psycopg2.extras import DictCursor
from datetime import date
from flask import current_app


def connect():
    db_url = current_app.config.get('DATABASE_URL')
    if not db_url:
        raise ValueError('$DATABASE_URL is not found')
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except psycopg2.Error:
        print('Can\'t connect to the database!')


def execute(query: str, data=None, fetch: str = None) -> int or list:
    with connect() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, data)
            response = None
            match fetch:
                case 'all':
                    response = cursor.fetchall()
                case 'one':
                    response = cursor.fetchone()
            return response


def get_urls():
    query = "SELECT * FROM urls"
    response = execute(query, fetch='all')
    return response


def get_urls_checks(id=None) -> list[dict]:
    if id:
        query = "SELECT * FROM urls_checks WHERE url_id = (%s)"
        response = execute(query, (id,), fetch='all')
    else:
        query = "SELECT * FROM urls_checks"
        response = execute(query, fetch='all')
    return response


def get_url(urls_id: int):
    query = "SELECT * FROM urls WHERE id = (%s)"
    response = execute(query, (urls_id,), fetch='one')
    return response


def find_existing_url(url):
    query = "SELECT id FROM urls WHERE name = (%s)"
    response = execute(query, (url,), fetch='one')
    if response:
        response = response.get('id')
    return response


def insert_urls(url):
    query = "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id"
    data = url, date.today()
    response = execute(query, data, fetch='one')
    return response.get('id')


def insert_urls_checks(check: dict):
    query = """
    INSERT INTO urls_checks (url_id, status_code,
    h1, title, description, created_at)
    VALUES (%(url_id)s, %(status_code)s, %(h1)s,
    %(title)s, %(description)s, %(created_at)s)
    """
    execute(query, check)
