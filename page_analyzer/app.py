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
from page_analyzer.validator import validate_url, normalize_url
from page_analyzer.parser import make_check

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def urls_get():
    with db.connect() as conn:
        urls = db.get_urls_with_last_checks(conn)
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def urls_post():
    url_string = request.form.get('url')
    url_validation_error = validate_url(url_string)

    if url_validation_error:
        flash(url_validation_error, 'error')
        return render_template('index.html', error=url_validation_error), 422

    normalized_url = normalize_url(url_string)

    with db.connect() as conn:
        url = db.get_url_by_name(normalized_url, conn)

        if url:
            url_id = url.get('id')
            flash('Страница уже существует', 'info')
            return redirect(url_for('url_info', id=url_id))
        else:
            url_id = db.insert_url(normalized_url, conn)
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('url_info', id=url_id))


@app.get('/urls/<int:id>')
def url_info(id: int):
    with db.connect() as conn:
        url = db.get_url_by_id(id, conn)
        checks = db.get_url_checks(id, conn)
    if not url:
        return abort(404)
    return render_template('urls_id.html', url=url, checks=checks)


@app.post('/urls/<int:id>/checks')
def check_url(id: int):
    with db.connect() as conn:
        url = db.get_url_by_id(id, conn)
        check = make_check(url.get('name'), id)
        if not check:
            flash('Произошла ошибка при проверке', 'error')
            return redirect(url_for('url_info', id=id))
        db.insert_url_check(check, conn)

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_info', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
