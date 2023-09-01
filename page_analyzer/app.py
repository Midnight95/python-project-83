from flask import Flask, render_template
from dotenv import load_dotenv
import psycopg2
load_dotenv()

# Database block


class Database:
    def __int__(self, url):
        self.url = url
        self.conn = psycopg2.connect(url)
        self.cursor = self.conn.cursor()

    def insert(self):
        self.cursor.execute('INSERT INTO urls (name) VALUES (%s)', self.url)
        self.conn.commit()

    def close(self):
        self.conn.close()

# Validator block

# App block


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls():
    return render_template('urls.html')
