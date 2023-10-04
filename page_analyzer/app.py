import os
import requests
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    url_for,
    redirect,
    request,
    flash,
    abort
)
from validators.url import url

from page_analyzer.db import Database
from page_analyzer.config import (
    get_url_config,
    get_urls_checks,
    get_last_status_codes
)

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
db_url = os.getenv('DATABASE_URL')


def validate(addr: str):
    """
    Checks if valid url is provided.

    :return: Error string or nothing
    """
    if not url:
        return 'URL обязателен'
    if not url(addr):
        return 'Некорректный URL'
    if len(addr) > 255:
        return 'URL превышает 255 символов'


def normalize(addr: str):
    """
    Normalizes the provided URL by removing any unnecessary components.

    :return: Normalized URL.
    """
    normalized_addr = urlparse(addr)
    return f'{normalized_addr.scheme}://{normalized_addr.netloc}'


def render_url(id, table, col):
    """
    Retrieves all rows from the specified table where
    the provided item matches the specified column.

    :param id: The item to filter the rows by.
    :param table: The name of the table (urls or urls_checks).
    :param col: The name of the column to compare the item against.
    :return: A list of dictionaries representing the matching rows.
    """
    with Database(db_url) as db:
        site = db.render(table=table, item=id, col=col)
    return site


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    with Database(db_url) as db:
        sites = db.render(table='urls')
        latest_checks = get_last_status_codes(db.render(table='urls_checks'))
    return render_template('urls.html', sites=sites, checks=latest_checks)


@app.post('/urls')
def post_urls():
    data = request.form.get('url')
    error = validate(data)

    if error:
        flash(error, 'error')
        return render_template('index.html', error=error), 422

    data = normalize(data)

    with Database(db_url) as db:
        row = db.render('urls', item=data, col='name')

        if row:
            flash('Страница уже существует', 'info')
            return redirect(url_for('url_info', id=row[0]['id']))

        else:
            flash('Страница успешно добавлена', 'success')
            urls = get_url_config(data)
            url_id = db.insert(
                table='urls',
                cols=urls.keys(),
                data=urls.values()
            )
            return redirect(url_for('url_info', id=url_id))


@app.get('/urls/<int:id>')
def url_info(id: int):
    site = render_url(id=id, table='urls', col='id')
    if not site:
        return abort(404)
    site = site[0]
    checks = render_url(id=id, table='urls_checks', col='url_id')
    return render_template('urls_id.html', site=site, checks=checks)


@app.post('/urls/<int:id>/checks')
def check_url(id: int):
    addr = render_url(id=id, table='urls', col='id')[0]['name']
    try:
        _request = requests.get(addr, timeout=5)
        _request.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_info', id=id))

    checks = get_urls_checks(_request, id)

    with Database(db_url) as db:
        db.insert(
            table='urls_checks',
            cols=checks.keys(),
            data=checks.values()
        )

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_info', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
