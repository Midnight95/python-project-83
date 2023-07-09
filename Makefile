#variables
export FLASK_APP=page_analyzer:app
PORT ?= 8000


install:
	python3 -m poetry install


build:
	python3 -m poetry build


package-install:
	python3 -m pip install --user dist/*.whl


test:
	python3 -m poetry run pytest


lint:
	python3 -m poetry run flake8 page_analyzer


dev:
	python3 -m poetry run flask --app $(FLASK_APP) run



start:
	python3 -m poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) $(FLASK_APP)



routes:
	python3 -m poetry run python -m flask routes
