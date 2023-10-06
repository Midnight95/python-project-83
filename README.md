### Hexlet tests and linter status:
[![Actions Status](https://github.com/Midnight95/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Midnight95/python-project-83/actions)
[![Github Actions Status](https://github.com/Midnight95/python-project-83/workflows/Python%20CI/badge.svg)](https://github.com/Midnight95/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/a35829300219c07f6809/maintainability)](https://codeclimate.com/github/Midnight95/python-project-83/maintainability)


# Page analyzer 

Page Analyzer is a web app that analyzes web pages for SEO suitability, similar to PageSpeed Insights.

### You can check project [here](http://granovskydev.ru/) 
(sorry no ssl right now)

***

## Installation
* Clone the repo: 
```git clone https://github.com/Midnight95/python-project-83```. We'll install dependencies later.
* If you don't have poetry installed - [do it](https://python-poetry.org/docs/).


## Requirements
* python >=3.10
* Poetry >= 1.6
* PostgreSQL >= 15.4

***

## Required packages
* psycopg2-binary ^2.9.7 for postgres.
* Other packages inside pyproject.toml

*** 

## Running the app
To use app properly you'll need to provide it with `$DATABASE_URL` and `$SECRET_KEY` vars.

You can create `.env` file inside of this project and define variables there or do it your way.
```
DATABASE_URL = 'postgresql://{user}:{password}@{host}:{port}/{db}'
# postgresql://janedoe:mypassword@localhost:5432/mydb
SECRET_KEY = 'I AM THE SECRET'
```

Run ```make build``` to install all required packages and create necessary tables in database.

You can run an app from gunicorn with `make start`, from flask in debug mode with `make dev` or you can create a service file to run it constantly.
```
sudo tee <<EOF >/dev/null /etc/systemd/system/page_analyzer.service
[Unit]
Description=Gunicorn instance for page_analyzer
After=network.target

[Service]
User=your user
Group=www-data
WorkingDirectory=/home/path/to/project/
Environment="PATH=/home/path/to/poetry/venv/bin"
ExecStart=/path/to/gunicorn/binary/bin/gunicorn --workers 1 --bind unix:page_analyzer.sock -m 007 page_analyzer:app

[Install]
WantedBy=multi-user.target
EOF
```



**If you have any questions or something to add feel free to contact [me](https://github.com/Midnight95)**
