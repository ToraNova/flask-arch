import pytest
import os
import re
import tempfile
from email_account import create_app

@pytest.fixture()
def volatile_app():
    app = create_app({
        'TESTING': True,
        'PERSIST': False
    })
    yield app

@pytest.fixture()
def persist_app():
    db_fd, db_file = tempfile.mkstemp()
    db_uri = 'sqlite:///%s' % db_file
    app = create_app({
        'TESTING': True,
        'DBURI': db_uri,
        'PERSIST':True}
    )
    yield app
    os.close(db_fd)
    os.unlink(db_file)

@pytest.fixture()
def volatile_client(volatile_app):
    return volatile_app.test_client()

@pytest.fixture()
def persist_client(persist_app):
    return persist_app.test_client()

def test_2(volatile_client):
    c = volatile_client
    resp = c.post('/email_verify', data={'email':'user@domain.com'})
    assert resp.status_code == 200
    mt = re.search(b'\\?token=(\\S+)"', resp.data)
    token = mt.group(1).decode()

    resp = c.post('/auth/register', data={'username':'newuser', 'password': 'newpass', 'password_confirm': 'newpass', 'jwt':token}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'green">register successful' in resp.data

    resp = c.post('/password_reset', data={'email':'user@domain.com'})
    assert resp.status_code == 200
    mt = re.search(b'\\?token=(\\S+)"', resp.data)
    token = mt.group(1).decode()

    resp = c.post('/auth/login', data={'email':'user@domain.com', 'password': 'newpass'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'green">login successful' in resp.data

    resp = c.post('/auth/remove', data={'password': 'newpass', 'password_confirm':'newpass'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'green">remove successful' in resp.data
    assert b'login' in resp.data

    resp = c.post('/auth/reset', data={'password_new': 'hunter2', 'password_confirm': 'hunter2', 'jwt':token}, follow_redirects=True)
    assert resp.status_code == 401
    assert b'red">invalid credentials' in resp.data

def test_1(volatile_client, persist_client):

    volatile = True
    for c in [volatile_client, persist_client]:

        resp = c.get('/auth/login')
        assert resp.status_code == 200
        assert b'href="/email_verify' in resp.data

        resp = c.get('/email_verify')
        assert resp.status_code == 200
        assert b'' in resp.data

        resp = c.post('/email_verify', data={'email':'user@domain.com'})
        assert resp.status_code == 200
        mt = re.search(b'\\?token=(\\S+)"', resp.data)
        token = mt.group(1).decode()

        resp = c.get('/auth/register', data={'token':token})
        assert resp.status_code == 200

        resp = c.post('/auth/register', data={'username':'newuser', 'password': 'newpass', 'password_confirm': 'newpass'})
        assert resp.status_code == 400

        taint = token
        taint += 'z'
        resp = c.post('/auth/register', data={'username':'newuser', 'password': 'newpass', 'password_confirm': 'newpass', 'jwt':taint})
        assert resp.status_code == 400

        resp = c.post('/auth/register', data={'username':'newuser', 'password': 'newpass', 'password_confirm': 'newpass', 'token':taint})
        assert resp.status_code == 400

        resp = c.post('/auth/register', data={'username':'newuser', 'password': 'newpass', 'password_confirm': 'newpass', 'jwt':token}, follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.status_code == 200
        assert b'green">register successful' in resp.data

        resp = c.post('/auth/register', data={'username':'newuser', 'password': 'newpass', 'password_confirm': 'newpass', 'jwt':token}, follow_redirects=True)
        assert resp.status_code == 409
        if volatile:
            assert b'red">AuthUser exists' in resp.data
        else:
            assert b'red">integrity error' in resp.data

        resp = c.post('/auth/login', data={'email':'user@domain.com', 'password': 'newpass'}, follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.status_code == 200
        assert b'login success' in resp.data
        assert b'welcome newuser, your email is user@domain.com' in resp.data

        resp = c.post('/password_reset', data={'email':'user@domain.com'})
        assert resp.status_code == 200
        mt = re.search(b'\\?token=(\\S+)"', resp.data)
        token = mt.group(1).decode()

        resp = c.get('/auth/reset', data={'token':token})
        assert resp.status_code == 200

        resp = c.post('/auth/reset', data={'password_new': 'hunter2', 'password_confirm': 'hunter2'})
        assert resp.status_code == 400

        resp = c.post('/auth/reset', data={'password_new': 'hunter2', 'password_confirm': 'hunter2', 'token':token})
        assert resp.status_code == 400

        taint = token
        taint += 'z'
        resp = c.post('/auth/reset', data={'password_new': 'hunter2', 'password_confirm': 'hunter2', 'jwt':taint})
        assert resp.status_code == 401
        assert b'red">invalid token' in resp.data

        resp = c.post('/auth/reset', data={'password_new': 'hunter2', 'password_confirm': 'hunter2', 'jwt':token}, follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.status_code == 200
        assert b'green">reset successful' in resp.data

        resp = c.post('/auth/login', data={'email':'user@domain.com', 'password': 'newpass'}, follow_redirects=True)
        assert resp.status_code == 401

        resp = c.post('/auth/login', data={'email':'user@domain.com', 'password': 'hunter2'}, follow_redirects=True)
        assert len(resp.history) == 1
        assert resp.status_code == 200

        # should not be able to re-use the same token after reset successful
        resp = c.post('/auth/reset', data={'password_new': 'hunter2', 'password_confirm': 'hunter2', 'jwt':token}, follow_redirects=True)
        assert resp.status_code == 401
        assert b'red">invalid token' in resp.data

        volatile = False
