import psycopg2
import psycopg2.extras


class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def __enter__(self):
        self.conn = psycopg2.connect(self.db_url)
        self.cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        return self

    def insert(self, table: str, cols, data: tuple) -> dict:
        self.cursor.execute(
            f'INSERT INTO {table} ({", ".join(str(i) for i in cols)}) '
            f'VALUES ({", ".join("%s" for _ in cols)}) RETURNING id;',
            data
        )
        return self.cursor.fetchone()

    def render(self, table: str, item=None, col=None, show='*') -> tuple:
        """
        Renders all rows from a table if item is not provided,
        or shows all rows where item == col.
        table: str
        """
        if item is None or col is None:
            self.cursor.execute(f'SELECT {show} FROM {table}')
            return self.cursor.fetchall()
        else:
            self.cursor.execute(
                f'SELECT {show} FROM {table} WHERE {col} = (%s)',
                (item,)
            )
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
