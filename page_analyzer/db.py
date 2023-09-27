import psycopg2
import psycopg2.extras


class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def __enter__(self):
        self.conn = psycopg2.connect(self.db_url)
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self

    def insert(self, table: str, cols: list, *args):
        self.cursor.execute(
            f'INSERT INTO {table} ({", ".join(str(i) for i in cols)}) '
            f'VALUES ({", ".join("%s" for i in cols)}) RETURNING *;',
            args
        )
        return self.cursor.fetchone()

    def render(self, table, to_find=None, col=None, show='*'):
        if to_find and col:
            self.cursor.execute(
                f'SELECT {show} FROM {table} WHERE {col} = (%s)',
                (to_find,)
                )
            return self.cursor.fetchone()
        else:
            self.cursor.execute(f'SELECT {show} FROM {table}')
            return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
