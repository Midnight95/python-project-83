import os
import requests

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


from page_analyzer.db import Database, render_url
from page_analyzer.validator import validate, normalize
from page_analyzer.config import (
    get_url_config,
    get_urls_checks,
    get_last_status_codes
)

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    with Database(app.config['DATABASE_URL']) as db:
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

    with Database(app.config['DATABASE_URL']) as db:
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
    site = render_url(
        id=id, table='urls', col='id',
        db_url=app.config['DATABASE_URL']
    )
    if not site:
        return abort(404)
    site = site[0]
    checks = render_url(
        id=id, table='urls_checks', col='url_id',
        db_url=app.config['DATABASE_URL']
    )
    return render_template('urls_id.html', site=site, checks=checks)


@app.post('/urls/<int:id>/checks')
def check_url(id: int):
    addr = render_url(
        id=id, table='urls', col='id',
        db_url=app.config['DATABASE_URL']
    )[0]['name']
    try:
        _request = requests.get(addr, timeout=5)
        _request.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_info', id=id))

    checks = get_urls_checks(_request, id)

    with Database(app.config['DATABASE_URL']) as db:
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
