from flask import Flask, render_template
from dotenv import load_dotenv
from urllib.parse import urlparse
from validators.url import url
from datetime import date
import psycopg2
load_dotenv()


class Database:
    def __init__(self, addr):
        self.addr = addr

    def __enter__(self):
        self.conn = psycopg2.connect(self.addr)
        self.cursor = self.conn.cursor()
        return self

    def insert(self):
        self.cursor.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s);",
            (self.addr, date.today())
        )

    def check(self, address):
        self.cursor.execute(
            "SELECT * FROM urls WHERE name = (%s)",
            (address,)
        )

        return self.cursor.fetchone()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn is not None:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()

# Validator block


def validate(addr):
    errors = []
    if len(addr) > 255:
        errors.append('URL превышает 255 символов')
    if not url(addr):
        errors.append('Некорректный URL')
    if not url:
        errors.append('URL обязателен')

    return errors
    #


def normalize(addr):
    normalized_addr = urlparse(addr)
    return f'{normalized_addr.scheme}://{normalized_addr.netloc}'


# App block


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls():
    return render_template('urls.html')
