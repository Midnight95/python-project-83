from datetime import date
import psycopg2


class Database:
    def __init__(self, addr):
        self.addr = addr

    def __enter__(self):
        self.conn = psycopg2.connect(self.addr)
        self.cursor = self.conn.cursor()
        return self

    def insert(self):
        self.cursor.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING *;",
            (self.addr, date.today())
        )

        return self.cursor.fetchone()

    def check(self, address):
        self.cursor.execute(
            "SELECT EXISTS(SELECT * FROM urls WHERE name = (%s))",
            (address,)
        )
        return self.cursor.fetchone()[0]

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
