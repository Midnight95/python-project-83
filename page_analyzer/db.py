from datetime import date
import psycopg2


class DatabaseCM:
    def __init__(self, addr):
        self.addr = addr

    def __enter__(self):
        self.conn = psycopg2.connect(self.addr)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn is not None:
            self.conn.close()

