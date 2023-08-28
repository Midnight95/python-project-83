import pytest
from app import app as application


@pytest.fixture()
def app():
    app = application
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
