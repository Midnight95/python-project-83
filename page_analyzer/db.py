import psycopg2
import psycopg2.extras


class Database:
    def __init__(self, db_url):
        self.db_url = db_url

    def __enter__(self):

        self.conn = psycopg2.connect(self.db_url)
        self.cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )
        return self

    def insert(self, table: str, cols, data):
        self.cursor.execute(
            f'INSERT INTO {table} ({", ".join(str(i) for i in cols)}) '
            f'VALUES ({", ".join("%s" for _ in cols)}) RETURNING id;',
            data if isinstance(data, tuple) else tuple(data)
        )
        return self.cursor.fetchone().get('id')

    def get_urls_checks(self):
        self.cursor.execute("SELECT * FROM urls_checks")
        data = self.cursor.fetchall()
        return data if any(isinstance(i, list) for i in data) else [data]

    def get_urls_checks_by_id(self, url_id):
        self.cursor.execute(
            "SELECT * FROM urls_checks WHERE url_id = (%s)",
            (url_id,)
        )
        data = self.cursor.fetchall()
        return data if any(isinstance(i, list) for i in data) else [data]

    def get_urls(self):
        self.cursor.execute(
            "SELECT * FROM urls"
        )
        return self.cursor.fetchall()

    def get_urls_id_by_name(self, name):
        self.cursor.execute(
            "SELECT id FROM urls WHERE name = (%s)",
            (name,)
        )
        return self.cursor.fetchone()

    def get_urls_by_id(self, id):
        self.cursor.execute(
            "SELECT * FROM urls WHERE id = (%s)",
            (id,)
        )
        return self.cursor.fetchone()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
