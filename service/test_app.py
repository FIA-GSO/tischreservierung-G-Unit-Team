import os
import tempfile
import pytest
from server import app, init_db

# This fixture will create a temporary database for testing
@pytest.fixture
def client():
    app.config['TESTING'] = True
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

# Test if the app is initialized successfully
def test_init_db(client):
    response = client.get('/')
    assert b'Database connection successful' in response.data

# Test the endpoint for getting all reservations
def test_get_reservierungen(client):
    response = client.get('/reservierungen/all')
    assert response.status_code == 200
    assert b'reservierungen' in response.data

# Test the endpoint for getting all tables
def test_get_tische(client):
    response = client.get('/tische/all')
    assert response.status_code == 200
    assert b'tische' in response.data

# Test the endpoint for getting reserved tables
def test_get_reserved_tische(client):
    response = client.get('/reservierungen/reserved')
    assert response.status_code == 200
    assert b'tische' in response.data
