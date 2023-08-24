#variables
export FLASK_APP=page_analyzer:app
PORT ?= 8000


install:
	poetry install


build:
	poetry build


package-install:
	pip install --user dist/*.whl


test:
	poetry run pytest


lint:
	poetry run flake8 page_analyzer


dev:
	poetry run flask --app $(FLASK_APP) run



start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) $(FLASK_APP)



routes:
	poetry run python -m flask routes
