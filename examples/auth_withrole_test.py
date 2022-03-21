import pytest
from auth_withrole import create_app

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

def test_admin_feature(client):
    resp = client.post("/auth/login", data={'username':'jason', 'password':'hunter2'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'welcome jason, your role is admin' in resp.data


    resp = client.post('/user/add', data={'username': 'newuser', 'password':'newpass', 'password_confirm': 'newpass', 'role': 'no role'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'jason (admin)' in resp.data
    assert b'john (premium)' in resp.data
    assert b'james (no role)' in resp.data
    assert b'newuser (no role)' in resp.data
    assert b'green">useradd successful' in resp.data

    resp = client.get('/user/mod')
    assert resp.status_code == 400

    resp = client.get('/user/mod?id=newuser')
    assert resp.status_code == 200
    assert b'no role' in resp.data

    resp = client.post('/user/mod?id=newuser', data={'role': 'admin'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'jason (admin)' in resp.data
    assert b'john (premium)' in resp.data
    assert b'james (no role)' in resp.data
    assert b'newuser (admin)' in resp.data
    assert b'green">usermod successful' in resp.data

    resp = client.get('/user/del')
    assert resp.status_code == 400

    resp = client.get('/user/del?id=newuser')
    assert resp.status_code == 200
    assert b'remove user newuser?' in resp.data

    resp = client.post('/user/del?id=newuser', follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'newuser (admin)' not in resp.data
    assert b'green">userdel successful' in resp.data

def test_admin(client):

    resp = client.post("/auth/login", data={'username':'jason', 'password':'hunter2'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'welcome jason, your role is admin' in resp.data

    resp = client.get("/treasure")
    assert resp.status_code == 403
    assert b'Forbidden' in resp.data

    resp = client.get("/admin_only")
    assert resp.status_code == 200
    assert b'you can see this because you are an admin' in resp.data

    resp = client.get("/user/list")
    assert resp.status_code == 200
    assert b'jason (admin)' in resp.data
    assert b'john (premium)' in resp.data
    assert b'james (no role)' in resp.data

    resp = client.get("/user/add")
    assert resp.status_code == 200
    assert b'option value="admin' in resp.data
    assert b'option value="premium' in resp.data
    assert b'option value="no role' in resp.data

    resp = client.get("/user/mod?id=john")
    assert resp.status_code == 200
    assert b'"premium" selected>' in resp.data

    resp = client.get("/user/del?id=james")
    assert resp.status_code == 200
    assert b'are you sure you want to remove user james?' in resp.data

def test_premium(client):

    resp = client.post("/auth/login", data={'username':'john', 'password':'asd'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'welcome john, your role is premium' in resp.data

    resp = client.get("/treasure")
    assert resp.status_code == 200
    assert b'secret' in resp.data

    resp = client.get("/admin_only")
    assert resp.status_code == 403

    resp = client.get("/user/list")
    assert resp.status_code == 403

    resp = client.get("/user/add")
    assert resp.status_code == 403

    resp = client.get("/user/mod")
    assert resp.status_code == 403

    resp = client.get("/user/del")
    assert resp.status_code == 403


def test_norole(client):

    resp = client.post("/auth/login", data={'username':'james', 'password':'test'}, follow_redirects=True)
    assert len(resp.history) == 1
    assert resp.status_code == 200
    assert b'welcome james, your role is no role' in resp.data

    resp = client.get("/treasure")
    assert resp.status_code == 403

    resp = client.get("/admin_only")
    assert resp.status_code == 403

    resp = client.get("/user/list")
    assert resp.status_code == 403

    resp = client.get("/user/add")
    assert resp.status_code == 403

    resp = client.get("/user/mod")
    assert resp.status_code == 403

    resp = client.get("/user/del")
    assert resp.status_code == 403
