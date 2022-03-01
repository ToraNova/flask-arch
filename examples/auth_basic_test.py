import pytest
from auth_basic import create_app

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

# tests
def test_4xx(client):
    resp = client.post("/simple/login")
    assert resp.status_code == 400
    assert b'400 Bad Request' in resp.data

    resp = client.post("/simple/login", data={'username':'asd'})
    assert resp.status_code == 400

    resp = client.post("/simple/register")
    assert resp.status_code == 404

    resp = client.post("/simple/renew")
    assert resp.status_code == 404

    resp = client.post("/simple/remove")
    assert resp.status_code == 404

    resp = client.post("/iud/login")
    assert resp.status_code == 400

    resp = client.post("/iud/register")
    assert resp.status_code == 400

    resp = client.post("/iud/renew")
    assert resp.status_code == 401

    resp = client.post("/iud/remove")
    assert resp.status_code == 401

    resp = client.post("/iud/login", data={'username':'jason', 'password':'wrong'})
    assert resp.status_code == 401

    resp = client.post("/simple/login", data={'username':'jason', 'password':'wrong'})
    assert resp.status_code == 401

def test_pw_update(client):
    resp = client.get('/iud/renew')
    assert resp.status_code == 401

    resp = client.post('/iud/renew', data={'password_new':'hunter3', 'password_confirm':'hunter3', 'password_old':'hunter1'})
    assert resp.status_code == 401
    assert b'401 Unauthorized' in resp.data

    resp = client.post('/iud/login', data={'username': 'jason', 'password': 'hunter2'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'color:green">welcome back jason' in resp.data

    resp = client.get('/iud/renew')
    assert resp.status_code == 200

    resp = client.post('/iud/renew', data={'password_new':'hunter3', 'password_confirm':'hunter3', 'password_old':'hunter1'})
    assert resp.status_code == 401
    assert b'red">invalid old password' in resp.data

    resp = client.post('/iud/renew', data={'password_new':'hunter3', 'password_confirm':'hunter1', 'password_old':'hunter2'})
    assert resp.status_code == 400
    assert b'red">new password do not match' in resp.data

    resp = client.post('/iud/renew', data={'password_new':'hunter1', 'password_confirm':'hunter1', 'password_old':'hunter2'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'green">renew successful' in resp.data

    resp = client.get('/iud/logout', follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'green">logout successful' in resp.data

    resp = client.post('/iud/login', data={'username': 'jason', 'password': 'hunter1'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'color:green">welcome back jason' in resp.data

def test_delete(client):
    resp = client.get('/iud/remove')
    assert resp.status_code == 401

    resp = client.post('/iud/remove', data={'password':'hunter3'})
    assert resp.status_code == 401

    resp = client.post('/iud/login', data={'username': 'jason', 'password': 'hunter2'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'color:green">welcome back jason' in resp.data

    resp = client.get('/iud/remove')
    assert resp.status_code == 200

    resp = client.post('/iud/remove', data={'password':'hunter3'})
    assert resp.status_code == 401
    assert b'red">invalid password' in resp.data

    resp = client.post('/iud/remove', data={'password':'hunter2'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200

    resp = client.post('/iud/login', data={'username': 'jason', 'password': 'hunter2'}, follow_redirects=True)
    assert resp.status_code == 401
    assert b'red">invalid credentials' in resp.data

def test_create(client):
    resp = client.get('/iud/register')
    assert resp.status_code == 200

    resp = client.post('/iud/register', data={'username':'newuser'})
    assert resp.status_code == 400

    resp = client.post('/iud/register', data={'username':'newuser', 'password': 'newpass', 'password_confirm': 'newpass'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'green">register successful' in resp.data

    resp = client.post('/iud/register', data={'username':'newuser', 'password': 'newpass', 'password_confirm': 'newpass'}, follow_redirects=True)
    assert resp.status_code == 409
    assert b'red">AuthUser exists' in resp.data

    resp = client.post('/iud/login', data={'username': 'newuser', 'password': 'newpass'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'color:green">welcome back newuser' in resp.data

def test_login(client):

    resp = client.get('/treasure')
    assert b'secret' not in resp.data
    assert resp.status_code == 401

    resp = client.post('/simple/login', data={'username': 'jason', 'password': 'wrong'}, follow_redirects=True)
    assert resp.status_code == 401
    assert b'red">invalid credentials' in resp.data

    resp = client.post('/simple/login', data={'username': 'jason', 'password': 'hunter2'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200

    resp = client.get('/treasure')
    assert resp.status_code == 200
    assert resp.data == b'secret'

    resp = client.get('/simple/logout', follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200

    resp = client.get('/treasure')
    assert b'secret' not in resp.data
    assert resp.status_code == 401
