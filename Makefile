FLASK_APP=page_analyzer:app
PORT ?= 8000

install:
	python3 -m poetry install

build:
	python3 -m poetry build

publish:
	python3 -m poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

#test:
#	python3 -m poetry run pytest

lint:
	python3 -m poetry run flake8 page_analyzer

dev:
	poetry run flask --app page_analyzer:app run

start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

routes:
	poetry run python -m flask routes