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


from page_analyzer.db import Database
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
        sites = db.get_urls()
        latest_checks = get_last_status_codes(db.get_urls_checks())
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
        url_id = db.get_urls_id_by_name(data)

        if url_id:
            flash('Страница уже существует', 'info')
            return redirect(url_for('url_info', id=url_id))

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
    with Database(app.config['DATABASE_URL']) as db:
        site = db.get_urls_by_id(id)
        checks = db.get_urls_checks_by_id(id)
    if not site:
        return abort(404)
    return render_template('urls_id.html', site=site, checks=checks)


@app.post('/urls/<int:id>/checks')
def check_url(id: int):
    with Database(app.config['DATABASE_URL']) as db:
        urls = db.get_urls_by_id(id)
        checks = get_urls_checks(urls['name'], id)
        if not checks:
            flash('Произошла ошибка при проверке', 'error')
            return redirect(url_for('url_info', id=id))

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
