import os
import requests
from datetime import date
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    url_for,
    redirect,
    request,
    flash
)
from validators.url import url

from page_analyzer.db import Database

load_dotenv()
db_url = os.getenv('DATABASE_URL')


# Validator
def validate(addr: str):
    if not url:
        return 'URL обязателен'
    if not url(addr):
        return 'Некорректный URL'
    if len(addr) > 255:
        return 'URL превышает 255 символов'


def normalize(addr: str):
    normalized_addr = urlparse(addr)
    return f'{normalized_addr.scheme}://{normalized_addr.netloc}'


# App block
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls/')
def get_urls():
    with Database(db_url) as db:
        sites = db.render(table='urls')
    return render_template('urls.html', sites=sites)


@app.post('/urls/')
def post_urls():
    data = request.form.get('url')
    error = validate(data)

    if error:
        flash(error, 'error')
        return render_template('index.html', error=error)
    else:
        data = normalize(data)

    with Database(db_url) as db:
        row = db.render('urls', item=data, col='name')

        if row:
            flash('Страница уже существует', 'info')
            url_id = row[0]['id']
            return redirect(url_for('url_info', id=url_id), code=302)

        else:
            flash('Страница успешно добавлена', 'success')
            row = db.insert(
                table='urls',
                cols=('name', 'created_at'),
                data=(data, date.today())
            )
            return redirect(url_for('url_info', id=row[0]), code=302)


def render_url(id, table, col):
    with Database(db_url) as db:
        site = db.render(table=table, item=id, col=col)
    return site


@app.get('/urls/<id>')
def url_info(id):
    site = render_url(id=id, table='urls', col='id')[0]
    checks = render_url(id=id, table='urls_checks', col='url_id')
    return render_template('urls_id.html', site=site, checks=checks)


@app.post('/urls/<id>/checks')
def check_url(id):
    status_code = requests.get(
        render_url(id=id, table='urls', col='id')[0]['name']
    ).status_code

    with Database(db_url) as db:
        db.insert(
            table='urls_checks',
            cols=(
                'url_id',
                'status_code',
                'created_at'
            ),
            data=(
                id,
                status_code,
                date.today(),
            )
        )
        return redirect(url_for('url_info', id=id), code=302)
