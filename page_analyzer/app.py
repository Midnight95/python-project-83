import os

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


from page_analyzer.db import Database, render_data
from page_analyzer.validator import validate, normalize
from page_analyzer.utils import (
    get_urls,
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
def urls_get():
    with Database(app.config['DATABASE_URL']) as db:
        sites = db.render(table='urls')
        latest_checks = get_last_status_codes(db.render(table='urls_checks'))
    return render_template('urls.html', sites=sites, checks=latest_checks)


@app.post('/urls')
def urls_post():
    data = request.form.get('url')
    error = validate(data)

    if error:
        flash(error, 'error')
        return render_template('index.html', error=error), 422

    data = normalize(data)

    with Database(app.config['DATABASE_URL']) as db:
        urls_data = db.render('urls', item=data, col='name')

        if urls_data:
            flash('Страница уже существует', 'info')
            return redirect(url_for('url_info', id=urls_data['id']))

        else:
            urls = get_urls(data)
            url_id = db.insert(
                table='urls',
                cols=urls.keys(),
                data=urls.values()
            )
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('url_info', id=url_id))


@app.get('/urls/<int:id>')
def url_info(id: int):
    site = render_data(
        id=id, table='urls', col='id',
        db_url=app.config['DATABASE_URL']
    )
    if not site:
        return abort(404)
    checks = render_data(
        id=id, table='urls_checks', col='url_id',
        db_url=app.config['DATABASE_URL']
    )
    # временный костыль
    if checks:
        if not isinstance(checks[0], list):
            checks = [checks]
    return render_template('urls_id.html', site=site, checks=checks)


@app.post('/urls/<int:id>/checks')
def check_url(id: int):
    data = render_data(
        id=id, table='urls', col='id',
        db_url=app.config['DATABASE_URL']
    )

    checks = get_urls_checks(data.get('name'), id)
    if not checks:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_info', id=id))

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
