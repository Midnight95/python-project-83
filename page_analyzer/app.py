from flask import (
    Flask,
    render_template,
    url_for,
    request
    )
from dotenv import load_dotenv
from urllib.parse import urlparse
from validators.url import url
load_dotenv()


# Validator
def validate(addr: str) -> str:
    if not url:
        return 'URL обязателен'
    if not url(addr):
        return 'Некорректный URL'
    if len(addr) > 255:
        return 'URL превышает 255 символов'


def normalize(addr: str) -> str:
    normalized_addr = urlparse(addr)
    return f'{normalized_addr.scheme}://{normalized_addr.netloc}'


# App block
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    if request.method == 'GET':
        pass

    if request.method == 'POST':
        data = request.form.get('url')
        errors = validate(data)

        return data


@app.get('/urls/<id>')
def url_info(id):
    pass
