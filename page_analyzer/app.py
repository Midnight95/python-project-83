import os

import psycopg2
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
    conn = db.connect(app.config['DATABASE_URL'])
    try:
        urls = db.get_urls_with_last_checks(conn)
    except psycopg2.Error as e:
        raise e
    finally:
        conn.close()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def urls_post():
    url_string = request.form.get('url')
    url_validation_error = validate_url(url_string)

    if url_validation_error:
        flash(url_validation_error, 'error')
        return render_template('index.html'), 422

    normalized_url = normalize_url(url_string)

    conn = db.connect(app.config['DATABASE_URL'])
    try:
        url = db.get_url_by_name(conn, normalized_url)
        if url:
            url_id = url.id
            flash('Страница уже существует', 'info')
        else:
            url_id = db.add_url(conn, normalized_url)
            flash('Страница успешно добавлена', 'success')
    except psycopg2.Error as e:
        raise e
    finally:
        conn.close()

    return redirect(url_for('url_info', id=url_id))


@app.get('/urls/<int:id>')
def url_info(id: int):
    conn = db.connect(app.config['DATABASE_URL'])
    try:
        url = db.get_url_by_id(conn, id)
        checks = db.get_url_checks(conn, id)
    except psycopg2.Error as e:
        raise e
    finally:
        conn.close()

    if not url:
        return abort(404)
    return render_template('urls_id.html', url=url, checks=checks)


@app.post('/urls/<int:id>/checks')
def check_url(id: int):
    message = {'message': 'Произошла ошибка при проверке', 'category': 'error'}

    conn = db.connect(app.config['DATABASE_URL'])
    try:
        url = db.get_url_by_id(conn, id)
        check = make_check(url.name)
        if check:
            db.add_url_check(conn, check, id)
            if check['status_code'] == 200:
                message['message'] = 'Страница успешно проверена'
                message['category'] = 'success'
        flash(**message)
    except psycopg2.Error as e:
        raise e
    finally:
        conn.close()

    return redirect(url_for('url_info', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
