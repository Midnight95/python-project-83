from flask import Flask, render_template
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

app = Flask(__name__)


@app.route('/')
def root():
    return render_template('index.html')
