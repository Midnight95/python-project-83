from flask import (
    Flask,
    render_template,
    url_for,
    redirect,
    request,
    flash
)

from dotenv import load_dotenv
from urllib.parse import urlparse
from validators.url import url

from page_analyzer.db import Database

import os

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
    sites = []

    with Database(db_url) as db:
        sites_tuple = db.render('urls')

    if sites_tuple:
        for db_entry in sites_tuple:
            id, addr, _ = db_entry
            sites.append({'id': id, 'addr': addr})
    return render_template('urls.html', sites=sites)


@app.post('/urls/')
def post_urls():
    data = request.form.get('url')
    error = validate(data)

    if error:
        flash(error, 'error')
        return render_template('index.html', error=error)

    with Database(db_url) as db:
        data = normalize(data)
        url_id = db.check(data)

        if url_id:
            flash('Страница уже существует', 'info')
            return redirect(url_for('url_info', id=url_id), code=302)

        else:
            flash('Страница успешно добавлена', 'success')
            url_id = db.insert_urls(data)
            return redirect(url_for('url_info', id=url_id), code=302)


def find_url(id):
    with Database(db_url) as db:
        site_tuple = db.render('urls', id, 'id')
        id, addr, date = site_tuple
        site = {
            'id': id,
            'addr': addr,
            'date': date
        }
    return site


@app.get('/urls/<id>')
def url_info(id):
    site = find_url(id)
    return render_template('urld_id.html', site=site)


@app.post('/urls/<id>/checks')
def check_url(id):
    site = find_url(id)

    checks = []

    with Database(db_url) as db:
        checks_tuple = db.insert_checks(id)
        if checks_tuple:
            for db_entry in checks_tuple:
                id, url_id, _, _, _, _, created_at = db_entry  # THIS IS A DRAFT I'M SORRY
                checks.append({'id': id, 'url_id': url_id, 'created_at': created_at})

        return render_template('urld_id.html', site=site, checks=checks)
