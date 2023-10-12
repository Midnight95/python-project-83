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
from page_analyzer import db
from page_analyzer.validator import validate, normalize
from page_analyzer.parser import make_check, find_last_status_codes

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    sites = db.get_urls()
    latest_checks = find_last_status_codes(db.get_urls_checks())
    return render_template('urls.html', sites=sites, checks=latest_checks)


@app.post('/urls')
def urls_post():
    data = request.form.get('url')
    error = validate(data)

    if error:
        flash(error, 'error')
        return render_template('index.html', error=error), 422

    data = normalize(data)
    url_id = db.find_existing_url(data)

    if url_id:
        flash('Страница уже существует', 'info')
        return redirect(url_for('url_info', id=url_id))
    else:
        url_id = db.insert_urls(data)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('url_info', id=url_id))


@app.get('/urls/<int:id>')
def url_info(id: int):
    site = db.get_url(id)
    checks = db.get_urls_checks(id)
    if not site:
        return abort(404)
    return render_template('urls_id.html', site=site, checks=checks)


@app.post('/urls/<int:id>/checks')
def check_url(id: int):
    urls = db.get_url(id)
    checks = make_check(urls.get('name'), id)
    if not checks:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_info', id=id))

    db.insert_urls_checks(checks)

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_info', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
