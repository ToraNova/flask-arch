import pytest
import os
import tempfile
from auth_database import create_app

@pytest.fixture()
def app():
    db_fd, db_file = tempfile.mkstemp()
    db_uri = 'sqlite:///%s' % db_file
    app = create_app({'TESTING': True, 'DBURI': db_uri})

    # other setup can go here

    yield app

    # clean up / reset resources here
    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_file)

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_login(client):

    resp = client.get('/database_test/profile')
    assert b'jason' not in resp.data
    assert resp.status_code == 401

    resp = client.post('/database_test/login', data={'username': 'jason'})
    assert resp.status_code == 400

    resp = client.post('/database_test/login', data={'username': 'jason', 'password': 'wrong'}, follow_redirects=True)
    assert resp.status_code == 401
    assert b'red">invalid credentials' in resp.data

    resp = client.post('/database_test/login', data={'username': 'jason', 'password': 'hunter2'}, follow_redirects=False)
    assert resp.status_code == 302

    resp = client.get('/database_test/profile')
    assert resp.status_code == 200
    assert b'welcome jason' in resp.data

    resp = client.get('/database_test/logout')
    assert resp.status_code == 302

    resp = client.get('/database_test/profile')
    assert resp.status_code == 401

def test_create(client):
    resp = client.get('/database_test/register')
    assert resp.status_code == 200

    resp = client.post('/database_test/register', data={'username':'newuser'})
    assert resp.status_code == 400

    resp = client.post('/database_test/register', data={'username':'newuser', 'password': 'newpass', 'password_confirm': 'newpass'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'green">register successful' in resp.data

    resp = client.post('/database_test/login', data={'username': 'newuser', 'password': 'newpass'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'welcome newuser' in resp.data

def test_update(client):
    resp = client.get('/database_test/update')
    assert resp.status_code == 401

    client.post('/database_test/login', data={'username': 'jason', 'password': 'hunter2'})
    resp = client.get('/database_test/update')
    assert resp.status_code == 200

    resp = client.post('/database_test/update')
    assert resp.status_code == 302

    resp = client.post('/database_test/update', data={'password_new':'a'})
    assert resp.status_code == 400

    resp = client.post('/database_test/update', data={'password_new':'hunter3', 'password_confirm':'hunter3', 'password_old':'hunter1'})
    assert resp.status_code == 401
    assert b'red">invalid old password' in resp.data

    resp = client.post('/database_test/update', data={'password_new':'ABC', 'password_confirm':'abc', 'password_old':'hunter2'})
    assert resp.status_code == 400
    assert b'red">new password do not match' in resp.data

    resp = client.post('/database_test/update', data={'password_new':'abc', 'password_confirm':'abc', 'password_old':'hunter2'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'green">update successful' in resp.data

    resp = client.get('/database_test/logout', follow_redirects=True)
    assert resp.status_code == 200
    assert b'green">logout successful' in resp.data

    resp =client.post('/database_test/login', data={'username': 'jason', 'password': 'hunter2'})
    assert resp.status_code == 401
    assert b'red">invalid credentials' in resp.data

    resp = client.get('/database_test/update')
    assert resp.status_code == 401

    client.post('/database_test/login', data={'username': 'jason', 'password': 'abc'})
    resp = client.get('/database_test/update')
    assert resp.status_code == 200

def test_delete(client):
    resp = client.get('/database_test/delete')
    assert resp.status_code == 401

    client.post('/database_test/login', data={'username': 'jason', 'password': 'hunter2'})
    resp = client.get('/database_test/delete')
    assert resp.status_code == 200

    resp = client.post('/database_test/delete')
    assert resp.status_code == 400

    resp = client.post('/database_test/delete', data={'a':'a'})
    assert resp.status_code == 400

    resp = client.post('/database_test/delete', data={'password':'Hunter2'})
    assert resp.status_code == 401
    assert b'red">invalid password' in resp.data

    resp = client.post('/database_test/delete', data={'password':'hunter2'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'green">delete successful' in resp.data

    resp = client.get('/database_test/delete')
    assert resp.status_code == 401

    resp = client.post('/database_test/login', data={'username': 'jason', 'password': 'hunter2'})
    assert resp.status_code == 401
    assert b'red">invalid credentials' in resp.data
