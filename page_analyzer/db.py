import psycopg2


def connect(url):
    return psycopg2.connect(url)


def close(conn):
    return conn.close()


def insert(conn, url):
    cur = conn.cursor()
    cur.execute('INSERT INTO urls (name) VALUES (%s)', url)
    conn.commit()


