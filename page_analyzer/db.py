from datetime import date
import psycopg2


class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def __enter__(self):
        self.conn = psycopg2.connect(self.db_url)
        self.cursor = self.conn.cursor()
        return self

    def insert(self, address: str):
        self.cursor.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;",
            (address, date.today())
        )
        entry_id = self.cursor.fetchone()
        return entry_id[0] if entry_id else None

    def check(self, address: str):
        self.cursor.execute(
            "SELECT id FROM urls WHERE name = (%s);",
            (address,)
        )
        entry_id = self.cursor.fetchone()
        return entry_id[0] if entry_id else None

    def find(self, id: int):
        self.cursor.execute(
            "SELECT * FROM urls WHERE id = (%s);",
            (id,)
        )
        return self.cursor.fetchone()

    def render(self):
        self.cursor.execute("SELECT * FROM urls")
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn is not None:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
