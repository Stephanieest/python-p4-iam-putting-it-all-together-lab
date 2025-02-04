import pytest
from app import app, db
from models import User, Recipe

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_signup(client):
    response = client.post('/signup', json={
        'username': 'testuser',
        'password': 'testpassword',
        'image_url': 'http://example.com/image.jpg',
        'bio': 'This is a test user.'
    })
    assert response.status_code == 201
    assert b'testuser' in response.data

def test_login(client):
    client.post('/signup', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    assert b'testuser' in response.data

def test_check_session(client):
    client.post('/signup', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.get('/check_session')
    assert response.status_code == 200
    assert b'testuser' in response.data

def test_create_recipe(client):
    client.post('/signup', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.post('/recipes', json={
        'title': 'Test Recipe',
        'instructions': 'These are the instructions for the test recipe.',
        'minutes_to_complete': 30
    })
    assert response.status_code == 201
    assert b'Test Recipe' in response.data

def test_get_recipes(client):
    client.post('/signup', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/recipes', json={
        'title': 'Test Recipe',
        'instructions': 'These are the instructions for the test recipe.',
        'minutes_to_complete': 30
    })
    response = client.get('/recipes')
    assert response.status_code == 200
    assert b'Test Recipe' in response.data
