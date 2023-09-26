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


@app.route('/urls/', methods=['GET', 'POST'])
def urls():
    if request.method == 'GET':
        sites = []

        with Database(db_url) as db:
            sites_tuple = db.render()

        if sites_tuple:
            for db_entry in sites_tuple:
                id, addr, _ = db_entry
                sites.append({'id': id, 'addr': addr})
        return render_template('urls.html', sites=sites)

    elif request.method == 'POST':
        data = request.form.get('url')
        error = validate(data)
        if error:
            flash(error)
            return render_template('index.html', error=error)

        with Database(db_url) as db:
            data = normalize(data)
            url_id = db.check(data)

            if url_id:
                flash('Страница уже существует')
                return redirect(url_for('url_info', id=url_id), code=302)

            else:
                url_id = db.insert(data)
                return redirect(url_for('url_info', id=url_id), code=302)


@app.get('/urls/<id>')
def url_info(id):
    with Database(db_url) as db:
        site_tuple = db.find(id)
        id, addr, date = site_tuple
        site = {
            'id': id,
            'addr': addr,
            'date': date
        }

    return render_template('urld_id.html', site=site)
