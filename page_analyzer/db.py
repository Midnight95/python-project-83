import psycopg2
from psycopg2.extras import NamedTupleCursor, RealDictCursor


def connect(db_url):
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except psycopg2.Error as e:
        print('Can\'t connect to the database!')
        raise e


def execute(connection, factory, query: str, data=None, fetch: str = None):
    with connection.cursor(cursor_factory=factory) as cursor:
        cursor.execute(query, data)
        result = None
        match fetch:
            case 'all':
                result = cursor.fetchall()
            case 'one':
                result = cursor.fetchone()
        return result


def get_urls(connection):
    query = 'SELECT id, name FROM urls ORDER BY id DESC'
    urls = execute(connection, RealDictCursor, query, fetch='all')
    return urls


def get_last_checks(connection):
    query = '''
    SELECT DISTINCT 
    ON (url_id)
    url_id, 
    created_at,
    status_code
    FROM urls_checks
    ORDER BY url_id DESC
    '''
    last_checks = execute(connection, RealDictCursor, query, fetch='all')
    return last_checks


def get_url_checks(connection, url_check_id: int):
    query = "SELECT * FROM urls_checks WHERE url_id = (%s)"
    url_checks = execute(connection, NamedTupleCursor, query, (url_check_id,), fetch='all')
    return url_checks


def get_url_by_id(connection, url_id: int):
    query = "SELECT * FROM urls WHERE id = (%s)"
    result = execute(connection, NamedTupleCursor, query, (url_id,), fetch='one')
    return result


def get_url_by_name(connection, url: str):
    query = "SELECT * FROM urls WHERE name = (%s)"
    result = execute(connection, NamedTupleCursor, query, (url,), fetch='one')
    return result


def add_url(connection, url: str):
    query = "INSERT INTO urls (name) VALUES (%s) RETURNING id"
    result = execute(connection, NamedTupleCursor, query, (url,), fetch='one')
    return result.id


def add_url_check(connection, check: dict, url_id: int):
    query = """
    INSERT INTO urls_checks (url_id, status_code,
    h1, title, description)
    VALUES (%(url_id)s, %(status_code)s, %(h1)s,
    %(title)s, %(description)s)
    """
    check['url_id'] = url_id
    execute(connection, NamedTupleCursor, query, check)
